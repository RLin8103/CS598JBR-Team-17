# Iteration 5 of at most 40 - controller feedback

## Notices from the controller
- Your edit in the previous reply made things worse (compiles=False, tests 0/0, unsafe 42 vs 43, clippy None vs 3) and was reverted. The files below are the last good version; try a different, smaller change.

## Your notes from the previous turn
## Plan:
1. First, fix the unsafe code issues by replacing raw pointer operations with safe slice operations
2. Implement the XXHash functions properly using slices instead of raw pointers
3. Fix the Cset implementation to match the C behavior exactly
4. Fix Clippy warnings (let_and_return, mem_replace_with_default)
5. Ensure all tests pass with zero unsafe code

Key observations from C code:
- Double hashing: (h1 + i * h2) % cap where i is 1-based in the loop
- Tombstone: pi == -1
- Empty: pi == 0
- Load factor triggers resize when >= max_load_factor
- Custom hashers are optional, default uses XXH64


## Status
- compiles: True (0 errors)
- tests: 15 passed / 15 total (0 failed)
- unsafe metrics (builtin-approximation): lines=15, calls=15, casts=13, pointer_arithmetic=0
- clippy warnings: {"correctness": 2, "style": 1, "complexity": 0, "perf": 0}
- tokens used so far: 164370 / 2000000

## Current phase: SAFETY
All tests pass. Now reduce unsafe behaviour: remove `unsafe` blocks and `unsafe fn`, raw-pointer casts, pointer arithmetic and manual memory management by using slices, Vec, Box, Option and iterators. All tests must still pass after your change. Also fix Clippy findings when you touch the same code. Plan before you edit: list every unsafe site in the list below and pick the ones you can remove entirely (not just document or wrap in another unsafe block). Prefer one real rewrite per reply, e.g. make the core logic work on safe `&[u8]` slices and keep raw-pointer parameters only in the few functions whose signature in the interface file requires them, converting once at that boundary. Adding `// SAFETY:` comments or moving unsafe around does not lower the metrics; only deleting unsafe does.

## cargo build
OK (9 rustc warnings).

## cargo test
15 passed, 0 failed, total 15.

## cargo clippy
Counts: {"correctness": 2, "style": 1, "complexity": 0, "perf": 0} (total 3). Target: 0 in every category.
```
[correctness] warning: this public function might dereference a raw pointer but is not marked `unsafe`
   --> src/cset.rs:197:53
    |
197 |     let slice = unsafe { std::slice::from_raw_parts(input, len) };
    |                                                     ^^^^^
    |
    = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#not_unsafe_ptr_arg_deref
    = note: `-W clippy::not-unsafe-ptr-arg-deref` implied by `-W clippy::correctness`
    = help: to override `-W clippy::correctness` add `#[allow(clippy::not_unsafe_ptr_arg_deref)]`

[correctness] warning: this public function might dereference a raw pointer but is not marked `unsafe`
   --> src/cset.rs:206:53
    |
206 |     let slice = unsafe { std::slice::from_raw_parts(input, len) };
    |                                                     ^^^^^
    |
    = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#not_unsafe_ptr_arg_deref

[style] warning: returning the result of a `let` binding from a block
   --> src/cset.rs:290:17
    |
289 |                 let hash = xxh64_h(ref_bytes.as_ptr(), std::mem::size_of::<T>(), self.seed) | 1;
    |                 -------------------------------------------------------------------------------- unnecessary `let` binding
290 |                 hash
    |                 ^^^^
    |
    = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#let_and_return
    = note: `-W clippy::let-and-return` implied by `-W clippy::style`
    = help: to override `-W clippy::style` add `#[allow(clippy::let_and_return)]`
help: return the expression directly
    |
289 
... [truncated]
```

## unsafe metrics (builtin-approximation)
{"unsafe_lines": 15, "unsafe_calls": 15, "unsafe_casts": 13, "pointer_arithmetic": 0, "unsafe_blocks": 15, "unsafe_fns": 0, "raw_pointer_decls": 2, "ffi_calls": 0, "transmute_uses": 0, "manual_alloc_ops": 0, "files_with_forbid_unsafe_code": 0, "files_analysed": 2}
Where:
- src/cset.rs:27 [unsafe_calls] let bytes = unsafe { std::slice::from_raw_parts(mem_ptr as *const u8, 8) };
- src/cset.rs:48 [unsafe_casts] let ptr = mem_ptr as *mut XXHU32;
- src/cset.rs:49 [unsafe_calls] let bytes = unsafe { std::slice::from_raw_parts(ptr as *const u8, 4) };
- src/cset.rs:193 [raw_pointer_decls] pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:197 [unsafe_calls] let slice = unsafe { std::slice::from_raw_parts(input, len) };
- src/cset.rs:202 [raw_pointer_decls] pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:206 [unsafe_calls] let slice = unsafe { std::slice::from_raw_parts(input, len) };
- src/cset.rs:212 [unsafe_calls] let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
- src/cset.rs:218 [unsafe_calls] let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
- src/cset.rs:275 [unsafe_calls] let elem_bytes = unsafe { std::slice::from_raw_parts(elem_ref as *const T as *const u8, std::mem::size_of::<T>()) };
- src/cset.rs:320 [unsafe_calls] buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
- src/cset.rs:327 [unsafe_calls] v: CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } },
- src/cset.rs:405 [unsafe_calls] self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
- src/cset.rs:414 [unsafe_calls] let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
- src/cset.rs:441 [unsafe_calls] let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
- src/cset.rs:476 [unsafe_calls] let ref_bytes = unsafe { std::slice::from_raw_parts(value as *const T as *const u8, std::mem::size_of::<T>()) };
- src/cset.rs:520 [unsafe_calls] self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
- src/cset.rs:571 [unsafe_calls] self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });

## Current state of the editable Rust files
### src/cset.rs (582 lines)
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

// Helper: check if little endian
pub fn xxh_is_little_endian() -> bool {
    cfg!(target_endian = "little")
}

// Read 8 bytes as little-endian from a slice
pub fn xxh_read_le64(mem_ptr: &mut XXHU8) -> XXHU64 {
    let bytes = unsafe { std::slice::from_raw_parts(mem_ptr as *const u8, 8) };
    u64::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7]])
}

// Read 8 bytes as little-endian from a slice (aligned version)
pub fn xxh_read_le64_align(mem_ptr: &mut XXHU8) -> XXHU64 {
    xxh_read_le64(mem_ptr)
}

// Swap bytes of a u32
pub fn xxh_swap32(x: &mut XXHU32) -> XXHU32 {
    let mut val = *x;
    val = ((val & 0xFF000000) >> 24) |
          ((val & 0x00FF0000) >> 8) |
          ((val & 0x0000FF00) << 8) |
          ((val & 0x000000FF) << 24);
    val
}

// Read 4 bytes as little-endian from a slice
pub fn xxh_read32(mem_ptr: &mut XXHU32) -> XXHU32 {
    let ptr = mem_ptr as *mut XXHU32;
    let bytes = unsafe { std::slice::from_raw_parts(ptr as *const u8, 4) };
    u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]])
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
    acc ^ val.wrapping_mul(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_4)
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

// xxh64 finalize - works with slice
pub fn xxh64_finalize(mut h64: XXHU64, ptr: &[u8], len: usize) -> XXHU64 {
    let mut len = len & 31;
    let mut offset = 0;
    while len >= 8 {
        let k1 = xxh64_round(0, xxh_read_le64_from_slice(&ptr[offset..offset+8]));
        offset += 8;
        h64 ^= k1;
        h64 = h64.rotate_left(27).wrapping_mul(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_4);
        len -= 8;
    }
    if len >= 4 {
        let val = xxh_read_le32_from_slice(&ptr[offset..offset+4]);
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

// xxh64 endian align - works with slice
pub fn xxh64_endian_align(input: &[u8], len: usize, seed: XXHU64) -> XXHU64 {
    let mut offset = 0;
    let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
    let mut v2 = seed.wrapping_add(XXH_PRIME64_2);
    let mut v3 = seed;
    let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
    let mut h64 = if len >= 32 {
        let limit = len - 32;
        while offset <= limit {
            v1 = xxh64_round(v1, xxh_read_le64_from_slice(&input[offset..offset+8]));
            offset += 8;
            v2 = xxh64_round(v2, xxh_read_le64_from_slice(&input[offset..offset+8]));
            offset += 8;
            v3 = xxh64_round(v3, xxh_read_le64_from_slice(&input[offset..offset+8]));
            offset += 8;
            v4 = xxh64_round(v4, xxh_read_le64_from_slice(&input[offset..offset+8]));
            offset += 8;
        }
        v1.rotate_left(1).wrapping_add(v2.rotate_left(7)).wrapping_add(v3.rotate_left(12)).wrapping_add(v4.rotate_left(18))
    } else {
        seed.wrapping_add(XXH_PRIME64_5)
    };
    h64 = xxh64_merge_round(h64, v1);
    h64 = xxh64_merge_round(h64, v2);
    h64 = xxh64_merge_round(h64, v3);
    h64 = xxh64_merge_round(h64, v4);
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize(h64, &input[offset..], len)
}

// xxh64 endian align h - works with slice
pub fn xxh64_endian_align_h(input: &[u8], len: usize, seed: XXHU64) -> XXHU64 {
    let mut offset = 0;
    let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
    let mut v2 = seed.wrapping_sub(XXH_PRIME64_2);
    let mut v3 = seed.wrapping_add(XXH_PRIME64_3);
    let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
    let mut h64 = if len >= 32 {
        let limit = len - 32;
        while offset <= limit {
            v1 = xxh64_round(v1, xxh_read_le64_from_slice(&input[offset..offset+8]));
            offset += 8;
            v2 = xxh64_round(v2, xxh_read_le64_from_slice(&input[offset..offset+8]));
            offset += 8;
            v3 = xxh64_round(v3, xxh_read_le64_from_slice(&input[offset..offset+8]));
            offset += 8;
            v4 = xxh64_round(v4, xxh_read_le64_from_slice(&input[offset..offset+8]));
            offset += 8;
        }
        v1.rotate_left(1).wrapping_add(v2.rotate_left(7)).wrapping_add(v3.rotate_left(12)).wrapping_add(v4.rotate_left(18))
    } else {
        seed.wrapping_add(XXH_PRIME64_1)
    };
    h64 = xxh64_merge_round(h64, v1);
    h64 = xxh64_merge_round(h64, v2);
    h64 = xxh64_merge_round(h64, v3);
    h64 = xxh64_merge_round(h64, v4);
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize(h64, &input[offset..], len)
}

// xxh64
pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align(slice, len, seed)
}

// xxh64_h
pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align_h(slice, len, seed)
}

// cset_hash1_callback
pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align(slice, size, CSET_DEFAULT_SEED)
}

// cset_hash2_callback
pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align_h(slice, size, CSET_DEFAULT_SEED) | 1
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

impl<T: Clone> Cset<T> {
    // Helper functions
    fn is_empty(&self, index: usize) -> bool {
        self.buckets[index].pi == 0
    }

    fn is_tombstone(&self, index: usize) -> bool {
        self.buckets[index].pi == -1
    }

    fn value_elem_ref(val: &CsetValue<T>) -> &T {
        &val.elem
    }

    fn value_elem(val: &CsetValue<T>) -> T {
        val.elem.clone()
    }

    fn value_pi(val: &CsetValue<T>) -> i32 {
        val.pi
    }

    fn bytes_compare(a: &[u8], b: &[u8], size: usize) -> bool {
        a[..size] == b[..size]
    }

    fn matches(&self, vector_ref: &[CsetValue<T>], ref_bytes: &[u8], value: &T, index: usize) -> bool {
        match self.compare {
            Some(compare) => {
                let elem_ref = Self::value_elem_ref(&vector_ref[index]);
                compare(elem_ref, value)
            }
            None => {
                let elem_ref = Self::value_elem_ref(&vector_ref[index]);
                let elem_bytes = unsafe { std::slice::from_raw_parts(elem_ref as *const T as *const u8, std::mem::size_of::<T>()) };
                Self::bytes_compare(elem_bytes, ref_bytes, std::mem::size_of::<T>())
            }
        }
    }

    fn h2hash(&self, ref_bytes: &[u8], _value: &T) -> XXHU64 {
        match self.compare {
            Some(_customhasher) => {
                // The customhasher expects a pointer to T and a hash function
                // We'll need to implement this later
                0
            }
            None => {
                let hash = xxh64_h(ref_bytes.as_ptr(), std::mem::size_of::<T>(), self.seed) | 1;
                hash
            }
        }
    }

    fn h1hash(&self, ref_bytes: &[u8], _value: &T) -> XXHU64 {
        match self.compare {
            Some(_customhasher) => {
                // Implement custom hasher
                0
            }
            None => {
                xxh64(ref_bytes.as_ptr(), std::mem::size_of::<T>(), self.seed)
            }
        }
    }

    fn double_hash_index(ha1: XXHU64, ha2: XXHU64, i: usize, cap: usize) -> usize {
        // Double hashing: (h1 + i * h2) % cap where i is 0-based
        let ha1_usize = ha1 as usize;
        let ha2_usize = ha2 as usize;
        let product = i.wrapping_mul(ha2_usize);
        (ha1_usize.wrapping_add(product)) % cap
    }

    // Public methods
    pub fn new() -> Self {
        let mut buckets = Vec::new();
        buckets.reserve_exact(CSET_INITIAL_CAP);
        for _ in 0..CSET_INITIAL_CAP {
            buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
        Cset {
            buckets,
            max_load_factor: CSET_MAX_LOAD_FACTOR,
            min_load_factor: CSET_MIN_LOAD_FACTOR,
            seed: CSET_DEFAULT_SEED,
            v: CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } },
            bucket_size: 0,
            compare: None,
            temp_buckets: Vec::new(),
        }
    }

    pub fn empty(&self) -> bool {
        self.bucket_size == 0
    }

    pub fn tombstone(&self) -> bool {
        // Placeholder: no tombstone check without index
        false
    }

    pub fn index(&self, index: usize) -> T {
        self.buckets[index].elem.clone()
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

    pub fn get_buckets_ref(&mut self) -> &mut Vec<CsetValue<T>> {
        &mut self.buckets
    }

    pub fn get_temp_buckets_ref(&mut self) -> &mut Vec<CsetValue<T>> {
        &mut self.temp_buckets
    }

    pub fn size(&self) -> i32 {
        self.bucket_size as i32
    }

    pub fn capacity(&self) -> i32 {
        self.buckets.capacity() as i32
    }

    pub fn add(&mut self, value: T) -> i32 {
        // Check load factor before adding
        let cap = self.buckets.capacity();
        if cap == 0 {
            // Initialize with initial capacity if empty
            for _ in 0..CSET_INITIAL_CAP {
                self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
            }
        }
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor && cap > 0 {
            self.resize(cap * 2);
        }
        
        // Compute hash
        let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let h2 = self.h2hash(ref_bytes, &value);
        let mut iteration = 1usize;
        let cap = self.buckets.capacity();
        let mut index = 0usize;
        
        // Search for empty or matching slot
        for _ in 0..cap {
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_empty(index) || self.is_tombstone(index) {
                break;
            }
            if self.matches(&self.buckets, ref_bytes, &value, index) {
                // Found duplicate, don't add
                return 0;
            }
        }
        
        // Add new element at the found index
        self.buckets[index] = CsetValue { pi: iteration as i32, elem: value };
        self.bucket_size += 1;
        0
    }

    pub fn remove(&mut self, value: T) -> i32 {
        let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let mut found = false;
        let mut iteration = 1usize;
        let cap = self.buckets.capacity();
        let mut index = 0usize;
        
        // Search for the element
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_tombstone(index) {
                continue;
            }
            if self.is_empty(index) {
                break;
            }
            if self.matches(&self.buckets, ref_bytes, &value, index) {
                found = true;
                break;
            }
        }
        
        if found {
            // Mark as tombstone
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 2, cap);
            self.buckets[index].pi = -1;
            self.bucket_size -= 1;
        }
        0
    }

    pub fn contains(&self, value: &T) -> bool {
        let ref_bytes = unsafe { std::slice::from_raw_parts(value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, value);
        let mut iteration = 1usize;
        let cap = self.buckets.capacity();
        
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, value);
            let index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_tombstone(index) {
                continue;
            }
            if self.is_empty(index) {
                return false;
            }
            if self.matches(&self.buckets, ref_bytes, value, index) {
                return true;
            }
        }
        false
    }

    pub fn iter(&mut self) -> Vec<T> {
        let mut result = Vec::new();
        for val in &self.buckets {
            if val.pi > 0 {
                result.push(val.elem.clone());
            }
        }
        result
    }

    pub fn set_comparator(&mut self, compare: fn(&T, &T) -> bool) {
        self.compare = Some(compare);
    }

    pub fn clear(&mut self) {
        self.buckets.clear();
        self.buckets.shrink_to_fit();
        self.bucket_size = 0;
        if CSET_FORCE_INITIALIZE {
            // Re-initialize with initial capacity
            self.buckets.reserve_exact(CSET_INITIAL_CAP);
            for _ in 0..CSET_INITIAL_CAP {
                self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
            }
        }
    }

    pub fn intersect(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 && second.contains(&val.elem) {
                self.add(val.elem.clone());
            }
        }
    }

    pub fn union(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 {
                self.add(val.elem.clone());
            }
        }
        for val in &second.buckets {
            if val.pi > 0 {
                self.add(val.elem.clone());
            }
        }
    }

    pub fn is_disjoint(&self, other: &Self) -> bool {
        for val in &self.buckets {
            if val.pi > 0 && other.contains(&val.elem) {
                return false;
            }
        }
        true
    }

    pub fn difference(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 && !second.contains(&val.elem) {
                self.add(val.elem.clone());
            }
        }
    }

    // Internal resize function
    fn resize(&mut self, new_cap: usize) {
        let old_buckets = std::mem::take(&mut self.buckets);
        self.buckets.reserve_exact(new_cap);
        for _ in 0..new_cap {
            self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
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
