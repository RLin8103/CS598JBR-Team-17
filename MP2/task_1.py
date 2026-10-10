import ast
import math
import random
import re
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

CRAFTED_TEMPLATE = """You will be given a Python function and a concrete function call. Predict the exact value that the call returns by simulating the execution of the code line by line, the way the Python interpreter would.

Follow these rules:
1. Start from the call and bind every parameter to its argument value.
2. Execute the statements in order. For every loop iteration, write down the loop variable and the new values of all variables that change. For every `if`/`elif`/`while` condition, write the condition with the concrete values and whether it is True or False.
3. Be careful with Python semantics: indexing starts at 0, slices and `range(a, b)` exclude the end, `//` floors, `%` follows the sign of the divisor, `sorted()` returns a new list, and the return type matters (list vs tuple, int vs float, quotes around strings).
4. Do not guess the answer from the function name or from what the function is supposed to do; trust only your trace.
5. After the trace, write the final return value as a Python literal (exactly as `repr()` would print it) between [Output] and [/Output]. Write the [Output] tags exactly once, at the very end.

Example 1

Function:
```python
def count_evens_above(nums, k):
    count = 0
    for n in nums:
        if n % 2 == 0 and n > k:
            count += 1
    return count
```
Call: count_evens_above([4, 7, 10, 2], 3)

Trace:
- nums = [4, 7, 10, 2], k = 3, count = 0
- n = 4: 4 % 2 == 0 is True and 4 > 3 is True -> count = 1
- n = 7: 7 % 2 == 0 is False -> count stays 1
- n = 10: 10 % 2 == 0 is True and 10 > 3 is True -> count = 2
- n = 2: 2 % 2 == 0 is True but 2 > 3 is False -> count stays 2
- the loop ends, return count = 2

[Output]2[/Output]

Example 2

Function:
```python
def long_words_upper(text):
    out = []
    for w in text.split():
        if len(w) > 2:
            out.append(w.upper())
    return tuple(out)
```
Call: long_words_upper("go far away")

Trace:
- text = "go far away", out = []
- text.split() = ['go', 'far', 'away']
- w = 'go': len('go') = 2, 2 > 2 is False -> out stays []
- w = 'far': len('far') = 3, 3 > 2 is True -> out = ['FAR']
- w = 'away': len('away') = 4, 4 > 2 is True -> out = ['FAR', 'AWAY']
- the loop ends, return tuple(out) = ('FAR', 'AWAY')

[Output]('FAR', 'AWAY')[/Output]

Now do the same for the following function and call.

Function:
```python
[PROGRAM]
```
Call: [CALL]

Write the trace first, then the final answer between [Output] and [/Output]."""


def save_file(content, file_path):
    with open(file_path, 'w') as file:
        file.write(content)

def build_prompt(instruction):
    return f"{SYSTEM_PROMPT}\n### Instruction:\n{instruction}\n### Response:\n"

def build_program(entry):
    """Prompt + canonical solution with docstrings removed, so the examples in the
    docstring cannot leak the expected output."""
    tree = ast.parse(entry["prompt"] + entry["canonical_solution"])
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                node.body = body[1:] or [ast.Pass()]
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

def values_equal(predicted, expected):
    if isinstance(expected, bool) or isinstance(predicted, bool):
        return type(predicted) is type(expected) and predicted == expected
    if isinstance(expected, (int, float)) and isinstance(predicted, (int, float)):
        return math.isclose(predicted, expected, rel_tol=1e-6, abs_tol=1e-6)
    return type(predicted) is type(expected) and predicted == expected

def is_prediction_correct(prediction, expected):
    if prediction is None:
        return False
    text = clean_prediction(prediction)
    try:
        if values_equal(ast.literal_eval(text), expected):
            return True
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        pass
    return isinstance(expected, str) and text == expected

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
    max_new_tokens = 512 if vanilla else 1024

    results = []
    for entry in dataset:
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
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.eos_token_id,
            )
        response = tokenizer.decode(output_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        # TODO: process the response and save it to results
        prediction = extract_prediction(response)
        verdict = is_prediction_correct(prediction, expected_output)

        print(f"Task_ID {entry['task_id']}:\nprompt:\n{prompt}\nresponse:\n{response}\nis_correct:\n{verdict}")
        print(f"test_input: {test_input}\nexpected_output: {expected_output!r}\npredicted_output: {prediction}\n")
        results.append({
            "task_id": entry["task_id"],
            "prompt": prompt,
            "response": response,
            "is_correct": verdict,
            "test_input": test_input,
            "expected_output": repr(expected_output),
            "predicted_output": prediction,
        })

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
