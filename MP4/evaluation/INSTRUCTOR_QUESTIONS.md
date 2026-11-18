# Questions requiring instructor clarification

These issues do not authorize changes to benchmark tests, public signatures, or manifests. Examples below are explanatory and must not be run as normal tests where they would invoke undefined behavior.

## cset: frozen interface and soundness

The original interface is `subjects/project_1/rust_skeleton/src/interfaces/cset.rs`.

1. `pub fn xxh_read_le64(mem_ptr: &mut u8) -> u64` can be called with a single initialized byte: `let mut byte = 1u8; xxh_read_le64(&mut byte);`. A reference to one byte carries no guarantee of seven additional readable bytes. The C function reads eight bytes. Returning one byte (current implementation) is incorrect for an eight-byte buffer; extending this reference into an eight-byte slice is unsound for the legitimate single-byte call. The same conflict affects callbacks and finalize/endian helpers taking `&mut u8` plus a length. May these parameters become slices, or what behavior is required for length > 1?
2. `get_buckets_ref(&self) -> &mut Vec<CsetValue<T>>` and `get_temp_buckets_ref(&self)` allow two mutable references to the same vector from the same shared receiver. A minimal call pattern is `let a = set.get_buckets_ref(); let b = set.get_buckets_ref();` followed by uses of both. There is no borrow guard or exclusive receiver in the return type. The fields are ordinary Vec, without interior-mutability machinery. Adding UnsafeCell alone would not make overlapping mutable references valid. May these methods take `&mut self`, or return a checked guard?
3. `Cset<T>` has a mandatory `v: CsetValue<T>` containing a mandatory `elem: T`, while `impl<T>::new() -> Cset<T>` has no bounds or value argument. For an uninhabited type such as `std::convert::Infallible`, no such value exists. A non-panicking constructor for every T cannot satisfy this layout. `Cset::<&'static u8>::new()` currently constructs an invalid null reference using zeroed(); that is invalid on construction, even if an empty slot is never explicitly read. May empty slots/scratch values use Option/MaybeUninit or the constructor take a value/bound? Changing only private field layout is still prohibited by the supplied interface check, so an explicit decision is needed.
4. `index(&self, usize) -> T`, `iter(&mut self) -> Vec<T>`, and set operations returning/copied owned elements have no Clone/Copy bound. A bitwise read of a Box or String duplicates ownership. With live owned storage this can cause double frees/dangling values. Panicking for all non-Copy types would avoid that operation but would fail the generic behavior requirement; detecting Copy generically is not available here. May these APIs borrow elements or require an approved bound?
5. Hashing/comparing arbitrary `&T` by `size_of::<T>()` bytes can expose uninitialized padding (e.g. `#[repr(C)] struct P { byte: u8, word: u32 }`) and does not define value equality for pointers/owned collections. Safe generic byte inspection needs a valid representation contract or approved bounds/serialization. What Rust types are actually in scope?
6. `xxh64(*const u8, usize, ...)` and `xxh64_h` are safe public functions, so callers can supply invalid/non-dereferenceable pointers without an unsafe call. Null checks alone do not establish allocation validity. May these functions be marked unsafe or take slices? Comments and lint suppressions cannot enforce a safety precondition on a safe API.

A panic or explicit unsupported result can sometimes avoid UB, but is not a faithful total implementation of these C operations. No blanket claim that *every function with these types* must be unsound is intended; the conflict is between the frozen types/layout and the requested useful behavior.

The two short-input accumulator defects were repaired without changing a public signature. Both Rust hash variants now pass the defined initialized-byte comparisons from the sanitized C oracle in `evaluation/harness/cset_oracle.c`. The interface questions above concern separate public API and generic safety issues.

## libpsbt: benchmark counter

Rust `rust_skeleton/src/bin/test.rs:122` creates `let mut step = 0` inside each callback. Thus every Record callback asserts type zero, including legitimate type-4 records in PSBT_HEX. C `c_source/test.c:90` obtains an `int *step` from user_data and increments it across *all* callback events. The C reader forwards transaction events before the global unsigned-transaction Record callback. Therefore even describing the original C test as checking the first two records is imprecise: the counter also advances on transaction events.

Please clarify/fix the test upstream or specify its intended stateful callback assertion. We preserved it and count its failure in both Cargo targets. The continuation fixed the measured counting, callback, range, and buffer regressions independently of this benchmark. Hidden behavior remains unverified.

## libpsbt: Base62

C's alphabet string contains 62 symbols plus a terminating NUL (array size 63), but base_encode uses 6-bit indices 0..63. Index 62 reads the NUL; index 63 is out of bounds (undefined behavior). The original Rust translation panicked on both indices. The selected translation returns a checked failure for both. There is no defined compatible output for index 63. Please specify the intended alphabet/radix. The separate harness requests checked failure for unrepresentable symbols pending that decision; this is a proposed safe extension, not an official expected encoding. Comparisons with C use only indices 0..61. No modulo remapping or invented alphabet is proposed.

## libpsbt: CompactSize and fixed skeleton limitations

- C compactsize_write does not advance dest after writing 253/254/255. For value 253 in an aa-filled 3-byte destination, sanitized C writes `fd 00 aa`; Rust writes Bitcoin CompactSize `fd fd 00`. Which behavior should hidden tests require? The harness's standard-encoding test is explicitly a format expectation, not a claim of C equivalence.
- C compactsize_write has no capacity parameter, so its undersized-buffer calls are undefined and cannot be a comparison oracle. The Rust signature returns (), so it cannot return PsbtResult without an interface change. A checked panic/no-op policy needs clarification. Existing Rust panics on undersized slices and can partly modify them.
- `PSBT_ERRMSG: &str` and the fixed `psbt_geterr() { PSBT_ERRMSG }` body are already supplied by the skeleton. The selected translation preserves the public items and uses a mutex-backed error slot for the unfinalized-encode path. Error-message parity for other paths still needs verification. The context-error regression is a requested improvement, not a supplied test.
- `cli::main` is a private `fn main() -> i32` inside a library module. Cargo.toml supplies no CLI target and src/lib.rs supplies no public entrypoint. The existing function is translated but unreachable as a normal CLI. Creating a binary or widening visibility requires approval to change the skeleton integration. No such changes were made.
- C transaction parsing casts byte cursors to u32/u64 pointers and may violate alignment; the comparison harness deliberately does not invoke those C paths. Callback requirements here come from source inspection, and the Rust fixtures use defined byte-buffer behavior. C undefined behavior is not a Rust compatibility obligation.

## External tools

Please provide the official unsafe analyzer and submission validator, their versions/checksums, and exact commands. Neither is present in the MP4 tree or configured. Other assignments' validators are not substitutes. Approximate safety counts are supplemental and cannot establish official compliance.
