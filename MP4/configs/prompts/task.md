# Project: {{PROJECT_NAME}}

{{TASK}}

## Workspace layout
{{TREE}}

## Toolchain and checks run after every iteration
- `cargo +{{TOOLCHAIN}} build --all-targets`
- `cargo +{{TOOLCHAIN}} test --no-fail-fast`
- `cargo +{{TOOLCHAIN}} clippy --all-targets --all-features -- -W clippy::<group>` for correctness, style, complexity and perf (reported separately)
- unsafe metrics: unsafe lines, unsafe calls, unsafe casts, pointer arithmetic

## Specification: Rust interface (do not change public items)
{{INTERFACE_FILES}}

## Tests (read-only, they are part of the specification)
{{TEST_FILES}}

{{SOURCE_INDEX}}## Original C source (this is the behaviour to preserve)
{{C_FILES}}

## Current state of the editable Rust files
{{CURRENT_FILES}}

## Baseline check result before your first edit
{{FEEDBACK}}
