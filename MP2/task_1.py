import ast
import math
import os
import random
import re
from collections import Counter
import jsonlines
import sys

# Colab T4 runtimes have about 15 GiB of VRAM.  Let PyTorch grow CUDA memory
# segments instead of reserving inflexible blocks when successive generations
# have different sequence lengths.  This must be set before importing torch.
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

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
3. Evaluate every expression one operation at a time and write each intermediate result, for example `2 + 3 * 4`: 3 * 4 = 12, then 2 + 12 = 14. Follow Python operator precedence: `**` first, then `*`, `/`, `//`, `%`, then `+` and `-`. Also write the result of every call such as abs(), min(), max(), len(), sum() and sorted(). For a list comprehension or generator expression, process the elements one at a time and write the value produced for each element.
4. For strings, list the characters explicitly and process them one at a time. When checking `x in [...]` or `x not in [...]`, compare x with the listed elements explicitly. `s.split(' ')` splits at every single space and consecutive spaces produce empty strings '', while `s.split()` splits on runs of whitespace. `sorted()` on a string orders the characters by their Unicode code point: punctuation such as '!', '.' and '?' comes before uppercase letters, and uppercase letters come before lowercase letters.
5. Before looking up a key in a dictionary, check whether it is one of the dictionary's keys. Looking up a missing key raises KeyError. If the lookup is inside a try block, the except branch runs instead.
6. For a recursive function, compute the results bottom-up, starting from the base cases (for example f(0), f(1), f(2), ...) until you reach the requested call.
7. For a loop with many iterations, first list the values of the loop variable for which the condition is True, then process only those iterations.
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
- w = 'zz': the keys of table are 'a' and 'b'; 'zz' is not one of them, so table['zz'] raises KeyError and the except branch runs `pass`. total stays 17
- w = 'b': table['b'] = 1. 1 ** 2 = 1, 1 * 2 = 2, 2 - 1 = 1. total = 17 + 1 = 18
- the loop ends, return total = 18

[Output]18[/Output]

Example 2

Function:
```python
def longest_ab_run(s):
    run = 0
    best = 0
    for c in s:
        if c.lower() in ['a', 'b']:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best
```
Call: longest_ab_run('Ab cab')

Trace:
- s = 'Ab cab', run = 0, best = 0
- the characters of s are 'A', 'b', ' ', 'c', 'a', 'b'
- c = 'A': 'A'.lower() = 'a'; 'a' is equal to 'a', so 'a' in ['a', 'b'] is True. run = 1, best = max(0, 1) = 1
- c = 'b': 'b'.lower() = 'b'; 'b' is equal to 'b', so 'b' in ['a', 'b'] is True. run = 2, best = max(1, 2) = 2
- c = ' ': ' ' is not equal to 'a' or 'b', so ' ' in ['a', 'b'] is False. run = 0
- c = 'c': 'c' is not equal to 'a' or 'b', so 'c' in ['a', 'b'] is False. run = 0
- c = 'a': 'a' in ['a', 'b'] is True. run = 1, best = max(2, 1) = 2
- c = 'b': 'b' in ['a', 'b'] is True. run = 2, best = max(2, 2) = 2
- the loop ends, return best = 2

[Output]2[/Output]

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

Example 4

Function:
```python
def gaps(text, m):
    return [abs(len(w) - m) for w in text.split(' ') if w]
```
Call: gaps('ab  cde f', 2)

Trace:
- text = 'ab  cde f', m = 2
- text.split(' ') splits at every single space; there are two spaces after 'ab', so the result is ['ab', '', 'cde', 'f']
- w = 'ab': 'ab' is not empty, so it is kept. len('ab') = 2, 2 - 2 = 0, abs(0) = 0
- w = '': '' is empty, so `if w` is False and it is skipped
- w = 'cde': len('cde') = 3, 3 - 2 = 1, abs(1) = 1
- w = 'f': len('f') = 1, 1 - 2 = -1, abs(-1) = 1
- the list is [0, 1, 1]

[Output][0, 1, 1][/Output]

Example 5

Function:
```python
def count_threes(n):
    total = 0
    for i in range(n):
        if i % 6 == 0 or i % 9 == 0:
            total += str(i).count('3')
    return total
```
Call: count_threes(40)

Trace:
- n = 40, total = 0. range(40) has 40 iterations, so first list the values of i for which the condition is True.
- i % 6 == 0 for i = 0, 6, 12, 18, 24, 30, 36
- i % 9 == 0 for i = 0, 9, 18, 27, 36
- the condition is True for i = 0, 6, 9, 12, 18, 24, 27, 30, 36
- str(i).count('3') is 0 for '0', '6', '9', '12', '18', '24', '27'; it is 1 for '30' and 1 for '36'
- total = 0 + 1 + 1 = 2

[Output]2[/Output]

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

# When the first-pass answers disagree, use a second, independently worded prompt to
# audit the candidate values.  A majority vote alone is unsafe for code execution:
# several independent samples can repeat the same arithmetic or indexing mistake.
AUDIT_NUM_SAMPLES = 2
AUDIT_SAMPLING_TEMPERATURE = 0.25

AUDIT_TEMPLATE = """Act as a meticulous Python execution auditor. Several attempts predicted different return values for the same call. Their answers are untrusted suggestions, not evidence; do not select an answer by popularity. Independently execute the code and correct every proposal that conflicts with Python semantics.

Use this audit procedure:
1. Bind the arguments, then execute the exact code in statement order. Do not infer behavior from the function name or docstring.
2. For every loop, comprehension, recursion level, slice, and string operation, write the concrete intermediate values. Preserve list and string order exactly.
3. Check arithmetic with a second calculation. For division or averages, keep an exact numerator and denominator until the final step.
4. Check dictionary membership using the literal keys. A missing lookup raises KeyError even when the number resembles a valid key (for example, 55 is not key 5).
5. For sorted strings, explicitly write the sorted characters of every word using Python/Unicode ordering, then join them.
6. Before finishing, compare the final value against the return expression and independently audit its type, delimiters, quoting, and element order.

Function:
```python
[PROGRAM]
```
Call: [CALL]

Distinct proposed outputs:
[CANDIDATES]

Write a concise audit trace. You may return a value that is not among the proposals. End with the exact Python `repr()` of the return value between [Output] and [/Output]. Write those tags exactly once, at the very end."""


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
    # Accept the common formatting slip `[Output]: value[/Output]` without
    # treating the colon as part of the predicted Python value.
    text = re.sub(r"^:\s*", "", text)
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
    # Code placeholders are not return values and must not win a vote merely
    # because multiple generations repeat the same formatting error.
    if candidate.startswith("#") or re.fullmatch(r"(?:repr|print)\s*\(.*\)(?:\s*#.*)?", candidate):
        return None
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


def has_unique_plurality(votes, minimum_votes=2):
    """Whether exactly one proposed value has meaningful first-pass support."""
    if not votes:
        return False
    best = max(votes.values())
    return best >= minimum_votes and sum(count == best for count in votes.values()) == 1


def reached_vote_threshold(responses, threshold):
    """Return True once a value has enough votes that remaining samples cannot beat it."""
    if threshold is None:
        return False
    counts = Counter(vote_key(extract_prediction(response)) for response in responses)
    counts.pop(None, None)
    return bool(counts) and max(counts.values()) >= threshold

def build_audit_prompt(program, call, votes):
    """Create a fresh verification prompt without revealing the computed ground truth."""
    candidates = "\n".join(
        f"- Candidate {index}: {candidate}"
        for index, candidate in enumerate(votes, start=1)
    )
    return AUDIT_TEMPLATE.replace("[PROGRAM]", program).replace("[CALL]", call).replace(
        "[CANDIDATES]", candidates
    )


def generate_responses(model, tokenizer, prompt, max_new_tokens, num_samples, seed,
                       temperature=SAMPLING_TEMPERATURE, early_stop_votes=None):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    prompt_length = inputs["input_ids"].shape[1]
    common = dict(max_new_tokens=max_new_tokens, eos_token_id=tokenizer.eos_token_id,
                  pad_token_id=tokenizer.eos_token_id)
    responses = []

    def generate_and_decode(**generation_options):
        output = model.generate(**inputs, **generation_options, **common)
        response = tokenizer.decode(output[0, prompt_length:], skip_special_tokens=True)
        del output
        return response

    with torch.no_grad():
        responses.append(generate_and_decode(do_sample=False))

        # Generate samples sequentially.  Asking generate() for several return
        # sequences at once duplicates the attention KV cache and exhausted the
        # 14.56-GiB T4 in Colab.  Per-sample seeding keeps runs reproducible while
        # preserving diverse candidates without the parallel VRAM spike.
        for sample_index in range(num_samples):
            torch.manual_seed(seed * 1_000 + sample_index)
            responses.append(generate_and_decode(
                do_sample=True,
                temperature=temperature,
                top_p=0.95,
                num_return_sequences=1,
            ))
            if reached_vote_threshold(responses, early_stop_votes):
                break

    return responses

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
    max_new_tokens = 512 if vanilla else 1536
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
        responses = generate_responses(
            model,
            tokenizer,
            prompt,
            max_new_tokens,
            num_samples,
            seed=index,
            # Three matching answers already guarantee the winner of a five-answer vote.
            early_stop_votes=3 if not vanilla else None,
        )

        # TODO: process the response and save it to results
        predictions = [extract_prediction(r) for r in responses]
        chosen, votes = majority_vote(predictions)
        response = responses[chosen]
        prediction = predictions[chosen]
        final_prompt = prompt
        audit_responses = []
        audit_votes = Counter()

        # Only use the audit to break a first-pass tie or all-unique result.  Earlier
        # runs showed that an uncertain audit could replace a correct plurality.
        # The expected output is never included in either prompt or this decision.
        if not vanilla and len(votes) > 1 and not has_unique_plurality(votes):
            call = f"{entry['entry_point']}({test_input})"
            audit_instruction = build_audit_prompt(program, call, votes)
            final_prompt = build_prompt(audit_instruction)
            audit_responses = generate_responses(
                model,
                tokenizer,
                final_prompt,
                max_new_tokens=1024,
                num_samples=AUDIT_NUM_SAMPLES,
                seed=10_000 + index,
                temperature=AUDIT_SAMPLING_TEMPERATURE,
                # Two matching answers already guarantee the winner of a three-answer vote.
                early_stop_votes=2,
            )
            audit_predictions = [extract_prediction(r) for r in audit_responses]
            audit_chosen, audit_votes = majority_vote(audit_predictions)
            if audit_predictions[audit_chosen] is not None:
                response = audit_responses[audit_chosen]
                prediction = audit_predictions[audit_chosen]

        verdict = is_prediction_correct(prediction, expected_output)

        print(f"Task_ID {entry['task_id']}:\nprompt:\n{final_prompt}\nresponse:\n{response}\nis_correct:\n{verdict}")
        print(f"test_input: {test_input}\nexpected_output: {expected_output!r}\npredicted_output: {prediction}")
        if num_samples:
            print(f"initial_votes: {dict(votes)}")
        if audit_responses:
            print(f"audit_votes: {dict(audit_votes)}")
        print()
        result = {
            "task_id": entry["task_id"],
            "prompt": final_prompt,
            "response": response,
            "is_correct": verdict,
            "test_input": test_input,
            "expected_output": repr(expected_output),
            "predicted_output": prediction,
        }
        if num_samples:
            result["initial_prompt"] = prompt
            result["initial_votes"] = dict(votes)
            result["initial_responses"] = responses
            # Keep the original diagnostic field names for compatibility with
            # notebooks written against the earlier crafted-run schema.
            result["votes"] = dict(audit_votes) if audit_responses else dict(votes)
            result["all_responses"] = audit_responses if audit_responses else responses
        if audit_responses:
            result["audit_votes"] = dict(audit_votes)
            result["audit_responses"] = audit_responses
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
