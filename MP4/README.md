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
| Model | set in `configs/pipeline.json` (`llm.model`, default `google/gemma-4-31b-it:free`, with `cohere/north-mini-code:free` and `nvidia/nemotron-3-ultra-550b-a55b:free` as automatic fallbacks); the model actually used for each run is recorded in `trajectories/project_N/run_*/config_used.json` and `final_status.json`. The reasoning models tried first (`cohere/north-mini-code:free`) spent most of their output budget on hidden reasoning tokens and were repeatedly cut off, so a non-reasoning instruct model is now the default |
| Provider / runtime | any OpenAI-compatible `chat/completions` endpoint; default OpenRouter (`https://openrouter.ai/api/v1`). Local runtimes (Ollama, vLLM, llama.cpp server, LM Studio) work by setting `LLM_BASE_URL` |
| Inference settings | temperature 0.2, top_p 0.95, max_tokens 24000 per reply (the cap also counts any hidden reasoning tokens), reasoning effort low where the provider supports it, request timeout 900 s, 3 retries per model with back-off, then fallback (`configs/pipeline.json`) |
| Rust toolchain | `nightly-2025-05-13` (cargo 1.89.0-nightly, clippy 0.1.88), the same one used for grading |
| Host OS / runtime | Windows 11 host, pipeline run inside WSL2 Ubuntu (Linux x86_64), Python 3 |
| Tools available to the agent | file write / patch (`src/*.rs` only), file read (`c_source/*`, crate files), `cargo build`, `cargo test`, `cargo clippy` (correctness / style / complexity / perf counted separately), unsafe-metrics analysis |
| Multiple agents or models | No. One agent, one model per run |

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
5. The feedback has a *phase* that tells the model what to prioritise: `COMPILE` -> `TESTS` -> `SAFETY` -> `CLIPPY` -> `DONE`.
6. The best snapshot (lexicographic score: compiles, tests passed, fewer build errors, lower unsafe total, lower Clippy total)
   is restored at the end, so a regression in the final iteration cannot be what gets submitted.

Guard rails (enforced by the controller, logged in the trajectory): the agent cannot write outside `src/*.rs`;
tests, interfaces, `lib.rs` and `Cargo.toml` are hash-checked every iteration; `extern "C"`, `libc::`, `#[link(`
and `build.rs` (FFI back into the C code) are flagged as policy violations that must be fixed first.

## Stopping condition

The run stops at the first of:

1. **success**: build OK, every test passes, all primary unsafe metrics are 0 and the Clippy total is `<= clippy_accept` (0);
2. `max_iterations` (40 repair iterations);
3. `max_total_tokens` (2,000,000 prompt + completion tokens);
4. `no_progress_patience`: 8 consecutive iterations without improving the best score (turns spent finishing a cut-off file do not count);
5. `agent_done`: the model sent `<done/>` twice in a row while the crate compiles and all tests pass;
6. an unrecoverable LLM/API error (the best snapshot is still restored and recorded).

## Trajectories

`trajectories/project_N/run_<timestamp>/` contains, for each run: `config_used.json`, `system_prompt.md`,
`initial_prompt.md`, `pipeline.log`, `trajectory.jsonl` (every LLM call with token usage, every tool call, every check
result, the stop event), `metrics_by_iteration.json`, `final_status.json`, and one `iteration_NN/` directory per
iteration holding the prompts sent to / replies received from the model, `build.txt`, `test.txt`, `clippy.txt`,
`unsafe_metrics.json`, `metrics.json` and a snapshot of the Rust files after that iteration.
`trajectories/project_N/latest_run.txt` names the run that produced the submitted translation.
API keys are never written to disk and are scrubbed from every log line (`tools.redact`).

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
- API / usage limits that affected the experiment: _to be filled in after the final runs (rate limits, daily request caps of the free tier, context limits)._
