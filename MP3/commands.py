# %% [markdown]
# # MP3 - Task 1: Code translation
#
# **CS598JBR - Team 17**
#
# This notebook compares vanilla and crafted prompts for Python-to-Java translation on the team’s 20 HumanEval-X problems. A translation is correct if it compiles and passes the provided Java tests.

# %% [markdown]
# ## 1. Input files
#
# The archive contains the scripts and the MP1 dataset in `MP3/`.

# %%
from google.colab import files
import io
from pathlib import Path
import zipfile

uploaded = files.upload()
archives = [(name, data) for name, data in uploaded.items() if name.lower().endswith(".zip")]
if len(archives) != 1:
    raise ValueError("Expected exactly one ZIP archive containing MP3/.")
with zipfile.ZipFile(io.BytesIO(archives[0][1])) as archive:
    archive.extractall("/content")
assert Path("/content/MP3/task_1.py").is_file(), "Missing MP3/task_1.py in the uploaded archive."
del uploaded, archives

# %%
%cd /content/MP3

import os
import subprocess
import sys

seed = "126511212782177902231984929477270226141"
model = "deepseek-ai/deepseek-coder-6.7b-instruct"
humaneval_input_dataset = f"selected_humaneval_{seed}.jsonl"
input_python_dataset = f"selected_humanevalx_python_{seed}.jsonl"
input_java_dataset = f"selected_humanevalx_java_{seed}.jsonl"
task_1_vanilla_jsonl = f"task_1_{seed}_vanilla.jsonl"
task_1_crafted_jsonl = f"task_1_{seed}_crafted.jsonl"
assert Path(humaneval_input_dataset).is_file(), f"Missing MP1 selection: {humaneval_input_dataset}"
os.environ["HF_DATASETS_TRUST_REMOTE_CODE"] = "1"


def run_logged(command, log_name):
    """Print command output and save it to a log file."""
    with open(log_name, "w", encoding="utf-8") as log:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, bufsize=1) as process:
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
            returncode = process.wait()
    if returncode:
        raise subprocess.CalledProcessError(returncode, command)

# %% [markdown]
# ## 2. Setup
#
# Dependencies use the supplied setup scripts. Java 17 supports the switch syntax used in the reference solution for HumanEval/105.

# %%
subprocess.run(["nvidia-smi"], check=True)
run_logged(["bash", "-e", "setup_dataset.sh"], "setup_dataset.log")
run_logged(["bash", "-e", "setup_models.sh"], "setup_models.log")


jdk_homes = sorted(path for path in Path("/usr/lib/jvm").glob("java-17-openjdk-*")
                   if (path / "bin/javac").is_file() and (path / "bin/java").is_file())
if not jdk_homes:
    subprocess.run(["apt-get", "update", "-qq"], check=True)
    subprocess.run(["apt-get", "install", "-y", "openjdk-17-jdk-headless"], check=True)
    jdk_homes = sorted(path for path in Path("/usr/lib/jvm").glob("java-17-openjdk-*")
                       if (path / "bin/javac").is_file() and (path / "bin/java").is_file())
if not jdk_homes:
    raise RuntimeError("JDK 17 installation was not found.")
os.environ["JAVA_HOME"] = str(jdk_homes[0])
os.environ["PATH"] = str(jdk_homes[0] / "bin") + os.pathsep + os.environ["PATH"]
from task_1 import require_java
require_java()

# %% [markdown]
# ## 3. Dataset checks
#
# The generator selects the Python and Java versions of the same 20 problems. The reference Java solutions and unit tests check the evaluation code before inference. Reference checks are not included in the model’s score.

# %%
run_logged([sys.executable, "-u", "humanevalx_dataset_generation.py", humaneval_input_dataset],
           "humanevalx_dataset_generation.log")

# %%
run_logged([sys.executable, "-u", "task_1.py", input_python_dataset, "--check-reference"],
           "task_1_reference_check.log")
run_logged([sys.executable, "-m", "unittest", "-v", "test_task_1"], "task_1_checks.log")

# %% [markdown]
# ## 4. Experiments
#
# | Setting | Both runs |
# |---|---|
# | Model | `deepseek-ai/deepseek-coder-6.7b-instruct` |
# | Quantization | 4-bit NF4, double quantization, float16 computation |
# | Decoding | Greedy; one response per problem |
# | Output budget | 1,024 tokens |
#
# The crafted prompt adds the Java declaration and guidance on differences between Python and Java. All other settings stay the same.

# %%
# Vanilla prompting
assert not Path(task_1_vanilla_jsonl).exists(), "An experiment result file already exists; replacement is disabled."
run_logged([sys.executable, "-u", "task_1.py", input_python_dataset, model,
            task_1_vanilla_jsonl, "True"], "task_1_vanilla.log")

# %%
# Crafted prompting
assert not Path(task_1_crafted_jsonl).exists(), "An experiment result file already exists; replacement is disabled."
run_logged([sys.executable, "-u", "task_1.py", input_python_dataset, model,
            task_1_crafted_jsonl, "False"], "task_1_crafted.log")

# %% [markdown]
# ## 5. Results
#
# The table compares outcomes for each problem and identifies compilation errors. Success rates and the difference in percentage points are calculated below.

# %%
import csv
import json
from IPython.display import Markdown, display


def read_results(filename):
    rows = [json.loads(line) for line in Path(filename).read_text().splitlines()]
    assert len(rows) == 20 and len({row["task_id"] for row in rows}) == 20
    assert all(type(row["is_correct"]) is bool for row in rows)
    return {row["task_id"]: row for row in rows}


vanilla_results = read_results(task_1_vanilla_jsonl)
crafted_results = read_results(task_1_crafted_jsonl)
assert vanilla_results.keys() == crafted_results.keys(), "Experiment IDs differ."
vanilla_artifacts = Path(task_1_vanilla_jsonl).with_suffix("").with_name(Path(task_1_vanilla_jsonl).stem + "_artifacts")
crafted_artifacts = Path(task_1_crafted_jsonl).with_suffix("").with_name(Path(task_1_crafted_jsonl).stem + "_artifacts")
configs = [json.loads((root / "config.json").read_text()) for root in (vanilla_artifacts, crafted_artifacts)]
assert {k: v for k, v in configs[0].items() if k != "mode"} == {k: v for k, v in configs[1].items() if k != "mode"}, "The experiment configurations differ."


def outcome(row, root):
    status = json.loads((root / row["task_id"].replace("/", "_") / "evaluation.json").read_text())["status"]
    if row["is_correct"]:
        return "True"
    if status == "compilation_error":
        return "False (compilation issue)"
    return f"False ({status})"


comparison = []
for task_id in sorted(vanilla_results, key=lambda task: int(task.split("/")[-1])):
    comparison.append([task_id, outcome(vanilla_results[task_id], vanilla_artifacts),
                       outcome(crafted_results[task_id], crafted_artifacts)])
with open("task_1_comparison.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["task_id", "vanilla", "crafted"])
    writer.writerows(comparison)
vanilla_correct = sum(row["is_correct"] for row in vanilla_results.values())
crafted_correct = sum(row["is_correct"] for row in crafted_results.values())
report = ["# MP3 — Task 1 results", "", "| Problem | Vanilla | Crafted |", "|---|---|---|"]
report += ["| " + " | ".join(row) + " |" for row in comparison]
report += ["", f"Vanilla: {vanilla_correct}/20 ({vanilla_correct / 20:.0%}).",
           f"Crafted: {crafted_correct}/20 ({crafted_correct / 20:.0%}).",
           f"Absolute improvement: {(crafted_correct - vanilla_correct) / 20 * 100:+.0f} percentage points.",
           ]
Path("task_1_summary.md").write_text("\n".join(report), encoding="utf-8")
display(Markdown("\n".join(report)))

# %% [markdown]
# ## 6. Saved files
#
# The ZIP contains the code, datasets, results, logs, and comparison table.

# %%
archive_path = Path("/content/MP3_task_1_results.zip")
with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(Path.cwd().rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".class":
            archive.write(path, Path("MP3") / path.relative_to(Path.cwd()))
files.download(str(archive_path))
