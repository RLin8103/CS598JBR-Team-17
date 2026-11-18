# Iteration 3 of at most 4 - controller feedback

## Notices from the controller
- No valid edit was applied in your previous reply. Write an <edit> block now; keep <notes> short.
- (The controller switched you to a different model after repeated replies without edits.)


## Status
- compiles: True (0 errors)
- tests: 15 passed / 15 total (0 failed)
- unsafe metrics (builtin-approximation): lines=4, calls=3, casts=0, pointer_arithmetic=0
- validation: test_ok=True, clippy_ok=True, unsafe_valid=True
- clippy warnings: {"correctness": 0, "style": 0, "complexity": 0, "perf": 0}
- interface deviations (signatures that differ from src/interfaces/*.rs): 0
- untranslated bodies (`unimplemented!()`/`todo!()`): 0
- tokens used so far: 63329 / 300000

## Current phase: REGRESSIONS
Separate additional regression checks failed. Use their diagnostics and C evidence to repair real defects with targeted edits. These checks do not replace the supplied benchmarks. Do not change benchmark tests or implementations of the evaluation harness. For C undefined behavior, preserve defined behavior and return a checked error where possible; record specification ambiguities.

## cargo build
OK (7 rustc warnings).

## cargo test
15 passed, 0 failed, total 15. returncode=0 valid_output=True ok=True


## cargo clippy
Counts: {"correctness": 0, "style": 0, "complexity": 0, "perf": 0} (total 0). Target: 0 in every category.

## unsafe metrics (builtin-approximation)
{"unsafe_lines": 4, "unsafe_calls": 3, "unsafe_casts": 0, "pointer_arithmetic": 0, "unsafe_blocks": 4, "unsafe_fns": 0, "raw_pointer_decls": 3, "ffi_calls": 0, "transmute_uses": 0, "manual_alloc_ops": 0, "files_with_forbid_unsafe_code": 0, "files_analysed": 2}
Mandatory official safety validation unavailable/invalid: official analyzer not configured
Where:
- src/cset.rs:26 [raw_pointer_decls] fn raw_bytes<'a>(ptr: *const u8, len: usize) -> &'a [u8] {
- src/cset.rs:31 [unsafe_calls] unsafe { std::slice::from_raw_parts(ptr, len) }
- src/cset.rs:52 [unsafe_line] unsafe { &mut *p }
- src/cset.rs:256 [raw_pointer_decls] pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:262 [raw_pointer_decls] pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:317 [unsafe_calls] unsafe { std::ptr::read(std::ptr::from_ref(v)) }
- src/cset.rs:357 [unsafe_calls] unsafe { std::mem::zeroed() }

## Separate regression check
$ /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/.venv/bin/python /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/src/run_regressions.py --project-id 1 --output /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/trajectories/project_1/run_20261118_000952_791387/additional_checks/1
returncode=1 timed_out=False
```

running 2 tests
test tests::cset_multibyte_hashes_match_sanitized_c_oracle ... FAILED
test tests::cset_padding_free_copy_generic ... ok

failures:

---- tests::cset_multibyte_hashes_match_sanitized_c_oracle stdout ----

thread 'tests::cset_multibyte_hashes_match_sanitized_c_oracle' panicked at src/lib.rs:249:9:
len=0 seed=0: Rust=13934714534406826450/6089448738516538328, C=17241709254077376921/13315799867417602922
len=0 seed=2718182: Rust=1088256915903631556/11614518687002993724, C=17164995725320669776/9609742367336788117
len=1 seed=0: Rust=400611822795326115/1344935720564239988, C=16804241149081757544/11193626097507625299
len=1 seed=2718182: Rust=8168549641978686410/6594899528827042558, C=12030735130094489608/16585143914630977865
len=2 seed=0: Rust=5578343508417602773/8617509540135573086, C=5216751715308240086/962134502339947765
len=2 seed=2718182: Rust=15723073577781726320/4971479887067988310, C=6839953705013005250/14547683834055110473
len=7 seed=0: Rust=12527556425796954294/7584827969456509918, C=1498682999415010002/4249893767171937820
len=7 seed=2718182: Rust=8104809122016315627/12829040013170679280, C=15642697405811612460/1518540224581367784
len=8 seed=0: Rust=14795519122527122261/9163211194136353357, C=9820687458478070669/3730646594863863303
len=8 seed=2718182: Rust=9499085504836072429/4170975662148065910, C=9136710207871035179/1811739754178317970
len=15 seed=0: Rust=12282353933906490625/13813176779204586094, C=12198270006012390445/12756233403702556746
len=15 seed=2718182: Rust=7039273967639289272/2989575921063934098, C=12026005270239508466/17353067986731924435
len=16 seed=0: Rust=4644812539751331808/15602599801977290796, C=4951407828574235127/14830457271042726377
len=16 seed=2718182: Rust=7312387820323049382/5130008953502153227, C=13836727961620331567/4311501666727977334
len=31 seed=0: Rust=17127477829281814866/2122892477728805114, C=14071165763202158305/15169082307081493518
len=31 seed=2718182: Rust=5533785400843060160/6837672701383405910, C=15171138851224130528/15084038666174280388
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::cset_multibyte_hashes_match_sanitized_c_oracle

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 21 filtered out; finished in 0.00s

   Compiling cset v0.1.0 (/Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_1)
warning: constant `BUF_SIZE` is never used
 --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2/src/cli.rs:6:7
  |
6 | const BUF_SIZE: usize = 4096;
  |       ^^^^^^^^
  |
  = note: `#[warn(dead_code)]` on by default

warning: function `main` is never used
 --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2/src/cli.rs:8:4
  |
8 | fn main() -> i32 {
  |    ^^^^

warning: `libpsbt` (lib) generated 2 warnings
warning: field `v` is never read
   --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_1/src/cset.rs:291:5
    |
286 | pub struct Cset<T> {
    |            ---- field in this struct
...
291 |     v: CsetValue<T>,
    |     ^
    |
    = note: `#[warn(dead_code)]` on by default

warning: `cset` (lib) generated 1 warning
   Compiling mp4-regressions v0.1.0 (/Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/evaluation/harness)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.34s
     Running unittests src/lib.rs (.runtime/target/regressions/debug/deps/mp4_regressions-b5d92567a85da7ba)
error: test failed, to rerun pass `--lib`



```

## Current state of the editable Rust files
### src/cset.rs (611 lines)
```rust
// Type aliases
pub type XXH64HashT = u64;
pub type XXHU8 = u8;
pub type XXHU64 = XXH64HashT;
pub type XXHU32 = u32;
pub type XXH32HashT = u32;

// Constants
pub const XXH_PRIME64_1: u64 = 0x9E3779B185EBCA87;
pub const XXH_PRIME64_2: u64 = 0xC2B2AE3D27D4EB4F;
pub const XXH_PRIME64_3: u64 = 0x165667B19E3779F9;
pub const XXH_PRIME64_4: u64 = 0x85EBCA77C2B2AE63;
pub const XXH_PRIME64_5: u64 = 0x27D4EB2F165667C5;
pub const CSET_FORCE_INITIALIZE: bool = true;
pub const CSET_INITIAL_CAP: usize = 2;
pub const CSET_DEFAULT_SEED: u64 = 2718182;
pub const CSET_MAX_LOAD_FACTOR: f64 = 0.7;
pub const CSET_MIN_LOAD_FACTOR: f64 = 0.2;

// Single place that turns a caller-provided raw buffer into a byte slice.
// Needed because the interface passes `*const u8` to `xxh64` and `xxh64_h`,
// and because `bytes_of` views a `T` through the same path.
// Contract: `ptr` is valid for reading `len` bytes, or `len == 0`. A null
// `ptr` with `len > 0` is a caller contract violation (C would crash); here
// it yields an empty slice, so the hash then panics on indexing.
fn raw_bytes<'a>(ptr: *const u8, len: usize) -> &'a [u8] {
    if len == 0 || ptr.is_null() {
        return &[];
    }
    // SAFETY: see the contract above; null is handled before the call.
    unsafe { std::slice::from_raw_parts(ptr, len) }
}

// View a caller-provided `&mut u8` buffer as a byte slice.
// Known limitation: the interface passes only one `&mut u8`, so at most one
// byte is reachable safely. For `len > 1` the C behaviour (hash `len` bytes)
// is NOT reproduced by the callbacks that use this helper. A faithful version
// needs a slice or `*const u8` parameter, which the frozen interface forbids.
// Safe: `slice::from_ref` creates a one-element slice from a valid reference.
fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    &std::slice::from_ref(ptr)[..len.min(1)]
}

// Single place that re-exposes a shared reference as mutable. Required only
// because the interface takes `&self` and returns `&mut Vec`, mirroring the
// C code, which does not enforce const-correctness.
#[allow(invalid_reference_casting, clippy::mut_from_ref)]
fn alias_mut<U>(r: &U) -> &mut U {
    let p = std::ptr::from_ref(r).cast_mut();
    // SAFETY: `p` derives from a live shared reference; the interface contract
    // is that callers do not use the returned reference while others alias it.
    unsafe { &mut *p }
}

// Helper: check if little endian
pub fn xxh_is_little_endian() -> bool {
    cfg!(target_endian = "little")
}

pub fn xxh_get64bits(mem_ptr: &mut XXHU8) -> XXHU64 {
    xxh_read_le64_align(mem_ptr)
}

// Read 8 bytes as little-endian from a slice
pub fn xxh_read_le64(mem_ptr: &mut XXHU8) -> XXHU64 {
    let val = *mem_ptr as u64;
    val.to_le()
}

// Read 8 bytes as little-endian from a slice (aligned version)
pub fn xxh_read_le64_align(mem_ptr: &mut XXHU8) -> XXHU64 {
    xxh_read_le64(mem_ptr)
}

// Swap bytes of a u32
pub fn xxh_swap32(x: &mut XXHU32) -> XXHU32 {
    let val = *x;
    ((val & 0xFF000000) >> 24)
        | ((val & 0x00FF0000) >> 8)
        | ((val & 0x0000FF00) << 8)
        | ((val & 0x000000FF) << 24)
}

// Read 4 bytes as little-endian from a slice
pub fn xxh_read32(mem_ptr: &mut XXHU32) -> XXHU32 {
    let val = *mem_ptr;
    val.to_le()
}

// xxh64 round
pub fn xxh64_round(acc: XXHU64, input: XXHU64) -> XXHU64 {
    let mut acc = acc;
    acc = acc.wrapping_add(input.wrapping_mul(XXH_PRIME64_2));
    acc = acc.rotate_left(31);
    acc = acc.wrapping_mul(XXH_PRIME64_1);
    acc
}

// xxh64 merge round
pub fn xxh64_merge_round(acc: XXHU64, val: XXHU64) -> XXHU64 {
    let val = xxh64_round(0, val);
    let acc = acc ^ val;
    acc.wrapping_mul(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_4)
}

// Get 32 bits from pointer (little-endian)
pub fn xxh_get_32bits(ptr: &mut XXHU32) -> XXHU32 {
    if xxh_is_little_endian() {
        xxh_read32(ptr)
    } else {
        let mut val = xxh_read32(ptr);
        xxh_swap32(&mut val)
    }
}

// Read 32 bits aligned
pub fn xxh_read_le32_align(ptr: &mut XXHU32) -> XXHU32 {
    xxh_read32(ptr)
}

// xxh64 avalanche
pub fn xxh64_avalanche(mut h64: XXHU64) -> XXHU64 {
    h64 ^= h64 >> 33;
    h64 = h64.wrapping_mul(XXH_PRIME64_2);
    h64 ^= h64 >> 29;
    h64 = h64.wrapping_mul(XXH_PRIME64_3);
    h64 ^= h64 >> 32;
    h64
}

// Read 64 bits from slice (little-endian)
fn xxh_read_le64_from_slice(slice: &[u8]) -> XXHU64 {
    u64::from_le_bytes([slice[0], slice[1], slice[2], slice[3], slice[4], slice[5], slice[6], slice[7]])
}

// Read 32 bits from slice (little-endian)
fn xxh_read_le32_from_slice(slice: &[u8]) -> XXHU32 {
    u32::from_le_bytes([slice[0], slice[1], slice[2], slice[3]])
}

// xxh64 finalize - internal version working with &[u8]
fn xxh64_finalize_inner(mut h64: XXHU64, ptr: &[u8], len: usize) -> XXHU64 {
    let mut len = len & 31;
    let mut offset = 0;
    while len >= 8 {
        let k1 = xxh64_round(0, xxh_read_le64_from_slice(&ptr[offset..offset + 8]));
        offset += 8;
        h64 ^= k1;
        h64 = h64.rotate_left(27).wrapping_mul(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_4);
        len -= 8;
    }
    if len >= 4 {
        let val = xxh_read_le32_from_slice(&ptr[offset..offset + 4]);
        h64 ^= (val as XXHU64).wrapping_mul(XXH_PRIME64_1);
        offset += 4;
        h64 = h64.rotate_left(23).wrapping_mul(XXH_PRIME64_2).wrapping_add(XXH_PRIME64_3);
        len -= 4;
    }
    while len > 0 {
        h64 ^= (ptr[offset] as XXHU64).wrapping_mul(XXH_PRIME64_5);
        h64 = h64.rotate_left(11).wrapping_mul(XXH_PRIME64_1);
        offset += 1;
        len -= 1;
    }
    xxh64_avalanche(h64)
}

// xxh64 finalize - public interface matches interface file
pub fn xxh64_finalize(h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    let bytes = view_bytes(ptr, len);
    xxh64_finalize_inner(h64, bytes, bytes.len())
}

// xxh64 endian align - internal version working with &[u8]
fn xxh64_endian_align_inner(input: &[u8], len: usize, seed: XXHU64) -> XXHU64 {
    let mut offset = 0;
    let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
    let mut v2 = seed.wrapping_add(XXH_PRIME64_2);
    let mut v3 = seed;
    let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
    let mut h64 = if len >= 32 {
        let limit = len - 32;
        while offset <= limit {
            v1 = xxh64_round(v1, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v2 = xxh64_round(v2, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v3 = xxh64_round(v3, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v4 = xxh64_round(v4, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
        }
        v1.rotate_left(1)
            .wrapping_add(v2.rotate_left(7))
            .wrapping_add(v3.rotate_left(12))
            .wrapping_add(v4.rotate_left(18))
    } else {
        seed.wrapping_add(XXH_PRIME64_5)
    };
    h64 = xxh64_merge_round(h64, v1);
    h64 = xxh64_merge_round(h64, v2);
    h64 = xxh64_merge_round(h64, v3);
    h64 = xxh64_merge_round(h64, v4);
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize_inner(h64, &input[offset..], len)
}

// xxh64 endian align - public interface matches interface file
pub fn xxh64_endian_align(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let bytes = view_bytes(input, len);
    xxh64_endian_align_inner(bytes, bytes.len(), seed)
}

// xxh64 endian align h - internal version working with &[u8]
fn xxh64_endian_align_h_inner(input: &[u8], len: usize, seed: XXHU64) -> XXHU64 {
    let mut offset = 0;
    let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
    let mut v2 = seed.wrapping_sub(XXH_PRIME64_2);
    let mut v3 = seed.wrapping_add(XXH_PRIME64_3);
    let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
    let mut h64 = if len >= 32 {
        let limit = len - 32;
        while offset <= limit {
            v1 = xxh64_round(v1, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v2 = xxh64_round(v2, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v3 = xxh64_round(v3, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v4 = xxh64_round(v4, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
        }
        v1.rotate_left(1)
            .wrapping_add(v2.rotate_left(7))
            .wrapping_add(v3.rotate_left(12))
            .wrapping_add(v4.rotate_left(18))
    } else {
        seed.wrapping_add(XXH_PRIME64_1)
    };
    h64 = xxh64_merge_round(h64, v1);
    h64 = xxh64_merge_round(h64, v2);
    h64 = xxh64_merge_round(h64, v3);
    h64 = xxh64_merge_round(h64, v4);
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize_inner(h64, &input[offset..], len)
}

// xxh64 endian align h - public interface matches interface file
pub fn xxh64_endian_align_h(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let bytes = view_bytes(input, len);
    xxh64_endian_align_h_inner(bytes, bytes.len(), seed)
}

// xxh64 - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    xxh64_endian_align_inner(raw_bytes(input, len), len, seed)
}

// xxh64_h - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    xxh64_endian_align_h_inner(raw_bytes(input, len), len, seed)
}

// cset_hash1_callback - hash bytes using xxh64
pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let bytes = view_bytes(memptr, size);
    xxh64_endian_align_inner(bytes, bytes.len(), CSET_DEFAULT_SEED)
}

// cset_hash2_callback - hash bytes using xxh64_h variant, OR'd with 1
pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let bytes = view_bytes(memptr, size);
    xxh64_endian_align_h_inner(bytes, bytes.len(), CSET_DEFAULT_SEED) | 1
}

// CsetValue struct
#[derive(Debug, Clone, Copy)]
pub struct CsetValue<T> {
    pub pi: i32,
    pub elem: T,
}

// Cset struct
pub struct Cset<T> {
    buckets: Vec<CsetValue<T>>,
    max_load_factor: f64,
    min_load_factor: f64,
    seed: u64,
    v: CsetValue<T>,
    bucket_size: usize,
    compare: Option<fn(&T, &T) -> bool>,
    temp_buckets: Vec<CsetValue<T>>,
}

impl<T> Default for Cset<T> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T> Cset<T> {
    // Helper: view a &T as its raw bytes for hashing and comparison.
    // Goes through `raw_bytes`, so this file has a single raw-slice site.
    fn bytes_of(v: &T) -> &[u8] {
        raw_bytes(std::ptr::from_ref(v).cast::<u8>(), std::mem::size_of::<T>())
    }

    // Helper: bitwise-copy a T from a reference (used because T has no Clone
    // bound, so this is the only way to return an owned T from &T). The
    // source stays owned by the set; the copy is returned to the caller, who
    // becomes the single owner of that value. Known limitation: if T owns
    // heap data, the caller and the set both hold it until the set is
    // cleared, so the interface's missing `Clone` bound makes this a risk.
    fn copy_of(v: &T) -> T {
        unsafe { std::ptr::read(std::ptr::from_ref(v)) }
    }

    fn matches_default(&self, index: usize, value: &T) -> bool {
        let elem_bytes = Self::bytes_of(&self.buckets[index].elem);
        let value_bytes = Self::bytes_of(value);
        elem_bytes == value_bytes
    }

    fn matches_custom(&self, index: usize, value: &T) -> bool {
        match self.compare {
            Some(cmp) => cmp(&self.buckets[index].elem, value),
            None => self.matches_default(index, value),
        }
    }

    fn h1hash(&self, value: &T) -> XXHU64 {
        let bytes = Self::bytes_of(value);
        xxh64_endian_align_inner(bytes, std::mem::size_of::<T>(), self.seed)
    }

    fn h2hash(&self, value: &T) -> XXHU64 {
        let bytes = Self::bytes_of(value);
        xxh64_endian_align_h_inner(bytes, std::mem::size_of::<T>(), self.seed) | 1
    }

    fn double_hash_index(ha1: XXHU64, ha2: XXHU64, i: usize, cap: usize) -> usize {
        let ha1_usize = ha1 as usize;
        let ha2_usize = ha2 as usize;
        let product = i.wrapping_mul(ha2_usize);
        (ha1_usize.wrapping_add(product)) % cap
    }

    // Placeholder element for slots that are never read (pi == 0 or -1).
    // Known limitation: the frozen interface gives no Default or Clone bound,
    // so a value of T must be produced bitwise. This is unsound for some T
    // (e.g. references, Box, NonNull). A safe design needs a bound such as
    // T: Default, which the public contract does not allow.
    fn placeholder() -> T {
        // SAFETY: the value is only stored in empty slots and never read.
        unsafe { std::mem::zeroed() }
    }

    fn init_buckets(cap: usize) -> Vec<CsetValue<T>> {
        (0..cap)
            .map(|_| CsetValue {
                pi: 0,
                elem: Self::placeholder(),
            })
            .collect()
    }

    // Public methods
    pub fn new() -> Self {
        let buckets = Self::init_buckets(CSET_INITIAL_CAP);
        Cset {
            buckets,
            max_load_factor: CSET_MAX_LOAD_FACTOR,
            min_load_factor: CSET_MIN_LOAD_FACTOR,
            seed: CSET_DEFAULT_SEED,
            v: CsetValue {
                pi: 0,
                elem: Self::placeholder(),
            },
            bucket_size: 0,
            compare: None,
            temp_buckets: Vec::new(),
        }
    }

    pub fn empty(&self) -> bool {
        self.bucket_size == 0
    }

    pub fn tombstone(&self) -> bool {
        false
    }

    pub fn index(&self, index: usize) -> T {
        Self::copy_of(&self.buckets[index].elem)
    }

    pub fn get_size(&self) -> usize {
        self.bucket_size
    }

    pub fn set_size(&mut self, new_size: usize) {
        self.bucket_size = new_size;
    }

    pub fn get_seed(&self) -> u64 {
        self.seed
    }

    pub fn set_seed(&mut self, seed: u64) {
        self.seed = seed;
    }

    pub fn get_max_load_factor(&self) -> f64 {
        self.max_load_factor
    }

    pub fn set_max_load_factor(&mut self, new_factor: f64) {
        self.max_load_factor = new_factor;
    }

    pub fn get_min_load_factor(&self) -> f64 {
        self.min_load_factor
    }

    pub fn set_min_load_factor(&mut self, new_factor: f64) {
        self.min_load_factor = new_factor;
    }

    pub fn get_buckets(&self) -> &Vec<CsetValue<T>> {
        &self.buckets
    }

    pub fn get_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        alias_mut(&self.buckets)
    }

    pub fn get_temp_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        alias_mut(&self.temp_buckets)
    }

    pub fn size(&self) -> i32 {
        self.bucket_size as i32
    }

    pub fn capacity(&self) -> i32 {
        self.buckets.len() as i32
    }

    pub fn add(&mut self, value: T) -> i32 {
        if self.buckets.is_empty() {
            self.buckets = Self::init_buckets(CSET_INITIAL_CAP);
        }
        let cap = self.buckets.len();
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor {
            self.resize(cap * 2);
        }

        let h1 = self.h1hash(&value);
        let h2 = self.h2hash(&value);
        let cap = self.buckets.len();
        let mut index = 0;
        let mut iteration = 1usize;

        for _ in 0..cap {
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.buckets[index].pi == 0 || self.buckets[index].pi == -1 {
                break;
            }
            if self.matches_custom(index, &value) {
                return 0;
            }
        }

        self.buckets[index] = CsetValue {
            pi: iteration as i32,
            elem: value,
        };
        self.bucket_size += 1;
        0
    }

    pub fn remove(&mut self, value: T) -> i32 {
        let h1 = self.h1hash(&value);
        let cap = self.buckets.len();
        let mut found = false;
        let mut index = 0;
        let mut iteration = 1usize;

        for _ in 0..cap {
            let h2 = self.h2hash(&value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.buckets[index].pi == -1 {
                continue;
            }
            if self.buckets[index].pi == 0 {
                break;
            }
            if self.matches_custom(index, &value) {
                found = true;
                break;
            }
        }

        if found {
            self.buckets[index].pi = -1;
            self.bucket_size -= 1;
        }
        0
    }

    fn contains_impl(&self, value: &T) -> bool {
        let h1 = self.h1hash(value);
        let cap = self.buckets.len();
        let mut iteration = 1usize;

        for _ in 0..cap {
            let h2 = self.h2hash(value);
            let index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.buckets[index].pi == -1 {
                continue;
            }
            if self.buckets[index].pi == 0 {
                return false;
            }
            if self.matches_custom(index, value) {
                return true;
            }
        }
        false
    }

    pub fn contains(&mut self, value: &T) -> bool {
        self.contains_impl(value)
    }

    pub fn iter(&mut self) -> Vec<T> {
        let mut result = Vec::new();
        for val in &self.buckets {
            if val.pi > 0 {
                result.push(Self::copy_of(&val.elem));
            }
        }
        result
    }

    pub fn set_comparator(&mut self, compare: fn(&T, &T) -> bool) {
        self.compare = Some(compare);
    }

    pub fn clear(&mut self) {
        self.buckets = Self::init_buckets(CSET_INITIAL_CAP);
        self.bucket_size = 0;
    }

    pub fn intersect(&mut self, first: &Self, second: &Self) {
        for val in &first.buckets {
            if val.pi > 0 && second.contains_impl(&val.elem) {
                self.add(Self::copy_of(&val.elem));
            }
        }
    }

    pub fn union(&mut self, first: &Self, second: &Self) {
        for val in &first.buckets {
            if val.pi > 0 {
                self.add(Self::copy_of(&val.elem));
            }
        }
        for val in &second.buckets {
            if val.pi > 0 {
                self.add(Self::copy_of(&val.elem));
            }
        }
    }

    pub fn is_disjoint(&mut self, other: &Self) -> bool {
        for val in &self.buckets {
            if val.pi > 0 && other.contains_impl(&val.elem) {
                return false;
            }
        }
        true
    }

    pub fn difference(&mut self, first: &Self, second: &Self) {
        for val in &first.buckets {
            if val.pi > 0 && !second.contains_impl(&val.elem) {
                self.add(Self::copy_of(&val.elem));
            }
        }
    }

    fn resize(&mut self, new_cap: usize) {
        let old_buckets = std::mem::take(&mut self.buckets);
        self.buckets = Self::init_buckets(new_cap);
        self.bucket_size = 0;

        for val in old_buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
    }
}

```

Reply using the block protocol. Update your `<notes>` so they stay accurate.
