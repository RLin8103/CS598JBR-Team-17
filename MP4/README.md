# MP4 - Agentic C-to-Rust translation (Team 17)

Group 17 projects (CRUST-Bench): **project_1 = `cset`**, **project_2 = `libpsbt`**.

The pipeline is a custom Python controller (`src/agent.py`, standard library only). An LLM edits the
Rust crate; after every edit the controller runs `cargo build`, `cargo test`, `cargo clippy` (four
categories) and an unsafe-metrics analysis with the pinned toolchain, then returns that output to the
model, which decides the next edit. Nothing about individual C functions is hard-coded: the same
controller and prompts are used for both projects.

## Directory layout

```
MP4/
├── README.md
├── src/                     # pipeline code
│   ├── agent.py             # controller / main loop / prompt building / logging
│   ├── tools.py             # cargo runner, result parsers, guarded file edits, redaction
│   ├── llm.py               # OpenAI-compatible chat client (API key from env var only)
│   ├── unsafe_check.py      # built-in approximation of the unsafe-metrics tool (fallback)
│   ├── run_pipeline.sh      # one-command reproduction for a project
│   └── dev/mock_llm_server.py   # offline smoke test of the plumbing only (not used for results)
├── configs/
│   ├── pipeline.json        # model, inference settings, limits, stopping condition, guard rails
│   ├── projects.json        # group 17 -> project mapping and paths
│   └── prompts/             # system.md, task.md, feedback.md, phases.json
├── subjects/project_{1,2}/  # c_source/ (original C) + rust_skeleton/ (CRUST-Bench interface + tests)
├── translations/project_{1,2}/   # final generated Rust crates (cargo projects)
└── trajectories/project_{1,2}/   # run_<timestamp>/ execution logs, see "Trajectories"
```

## Frameworks, models and tools

| Item | Value |
|---|---|
| Agentic framework | `crust_agent` 1.0.0 - own controller in Python (no third-party agent framework) |
| Model | set in `configs/pipeline.json` (`llm.model`, default `qwen/qwen3-coder-next` via OpenRouter, with `anthropic/claude-haiku-5.5` and `deepseek/deepseek-v4-flash` as automatic fallbacks); the model actually used for each call is recorded in `trajectories/project_N/run_*/trajectory.jsonl` and `config_used.json`. History: the first runs used free OpenRouter models (`google/gemma-4-31b-it:free`, `cohere/north-mini-code:free`, `nvidia/nemotron-3-ultra-550b-a55b:free`); they were rate-limited (50 free requests/day), spent most of their output on hidden reasoning tokens, and never got the crate to compile, so the pipeline switched to a paid non-reasoning coding model. Those earlier runs are kept in `trajectories/` |
| Provider / runtime | any OpenAI-compatible `chat/completions` endpoint; default OpenRouter (`https://openrouter.ai/api/v1`). Local runtimes (Ollama, vLLM, llama.cpp server, LM Studio) work by setting `LLM_BASE_URL` |
| Inference settings | temperature 0.2, top_p 0.95, max_tokens 16000 per reply, request timeout 900 s, 2 retries per model with back-off, then fallback to the next model (`configs/pipeline.json`) |
| Rust toolchain | `nightly-2025-05-13` (cargo 1.89.0-nightly, clippy 0.1.88), the same one used for grading |
| Host OS / runtime | Windows 11 host, pipeline run inside WSL2 Ubuntu (Linux x86_64), Python 3 |
| Tools available to the agent | file write / patch (`src/*.rs` only), file read (`c_source/*`, crate files), `cargo build`, `cargo test`, `cargo clippy` (correctness / style / complexity / perf counted separately), unsafe-metrics analysis |
| Multiple agents or models | One agent (single controller loop, no multi-agent setup). Several models were used across the experiment: the default model works until a rate limit/failure or until it produces 2 replies in a row without an applied edit, then the controller switches (sticky) to the next model in `fallback_models` (`model_switches` / `escalate` events in the trajectory). The model used for every call is logged |

The agent does not get a free shell: the controller runs the fixed set of tools after each edit so
the feedback always matches the grading environment (same toolchain, same Clippy flags).

## Dependency installation

```bash
# Rust toolchain (Linux / WSL / macOS)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
rustup toolchain install nightly-2025-05-13 --profile minimal -c clippy -c rustfmt

# Python 3.9+ is the only other requirement (the pipeline uses the standard library only)
python3 --version
```

`libpsbt` depends on the crates `thiserror` and `base64` (declared in its `Cargo.toml`); cargo downloads
them, so the machine needs internet access the first time.

## How to run the pipeline

```bash
export OPENROUTER_API_KEY=...        # never commit this; or set another variable named in configs/pipeline.json
# optional overrides: LLM_MODEL=<model id>  LLM_BASE_URL=<endpoint>  LLM_API_KEY_ENV=<variable name>

bash MP4/src/run_pipeline.sh 1          # project_1 (cset)    -> translations/project_1, trajectories/project_1
bash MP4/src/run_pipeline.sh 2          # project_2 (libpsbt) -> translations/project_2, trajectories/project_2

# useful flags: --fresh (restart from the skeleton), --max-iterations N, --target-dir DIR
```

The same entry point works for any CRUST-Bench project that follows the `subjects/<id>/c_source` +
`rust_skeleton` layout:
`python3 MP4/src/agent.py --project NAME --subject DIR --out DIR --log DIR`.

Verify a finished translation exactly like the graders do:

```bash
cd MP4/translations/project_1
cargo +nightly-2025-05-13 build
cargo +nightly-2025-05-13 test
cargo +nightly-2025-05-13 clippy --all-targets --all-features -- \
    -W clippy::correctness -W clippy::style -W clippy::complexity -W clippy::perf
```

## Pipeline cycle

1. `setup`: copy `rust_skeleton` into `translations/project_N`; each module declared in `src/lib.rs` starts as a
   copy of its interface stub (`unimplemented!()` bodies). Hash all protected files (`Cargo.toml`, `Cargo.lock`,
   `src/lib.rs`, `src/bin/**` tests, `src/interfaces/**`).
2. `baseline`: run build, tests, Clippy and unsafe metrics once (iteration 0).
3. First prompt: task description, workspace tree, Rust interface, tests, all C sources, current Rust files, baseline feedback.
4. Each iteration: the model replies with `<file>` / `<edit>` / `<append>` / `<read>` / `<notes>` / `<done/>` blocks (replies are limited to about 16k output tokens, so the prompt tells it to work function by function; if a reply is cut off the controller saves the complete lines and asks the model to continue with `<append>`);
   the controller applies edits (refusing protected paths), re-runs all four checks and sends back the compiler
   errors, failing tests and panic messages, Clippy findings per category, unsafe metrics with offending lines,
   plus the current Rust files and the model's own notes.
5. The feedback has a *phase* that tells the model what to prioritise: `COMPILE` -> `TESTS` -> `STUBS` (bodies still `unimplemented!()`, e.g. modules the tests do not exercise) -> `SAFETY` -> `CLIPPY` -> `DONE`.
6. The best snapshot (lexicographic score: compiles, tests passed, fewer build errors, lower unsafe total, lower Clippy total)
   is restored at the end, so a regression in the final iteration cannot be what gets submitted.

Guard rails (enforced by the controller, logged in the trajectory): the agent cannot write outside `src/*.rs`;
tests, interfaces, `lib.rs` and `Cargo.toml` are hash-checked every iteration; `extern "C"`, `libc::`, `#[link(`
and `build.rs` (FFI back into the C code) are flagged as policy violations that must be fixed first.

## Stopping condition

The run stops at the first of:

1. **success**: build OK, every test passes, no `unimplemented!()`/`todo!()` is left, all primary unsafe metrics are 0 and the Clippy total is `<= clippy_accept` (0);
2. `max_iterations` (40 repair iterations);
3. `max_total_tokens` (2,000,000 prompt + completion tokens);
4. `no_progress_patience`: 8 consecutive iterations without improving the best score (turns spent finishing a cut-off file do not count);
5. `agent_done`: the model sent `<done/>` twice in a row while the crate compiles and all tests pass;
6. an unrecoverable LLM/API error. Rate-limit/empty-completion stops keep the latest files in place so that the run can be resumed
   (rerun without `--fresh`); other stops restore the best snapshot.

Repair-loop safeguards added during the experiments (all visible in the trajectories):

- *Rollback*: in the `SAFETY`/`CLIPPY` phases an edit that breaks the build or tests, or makes unsafe/Clippy worse, is reverted and the model is
  shown the errors of the reverted attempt (`rollback` events).
- *Escalation*: after 2 consecutive replies without an applied edit the controller switches to the next model in `fallback_models` (`escalate` events).
- *Tolerant parsing*: unclosed `<edit>`/`<file>` blocks and CDATA/fences are accepted; malformed edit blocks are reported back to the model.
- Edits only reset the no-progress counter in the `COMPILE`/`TESTS`/`POLICY` phases; in `SAFETY`/`CLIPPY` only score improvements count.

## Trajectories

`trajectories/project_N/run_<timestamp>/` contains, for each run: `config_used.json`, `system_prompt.md`,
`initial_prompt.md`, `pipeline.log`, `trajectory.jsonl` (every LLM call with token usage, every tool call, every check
result, the stop event), `metrics_by_iteration.json`, `final_status.json`, and one `iteration_NN/` directory per
iteration holding the prompts sent to / replies received from the model, `build.txt`, `test.txt`, `clippy.txt`,
`unsafe_metrics.json`, `metrics.json` and a snapshot of the Rust files after that iteration.
`trajectories/project_N/latest_run.txt` names the last run (the one that produced the submitted translation).
API keys are never written to disk and are scrubbed from every log line (`tools.redact`).

Each project's submitted translation is the result of several runs in sequence: a run that stops (rate limit, patience, token budget)
is resumed by running the pipeline again without `--fresh`, which continues from the files left in `translations/project_N`.
Run history (all runs are kept; early runs used free models and show the problems that led to the pipeline safeguards):

| Project | Run | Models used | Iterations | Stop reason | Result at end |
|---|---|---|---|---|---|
| 1 cset | `run_20261112_200435` | cohere/north-mini-code:free (+ free fallbacks) | 15 | free-tier daily limit (50 req/day) | did not compile |
| 1 cset | `run_20261112_203533` | free models (cohere, nemotron) | 27 | all models failed (empty completions) | did not compile |
| 1 cset | `run_20261112_210939` | qwen/qwen3-coder-next | 4 | interrupted by hand (no `final_status.json`) | - |
| 1 cset | `run_20261112_212222` | qwen/qwen3-coder-next | 15 | no_progress (unclosed `<edit>` blocks were dropped by the parser; fixed afterwards) | compiles, 5/15 tests |
| 1 cset | `run_20261112_213748` | qwen/qwen3-coder-next | 35 | token_budget | 15/15 tests, unsafe 44, Clippy 4 |
| 1 cset | `run_20261112_215837` | qwen/qwen3-coder-next | 7 | crashed on a transient Windows file lock (no `final_status.json`; fixed with write retries) | - |
| 1 cset | `run_20261112_220540` | qwen/qwen3-coder-next | 12 | no_progress | 15/15 tests, unsafe 36, Clippy 3 |
| 1 cset | `run_20261112_225516` | claude-haiku-5.5 (failed), then deepseek/deepseek-v4-flash | 12 | no_progress | **15/15 tests, unsafe 14, Clippy 0** |
| 2 libpsbt | `run_20261112_222714` | qwen/qwen3-coder-next | 19 | no_progress (model looped in its notes without edits) | compiles, 2/8 tests |
| 2 libpsbt | `run_20261112_223757` | qwen/qwen3-coder-next, then claude-haiku-5.5 | 19 | token_budget | 6/8 tests, unsafe 0, Clippy 2 (`cli.rs` still a stub; found by the final audit, which led to the `STUBS` phase) |
| 2 libpsbt | `run_20261112_233622` | qwen/qwen3-coder-next, then claude-haiku-5.5 | 19 | token_budget (after `cli.rs` was translated in iteration 6, the model kept retrying the defective test) | **6/8 tests, unsafe 0, Clippy 2, no stubs** |

## Safety metrics

The instructor-provided unsafe-metrics tool is run when its command is set in `configs/pipeline.json`
(`unsafe_metrics.command`, with `{path}` standing for the crate root). Until then the pipeline uses
`src/unsafe_check.py`, a lexical approximation of the same four primary metrics (unsafe lines, unsafe calls,
unsafe casts, pointer arithmetic) plus extras; the trajectory records which tool produced each number
(`unsafe_tool`). The numbers reported in the progress report come from the official tool.

## Manual interventions and limits

- No program logic was edited by hand. Any infrastructure fix will be listed here with the reason and whether program logic was affected.
- Setup changes made by hand: none to the translated code. The skeleton's missing module files are created automatically by the controller
  from the provided interface stubs.
- Infrastructure fixes made by hand (pipeline code only, never the translated Rust): tolerant reply parsing, `<append>` continuation for cut-off files,
  rollback of regressing edits, model escalation, retrying file writes after a transient Windows lock, resume support. None of these changes program logic.
- API / usage limits that affected the experiment: OpenRouter's free tier allows 50 requests/day (1000 with at least $10 of credit) and individual free
  providers return upstream 429s; the first runs hit both and one run ended on the daily cap. The free reasoning models (cohere/north-mini-code, nemotron)
  also spend the output budget on hidden reasoning tokens and often return empty completions, so the pipeline moved to paid non-reasoning models
  (`qwen/qwen3-coder-next` by default; `anthropic/claude-haiku-5.5` and `deepseek/deepseek-v4-flash` as fallbacks). `max_tokens` per reply is 16,000, so
  long files must be written function by function; the whole project cost roughly $3 of credit (about $0.01 per iteration for qwen, more for haiku).
  Context is about 40-120k prompt tokens per iteration because the C sources, interface, tests and current Rust files are resent every turn.
- Known test defect (project 2): `read_test_vector` in the provided `src/bin/test.rs` declares `step` as a local variable, so it asserts that *every* record
  has type 0, while the C test shares the counter and only checks the first two records. A faithful `psbt_read` emits a type-4 record and fails it
  (`left: 4, right: 0`); passing would require special-casing the test data, which the assignment forbids, so the translation keeps the faithful behaviour
  (6/8 test results, i.e. one failing test counted in two targets).
- Project 1 design note: the submitted `cset.rs` adds the bounds `T: Clone + Hash + PartialEq` to `impl<T> Cset<T>` and hashes with Rust's `DefaultHasher`
  instead of xxh64 (this is what removed most unsafe code). The interface file itself is unchanged. The bound-free version (unsafe 36) is kept in git
  history (commit `7d2e323`).
