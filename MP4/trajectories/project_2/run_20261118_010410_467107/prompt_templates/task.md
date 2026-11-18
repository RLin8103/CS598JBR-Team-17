# Project: {{PROJECT_NAME}}

Translate the C project `{{PROJECT_NAME}}` to Rust. The Rust crate already exists in your workspace. The module files declared by `src/lib.rs` are copies of the interface stubs, with `unimplemented!()` bodies that you must replace by real implementations.

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

## Original C source (this is the behaviour to preserve)
{{C_FILES}}

## Current state of the editable Rust files
{{CURRENT_FILES}}

## Baseline check result before your first edit
{{FEEDBACK}}

Start by studying the C code, the interface and the tests, then write your first implementation. Cover every function and type in the interface.
