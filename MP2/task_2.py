import jsonlines
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

import ast
import importlib.util
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
#####################################################
# Please finish all TODOs in this file for MP2;
#####################################################
#Constants
SYSTEM_PROMPT = ( "You are an AI programming assistant. You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, "
"and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer" )
NUM_TESTS = 15
MAX_TOKENS = 2048
FEEDBACK_ROUNDS = 1
PYTEST_TIMEOUT = 120

#helper functions
def wrap(instruction):
    # DeepSeek Coder instruct format
    return f"{SYSTEM_PROMPT}\n### Instruction:\n{instruction}\n### Response:\n"
 
def ask(tokenizer, model, prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_TOKENS,
            do_sample=False,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
 
def top_level_names(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()
    return {n.name for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
 
def strip_docstrings(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
                node.body = body[1:] or [ast.Pass()]
    return ast.unparse(tree)
 
def example_assertion(entry):
    for line in entry["test"].splitlines():
        line = line.strip()
        if line.startswith("assert") and "candidate(" in line:
            return re.sub(r"\bcandidate\b", entry["entry_point"], line)
    return None
 
def extract_code(text):
    blocks = re.findall(r"```(?:python|py)?[^\n]*\n(.*?)```", text, re.DOTALL)
    if blocks:
        useful = [b for b in blocks if "def test" in b or "assert" in b]
        return "\n\n".join(useful or blocks)
    if "```" in text:  # code block opened but cut off by the token limit
        after = text.split("```", 1)[1]
        return after.split("\n", 1)[1] if "\n" in after else after
    return text
 
def parse_lenient(code):
    # try to parse the code, dropping lines from the end until it parses or is empty
    lines = code.splitlines()
    while lines:
        try:
            return ast.parse("\n".join(lines))
        except SyntaxError:
            lines.pop()
    return None
 
def module_available(name):
    if not name:
        return False
    try:
        return importlib.util.find_spec(name.split(".")[0]) is not None
    except (ImportError, ValueError):
        return False
 
def clean_tests(text, module, program):
    # keep only the model's tests drop copies of the function, fake imports, main guards
    program_names = top_level_names(program)
    tree = parse_lenient(extract_code(text))
    body = []
    if tree is not None:
        for node in tree.body:
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    and node.name in program_names):
                continue
            if isinstance(node, ast.ImportFrom):
                imported = {a.name for a in node.names}
                if (node.module == module or imported & program_names or not module_available(node.module)):
                    continue
            if isinstance(node, ast.Import):
                node.names = [a for a in node.names if a.name != "pytest" and module_available(a.name)]
                if not node.names:
                    continue
            if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__"):
                continue
            body.append(node)
    return body
 
def render_tests(body, module):
    header = f"import pytest\nfrom {module} import *\n\n"
    return header + ast.unparse(ast.Module(body=body, type_ignores=[])) + "\n"
 
def merge_tests(base_body, new_body):
    # new tests are added; a test with an existing name replaces the old one
    merged = list(base_body)
    index = {n.name: i for i, n in enumerate(merged)
                if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    seen = {ast.unparse(n) for n in merged if isinstance(n, (ast.Import, ast.ImportFrom))}
    for node in new_body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in index:
            merged[index[node.name]] = node
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if ast.unparse(node) not in seen:
                merged.insert(0, node)
                seen.add(ast.unparse(node))
        else:
            merged.append(node)
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                index[node.name] = len(merged) - 1
    return merged
 
def run_tests(module, program, test_code, mode):
    mp2_dir = os.path.dirname(os.path.abspath(__file__))
    coverage_dir = os.path.join(mp2_dir, "Coverage")
    run_dir = os.path.join(mp2_dir, "GeneratedTests", mode)
    os.makedirs(coverage_dir, exist_ok=True)
    os.makedirs(run_dir, exist_ok=True)
    save_file(program, os.path.join(run_dir, f"{module}.py"))
    save_file(test_code, os.path.join(run_dir, f"{module}_test.py"))
    cov_json = os.path.join(coverage_dir, f"{module}_test_{mode}.json")
    junit = os.path.join(run_dir, f"{module}_junit.xml")
    for stale in (cov_json, junit, os.path.join(run_dir, ".coverage")):
        if os.path.exists(stale):
            os.remove(stale)
    cmd = [sys.executable, "-m", "pytest", f"{module}_test.py","--cov", module, "--cov-report", f"json:{cov_json}",f"--junitxml={junit}", "-q", "-p", "no:cacheprovider", "--rootdir", run_dir]
    try:
        proc = subprocess.run(cmd, cwd=run_dir, capture_output=True, text=True,timeout=PYTEST_TIMEOUT)
        pytest_output = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        pytest_output = f"pytest timed out after {PYTEST_TIMEOUT}s"
 
    cov, missing = 0.0, []
    if os.path.exists(cov_json):
        with open(cov_json) as f:
            report = json.load(f)
        cov = round(report.get("totals", {}).get("percent_covered", 0.0), 2)
        for path, info in report.get("files", {}).items():
            if os.path.basename(path) == f"{module}.py":
                missing = info.get("missing_lines", [])
    else:
        save_file(json.dumps({"meta": {"note": "no coverage, generated tests did not run"},"files": {}, "totals": {"percent_covered": 0.0}}, indent=2),cov_json)
 
    tests = failed = errors = skipped = 0
    failures = []
    if os.path.exists(junit):
        root = ET.parse(junit).getroot()
        suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
        for s in suites:
            tests += int(s.get("tests", 0))
            failed += int(s.get("failures", 0))
            errors += int(s.get("errors", 0))
            skipped += int(s.get("skipped", 0))
        for case in root.iter("testcase"):
            bad = case.find("failure")
            if bad is None:
                bad = case.find("error")
            if bad is not None:
                msg = (bad.get("message") or "").replace("\n", " ")[:200]
                failures.append((case.get("name"), msg))
 
    return {"coverage": cov, "missing_lines": missing, "num_tests": tests,
            "num_passed": tests - failed - errors - skipped,
            "num_failed": failed + errors, "failures": failures,
            "pytest_output": pytest_output[-3000:]}
 
def save_file(content, file_path):
    with open(file_path, 'w') as file:
        file.write(content)

def prompt_model(dataset, model_name = "deepseek-ai/deepseek-coder-6.7b-instruct", vanilla = True):
    print(f"Working with {model_name} prompt type {vanilla}...")
    
    # TODO: download the model
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    # TODO: load the model with quantization
    mode = "vanilla" if vanilla else "crafted"
    run_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GeneratedTests", mode)
    os.makedirs(run_dir, exist_ok=True)

    results = []
    for entry in dataset:
        # TODO: create prompt for the model
        # Tip : Use can use any data from the dataset to create 
        #       the prompt including prompt, canonical_solution, test, etc.
        module = entry["task_id"].replace("/", "_")   # HumanEval/132 -> HumanEval_132
        fn = entry["entry_point"]
        program = entry["prompt"] + entry["canonical_solution"]
 
        if vanilla:
            prompt = wrap(
                "Generate a pytest test suite for the following code.\n"
                "Only write unit tests in the output and nothing else.\n"
                f"{strip_docstrings(program)}"
            )
        else:
            example = example_assertion(entry)
            example_block = ""
            if example:
                example_block = (
                    "Here is one known-correct test you can use as a model for the format "
                    "and the expected values:\n"
                    f"```python\ndef test_example():\n    {example}\n```\n\n"
                )
            prompt = wrap(
                f"Write a pytest test suite for the Python function `{fn}` shown below. "
                "The goal is 100% line and branch coverage with tests that pass.\n\n"
                f"The function already exists in a module named `{module}`. The test file will "
                f"start with `from {module} import *`. Do NOT redefine `{fn}`, do NOT copy its "
                "code, and do NOT import it from any other module.\n\n"
                "Follow these steps:\n"
                "1. Read the docstring to understand what the function should do.\n"
                "2. List every branch in the code: each if/elif/else, each loop running zero, "
                "one, and many times, each early return, and each exception that can be raised.\n"
                "3. For each branch, choose a concrete input that reaches it. Also include edge "
                "cases such as empty inputs, a single element, zero, negative numbers, and "
                "boundary values.\n"
                "4. For each input, trace the code line by line to compute the exact return "
                "value. The code is correct, so the expected value must be what the code "
                "actually returns, not what you guess.\n"
                f"5. Write exactly {NUM_TESTS} test functions named test_<something>. Use "
                "pytest.approx for floats and pytest.raises only if the code really raises.\n\n"
                f"{example_block}"
                f"Code:\n```python\n{program}\n```\n\n"
                "After your analysis, output ONE ```python code block containing the complete "
                "test file."
            )
        
        # TODO: prompt the model and get the response
        
        response = ask(tokenizer, model,prompt)

        # TODO: process the response, generate coverage and save it to results
        body = clean_tests(response, module, program)
        test_code = render_tests(body, module)
        r = run_tests(module, program, test_code, mode)
        print(f"[{entry['task_id']}] first run: coverage {r['coverage']}, "
              f"{r['num_passed']}/{r['num_tests']} tests pass, missing lines {r['missing_lines']}")
 
        feedback = []
        if not vanilla:
            for round_num in range(1, FEEDBACK_ROUNDS + 1):
                if not r["missing_lines"] and not r["failures"]:
                    break
                numbered = "\n".join(f"{i:>3}: {l}" for i, l in
                                     enumerate(program.splitlines(), start=1))
                parts = [
                    f"Below is the Python function `{fn}` (module `{module}`) with line numbers, "
                    "and a pytest test suite for it.\n",
                    f"Code:\n```\n{numbered}\n```\n",
                    f"Current tests:\n```python\n{test_code}\n```\n",
                ]
                if r["missing_lines"]:
                    parts.append(
                        "The coverage report shows these lines are never executed by the tests: "
                        f"{', '.join(map(str, r['missing_lines']))}. Write NEW test functions whose "
                        "inputs make the code execute those lines. Trace the code to get the exact "
                        "expected values.\n"
                    )
                if r["failures"]:
                    fail_text = "\n".join(f"- {name}: {msg}" for name, msg in r["failures"])
                    parts.append(
                        "These tests FAIL because their expected values are wrong (the code is "
                        f"correct):\n{fail_text}\nFor each one, trace the code carefully and write "
                        "a corrected version with the SAME function name.\n"
                    )
                parts.append(
                    f"Do not redefine `{fn}`. Output ONE ```python code block that contains only "
                    "the new and corrected test functions."
                )
                fb_prompt = wrap("\n".join(parts))
                fb_response = ask(tokenizer, model, fb_prompt)
                body = merge_tests(body, clean_tests(fb_response, module, program))
                test_code = render_tests(body, module)
                before = r["coverage"]
                r = run_tests(module, program, test_code, mode)
                feedback.append({"prompt": fb_prompt, "response": fb_response,
                                 "coverage_before": before, "coverage_after": r["coverage"]})
                print(f"[{entry['task_id']}] feedback round {round_num}:\nprompt:\n{fb_prompt}\n"
                      f"response:\n{fb_response}\ncoverage {before} -> {r['coverage']}")
 
        coverage = r["coverage"]

        print(f"[{entry['task_id']}] final: {r['num_tests']} tests, {r['num_passed']} pass, "
              f"{r['num_failed']} fail, missing lines {r['missing_lines']}")
        print(f"final test file:\n{test_code}\npytest output:\n{r['pytest_output']}")
 
        save_file(json.dumps({
            "task_id": entry["task_id"], "coverage": coverage,
            "num_tests": r["num_tests"], "num_passed": r["num_passed"],
            "num_failed": r["num_failed"], "missing_lines": r["missing_lines"],
            "failures": r["failures"], "test_code": test_code, "feedback": feedback,
        }, indent=2), os.path.join(run_dir, f"{module}_stats.json"))
 
        print(f"Task_ID {entry['task_id']}:\nprompt:\n{prompt}\nresponse:\n{response}\ncoverage:\n{coverage}")
        results.append({
            "task_id": entry["task_id"],
            "prompt": prompt,
            "response": response,
            "coverage": coverage
        })
 
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