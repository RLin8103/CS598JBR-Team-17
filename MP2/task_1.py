import ast
import math
import random
import re
from collections import Counter
import jsonlines
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

#####################################################
# Please finish all TODOs in this file for MP2;
#####################################################

SYSTEM_PROMPT = (
    "You are an AI programming assistant, utilizing the DeepSeek Coder model, "
    "developed by DeepSeek Company, and you only answer questions related to computer science. "
    "For politically sensitive questions, security and privacy issues, and other non-computer "
    "science questions, you will refuse to answer."
)

VANILLA_TEMPLATE = """If the input is [INPUTS], what will the following code return?
The return value prediction must be enclosed between [Output] and [/Output] tags. For example : [Output]prediction[/Output].

[PROGRAM]"""

CRAFTED_TEMPLATE = """You will be given a Python function and a concrete function call. Predict the exact value that the call returns by simulating the execution of the code step by step, the way the Python interpreter would.

Follow these rules:
1. Start from the call and bind every parameter to its argument value.
2. Execute the statements in order. After every statement that changes a variable, write the new value of that variable.
3. Evaluate every expression one operation at a time and write each intermediate result, for example `2 + 3 * 4`: 3 * 4 = 12, then 2 + 12 = 14. Follow Python operator precedence: `**` first, then `*`, `/`, `//`, `%`, then `+` and `-`. Also write the result of every call such as abs(), min(), max(), len(), sum() and sorted().
4. For strings, list the characters explicitly and process them one at a time. `sorted()` on a string orders the characters by their Unicode code point: punctuation such as '!', '.' and '?' comes before uppercase letters, and uppercase letters come before lowercase letters.
5. Looking up a key that is not in a dictionary raises KeyError. If the lookup is inside a try block, the except branch runs instead.
6. For a recursive function, compute the results bottom-up, starting from the base cases (for example f(0), f(1), f(2), ...) until you reach the requested call.
7. For a loop with many iterations, first list the iterations in which the condition is True, then process only those iterations.
8. Do not guess the answer from the function name or from what the function is supposed to do; trust only your trace.
9. After the trace, write the final return value as a Python literal (exactly as `repr()` would print it) between [Output] and [/Output]. Write the [Output] tags exactly once, at the very end.

Example 1

Function:
```python
def score(words, table):
    total = 0
    for w in words:
        try:
            total += table[w] ** 2 * 2 - 1
        except KeyError:
            pass
    return total
```
Call: score(['a', 'zz', 'b'], {'a': 3, 'b': 1})

Trace:
- words = ['a', 'zz', 'b'], table = {'a': 3, 'b': 1}, total = 0
- w = 'a': table['a'] = 3. 3 ** 2 = 9, 9 * 2 = 18, 18 - 1 = 17. total = 0 + 17 = 17
- w = 'zz': 'zz' is not a key of table, so table['zz'] raises KeyError and the except branch runs `pass`. total stays 17
- w = 'b': table['b'] = 1. 1 ** 2 = 1, 1 * 2 = 2, 2 - 1 = 1. total = 17 + 1 = 18
- the loop ends, return total = 18

[Output]18[/Output]

Example 2

Function:
```python
def longest_a_run(s):
    run = 0
    best = 0
    for c in s:
        if c == 'a':
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best
```
Call: longest_a_run('aab aaa')

Trace:
- s = 'aab aaa', run = 0, best = 0
- the characters of s are 'a', 'a', 'b', ' ', 'a', 'a', 'a'
- c = 'a': run = 1, best = max(0, 1) = 1
- c = 'a': run = 2, best = max(1, 2) = 2
- c = 'b': c == 'a' is False, run = 0
- c = ' ': c == 'a' is False, run = 0
- c = 'a': run = 1, best = max(2, 1) = 2
- c = 'a': run = 2, best = max(2, 2) = 2
- c = 'a': run = 3, best = max(2, 3) = 3
- the loop ends, return best = 3

[Output]3[/Output]

Example 3

Function:
```python
def tri(n):
    if n <= 1:
        return n
    return tri(n - 1) + n
```
Call: tri(4)

Trace:
- tri is recursive, so compute it bottom-up from the base case.
- tri(1): 1 <= 1 is True, return 1
- tri(2) = tri(1) + 2 = 1 + 2 = 3
- tri(3) = tri(2) + 3 = 3 + 3 = 6
- tri(4) = tri(3) + 4 = 6 + 4 = 10

[Output]10[/Output]

Now do the same for the following function and call.

Function:
```python
[PROGRAM]
```
Call: [CALL]

Write the trace first, then the final answer between [Output] and [/Output]."""

# Self-consistency for the crafted prompt: one greedy answer plus sampled answers, majority vote.
NUM_SAMPLES = 4
SAMPLING_TEMPERATURE = 0.7


def save_file(content, file_path):
    with open(file_path, 'w') as file:
        file.write(content)

def build_prompt(instruction):
    return f"{SYSTEM_PROMPT}\n### Instruction:\n{instruction}\n### Response:\n"

def build_program(entry):
    """Prompt + canonical solution with docstrings removed, so the examples in the
    docstring cannot leak the expected output. Some prompts place the docstring after
    an import, so every bare string statement is removed, not only the first one."""
    tree = ast.parse(entry["prompt"] + entry["canonical_solution"])
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = [stmt for stmt in node.body
                    if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                            and isinstance(stmt.value.value, str))]
            node.body = body or [ast.Pass()]
    return ast.unparse(tree)

def extract_test_inputs(test_code):
    """Return the argument source of every `candidate(...)` call used in an assertion."""
    tree = ast.parse(test_code)
    asserts = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Assert)), key=lambda n: n.lineno)
    inputs = []
    for node in asserts:
        call = next((n for n in ast.walk(node.test)
                     if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "candidate"),
                    None)
        if call is None:
            continue
        parts = [ast.get_source_segment(test_code, arg) for arg in call.args]
        parts += [f"{kw.arg}={ast.get_source_segment(test_code, kw.value)}" for kw in call.keywords]
        inputs.append(", ".join(parts))
    return inputs

def select_test_input(entry):
    # Seeded by task_id so the vanilla and crafted runs use the same test.
    return random.Random(entry["task_id"]).choice(extract_test_inputs(entry["test"]))

def compute_expected_output(entry, inputs):
    namespace = {}
    exec(entry["prompt"] + entry["canonical_solution"], namespace)
    return eval(f"{entry['entry_point']}({inputs})", namespace)

def extract_prediction(response):
    matches = re.findall(r"\[Output\](.*?)\[\s*[/\\]\s*Output\s*\]", response, re.DOTALL | re.IGNORECASE)
    matches = [m.strip() for m in matches if m.strip() and m.strip().lower() != "prediction"]
    if matches:
        return matches[-1]
    unclosed = re.search(r"\[Output\]\s*(.+)", response, re.IGNORECASE)
    if unclosed:
        return unclosed.group(1).strip()
    return None

def clean_prediction(prediction):
    text = prediction.strip()
    text = re.sub(r"^```(?:python)?\s*|\s*```$", "", text).strip()
    text = text.strip("`").strip()
    if text.endswith(".") and not re.search(r"\d\.$", text):
        text = text[:-1].strip()
    return {"true": "True", "false": "False", "none": "None"}.get(text.lower(), text)

def prediction_candidates(prediction):
    text = clean_prediction(prediction)
    # The model sometimes echoes the call, e.g. "fib(8) == 21".
    return [text] + ([clean_prediction(text.rsplit("==", 1)[1])] if "==" in text else [])

def values_equal(predicted, expected):
    if isinstance(expected, bool) or isinstance(predicted, bool):
        return type(predicted) is type(expected) and predicted == expected
    if isinstance(expected, (int, float)) and isinstance(predicted, (int, float)):
        return math.isclose(predicted, expected, rel_tol=1e-6, abs_tol=1e-6)
    return type(predicted) is type(expected) and predicted == expected

def is_prediction_correct(prediction, expected):
    if prediction is None:
        return False
    for candidate in prediction_candidates(prediction):
        try:
            if values_equal(ast.literal_eval(candidate), expected):
                return True
        except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
            pass
        if isinstance(expected, str) and candidate == expected:
            return True
    return False

def vote_key(prediction):
    """Canonical form of a prediction, so that e.g. "'NO'" and "NO" count as the same vote."""
    if prediction is None:
        return None
    candidate = prediction_candidates(prediction)[-1]
    try:
        return repr(ast.literal_eval(candidate))
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        return repr(candidate)

def majority_vote(predictions):
    """Index of the first prediction with the most votes; the greedy answer (index 0) wins ties."""
    keys = [vote_key(p) for p in predictions]
    counts = Counter(k for k in keys if k is not None)
    if not counts:
        return 0, counts
    best = max(counts.values())
    return next(i for i, k in enumerate(keys) if k is not None and counts[k] == best), counts

def generate_responses(model, tokenizer, prompt, max_new_tokens, num_samples, seed):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    prompt_length = inputs["input_ids"].shape[1]
    common = dict(max_new_tokens=max_new_tokens, eos_token_id=tokenizer.eos_token_id,
                  pad_token_id=tokenizer.eos_token_id)
    with torch.no_grad():
        outputs = list(model.generate(**inputs, do_sample=False, **common))
        if num_samples > 0:
            torch.manual_seed(seed)
            outputs += list(model.generate(**inputs, do_sample=True, temperature=SAMPLING_TEMPERATURE,
                                           top_p=0.95, num_return_sequences=num_samples, **common))
    return [tokenizer.decode(output[prompt_length:], skip_special_tokens=True) for output in outputs]

def prompt_model(dataset, model_name = "deepseek-ai/deepseek-coder-6.7b-instruct", vanilla = True):
    print(f"Working with {model_name} prompt type {vanilla}...")
    
    # TODO: download the model
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    # TODO: load the model with quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    model.eval()
    max_new_tokens = 512 if vanilla else 2048
    num_samples = 0 if vanilla else NUM_SAMPLES

    results = []
    for index, entry in enumerate(dataset):
        # TODO: create prompt for the model
        # Tip : Use can use any data from the dataset to create 
        #       the prompt including prompt, canonical_solution, test, etc.
        program = build_program(entry)
        test_input = select_test_input(entry)
        expected_output = compute_expected_output(entry, test_input)
        if vanilla:
            instruction = VANILLA_TEMPLATE.replace("[INPUTS]", test_input).replace("[PROGRAM]", program)
        else:
            call = f"{entry['entry_point']}({test_input})"
            instruction = CRAFTED_TEMPLATE.replace("[PROGRAM]", program).replace("[CALL]", call)
        prompt = build_prompt(instruction)
        
        # TODO: prompt the model and get the response
        responses = generate_responses(model, tokenizer, prompt, max_new_tokens, num_samples, seed=index)

        # TODO: process the response and save it to results
        predictions = [extract_prediction(r) for r in responses]
        chosen, votes = majority_vote(predictions)
        response = responses[chosen]
        prediction = predictions[chosen]
        verdict = is_prediction_correct(prediction, expected_output)

        print(f"Task_ID {entry['task_id']}:\nprompt:\n{prompt}\nresponse:\n{response}\nis_correct:\n{verdict}")
        print(f"test_input: {test_input}\nexpected_output: {expected_output!r}\npredicted_output: {prediction}")
        if num_samples:
            print(f"votes: {dict(votes)}")
        print()
        result = {
            "task_id": entry["task_id"],
            "prompt": prompt,
            "response": response,
            "is_correct": verdict,
            "test_input": test_input,
            "expected_output": repr(expected_output),
            "predicted_output": prediction,
        }
        if num_samples:
            result["votes"] = dict(votes)
            result["all_responses"] = responses
        results.append(result)

    num_correct = sum(r["is_correct"] for r in results)
    print(f"Success rate: {num_correct}/{len(results)} = {num_correct / len(results):.2%}")
    return results

def read_jsonl(file_path):
    dataset = []
    with jsonlines.open(file_path) as reader:
        for line in reader: 
            dataset.append(line)
    return dataset

def write_jsonl(results, file_path):
    with jsonlines.open(file_path, "w") as f:
        for item in results:
            f.write_all([item])

if __name__ == "__main__":
    """
    This Python script is to run prompt LLMs for code synthesis.
    Usage:
    `python3 Task_1.py <input_dataset> <model> <output_file> <if_vanilla>`|& tee prompt.log

    Inputs:
    - <input_dataset>: A `.jsonl` file, which should be your team's dataset containing 20 HumanEval problems.
    - <model>: Specify the model to use. Options are "deepseek-ai/deepseek-coder-6.7b-base" or "deepseek-ai/deepseek-coder-6.7b-instruct".
    - <output_file>: A `.jsonl` file where the results will be saved.
    - <if_vanilla>: Set to 'True' or 'False' to enable vanilla prompt
    
    Outputs:
    - You can check <output_file> for detailed information.
    """
    args = sys.argv[1:]
    input_dataset = args[0]
    model = args[1]
    output_file = args[2]
    if_vanilla = args[3] # True or False
    
    if not input_dataset.endswith(".jsonl"):
        raise ValueError(f"{input_dataset} should be a `.jsonl` file!")
    
    if not output_file.endswith(".jsonl"):
        raise ValueError(f"{output_file} should be a `.jsonl` file!")
    
    vanilla = True if if_vanilla == "True" else False
    
    dataset = read_jsonl(input_dataset)
    results = prompt_model(dataset, model, vanilla)
    write_jsonl(results, output_file)
