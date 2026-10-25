"""Translate the selected Python solutions to Java and run the Java tests."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


DEFAULT_MODEL = "deepseek-ai/deepseek-coder-6.7b-instruct"
# Keep decoding settings fixed across both prompt versions.
GENERATION_CONFIG = {
    "max_new_tokens": 1024,
    "do_sample": False,
    "num_beams": 1,
    "num_return_sequences": 1,
}
COMPILE_TIMEOUT = 30
RUN_TIMEOUT = 5
JAVA_RELEASE = 17

VANILLA_TEMPLATE = """Can you translate the following Python code into Java?
The new Java code must be enclosed between [Java Start] and [Java End].

{source}"""

CRAFTED_TEMPLATE = """Translate the following Python implementation into Java, preserving its behavior.

Requirements:
1. Implement the exact Java method name, parameter types, and return type in the target declaration below. Return a complete class named Solution with the needed standard-library imports. Do not include a main method or tests.
2. Preserve the Python implementation's control flow and edge cases, including empty inputs, duplicates, boundary conditions, and negative numbers. Use the implementation as the source of truth.
3. Check differences between Python and Java: integer versus floating-point division, floor division and modulo for negative operands, numeric overflow, string equality, character indexing, slicing bounds, and collection types. Use .equals() for string values. Translate Python operations explicitly when Java's behavior differs.
4. Check that every return value and collection element has the required Java type. Include helper methods inside Solution if needed.
5. Return only compilable Java code between [Java Start] and [Java End].

Python implementation:
{source}

Required Java declaration (complete its method and class):
{declaration}"""

# Ignore braces and keywords inside Java comments and literals.
JAVA_NONCODE = re.compile(
    r'//[^\n]*|/\*.*?\*/|""".*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
    re.DOTALL,
)


def mask_java(code):
    return JAVA_NONCODE.sub(
        lambda match: re.sub(r"[^\n]", " ", match.group()), code
    )


def read_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                raise ValueError(f"{path}:{number}: empty JSONL line")
            rows.append(json.loads(line))
    return rows


def problem_number(task_id):
    language, number = task_id.split("/")
    if language not in {"HumanEval", "Python", "Java"} or not number.isdigit():
        raise ValueError(f"Unexpected task ID: {task_id}")
    return int(number)


def pair_datasets(python_path, java_path=None):
    python_path = Path(python_path)
    if java_path is None:
        name = python_path.name.replace("selected_humanevalx_python_", "selected_humanevalx_java_", 1)
        if name == python_path.name:
            raise ValueError("Cannot infer Java dataset path; supply --java-dataset.")
        java_path = python_path.with_name(name)
    python_rows, java_rows = read_jsonl(python_path), read_jsonl(java_path)
    for language, rows in (("Python", python_rows), ("Java", java_rows)):
        ids = [problem_number(row["task_id"]) for row in rows]
        if len(ids) != 20 or len(set(ids)) != 20:
            raise ValueError(f"{language} dataset must contain exactly 20 unique problems.")
        for row in rows:
            for field in ("prompt", "declaration", "canonical_solution", "test"):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    raise ValueError(f"{row['task_id']}: missing or empty {field}")
    java_by_id = {problem_number(row["task_id"]): row for row in java_rows}
    if {problem_number(row["task_id"]) for row in python_rows} != set(java_by_id):
        raise ValueError("Python and Java datasets contain different problem IDs.")
    return [(row, java_by_id[problem_number(row["task_id"])]) for row in python_rows]


def build_instruction(python_entry, java_entry, vanilla=True):
    # The prompt contains the signature; canonical_solution contains the body.
    source = python_entry["prompt"].rstrip() + "\n" + python_entry["canonical_solution"]
    template = VANILLA_TEMPLATE if vanilla else CRAFTED_TEMPLATE
    return template.format(source=source, declaration=java_entry["declaration"])


def extract_java(response):
    if "[Java Start]" in response or "[Java End]" in response:
        matches = re.findall(r"\[Java Start\](.*?)\[Java End\]", response, re.DOTALL)
        if not matches:
            raise ValueError("Missing a complete [Java Start]/[Java End] pair.")
        code = matches[-1].strip()
    else:
        code = response.strip()
    fences = re.findall(r"```([^\n`]*)\n(.*?)```", code, re.DOTALL)
    if fences:
        blocks = [body.strip() for language, body in fences
                  if language.strip().lower() in {"", "java"}]
        if not blocks:
            raise ValueError("Response contains no Java code block.")
        code = "\n\n".join(blocks)
    if not code.strip():
        raise ValueError("Empty Java response.")
    return code.strip()


def remove_headers(code):
    """Extract imports and remove package declarations."""
    masked = mask_java(code)
    matches = list(re.finditer(
        r"\b(?:import\s+(?:static\s+)?[\w.*]+|package\s+[\w.]+)\s*;", masked))
    imports = [code[m.start():m.end()].strip() for m in matches
               if m.group().startswith("import")]
    for match in reversed(matches):
        code = code[:match.start()] + code[match.end():]
    return code, imports


def top_level_classes(code):
    masked = mask_java(code)
    return [match for match in re.finditer(r"\bclass\s+([A-Za-z_$][\w$]*)", masked)
            if masked[:match.start()].count("{") == masked[:match.start()].count("}")]


def rename_identifier(code, old, new):
    matches = list(re.finditer(r"\b" + re.escape(old) + r"\b", mask_java(code)))
    for match in reversed(matches):
        code = code[:match.start()] + new + code[match.end():]
    return code


def prepare_java(code, java_entry):
    """Add the class wrapper and imports needed by the dataset tests."""
    code, imports = remove_headers(code)
    test, test_imports = remove_headers(java_entry["test"])
    _, required_imports = remove_headers(java_entry["declaration"])
    classes = top_level_classes(code)
    names = [match.group(1) for match in classes]
    if "Solution" not in names:
        if len(classes) == 1:
            code = rename_identifier(code, names[0], "Solution")
        elif not classes:
            code = "class Solution {\n" + code + "\n}\n"
        else:
            raise ValueError("Multiple top-level classes but no Solution class.")
    # Only Main can be public at the top level in Main.java.
    masked = mask_java(code)
    publics = list(re.finditer(
        r"\bpublic\s+(?=(?:(?:final|abstract|strictfp)\s+)*(?:class|interface|enum|record)\b)", masked))
    for match in reversed(publics):
        before = masked[:match.start()]
        if before.count("{") == before.count("}"):
            code = code[:match.start()] + code[match.end():]
    all_imports = list(dict.fromkeys(required_imports + imports + test_imports))
    return "\n".join(all_imports) + "\n\n" + code + "\n\n" + test + "\n"


def require_java():
    for executable in ("javac", "java"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"JDK {JAVA_RELEASE} or newer is required: both javac and java must be available.")
        version = subprocess.run([executable, "-version"], capture_output=True,
                                 text=True, check=True)
        description = (version.stdout + version.stderr).strip()
        print(description, flush=True)
        match = re.search(r'\b(?:javac|openjdk|java)(?:\s+version)?\s+"?(\d+)(?:\.(\d+))?', description)
        if not match:
            raise RuntimeError(f"Cannot determine the version of {executable}.")
        major = int(match.group(2) if match.group(1) == "1" else match.group(1))
        if major < JAVA_RELEASE:
            raise RuntimeError(f"{executable} {JAVA_RELEASE} or newer is required; found Java {major}.")


def evaluate_java(code, java_entry, artifact_dir, compile_timeout=COMPILE_TIMEOUT,
                  run_timeout=RUN_TIMEOUT):
    """Compile and run one translation, saving the source and diagnostics."""
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "response.java").write_text(code, encoding="utf-8")
    result = {"is_correct": False, "status": "preparation_error"}
    try:
        source = prepare_java(code, java_entry)
    except ValueError as error:
        result["detail"] = str(error)
    else:
        (artifact_dir / "Main.java").write_text(source, encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="mp3_java_") as temporary:
            Path(temporary, "Main.java").write_text(source, encoding="utf-8")
            commands = (
                ("compile", ["javac", "--release", str(JAVA_RELEASE), "-encoding", "UTF-8", "Main.java"], compile_timeout),
                ("run", ["java", "-ea", "-Xmx256m", "-cp", ".", "Main"], run_timeout),
            )
            for phase, command, timeout in commands:
                try:
                    completed = subprocess.run(command, cwd=temporary, capture_output=True,
                                               text=True, errors="replace", timeout=timeout)
                except subprocess.TimeoutExpired as error:
                    result.update(status=phase + "_timeout", detail=str(error))
                    break
                result[phase] = {"returncode": completed.returncode,
                                 "stdout": completed.stdout, "stderr": completed.stderr}
                if completed.returncode != 0:
                    status = "compilation_error" if phase == "compile" else (
                        "test_failure" if "AssertionError" in completed.stderr else "runtime_error")
                    result["status"] = status
                    break
            else:
                result.update(is_correct=True, status="passed")
    (artifact_dir / "evaluation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def check_references(pairs, artifact_root):
    require_java()
    failures = []
    for _, java_entry in pairs:
        number = problem_number(java_entry["task_id"])
        source = java_entry["declaration"].rstrip() + "\n" + java_entry["canonical_solution"]
        evaluation = evaluate_java(source, java_entry, Path(artifact_root) / f"HumanEval_{number}")
        print(f"Reference HumanEval/{number}: {evaluation['status']}", flush=True)
        if not evaluation["is_correct"]:
            failures.append(number)
    if failures:
        raise RuntimeError(f"Reference validation failed for {failures}. Inspect {artifact_root} before running the model.")
    print("All 20 reference Java solutions passed. The evaluator is ready.", flush=True)


def load_model(model_name):
    # Import GPU packages only for model runs.
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    if not torch.cuda.is_available():
        raise RuntimeError("Select a GPU runtime in Colab before running the model.")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                     bnb_4bit_compute_dtype=torch.float16,
                                     bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, quantization_config=quantization, device_map="auto",
        torch_dtype=torch.float16, trust_remote_code=True,
    )
    model.eval()
    return model, tokenizer


def generate_response(model, tokenizer, instruction):
    import torch

    if tokenizer.chat_template:
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": instruction}], tokenize=False,
            add_generation_prompt=True)
    else:
        # Base-model prompt format.
        prompt = "### Instruction:\n" + instruction + "\n\n### Response:\n"
    inputs = tokenizer(prompt, return_tensors="pt",
                       add_special_tokens=not bool(tokenizer.chat_template)).to(model.device)
    context_limit = model.config.max_position_embeddings
    if inputs["input_ids"].shape[-1] + GENERATION_CONFIG["max_new_tokens"] > context_limit:
        raise ValueError("Prompt and output budget exceed the model context; input was not truncated.")
    with torch.inference_mode():
        output = model.generate(**inputs, **GENERATION_CONFIG,
                                pad_token_id=tokenizer.eos_token_id,
                                eos_token_id=tokenizer.eos_token_id)
    generated = output[0, inputs["input_ids"].shape[-1]:]
    return prompt, tokenizer.decode(generated, skip_special_tokens=True)


def prompt_model(pairs, model_name, output_file, vanilla=True, overwrite=False):
    require_java()
    output_file = Path(output_file)
    artifact_root = output_file.with_name(output_file.stem + "_artifacts")
    if output_file.exists() and not overwrite:
        raise FileExistsError(f"{output_file} already exists. Download it first or use --overwrite.")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    artifact_root.mkdir(parents=True, exist_ok=True)
    config = {"model": model_name, "mode": "vanilla" if vanilla else "crafted",
              "generation": GENERATION_CONFIG,
              "quantization": "4-bit NF4, double quantization, float16",
              "compile_timeout": COMPILE_TIMEOUT, "run_timeout": RUN_TIMEOUT,
              "java_release": JAVA_RELEASE}
    print(json.dumps(config, indent=2), flush=True)
    model, tokenizer = load_model(model_name)
    (artifact_root / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    results = []
    # Flush each result so completed problems survive an interrupted run.
    with output_file.open("w", encoding="utf-8") as handle:
        for index, (python_entry, java_entry) in enumerate(pairs, 1):
            task_id = python_entry["task_id"]
            directory = artifact_root / f"HumanEval_{problem_number(task_id)}"
            directory.mkdir(parents=True, exist_ok=True)
            instruction = build_instruction(python_entry, java_entry, vanilla)
            print(f"\n[{index}/20] {task_id}\nInstruction:\n{instruction}", flush=True)
            prompt, response = generate_response(model, tokenizer, instruction)
            (directory / "prompt.txt").write_text(prompt, encoding="utf-8")
            (directory / "response.txt").write_text(response, encoding="utf-8")
            try:
                code = extract_java(response)
            except ValueError as error:
                evaluation = {"is_correct": False, "status": "extraction_error", "detail": str(error)}
                (directory / "evaluation.json").write_text(json.dumps(evaluation, indent=2), encoding="utf-8")
            else:
                evaluation = evaluate_java(code, java_entry, directory)
            result = {"task_id": task_id, "prompt": prompt, "response": response,
                      "is_correct": evaluation["is_correct"]}
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            handle.flush()
            results.append(result)
            print(f"Prompt:\n{prompt}\nResponse:\n{response}\nEvaluation:\n{json.dumps(evaluation, indent=2)}", flush=True)
    correct = sum(row["is_correct"] for row in results)
    print(f"\nSuccess rate: {correct}/20 = {correct / 20:.0%}\nResults: {output_file}\nDiagnostics: {artifact_root}", flush=True)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dataset", type=Path)
    parser.add_argument("model", nargs="?", default=DEFAULT_MODEL)
    parser.add_argument("output_file", nargs="?", type=Path)
    parser.add_argument("if_vanilla", nargs="?", choices=("True", "False"))
    parser.add_argument("--java-dataset", type=Path, help="Default: sibling selected Java JSONL")
    parser.add_argument("--check-reference", action="store_true",
                        help="Check the 20 canonical Java solutions without loading an LLM")
    parser.add_argument("--overwrite", action="store_true",
                        help="Replace an existing experiment result file")
    args = parser.parse_args()
    pairs = pair_datasets(args.input_dataset, args.java_dataset)
    if args.check_reference:
        check_references(pairs, args.input_dataset.parent / "task_1_reference_check")
        return
    if args.output_file is None or args.if_vanilla is None:
        parser.error("Supply <input_dataset> <model> <output_file> <True|False>.")
    if args.output_file.suffix != ".jsonl":
        parser.error("output_file must end in .jsonl")
    prompt_model(pairs, args.model, args.output_file, args.if_vanilla == "True", args.overwrite)


if __name__ == "__main__":
    main()
