# MP4 — Group 17: cset and libpsbt

`project_1` is **cset**; `project_2` is **libpsbt**. The required directory layout is retained.
The reusable Python controller inspects C, the frozen Rust interface and tests; asks one model to make
edits; runs build/test/Clippy/safety checks; returns diagnostics; and repeats. Translated logic may only
be changed by that controller. The translation model independently diagnosed and edited both submitted implementations.

## Current submission

Both translations build on `nightly-2025-05-13`. The official structure validator passed on
a fresh clone of `main` at `6a07f9a`.

| Project | Supplied test executions | Distinct supplied tests | Independent checks, baseline → final | Official NewMetrics | Clippy |
|---|---:|---:|---:|---:|---:|
| cset | 15/15 | 15/15 | 13/29 → 29/29 | 4/4/0/0 | 0/0/0/0 |
| libpsbt | 6/8 | 3/4 | 4/21 → 21/21 | 0/0/0/0 | 0/2/0/0 |

NewMetrics columns are unsafe lines, unsafe calls, unsafe casts and pointer arithmetic.
Clippy columns are correctness, style, complexity and performance. Both libpsbt style diagnostics
come from the protected benchmark code. Its two failed executions are the same `read_test_vector`
test in two targets. The Rust checker resets its callback counter each time and expects type 0
where the fixture contains type 4. Both failures are included in the table.
See the [checker and interface analysis](evaluation/INSTRUCTOR_QUESTIONS.md).

## Framework and environment

| Item | Current audit / repair setup |
|---|---|
| Controller | `crust_agent` 1.1.0, custom standard-library Python; original runs used 1.0.0 |
| Python | local `.venv`, Python 3.13.17; source requires Python 3.10+ |
| Host | macOS, aarch64-apple-darwin; exact OS/runtime versions in evaluation JSON |
| Required Rust | nightly-2025-05-13: rustc 1.89.0-nightly (8405332bd, 2025-05-12), Cargo 1.89.0-nightly (056f5f4f3, 2025-05-09) |
| Tools | Clippy 0.1.88, rustfmt 1.8.0-nightly; fixed Cargo commands, guarded source reads/edits, lexical interface check, official NewMetrics 0.1.0, supplemental lexical source hints, separate sanitized C/Rust regressions |
| Model/provider | OpenRouter chat/completions; `qwen/qwen3-coder-next`, fallbacks `deepseek/deepseek-v4-flash`, `anthropic/claude-haiku-5.5` |
| Access evidence | Historical catalogue evidence is in `evaluation/model_availability.json`. Authenticated Haiku preflight for the autonomous batch is in `evaluation/autonomous_access.json`. |
| Arrangement | One model-driven controller loop, one active model at a time; no concurrent agents. The Python controller runs independently of external agent CLIs. |
| Settings | General config: temperature .2, top_p .95, max_tokens 16000, two attempts/model, 900-second request timeout. Targeted repair config: 6000 output tokens, one attempt/model, 180 seconds. Unsupported temperature/top_p parameters are omitted using fresh catalogue metadata. |

Historical trajectories came from Windows/WSL/Linux; their saved configurations are the source of
truth for those runs. The current pinned toolchain is isolated in `.runtime/`, and Homebrew Rust was
left in place. The controller uses the Python standard library. The course structure validator separately requires GitPython and colorama.

## Files and evidence

- `src/`: controller, tool adapters, access preflight, budget reservations, offline evaluator and history audit.
- `configs/pipeline.json`: general settings; `repair_experiments.json`: short controlled runs with additional checks.
- `configs/repairs/project_{1,2}.md`: verified defects and bounded targeted repair context, without implementations.
- `subjects/project_{1,2}/`: original C and supplied skeletons; unchanged.
- `translations/project_{1,2}/`: selected model-generated implementations.
- `trajectories/project_{1,2}/`: all original runs retained. `latest_run.txt` identifies the latest run and its selected snapshot.
- `evaluation/baseline/`: pre-repair source/config snapshot, commit and hashes; pinned execution evidence.
- `evaluation/harness/`: separate Rust regression crate and sanitizer-enabled C oracles. These do not alter supplied tests.
- `evaluation/indexed_continuation_final/`: current evaluation and exact selected snapshots. Earlier batch results remain under `evaluation/indexed_paid_final/`, `evaluation/autonomous_final/` and `evaluation/submission_check/`.
- `evaluation/INSTRUCTOR_QUESTIONS.md`: minimal interface, benchmark, C-behavior and tool questions.

## Setup without replacing the system toolchain

From the repository root:

```bash
python3.13 -m venv MP4/.venv
mkdir -p MP4/.runtime
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o MP4/.runtime/rustup-init.sh
export CARGO_HOME="$PWD/MP4/.runtime/cargo"
export RUSTUP_HOME="$PWD/MP4/.runtime/rustup"
RUSTUP_INIT_SKIP_PATH_CHECK=yes sh MP4/.runtime/rustup-init.sh -y --no-modify-path \
  --profile minimal --default-toolchain nightly-2025-05-13 -c clippy -c rustfmt
export PATH="$CARGO_HOME/bin:$PATH"
rustc +nightly-2025-05-13 -Vv
cargo +nightly-2025-05-13 clippy --version
cargo +nightly-2025-05-13 fmt --version
cargo +nightly-2025-05-13 fetch --locked --manifest-path MP4/translations/project_2/Cargo.toml
```

Installation/downloads need network access. Subsequent regression runs use `--offline --locked`.
The harness lockfile retains the versions in the supplied libpsbt lockfile. `.venv/`, `.runtime/`,
Cargo targets, environment files and keys are ignored by Git. The launcher checks installation and
never silently installs or changes the user's global toolchain.

## Reproduce evaluation without paid model calls

Use a **new output directory** on each invocation; evaluation refuses to overwrite evidence.

```bash
MP4/.venv/bin/python -m unittest discover -s MP4/src/tests -v
MP4/.venv/bin/python MP4/src/evaluate.py --config MP4/configs/newmetrics_six_turn.json \
  --output MP4/evaluation/reproduction_1
MP4/.venv/bin/python MP4/src/run_regressions.py --output MP4/evaluation/regressions_1
MP4/.venv/bin/python MP4/src/history_audit.py
```

Install NewMetrics and the pinned compiler components before using this configuration. Follow the
[official analyzer setup and validation steps](evaluation/official_newmetrics/README.md).
The evaluator exits nonzero when required validation is incomplete or fails. It retains each command,
stdout/stderr, return status, timeout status, exact config, tool versions and source hashes. Its JSON
has `mandatory_validation_clean: false` while official tooling or correctness checks are unresolved.
The evaluator can run a configured instructor validator. The course validator was run
separately against a fresh clone. Set
`unsafe_metrics.command` and `submission_validator.command` in the configuration to the **actual
instructor tools**, using `{path}` for the crate/submission root. Do not configure the approximation
as the official tool. The analyzer adapter expects an object containing four nonnegative integer
primary metrics, directly or under `totals`; other official output formats require an explicit adapter.
Missing metrics are unknown, never zero.

The exact required command is retained in the evaluation's `clippy.exact_command`:

```bash
cd MP4/translations/project_1  # repeat for project_2
cargo +nightly-2025-05-13 build
cargo +nightly-2025-05-13 test
cargo +nightly-2025-05-13 clippy --all-targets --all-features -- \
  -W clippy::correctness -W clippy::style -W clippy::complexity -W clippy::perf
```

The controller builds all targets and tests with `--no-fail-fast`. Four additional JSON Clippy probes
use `-A clippy::all -W clippy::<group>` solely to attribute categories independently. The mandatory
combined command has no such suppression. Counts deduplicate identical rendered findings across
Cargo targets; raw diagnostics are retained. Existing source `allow` attributes still suppress
correctness findings in cset and must be reviewed structurally. libpsbt's two emitted style findings
are in protected benchmark code; generated modules emit zero in these four categories.

## Reproduce the free repair runs

Provide `OPENROUTER_API_KEY` in the runtime environment and keep it out of version control.
The preflight verifies authentication and catalogue prices using GET requests. The free configuration
pins Cohere North Mini Code with Nemotron Ultra as its only fallback. It allows four iterations and
four API attempts per project with a shared $0 budget and zero-price routing. Each run snapshots the
generic templates. The model receives automatic diagnostics, including the separate regression output.
The human-written audit notes were excluded from this batch. Compare runs from identical starting
snapshots if evaluating the effect of changing models or prompts.

```bash
MP4/.venv/bin/python MP4/src/preflight.py --config MP4/configs/free_experiments.json \
  --output MP4/evaluation/free_access_verified.json
bash MP4/src/run_pipeline.sh 1 --config MP4/configs/free_experiments.json
bash MP4/src/run_pipeline.sh 2 --config MP4/configs/free_experiments.json
```

Validated API access expires after 24 hours. Budget reservations and provider-reported costs are
separate. Failed requests count against the API attempt limit.

## Snapshot selection, stopping and resumption

The score orders policy cleanliness, policy count, interface deviation count, compilation, valid
completed test output, clean test execution, passed/failed execution counts, build errors, stubs,
additional check failures, successful Clippy execution, available safety metrics, lower primary
safety total, then lower Clippy count. This is a heuristic, not a correctness proof. The historical selection mode retains tied compiling edits. The autonomous repair configuration uses named, complete regression results and rejects candidates that lose a previously passing case.

In interface/safety/Clippy/review refinement, a lower score rolls back. **Rejected files and their
validation stay under that iteration**, while `selection.json` identifies the selected hashes.
All normal exits, model/API failures and handled interruptions select the best evaluated snapshot;
partial/unvalidated interrupted work is retained separately in `interrupted_work/files/`. Final
selected files are reevaluated and hashed. Hard process kills cannot guarantee finalization; inspect
logs and evaluate the working tree before resuming such a run. This differs from version 1.0.0,
which sometimes left the latest files in place on API failure/interruption. Original evidence is
preserved in `evaluation/baseline/snapshot/` and the old trajectories.

Without `--fresh`, the pipeline starts from the current translation, with a fresh model conversation.
`--resume-from RUN:ITER` restores exactly that run's editable snapshot, removing stale editable files.
`--fresh` starts from the original skeleton after archiving the previous workspace in the new run's
`pre_fresh_workspace/`. Neither option changes the supplied skeleton. Use a separate output/log path
if comparing multiple experiments; do not overwrite unrelated user files.

`DONE` requires protected/interface/policy checks, no stubs, successful build, successful complete
nonempty test execution, successful mandatory combined Clippy and category probes, clean additional
checks, valid **official** safety output with all four primary metrics zero, and accepted Clippy
counts. Missing tools, malformed JSON, launch errors, nonzero exits, crashes, timeouts and incomplete
output cannot count as clean. Two `<done/>` replies do not bypass these requirements. Other stops
(iteration/token/USD budget, no progress, model failure/interruption) remain explicitly unsuccessful.
The instructor validator is an additional final submission gate. Even clean validation is not proof
of full correctness or memory safety.

## Results and reporting limitations

The free batch used Cohere North Mini Code and Nemotron Ultra. Both runs selected iteration zero.
The recorded cost was **$0** across six API attempts and five completed turns.

| Project | Run | Attempts / completed turns | Outcome |
|---|---|---:|---|
| cset | `run_20261118_000952_791387` | 3 / 3 | Cohere made no applicable edits. Nemotron proposed using a single-byte reference as a longer slice. The regression persisted, lexical unsafe counts rose, and the controller restored iteration zero. |
| libpsbt | `run_20261118_001109_142127` | 3 / 2 | Cohere made no applicable edits. Nemotron spent the 10,000-token output limit on reasoning and returned no editable response. Iteration zero was selected. |

The cumulative attempted iteration, response-bearing iteration and successful response counts are
233/231/248 for cset across 13 runs and 110/109/111 for libpsbt across eight runs.

Baseline and current benchmark results: cset 15/15 (exit 0), libpsbt 6/8 executions / 3/4 distinct
(exit 101). Both exact Clippy commands exit 0; categories are `0/0/0/0` and `0/2/0/0` in order
correctness/style/complexity/performance. The two libpsbt style findings are in the protected benchmark.
The independent harness results for the selected submissions are listed below. The harness includes
checked-error policies identified in the instructor questions.

The [official NewMetrics evidence](evaluation/official_newmetrics/) records library counts,
full analyzer logs, and the structure validator result. The library counts exclude the benchmark
binaries and dependencies. The cset library also has one raw-pointer dereference and four
raw-pointer declarations. Its four unsafe blocks create a slice from a caller-supplied pointer
and length, create a mutable reference from a shared reference, copy an arbitrary owned value
and zero-initialize an arbitrary `T`. Generic byte views can also expose uninitialized padding.
The frozen pointer, borrow, ownership and storage contracts limit which repairs can preserve
behavior. The tested hash repairs left these issues in place.

Pre-batch historical counts are reproducible with `history_audit.py`: cset has 230 attempted iteration banners,
228 iterations with successful LLM events and 245 successful responses across 12 runs; libpsbt has
107/107/109 across seven. Exact legacy HTTP-attempt and completed-turn totals are unknown. The former
report's 229 was a mixture of inconsistent per-run entries: it listed 15 instead of 14 in the first
cset run, omitted the interrupted fifth attempt in another, and listed seven rather than eight
response-bearing iterations in the file-lock run. Final historical runs have 29 and 10 response-bearing
iterations. New evaluation/checks are not translation iterations. See the JSON audits for every run.

`evaluation/INSTRUCTOR_QUESTIONS.md` explains the suspected state-reset benchmark defect, frozen cset
interface conflicts, Base62's undefined/missing symbols, CompactSize ambiguity, partial error-message
coverage and absent CLI integration. These remain unresolved; the benchmark failure is preserved and
reported. Miri is an optional diagnostic, not a replacement for the official safety analyzer.

## Local Devstral follow-up

The libpsbt run `run_20261118_002700_742995` tried the installed
`devstral-small-2:24b` model through Ollama. It used the same generic prompts
and validation feedback with a two-iteration limit. The first request reached
the 600-second timeout before returning a reply. The controller recorded one
attempt, zero completed turns, and selected the original snapshot. The final
pinned checks reproduced the same build, benchmark and Clippy results above.
This experiment made no remote inference calls.

## Earlier November 18 experiments

Across ten November 18 runs the controller attempted 15 iterations, completed eight model turns and made 14 inference requests, including three local requests. Eleven requests returned responses. All ten runs selected iteration zero. Local Devstral, Qwen and gpt-oss timed out. The first Flint run issued zero requests and the second completed one turn. Two Haiku runs exhausted their output allowance before returning edits. In the last run of that batch one edit failed compilation and the next passed four of eight benchmark executions. Restoring iteration zero returned libpsbt to six of eight. The fresh pinned evaluation reproduced baseline benchmark and Clippy results. The selected source hashes for that batch are in `evaluation/submission_check/`.

| Project | Trajectory directory | Model | Attempts | Completed turns | Requests | Responses |
|---|---|---|---:|---:|---:|---:|
| project_1 | run_20261118_000952_791387 | nvidia/nemotron-3-ultra-550b-a55b:free | 3 | 3 | 3 | 3 |
| project_2 | run_20261118_001109_142127 | nvidia/nemotron-3-ultra-550b-a55b:free | 3 | 2 | 3 | 3 |
| project_2 | run_20261118_002700_742995 | devstral-small-2:24b | 1 | 0 | 1 | 0 |
| project_2 | run_20261118_004031_776861 | qwen3.5:9b | 1 | 0 | 1 | 0 |
| project_2 | run_20261118_004512_735377 | recursive/flint-v1.0:free | 1 | 0 | 0 | 0 |
| project_2 | run_20261118_004634_277397 | recursive/flint-v1.0:free | 1 | 1 | 1 | 1 |
| project_2 | run_20261118_005129_155138 | gpt-oss:20b | 1 | 0 | 1 | 0 |
| project_2 | run_20261118_010306_447410 | anthropic/claude-haiku-5.5 | 1 | 0 | 1 | 1 |
| project_2 | run_20261118_010410_467107 | anthropic/claude-haiku-5.5 | 1 | 0 | 1 | 1 |
| project_2 | run_20261118_010837_713513 | anthropic/claude-haiku-5.5 | 2 | 2 | 2 | 2 |

## Autonomous repair and offline replay

Both continuations used `configs/autonomous_repair.json` and authenticated
`anthropic/claude-haiku-5.5` through OpenRouter. The model received C and Rust source, the frozen
interface, and observed check failures. The hand-authored diagnosis files were excluded. It
chose the defects, diagnosed them and authored the edits. The controller allowed two attempted
iterations and two inference requests per project, with a 180-second request timeout, 28,000 output
tokens, low reasoning effort and no fallbacks. Four requests returned responses. Provider-reported
charges for these runs were $0.0278049. The shared reservation ledger reached $4.975 of the $5 ceiling.

| Project | Model trajectory | Attempted iterations | Completed turns | Requests | Regression passes before → selected | Benchmark before → selected |
|---|---|---:|---:|---:|---:|---:|
| cset | `run_20261118_114859_292068` | 2 | 1 | 2 | 13/29 → 21/29 | 15/15 → 15/15 |
| libpsbt | `run_20261118_114933_162219` | 2 | 2 | 2 | 4/21 → 7/21 | 6/8 → 6/8 |

- **cset.** C-oracle mismatches on short inputs led the model to move accumulator merges inside
  the long-input branch of standard XXH64. The initial harness combined standard and h-variant
  outcomes in each assertion, so the first edit was rejected with 7/15 before and after. The model
  recognized that the standard output now matched and requested the truncated C header in its
  second iteration. That read used the last available reply, leaving no completed second turn.
  We split the two variants into separate checks and replayed the exact saved edit. It fixed eight
  standard cases and preserved every previous pass. At that point the h variant still differed on short inputs.
  The selected snapshot comes from offline replay `run_20261118_115034_652066`, with zero model calls.
- **libpsbt.** The model used a short-destination panic to add an actual slice-length guard to
  hex decoding, improving the harness to 5/21. It then used two Base62 panic reports to add
  checked alphabet lookup, improving to 7/21. Table indices 62 and 63 now return failure. This is a
  defensive policy while the intended encoding remains unresolved. The second edit also shares the
  Base64/Base62 encoder and stages output in a temporary vector. Benchmark and Clippy results were
  preserved. Map/index and callback behavior, requested lengths and other buffer bounds remained open after that batch.

The harness enumerates expected test IDs and requires a complete result for each. A failing assertion
can produce usable evidence. A timeout, malformed report, missing case or mismatched source hash
blocks comparison. The controller saves rejected edits and diagnostics before restoring a prior snapshot.
The final pinned evaluation in `evaluation/autonomous_final/` matches both selected trajectories.

To run a new autonomous continuation from the current files after verifying provider access and an
authorized spending limit, use `bash MP4/src/run_pipeline.sh 1 --config MP4/configs/autonomous_repair.json`
(with project ID 2 for libpsbt). The current ledger has insufficient room for another request at
these settings. `--fresh` starts from the skeleton and `--resume-from RUN:ITER` uses a saved snapshot
as the starting point. To reproduce the original cset replay from its pre-edit snapshot, the
credential-free command is:

```bash
bash MP4/src/run_pipeline.sh 1 --config MP4/configs/autonomous_repair.json \
  --replay-candidate run_20261118_114859_292068:1
```

Replay compares against the files currently in the workspace. Use an isolated checkout with the
pre-edit files from `evaluation/submission_check/project_1/snapshot/` to reproduce the original gain.

## Inspect the indexed context before inference

`configs/indexed_repair.json` and `configs/indexed_local_repair.json` use the same repair loop with
a file index and implementation-first context. The controller gives priority to C files that
correspond to Rust files cited in diagnostics and includes selected files in full. C test sources
and documentation remain available on demand. The first message includes the frozen Rust interface,
selected C and Rust, and named regression observations. Follow-up messages use a stable C/interface
reference and the latest Rust snapshot, diagnostics and notes. The model chooses the defect and
implements the repair as before.

The model can request a file or a bounded line range, for example
`<read path="c_source/tx.c" start="80" end="150"/>`. Each of the two repair iterations can use one
read follow-up. The four-request limit leaves room for both read and edit replies. The local
configuration uses the installed Qwen model through Ollama and does not require OpenRouter access.

From the repository root, use a fresh output path for a credential-free preview:

```bash
bash MP4/src/run_pipeline.sh 1 --config MP4/configs/indexed_local_repair.json \
  --preview-context MP4/evaluation/context-preview-1
```

Use project ID 2 and a separate output path for libpsbt. The previews saved under
`evaluation/indexed_context_final_preview/` include full copies of `cset.h`, `tx.c`, and `tx.rs`.
The previous autonomous prompts contained only excerpts of these files. The initial messages report all eight current cset failures and all fourteen
current libpsbt regression failures. A preview records the checks and prompts without changing the
selected translation or latest-run pointer. Omit `--preview-context` to start the local repair loop.
The remote configuration uses the existing ledger and requires enough authorized capacity for the
planned requests.

The no-cost cset trial `run_20261118_121239_826049` used `qwen3.5:9b` on localhost.
Its first request timed out after 180 seconds. It completed zero model turns and left the previous
implementation selected, with 15/15 benchmark executions and 21/29 independent checks passing.
libpsbt was verified in the offline preview. The trial made zero remote inference calls.

## Haiku trial with indexed prompts

`configs/indexed_paid_repair.json` uses the indexed prompt with authenticated Haiku access through
OpenRouter. It permits three repair iterations per project and a read follow-up within each
iteration. The controller records token usage and provider-reported charges without setting an
output-token cap or cumulative token stop. This experiment used the provider's prepaid-credit
enforcement at the user's direction. The earlier reservation ledger remains historical evidence.

To reproduce the standalone evaluation from the repository root with the installed local toolchain:

```bash
export CARGO_HOME="$PWD/MP4/.runtime/cargo"
export RUSTUP_HOME="$PWD/MP4/.runtime/rustup"
export PATH="$CARGO_HOME/bin:$PATH"
MP4/.venv/bin/python MP4/src/evaluate.py --config MP4/configs/indexed_paid_repair.json \
  --output MP4/evaluation/indexed-paid-recheck
```

| Project | Indexed Haiku run | Selected iteration | Benchmark before → after | Independent regressions before → after |
|---|---|---:|---:|---:|
| cset | `run_20261118_122059_113254` | 1 | 15/15 → 15/15 | 21/29 → 29/29 |
| libpsbt | `run_20261118_122204_929447` | 3 | 6/8 → 6/8, 3/4 distinct | 7/21 → 10/21 |

Each project attempted three iterations, completed three turns, and issued three requests.
With the full C header in its first prompt, the cset agent diagnosed and fixed short-input
accumulator mixing in the alternate hash variant. Its two later turns explained remaining
frozen-interface safety conflicts and made no edits. In libpsbt, the model moved map counting
to map boundaries by removing the per-record increment. This corrected map scopes and callback
record indices. A source/destination-length candidate failed with borrow checker error E0502
and was rolled back. The final edit corrected the label for unknown global record types.

The standalone pinned evaluation in `evaluation/indexed_paid_final/` verifies both snapshots
selected at the end of that batch. cset still has unsafe generic storage and aliasing issues. At
that stage, libpsbt had eleven failing regressions covering ranges, buffer bounds, transaction
callbacks and contextual errors.
Its suspected benchmark callback defect remains in the count. This historical batch predates
the official analyzer and validator runs documented above.

## Six-turn libpsbt continuation

`configs/indexed_paid_continuation.json` keeps the indexed prompt and validation from the previous
Haiku batch. It permits six iterations, up to twelve requests, and stops after three iterations
without a retained improvement. Run `run_20261118_122821_165101` completed six iterations and used
seven requests, including one read follow-up. Iteration four was selected.

| Project | Benchmark before → after | Independent regressions before → after | Clippy groups before → after |
|---|---:|---:|---:|
| cset, re-evaluated | 15/15 → 15/15 | 29/29 → 29/29 | 0/0/0/0 → 0/0/0/0 |
| libpsbt | 6/8 → 6/8, 3/4 distinct | 10/21 → 21/21 | 0/2/0/0 → 0/2/0/0 |

The first libpsbt patch for transaction callbacks failed to build because it left a reference to
`tx_io_counts`. The second turn repaired the call path and the callback-order case passed. Turn
three fixed the nine failing range and capacity cases by honoring declared source lengths and
bounding writes to the declared and actual destination. Turn four backed the public error getter
with a safe process-wide slot and set it for the unfinalized-encode error path. The protected
benchmark still fails `read_test_vector` in both targets. All independent cases pass, while full
error-message coverage and parity on untested inputs remain open.

The standalone pinned evaluation is in `evaluation/indexed_continuation_final/`. Use the evaluation
command above with `configs/indexed_paid_continuation.json` and a fresh output path to reproduce it.

## Official NewMetrics cset continuations

Both continuations used Claude Haiku 5.5 through OpenRouter and started from the selected cset
translation. They retained the starting implementation and verified the same source hash.

| Run | Completed turns | API requests | Stop | Outcome |
|---|---:|---:|---|---|
| [Initial official-feedback run](trajectories/project_1/run_20261118_151939_418020/final_status.json) | 2 | 2 | No progress | Official library counts plus lexical source hints. A comment-only edit was reverted. |
| [Six-turn official-feedback run](trajectories/project_1/run_20261118_152320_378724/final_status.json) | 6 | 6 | Iteration limit | Official counts and library reports for unsafe spans, pointer declarations and dereferences. Three comment-only edits were reverted. |

The six-turn run used `configs/newmetrics_six_turn.json`. The final snapshot reproduced 15/15
supplied tests, 29/29 independent checks, zero emitted warnings in the four Clippy categories
and official counts of `4/4/0/0`. The adapter also reproduced libpsbt's `0/0/0/0` in an offline
check. The selected libpsbt translation comes from the earlier six-turn continuation above.
