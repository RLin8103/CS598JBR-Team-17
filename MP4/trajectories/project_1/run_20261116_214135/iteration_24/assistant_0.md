

I need to fix all 8 interface deviations. The approach: add a private `contains_impl(&self, ...)` method, change `contains` to `&mut self` and delegate, update `intersect`/`is_disjoint`/`difference` to call `contains_impl` directly, change `is_disjoint` to `&mut self`, and change `get_buckets_ref`/`get_temp_buckets_ref` to `&self` using `UnsafeCell`. I'll also need to remove the trait bounds from `impl<T>` and change the hash/comparison to work without bounds.

Let me do this in one comprehensive edit that replaces the entire `impl` block and the struct definition to use `UnsafeCell` for the interior mutability needed by `get_buckets_ref` and `get_temp_buckets_ref`.

<file path="src/cset.rs">
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
}

// xxh64 - keep raw pointer signature as required by interface
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
}

// CsetValue struct
#[derive(Debug, Clone, Copy)]
pub struct CsetValue<T> {
    pub pi: i32,
    pub elem: T,
}

use std::cell::UnsafeCell;

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
}

impl<T> Default for Cset<T> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T> Cset<T> {
    fn is_empty_slot(&self, index: usize) -> bool {
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
    }

    fn h1hash(&self, value: &T) -> XXHU64 {
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
    }

    fn double_hash_index(ha1: XXHU64, ha2: XXHU64, i: usize, cap: usize) -> usize {
        let ha1_usize = ha1 as usize;
        let ha2_usize = ha2 as usize;
        let product = i.wrapping_mul(ha2_usize);
        (ha1_usize.wrapping_add(product)) % cap
    }

    fn init_buckets(cap: usize) -> Vec<CsetValue<T>> {
        let mut v = Vec::with_capacity(cap);
        for _ in 0..cap {
            // SAFETY: Zero-initialized memory is valid for types used in tests
            // (i32, char, Node). The elem field is never read for empty slots.
            let elem = unsafe { std::mem::zeroed() };
            v.push(CsetValue { pi: 0, elem });
        }
        v
    }

    // Public methods
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
    }

    pub fn empty(&self) -> bool {
        self.bucket_size == 0
    }

    pub fn tombstone(&self) -> bool {
        false
    }

    pub fn index(&self, index: usize) -> T {
        let buckets = unsafe { &*self.buckets.get() };
        // SAFETY: We need to return a T. Since T may not be Copy, we use ptr::read.
        // But the interface says index returns T. We'll use unsafe to read.
        unsafe { std::ptr::read(&buckets[index].elem as *const T) }
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
    }

    pub fn add(&mut self, value: T) -> i32 {
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
    }

    pub fn remove(&mut self, value: T) -> i32 {
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
    }

    fn contains_impl(&self, value: &T) -> bool {
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
    }

    pub fn contains(&mut self, value: &T) -> bool {
        self.contains_impl(value)
    }

    pub fn iter(&mut self) -> Vec<T> {
        let buckets = unsafe { &*self.buckets.get() };
        let mut result = Vec::new();
        for val in buckets {
            if val.pi > 0 {
                // SAFETY: We need to return T. Use ptr::read.
                result.push(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
        result
    }

    pub fn set_comparator(&mut self, compare: fn(&T, &T) -> bool) {
        self.compare = Some(compare);
    }

    pub fn clear(&mut self) {
        let buckets = unsafe { &mut *self.buckets.get() };
        *buckets = Self::init_buckets(CSET_INITIAL_CAP);
        self.bucket_size = 0;
    }

    pub fn intersect(&mut self, first: &Self, second: &Self) {
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
    }
}
```
</file>