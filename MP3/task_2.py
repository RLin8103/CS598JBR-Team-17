import re
import jsonlines
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

#####################################################
# MP3/task_2: bug detection with DeepSeek-Coder.
# Every problem in the HumanEvalPack dataset is given with its buggy solution, so the
# expected answer is always "Buggy"; a response is correct when the model predicts it.
#####################################################

SYSTEM_PROMPT = (
    "You are an AI programming assistant. You are an AI programming assistant utilizing the DeepSeek "
    "Coder model, developed by DeepSeek Company, and you only answer questions related to computer "
    "science. For politically sensitive questions, security and privacy issues, and other "
    "non-computer science questions, you will refuse to answer."
)

VANILLA_TEMPLATE = """[CODE]

Is the above code buggy or correct? Please explain your step by step reasoning. The prediction should be enclosed within <start> and <end> tags. For example: <start>Buggy<end>"""

CRAFTED_TEMPLATE = """You are reviewing a Python function against its specification. The specification is the docstring plus the example calls listed below the code. Decide whether the implementation is buggy or correct.

Follow these steps and write every step out:

Step 1 - Requirements: list each requirement stated in the docstring as a numbered list (what is returned, in which order, with which separator, which special cases).

Step 2 - Check the examples: for every example call (the docstring examples first, then the test assertions), write the expected value given in the specification. Then execute the code on that call one statement at a time, writing the new value of a variable after every change and the result of every operation, and write the value the code returns. Compare the two values and write MATCH or MISMATCH. Trust your own trace, not the first impression that the code looks reasonable, and do not assume the expected value is wrong.

Step 3 - Check the code against the requirements: for each requirement from Step 1, point to the line that implements it. Look for: an off-by-one error in a range or loop bound, a wrong operator (`and` instead of `or`, `<` instead of `<=`, `in` instead of `not in`), a wrong variable, a wrong constant or initial value (0 instead of 1), a wrong function (floor instead of ceil, min instead of max, sorted without reverse), a missing or extra condition, a misspelled string constant, a wrong separator in join, and a wrong return expression. A requirement that no line implements is a bug.

Step 4 - Verdict: if any example is a MISMATCH, or Step 3 found a line that contradicts a requirement, the code is Buggy. Otherwise it is Correct.

Write the final verdict enclosed in <start> and <end> tags, for example <start>Buggy<end> or <start>Correct<end>. Write the tags exactly once, at the very end.

Example 1

```python
def sum_of_evens(nums):
    \"\"\" Return the sum of the even numbers in the list.
    >>> sum_of_evens([1, 2, 3, 4])
    6
    \"\"\"
    total = 0
    for x in nums:
        if x % 2 == 0:
            total += 1
    return total
```

Step 1 - Requirements:
1. Only the even numbers are used.
2. The even numbers are added up; the result is their sum.

Step 2 - Check the examples:
- sum_of_evens([1, 2, 3, 4]): expected 6.
  total = 0
  x = 1: 1 % 2 = 1, not 0, skipped
  x = 2: 2 % 2 = 0, so total = 0 + 1 = 1
  x = 3: 3 % 2 = 1, skipped
  x = 4: 4 % 2 = 0, so total = 1 + 1 = 2
  the code returns 2. Expected 6, got 2: MISMATCH

Step 3 - Check the code against the requirements:
1. Only evens: `if x % 2 == 0` implements it.
2. Sum: `total += 1` adds 1 for each even number instead of adding x. This contradicts the requirement.

Step 4 - Verdict: Step 2 has a MISMATCH and Step 3 found a wrong value, so the code is Buggy.

<start>Buggy<end>

Example 2

```python
def count_vowels(s):
    \"\"\" Return the number of vowels (a, e, i, o, u) in the string, ignoring case.
    >>> count_vowels('Hello')
    2
    >>> count_vowels('xyz')
    0
    \"\"\"
    return sum(1 for c in s.lower() if c in 'aeiou')
```

Step 1 - Requirements:
1. Count the vowels a, e, i, o, u.
2. Upper-case and lower-case letters both count.
3. Other characters are not counted.

Step 2 - Check the examples:
- count_vowels('Hello'): expected 2.
  s.lower() = 'hello'
  characters: 'h' not in 'aeiou' (0), 'e' in 'aeiou' (1), 'l' no (1), 'l' no (1), 'o' in 'aeiou' (2)
  the code returns 2. Expected 2, got 2: MATCH
- count_vowels('xyz'): expected 0.
  s.lower() = 'xyz'; 'x', 'y', 'z' are not in 'aeiou', so the sum is 0
  the code returns 0. Expected 0, got 0: MATCH

Step 3 - Check the code against the requirements:
1. 'aeiou' contains all five vowels.
2. s.lower() makes the comparison case-insensitive.
3. The condition `c in 'aeiou'` skips every other character.
No operator, constant or bound is wrong.

Step 4 - Verdict: all examples MATCH and every requirement is implemented, so the code is Correct.

<start>Correct<end>

Example 3

```python
def sum_to(n):
    \"\"\" Return the sum of the integers from 1 to n, including n.
    >>> sum_to(4)
    10
    \"\"\"
    total = 0
    for i in range(1, n):
        total += i
    return total
```

Step 1 - Requirements:
1. Add the integers from 1 up to and including n.

Step 2 - Check the examples:
- sum_to(4): expected 10.
  total = 0; range(1, 4) produces 1, 2, 3
  i = 1: total = 1
  i = 2: total = 3
  i = 3: total = 6
  the code returns 6. Expected 10, got 6: MISMATCH

Step 3 - Check the code against the requirements:
1. `range(1, n)` stops at n - 1, so n itself is never added. It should be range(1, n + 1). This is an off-by-one error.

Step 4 - Verdict: Step 2 has a MISMATCH and Step 3 found an off-by-one error, so the code is Buggy.

<start>Buggy<end>

Now review the following function in the same way.

```python
[CODE]
```

Test assertions:
[TESTS]"""

MAX_TESTS = 4
MAX_TEST_LENGTH = 200


def save_file(content, file_path):
    with open(file_path, 'w') as file:
        file.write(content)


def build_prompt(instruction):
    """DeepSeek-Coder instruct format used in the assignment's sample prompt."""
    return f"{SYSTEM_PROMPT}\n### Instruction:\n{instruction}\n### Response:\n"


def build_code(entry):
    """The function the model reviews: the original prompt (imports, signature, docstring)
    followed by the buggy body."""
    return entry["prompt"].rstrip() + "\n" + entry["buggy_solution"].rstrip()


def extract_tests(entry, limit=MAX_TESTS):
    """First assertions of the dataset's test function, in file order, without the
    failure messages. The assertions are the executable part of the specification."""
    tests = []
    for line in entry["test"].splitlines():
        line = line.strip()
        if not re.match(r"assert\s+\(?\s*(?:abs\()?\s*" + re.escape(entry["entry_point"]) + r"\(", line):
            continue
        line = re.sub(r",\s*\"[^\"]*\"\s*$", "", line)
        if len(line) <= MAX_TEST_LENGTH:
            tests.append(line)
        if len(tests) == limit:
            break
    return tests


def build_instruction(entry, vanilla):
    code = build_code(entry)
    if vanilla:
        return VANILLA_TEMPLATE.replace("[CODE]", code)
    tests = "\n".join(extract_tests(entry)) or "(none)"
    return CRAFTED_TEMPLATE.replace("[CODE]", code).replace("[TESTS]", tests)


def parse_prediction(response):
    """The last <start>Buggy<end> / <start>Correct<end> in the response, or None.
    A missing <end> tag is tolerated; the last tag wins because the model may quote the
    format from the instruction while reasoning."""
    matches = re.findall(r"<start>\s*(buggy|correct)\b", response, re.IGNORECASE)
    return matches[-1].capitalize() if matches else None


def generate_response(model, tokenizer, prompt, max_new_tokens):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    prompt_length = inputs["input_ids"].shape[1]
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(output[0, prompt_length:], skip_special_tokens=True)


def prompt_model(dataset, model_name = "deepseek-ai/deepseek-coder-6.7b-instruct", vanilla = True):
    print(f"Working with {model_name} prompt type {vanilla}...")

    # Download the tokenizer and the model.
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    # Load the model with 4-bit quantization so it fits on a Colab T4.
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
    max_new_tokens = 768 if vanilla else 1280

    results = []
    for entry in dataset:
        # Create the vanilla or crafted prompt from the buggy solution (and its tests).
        prompt = build_prompt(build_instruction(entry, vanilla))

        # Prompt the model and get the response.
        response = generate_response(model, tokenizer, prompt, max_new_tokens)

        # Every program in the dataset is buggy, so the prediction is correct only if it is "Buggy".
        prediction = parse_prediction(response)
        verdict = prediction == "Buggy"

        print(f"Task_ID {entry['task_id']}:\nprompt:\n{prompt}\nresponse:\n{response}\nprediction:\n{prediction}\nis_expected:\n{verdict}")
        results.append({
            "task_id": entry["task_id"],
            "prompt": prompt,
            "response": response,
            "is_correct": verdict
        })
        print(f"Running success rate: {sum(r['is_correct'] for r in results)}/{len(results)}", flush=True)

    correct = sum(r["is_correct"] for r in results)
    print(f"\nSuccess rate: {correct}/{len(results)} = {correct / len(results):.2%}")
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
    This Python script is to run prompt LLMs for bug detection.
    Usage:
    `python3 task_2.py <input_dataset> <model> <output_file> <if_vanilla>`|& tee prompt.log

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
