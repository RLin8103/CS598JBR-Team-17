import ast
import math
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

# Crafted prompting is a two-stage pipeline.
#  Stage 1 (execution check): for several example calls taken from the tests, the model
#  simulates the execution of the code (docstring removed, so that it follows the code and
#  not the intended behaviour) and its predicted return value is compared with the
#  expected value.  Stage 2 (review): the model gets the execution report and explains
#  whether the code is buggy.
SIMULATION_TEMPLATE = """You will be given a Python function and a concrete function call. Predict the exact value that the call returns by simulating the execution of the code step by step, the way the Python interpreter would.

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

REVIEW_TEMPLATE = """You are reviewing a Python function against its specification, which is its docstring.

An execution check was run on the code. For several example calls taken from the tests of the specification, the value that the code returns was worked out by simulating its execution, and it was compared with the expected value.

Follow these steps and write every step out:

Step 1 - Requirements: list each requirement stated in the docstring as a numbered list.

Step 2 - Execution report: for every MISMATCH in the report, find the line of the code that makes the returned value differ from the expected value and say which requirement it violates. The simulated values can contain arithmetic mistakes, so re-check each MISMATCH once by tracing that call yourself before you rely on it.

Step 3 - Check the code against the requirements: for each requirement from Step 1, point to the line that implements it. Look for: an off-by-one error in a range or loop bound, a wrong operator (`and` instead of `or`, `<` instead of `<=`, `in` instead of `not in`), a wrong variable, a wrong constant or initial value (0 instead of 1), a wrong function (floor instead of ceil, sorted without reverse), a missing condition (for example a helper function that is defined but never used), a misspelled string constant, and a wrong separator in join. A requirement that no line implements is a bug.

Step 4 - Verdict: if a MISMATCH is confirmed, or Step 3 found a line that contradicts a requirement, the code is Buggy. Otherwise it is Correct.

Write the final verdict enclosed in <start> and <end> tags, for example <start>Buggy<end> or <start>Correct<end>. Write the tags exactly once, at the very end.

Example 1

Code:
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

Execution report:
- sum_to(4): expected 10, the code returned 6: MISMATCH
- sum_to(1): expected 1, the code returned 0: MISMATCH

Step 1 - Requirements:
1. Add the integers from 1 up to and including n.

Step 2 - Execution report:
- sum_to(4): range(1, 4) produces 1, 2, 3, so total = 1 + 2 + 3 = 6, not 10. The MISMATCH is confirmed.
  The line `for i in range(1, n)` stops at n - 1, so n is never added. This violates requirement 1.
- sum_to(1): range(1, 1) is empty, so total stays 0, not 1. The MISMATCH is confirmed.

Step 3 - Check the code against the requirements:
1. `range(1, n)` should be `range(1, n + 1)`. This is an off-by-one error.

Step 4 - Verdict: a MISMATCH is confirmed and Step 3 found an off-by-one error, so the code is Buggy.

<start>Buggy<end>

Example 2

Code:
```python
def count_vowels(s):
    \"\"\" Return the number of vowels (a, e, i, o, u) in the string, ignoring case.
    >>> count_vowels('Hello')
    2
    \"\"\"
    return sum(1 for c in s.lower() if c in 'aeiou')
```

Execution report:
- count_vowels('Hello'): expected 2, the code returned 2: MATCH
- count_vowels('xyz'): expected 0, the code returned 0: MATCH

Step 1 - Requirements:
1. Count the vowels a, e, i, o, u.
2. Upper-case and lower-case letters both count.
3. Other characters are not counted.

Step 2 - Execution report: there is no MISMATCH in the report.

Step 3 - Check the code against the requirements:
1. 'aeiou' contains all five vowels.
2. s.lower() makes the comparison case-insensitive.
3. The condition `c in 'aeiou'` skips every other character.
Every requirement is implemented by a line and no operator, constant or bound is wrong.

Step 4 - Verdict: there is no MISMATCH and every requirement is implemented, so the code is Correct.

<start>Correct<end>

Now review the following function in the same way.

Code:
```python
[CODE]
```

Execution report:
[REPORT]"""

MAX_TESTS = 5
MAX_CALL_LENGTH = 300
SIMULATION_MAX_NEW_TOKENS = 1024
REVIEW_MAX_NEW_TOKENS = 800


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


def build_program(entry):
    """The buggy function without docstrings.  Every bare string statement is removed (some
    prompts put the docstring after an import), so that the simulation follows the code."""
    tree = ast.parse(build_code(entry))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = [stmt for stmt in node.body
                    if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                            and isinstance(stmt.value.value, str))]
            node.body = body or [ast.Pass()]
    return ast.unparse(tree)


def expected_of_assertion(test, call):
    """The value that an assertion expects from `call`, or None if the form is unsupported."""
    try:
        if isinstance(test, ast.Compare) and len(test.ops) == 1:
            left, right = test.left, test.comparators[0]
            if isinstance(test.ops[0], ast.Eq):
                if left is call:
                    return (eval(ast.unparse(right), {}),)
                if right is call:
                    return (eval(ast.unparse(left), {}),)
            # assert abs(f(x) - y) < tolerance
            if (isinstance(test.ops[0], ast.Lt) and isinstance(left, ast.Call)
                    and isinstance(left.func, ast.Name) and left.func.id == "abs"
                    and len(left.args) == 1 and isinstance(left.args[0], ast.BinOp)
                    and isinstance(left.args[0].op, ast.Sub) and left.args[0].left is call):
                return (eval(ast.unparse(left.args[0].right), {}),)
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) and test.operand is call:
            return (False,)
        if test is call:
            return (True,)
    except Exception:
        pass
    return None


def extract_test_calls(entry, limit=MAX_TESTS):
    """(call, expected value) pairs of the assertions in the dataset's test function, spread
    evenly over the test so that simple and complex inputs are both covered."""
    source = entry["test"]
    tree = ast.parse(source)
    pairs = []
    for node in sorted((n for n in ast.walk(tree) if isinstance(n, ast.Assert)), key=lambda n: n.lineno):
        calls = [n for n in ast.walk(node.test)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == entry["entry_point"]]
        if not calls:
            continue
        expected = expected_of_assertion(node.test, calls[0])
        call = ast.unparse(calls[0])
        if expected is None or len(call) > MAX_CALL_LENGTH or any(call == c for c, _ in pairs):
            continue
        pairs.append((call, expected[0]))
    if len(pairs) <= limit:
        return pairs
    return [pairs[round(i * (len(pairs) - 1) / (limit - 1))] for i in range(limit)]


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


def parse_prediction(response):
    """The last <start>Buggy<end> / <start>Correct<end> in the response, or None.
    A missing <end> tag is tolerated; the last tag wins because the model may quote the
    format from the instruction while reasoning."""
    matches = re.findall(r"<start>\s*(buggy|correct)\b", response, re.IGNORECASE)
    return matches[-1].capitalize() if matches else None


def build_report(checks):
    lines = []
    for check in checks:
        if check["match"] is None:
            outcome = "the return value could not be determined: UNKNOWN"
        else:
            outcome = f"the code returned {check['simulated']}: {'MATCH' if check['match'] else 'MISMATCH'}"
        lines.append(f"- {check['call']}: expected {check['expected']}, {outcome}")
    return "\n".join(lines) or "- (no example calls available)"


def build_instruction(entry, vanilla, checks=None):
    if vanilla:
        return VANILLA_TEMPLATE.replace("[CODE]", build_code(entry))
    return REVIEW_TEMPLATE.replace("[CODE]", build_code(entry)).replace("[REPORT]", build_report(checks))


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


def run_execution_check(model, tokenizer, entry):
    """Stage 1: simulate the buggy code on example calls and compare with the expected values."""
    program = build_program(entry)
    checks, simulations = [], []
    for call, expected in extract_test_calls(entry):
        prompt = build_prompt(SIMULATION_TEMPLATE.replace("[PROGRAM]", program).replace("[CALL]", call))
        response = generate_response(model, tokenizer, prompt, SIMULATION_MAX_NEW_TOKENS)
        prediction = extract_prediction(response)
        match = None if prediction is None else is_prediction_correct(prediction, expected)
        simulated = None if prediction is None else clean_prediction(prediction)
        checks.append({"call": call, "expected": repr(expected), "simulated": simulated, "match": match})
        simulations.append({"call": call, "response": response})
        print(f"  execution check {call}\n  expected {expected!r}, simulated {simulated!r}: {match}", flush=True)
    return checks, simulations


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

    results = []
    for entry in dataset:
        extra = {}
        if vanilla:
            # Vanilla prompt: the buggy code and the question.
            prompt = build_prompt(build_instruction(entry, True))
            response = generate_response(model, tokenizer, prompt, 768)
        else:
            # Crafted prompt, stage 1: execution check; stage 2: review with the report.
            print(f"Task_ID {entry['task_id']}: execution check", flush=True)
            checks, simulations = run_execution_check(model, tokenizer, entry)
            prompt = build_prompt(build_instruction(entry, False, checks))
            response = generate_response(model, tokenizer, prompt, REVIEW_MAX_NEW_TOKENS)
            extra = {"execution_report": checks, "simulations": simulations}

        # Every program in the dataset is buggy, so the prediction is correct only if it is "Buggy".
        prediction = parse_prediction(response)
        verdict = prediction == "Buggy"

        print(f"Task_ID {entry['task_id']}:\nprompt:\n{prompt}\nresponse:\n{response}\nprediction:\n{prediction}\nis_expected:\n{verdict}")
        results.append({
            "task_id": entry["task_id"],
            "prompt": prompt,
            "response": response,
            "is_correct": verdict,
            **extra,
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
