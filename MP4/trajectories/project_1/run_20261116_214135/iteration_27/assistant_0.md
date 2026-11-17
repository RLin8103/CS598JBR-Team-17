

I need to fix the 4 interface deviations. The key insight: I need to change the public function signatures to match the interface exactly, but keep the internal implementation working. The problem with my previous attempt was that I changed the signatures but also changed the internal helpers, and the callers (like `xxh64`, `cset_hash1_callback`, `h1hash`, `h2hash`) still passed `&[u8]` to functions that now expect `&mut XXHU8`.

The approach: keep the public signatures matching the interface, but have them immediately delegate to internal slice-based versions. The internal versions stay as `&[u8]` and are used by all the internal callers. The public functions just convert the `&mut XXHU8` to a slice and call the internal version.

Let me make this change carefully.

<edit path="src/cset.rs">
<search>// Read 64 bits from slice (little-endian)
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
    xxh64_finalize(h64, &input[offset..], len)
}</search>
<replace>// Read 64 bits from slice (little-endian)
fn xxh_read_le64_from_slice(slice: &[u8]) -> XXHU64 {
    u64::from_le_bytes([slice[0], slice[1], slice[2], slice[3], slice[4], slice[5], slice[6], slice[7]])
}

// Read 32 bits from slice (little-endian)
fn xxh_read_le32_from_slice(slice: &[u8]) -> XXHU32 {
    u32::from_le_bytes([slice[0], slice[1], slice[2], slice[3]])
}

// Internal version: works with &[u8]
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
pub fn xxh64_finalize(mut h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    // SAFETY: caller guarantees ptr points to at least len bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(ptr as *const u8, len) };
    xxh64_finalize_inner(h64, slice, len)
}

// Internal version: works with &[u8]
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
    // SAFETY: caller guarantees input points to at least len bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(input as *const u8, len) };
    xxh64_endian_align_inner(slice, len, seed)
}

// Internal version: works with &[u8]
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
    // SAFETY: caller guarantees input points to at least len bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(input as *const u8, len) };
    xxh64_endian_align_h_inner(slice, len, seed)
}</replace>
</edit>

Now I need to update all callers that currently call `xxh64_endian_align` and `xxh64_endian_align_h` with `&[u8]` to call the `_inner` versions instead. Let me update `xxh64`, `xxh64_h`, `cset_hash1_callback`, `cset_hash2_callback`, `h1hash`, and `h2hash`.

<edit path="src/cset.rs">
<search>// xxh64 - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    // SAFETY: caller guarantees input points to valid memory of at least len bytes
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align(slice, len, seed)
}

// xxh64_h - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    // SAFETY: caller guarantees input points to valid memory of at least len bytes
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align_h(slice, len, seed)
}

// cset_hash1_callback - hash bytes using xxh64
pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    // SAFETY: memptr points to at least size bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align(slice, size, CSET_DEFAULT_SEED)
}

// cset_hash2_callback - hash bytes using xxh64_h variant, OR'd with 1
pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    // SAFETY: memptr points to at least size bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align_h(slice, size, CSET_DEFAULT_SEED) | 1
}</search>
<replace>// xxh64 - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    // SAFETY: caller guarantees input points to valid memory of at least len bytes
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align_inner(slice, len, seed)
}

// xxh64_h - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    // SAFETY: caller guarantees input points to valid memory of at least len bytes
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align_h_inner(slice, len, seed)
}

// cset_hash1_callback - hash bytes using xxh64
pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    // SAFETY: memptr points to at least size bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align_inner(slice, size, CSET_DEFAULT_SEED)
}

// cset_hash2_callback - hash bytes using xxh64_h variant, OR'd with 1
pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    // SAFETY: memptr points to at least size bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align_h_inner(slice, size, CSET_DEFAULT_SEED) | 1
}</search>
</edit>

Now update `h1hash` and `h2hash` to use the inner versions:

<edit path="src/cset.rs">
<search>    fn h1hash(&self, value: &T) -> XXHU64 {
        let bytes = unsafe {
            std::slice::from_raw_parts(
                value as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        };
        xxh64_endian_align(bytes, std::mem::size_of::<T>(), self.seed)
    }

    fn h2hash(&self, value: &T) -> XXHU64 {
        let bytes = unsafe {
            std::slice::from_raw_parts(
                value as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        };
        xxh64_endian_align_h(bytes, std::mem::size_of::<T>(), self.seed) | 1
    }</search>
<replace>    fn h1hash(&self, value: &T) -> XXHU64 {
        let bytes = unsafe {
            std::slice::from_raw_parts(
                value as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        };
        xxh64_endian_align_inner(bytes, std::mem::size_of::<T>(), self.seed)
    }

    fn h2hash(&self, value: &T) -> XXHU64 {
        let bytes = unsafe {
            std::slice::from_raw_parts(
                value as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        };
        xxh64_endian_align_h_inner(bytes, std::mem::size_of::<T>(), self.seed) | 1
    }</search>
</edit>

Now fix the Cset struct to match the interface exactly (remove UnsafeCell wrappers):

<edit path="src/cset.rs">
<search>use std::cell::UnsafeCell;

// Cset struct
pub struct Cset<T> {
    buckets: UnsafeCell<Vec<CsetValue<T>>>,
    max_load_factor: f64,
    min_load_factor: f64,
    seed: u64,
    v: UnsafeCell<CsetValue<T>>,
    bucket_size: usize,
    compare: Option<fn(&T, &T) -> bool>,
    temp_buckets: UnsafeCell<Vec<CsetValue<T>>>,
}</search>
<replace>// Cset struct - exactly as in interface file
pub struct Cset<T> {
    buckets: Vec<CsetValue<T>>,
    max_load_factor: f64,
    min_load_factor: f64,
    seed: u64,
    v: CsetValue<T>,
    bucket_size: usize,
    compare: Option<fn(&T, &T) -> bool>,
    temp_buckets: Vec<CsetValue<T>>,
}</search>
</edit>

Now update all methods that used `UnsafeCell` to use direct field access. I need to update `new()`, `is_empty_slot`, `is_tombstone_slot`, `matches_default`, `matches_custom`, `get_buckets`, `get_buckets_ref`, `get_temp_buckets_ref`, `capacity`, `add`, `remove`, `contains_impl`, `iter`, `clear`, `intersect`, `union`, `is_disjoint`, `difference`, `resize`, and `index`.

Let me update `new()` first:

<edit path="src/cset.rs">
<search>    // Public methods
    pub fn new() -> Self {
        let buckets = Self::init_buckets(CSET_INITIAL_CAP);
        // SAFETY: Zero-initialized memory is valid for types used in tests.
        // The v field is a scratch slot, initialized before use.
        let elem = unsafe { std::mem::zeroed() };
        Cset {
            buckets: UnsafeCell::new(buckets),
            max_load_factor: CSET_MAX_LOAD_FACTOR,
            min_load_factor: CSET_MIN_LOAD_FACTOR,
            seed: CSET_DEFAULT_SEED,
            v: UnsafeCell::new(CsetValue { pi: 0, elem }),
            bucket_size: 0,
            compare: None,
            temp_buckets: UnsafeCell::new(Vec::new()),
        }
    }</search>
<replace>    // Public methods
    pub fn new() -> Self {
        let buckets = Self::init_buckets(CSET_INITIAL_CAP);
        // SAFETY: Zero-initialized memory is valid for types used in tests.
        // The v field is a scratch slot, initialized before use.
        let elem = unsafe { std::mem::zeroed() };
        Cset {
            buckets,
            max_load_factor: CSET_MAX_LOAD_FACTOR,
            min_load_factor: CSET_MIN_LOAD_FACTOR,
            seed: CSET_DEFAULT_SEED,
            v: CsetValue { pi: 0, elem },
            bucket_size: 0,
            compare: None,
            temp_buckets: Vec::new(),
        }
    }</search>
</edit>

Now update `is_empty_slot`, `is_tombstone_slot`, `matches_default`, `matches_custom` to use `self.buckets` directly:

<edit path="src/cset.rs">
<search>    fn is_empty_slot(&self, index: usize) -> bool {
        // SAFETY: We only read pi, which is Copy, and we don't mutate
        let buckets = unsafe { &*self.buckets.get() };
        buckets[index].pi == 0
    }

    fn is_tombstone_slot(&self, index: usize) -> bool {
        let buckets = unsafe { &*self.buckets.get() };
        buckets[index].pi == -1
    }

    fn matches_default(&self, index: usize, value: &T) -> bool {
        let buckets = unsafe { &*self.buckets.get() };
        // Compare bytes using transmute to &[u8]
        let elem_bytes = unsafe {
            std::slice::from_raw_parts(
                &buckets[index].elem as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        };
        let value_bytes = unsafe {
            std::slice::from_raw_parts(
                value as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        };
        elem_bytes == value_bytes
    }

    fn matches_custom(&self, index: usize, value: &T) -> bool {
        let buckets = unsafe { &*self.buckets.get() };
        match self.compare {
            Some(cmp) => cmp(&buckets[index].elem, value),
            None => self.matches_default(index, value),
        }
    }</search>
<replace>    fn is_empty_slot(&self, index: usize) -> bool {
        self.buckets[index].pi == 0
    }

    fn is_tombstone_slot(&self, index: usize) -> bool {
        self.buckets[index].pi == -1
    }

    fn matches_default(&self, index: usize, value: &T) -> bool {
        // Compare bytes using transmute to &[u8]
        let elem_bytes = unsafe {
            std::slice::from_raw_parts(
                &self.buckets[index].elem as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        };
        let value_bytes = unsafe {
            std::slice::from_raw_parts(
                value as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        };
        elem_bytes == value_bytes
    }

    fn matches_custom(&self, index: usize, value: &T) -> bool {
        match self.compare {
            Some(cmp) => cmp(&self.buckets[index].elem, value),
            None => self.matches_default(index, value),
        }
    }</search>
</edit>

Now update `get_buckets`, `get_buckets_ref`, `get_temp_buckets_ref`, `capacity`:

<edit path="src/cset.rs">
<search>    pub fn get_buckets(&self) -> &Vec<CsetValue<T>> {
        unsafe { &*self.buckets.get() }
    }

    pub fn get_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        unsafe { &mut *self.buckets.get() }
    }

    pub fn get_temp_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        unsafe { &mut *self.temp_buckets.get() }
    }

    pub fn size(&self) -> i32 {
        self.bucket_size as i32
    }

    pub fn capacity(&self) -> i32 {
        let buckets = unsafe { &*self.buckets.get() };
        buckets.capacity() as i32
    }</search>
<replace>    pub fn get_buckets(&self) -> &Vec<CsetValue<T>> {
        &self.buckets
    }

    #[allow(clippy::mut_from_ref)]
    pub fn get_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        // SAFETY: The interface requires &self -> &mut Vec, which is unsound in general.
        // We use unsafe to satisfy the interface. Callers must not create aliasing references.
        unsafe { &mut *(&self.buckets as *const Vec<CsetValue<T>> as *mut Vec<CsetValue<T>>) }
    }

    #[allow(clippy::mut_from_ref)]
    pub fn get_temp_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        // SAFETY: Same as get_buckets_ref - required by interface.
        unsafe { &mut *(&self.temp_buckets as *const Vec<CsetValue<T>> as *mut Vec<CsetValue<T>>) }
    }

    pub fn size(&self) -> i32 {
        self.bucket_size as i32
    }

    pub fn capacity(&self) -> i32 {
        self.buckets.capacity() as i32
    }</search>
</edit>

Now update `add`, `remove`, `contains_impl`, `iter`, `clear`, `intersect`, `union`, `is_disjoint`, `difference`, `resize`, `index`:

<edit path="src/cset.rs">
<search>    pub fn index(&self, index: usize) -> T {
        let buckets = unsafe { &*self.buckets.get() };
        // SAFETY: We need to return a T. Since T may not be Copy, we use ptr::read.
        // But the interface says index returns T. We'll use unsafe to read.
        unsafe { std::ptr::read(&buckets[index].elem as *const T) }
    }</search>
<replace>    pub fn index(&self, index: usize) -> T {
        // SAFETY: We need to return a T. Since T may not be Copy, we use ptr::read.
        // But the interface says index returns T. We'll use unsafe to read.
        unsafe { std::ptr::read(&self.buckets[index].elem as *const T) }
    }</search>
</edit>

<edit path="src/cset.rs">
<search>    pub fn add(&mut self, value: T) -> i32 {
        let buckets = unsafe { &mut *self.buckets.get() };
        let cap = buckets.capacity();
        if cap == 0 {
            *buckets = Self::init_buckets(CSET_INITIAL_CAP);
        }
        let cap = buckets.capacity();
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor && cap > 0 {
            self.resize(cap * 2);
        }

        let h1 = self.h1hash(&value);
        let h2 = self.h2hash(&value);
        let buckets = unsafe { &mut *self.buckets.get() };
        let cap = buckets.capacity();
        let mut index = 0;
        let mut iteration = 1usize;

        for _ in 0..cap {
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if buckets[index].pi == 0 || buckets[index].pi == -1 {
                break;
            }
            if self.matches_custom(index, &value) {
                return 0;
            }
        }

        buckets[index] = CsetValue {
            pi: iteration as i32,
            elem: value,
        };
        self.bucket_size += 1;
        0
    }</search>
<replace>    pub fn add(&mut self, value: T) -> i32 {
        let cap = self.buckets.capacity();
        if cap == 0 {
            self.buckets = Self::init_buckets(CSET_INITIAL_CAP);
        }
        let cap = self.buckets.capacity();
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor && cap > 0 {
            self.resize(cap * 2);
        }

        let h1 = self.h1hash(&value);
        let h2 = self.h2hash(&value);
        let cap = self.buckets.capacity();
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
    }</search>
</edit>

<edit path="src/cset.rs">
<search>    pub fn remove(&mut self, value: T) -> i32 {
        let h1 = self.h1hash(&value);
        let buckets = unsafe { &mut *self.buckets.get() };
        let cap = buckets.capacity();
        let mut found = false;
        let mut index = 0;
        let mut iteration = 1usize;

        for _ in 0..cap {
            let h2 = self.h2hash(&value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if buckets[index].pi == -1 {
                continue;
            }
            if buckets[index].pi == 0 {
                break;
            }
            if self.matches_custom(index, &value) {
                found = true;
                break;
            }
        }

        if found {
            buckets[index].pi = -1;
            self.bucket_size -= 1;
        }
        0
    }</search>
<replace>    pub fn remove(&mut self, value: T) -> i32 {
        let h1 = self.h1hash(&value);
        let cap = self.buckets.capacity();
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
    }</search>
</edit>

<edit path="src/cset.rs">
<search>    fn contains_impl(&self, value: &T) -> bool {
        let h1 = self.h1hash(value);
        let buckets = unsafe { &*self.buckets.get() };
        let cap = buckets.capacity();
        let mut iteration = 1usize;

        for _ in 0..cap {
            let h2 = self.h2hash(value);
            let index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if buckets[index].pi == -1 {
                continue;
            }
            if buckets[index].pi == 0 {
                return false;
            }
            if self.matches_custom(index, value) {
                return true;
            }
        }
        false
    }</search>
<replace>    fn contains_impl(&self, value: &T) -> bool {
        let h1 = self.h1hash(value);
        let cap = self.buckets.capacity();
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
    }</search>
</edit>

<edit path="src/cset.rs">
<search>    pub fn iter(&mut self) -> Vec<T> {
        let buckets = unsafe { &*self.buckets.get() };
        let mut result = Vec::new();
        for val in buckets {
            if val.pi > 0 {
                // SAFETY: We need to return T. Use ptr::read.
                result.push(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
        result
    }</search>
<replace>    pub fn iter(&mut self) -> Vec<T> {
        let mut result = Vec::new();
        for val in &self.buckets {
            if val.pi > 0 {
                // SAFETY: We need to return T. Use ptr::read.
                result.push(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
        result
    }</search>
</edit>

<edit path="src/cset.rs">
<search>    pub fn clear(&mut self) {
        let buckets = unsafe { &mut *self.buckets.get() };
        *buckets = Self::init_buckets(CSET_INITIAL_CAP);
        self.bucket_size = 0;
    }</search>
<replace>    pub fn clear(&mut self) {
        self.buckets = Self::init_buckets(CSET_INITIAL_CAP);
        self.bucket_size = 0;
    }</search>
</edit>

<edit path="src/cset.rs">
<search>    pub fn intersect(&mut self, first: &Self, second: &Self) {
        self.clear();
        let first_buckets = unsafe { &*first.buckets.get() };
        for val in first_buckets {
            if val.pi > 0 && second.contains_impl(&val.elem) {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
    }

    pub fn union(&mut self, first: &Self, second: &Self) {
        self.clear();
        let first_buckets = unsafe { &*first.buckets.get() };
        for val in first_buckets {
            if val.pi > 0 {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
        let second_buckets = unsafe { &*second.buckets.get() };
        for val in second_buckets {
            if val.pi > 0 {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
    }

    pub fn is_disjoint(&mut self, other: &Self) -> bool {
        let self_buckets = unsafe { &*self.buckets.get() };
        for val in self_buckets {
            if val.pi > 0 && other.contains_impl(&val.elem) {
                return false;
            }
        }
        true
    }

    pub fn difference(&mut self, first: &Self, second: &Self) {
        self.clear();
        let first_buckets = unsafe { &*first.buckets.get() };
        for val in first_buckets {
            if val.pi > 0 && !second.contains_impl(&val.elem) {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
    }

    fn resize(&mut self, new_cap: usize) {
        let buckets = unsafe { &mut *self.buckets.get() };
        let old_buckets = std::mem::take(buckets);
        *buckets = Self::init_buckets(new_cap);
        self.bucket_size = 0;

        for val in old_buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
    }</search>
<replace>    pub fn intersect(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 && second.contains_impl(&val.elem) {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
    }

    pub fn union(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
        for val in &second.buckets {
            if val.pi > 0 {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
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
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 && !second.contains_impl(&val.elem) {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
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
    }</search>
</edit>

Now remove the unused `use std::cell::UnsafeCell;`:

<edit path="src/cset.rs">
<search>use std::cell::UnsafeCell;

// Cset struct - exactly as in interface file</search>
<replace>// Cset struct - exactly as in interface file</search>
</edit>

<notes>
Fixed all 4 interface deviations:
1. xxh64_finalize: signature now matches interface (&mut XXHU8)
2. xxh64_endian_align: signature now matches interface (&mut XXHU8)
3. xxh64_endian_align_h: signature now matches interface (&mut XXHU8)
4. Cset struct: removed UnsafeCell wrappers, fields match interface exactly

Internal _inner functions (xxh64_finalize_inner, xxh64_endian_align_inner, xxh64_endian_align_h_inner) work with &[u8] and are called by internal code. Public functions convert &mut XXHU8 to slice via unsafe and delegate.

For get_buckets_ref and get_temp_buckets_ref, added #[allow(clippy::mut_from_ref)] since the interface requires &self -> &mut Vec which is inherently unsound.

TODO: Remove remaining unsafe code (zeroed(), ptr::read, from_raw_parts for bytes comparison). The unsafe is needed because T is unbounded and we need to hash/compare raw bytes. This is inherent to the C interface design.
</notes>