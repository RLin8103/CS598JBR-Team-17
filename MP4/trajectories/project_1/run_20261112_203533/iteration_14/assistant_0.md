<edit path="src/cset.rs">
<search>
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

impl<T> Cset<T> {
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
        val.elem
    }

    fn value_pi(val: &CsetValue<T>) -> i32 {
        val.pi
    }

    fn bytes_compare(a: &[u8], b: &[u8], size: usize) -> bool {
        a[..size] == b[..size]
    }

    fn matches(&self, vector_ref: &Vec<CsetValue<T>>, ref_bytes: &[u8], value: &T, index: usize) -> bool {
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

    fn h2hash(&self, ref_bytes: &[u8], value: &T) -> XXHU64 {
        match self.compare {
            Some(customhasher) => {
                // The customhasher expects a pointer to T and a hash function
                // We'll need to implement this later
                0
            }
            None => {
                let hash = xxh64_h(ref_bytes.as_ptr() as *const u8, std::mem::size_of::<T>(), self.seed) | 1;
                hash
            }
        }
    }

    fn h1hash(&self, ref_bytes: &[u8], value: &T) -> XXHU64 {
        match self.compare {
            Some(customhasher) => {
                // Implement custom hasher
                0
            }
            None => {
                xxh64(ref_bytes.as_ptr() as *const u8, std::mem().size_of::<T>(), self.seed)
            }
        }
    }

    fn double_hash_index(ha1: XXHU64, ha2: XXHU64, i: usize, cap: usize) -> usize {
        ((ha1 as usize) + (i * (ha2 as usize))) % cap
    }

    // Public methods
    pub fn new() -> Self {
        let mut buckets = Vec::new();
        cset_vector__init_with_cap(&mut buckets, CSET_INITIAL_CAP);
        if CSET_FORCE_INITIALIZE {
            for i in 0..buckets.len() {
                buckets[i].pi = 0;
            }
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
        self.buckets[index].elem
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
        &mut self.buckets
    }

    pub fn get_temp_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        &mut self.temp_buckets
    }

    pub fn size(&self) -> i32 {
        self.bucket_size as i32
    }

    pub fn capacity(&self) -> i32 {
        self.buckets.capacity() as i32
    }

    pub fn add(&mut self, value: T) -> i32 {
        // Compute hash
        let mut ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let mut found = false;
        let mut iteration = 1;
        let mut index = 0;
        let cap = self.buckets.capacity();
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_empty(index) || self.is_tombstone(index) {
                break;
            }
            if self.matches(&self.buckets, ref_bytes, &value, index) {
                found = true;
                break;
            }
        }
        if !found {
            // Ensure capacity
            if self.bucket_size >= cap {
                self.resize(cap * 2);
            }
            let index = Self::double_hash_index(h1, self.h2hash(ref_bytes, &value), iteration - 1, self.buckets.capacity());
            self.buckets[index] = CsetValue { pi: iteration as i32, elem: value };
            self.bucket_size += 1;
        }
        0
    }

    pub fn remove(&mut self, value: T) -> i32 {
        let mut ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let mut found = false;
        let mut iteration = 1;
        let cap = self.buckets.capacity();
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, &value);
            let index = Self::double_hash_index(h1, h2, iteration - 1, cap);
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
            let index = Self::double_hash_index(h1, self.h2hash(ref_bytes, &value), iteration - 2, self.buckets.capacity());
            self.buckets[index].pi = -1;
            self.bucket_size -= 1;
        }
        0
    }

    pub fn contains(&mut self, value: &T) -> bool {
        let mut ref_bytes = unsafe { std::slice::from_raw_parts(value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, value);
        let mut iteration = 1;
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
                result.push(val.elem);
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
            cset_vector__init_with_cap(&mut self.buckets, CSET_INITIAL_CAP);
            for i in 0..self.buckets.len() {
                self.buckets[i].pi = 0;
            }
        }
    }

    pub fn intersect(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 && second.contains(&val.elem) {
                self.add(val.elem);
            }
        }
    }

    pub fn union(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
        for val in &second.buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
    }

    pub fn is_disjoint(&mut self, other: &Self) -> bool {
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
                self.add(val.elem);
            }
        }
    }

    // Internal resize function
    fn resize(&mut self, new_cap: usize) {
        let mut temp = Vec::new();
        cset_vector__init_with_cap(&mut temp, new_cap);
        for i in 0..temp.len() {
            temp[i].pi = 0;
        }
        let old_buckets = std::mem::replace(&mut self.buckets, temp);
        self.bucket_size = 1; // reset size before reinserting
        for val in old_buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
    }
}
[remaining lines]

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

// Read 8 bytes as little-endian from a pointer (unsafe but required by interface)
pub fn xxh_read_le64(mem_ptr: &mut XXHU8) -> XXHU64 {
    let ptr = mem_ptr as *mut XXHU8;
    // Safe to create a slice of 8 bytes from the pointer (caller guarantees validity)
    let bytes = unsafe { std::slice::from_raw_parts(ptr as *const u8, 8) };
    u64::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7]])
}

// Read 8 bytes as little-endian from a pointer (aligned version)
pub fn xxh_read_le64_align(mem_ptr: &mut XXHU8) -> XXHU64 {
    xxh_read_le64(mem_ptr)
}

// Swap bytes of a u32
</search>
<replace>
// Cset struct
pub struct Cset<T> {
    buckets: Vec<CsetValue<T>>,
    max_load_factor: f64,
    min_load_factor: f64,
    seed: u64,
    v: CsetValue<T>,
    bucket_size: usize,
    compare: Option<fn(&T, &T) -> bool>,
    custom_hasher: Option<fn(&T, fn(&[u8]) -> u64) -> u64>,
    temp_buckets: Vec<CsetValue<T>>,
}

impl<T> Cset<T> {
    // Helper functions
    fn is_empty(&self, index: usize) -> bool {
        self.buckets.get(index).map(|v| v.pi == 0).unwrap_or(true)
    }

    fn is_tombstone(&self, index: usize) -> bool {
        self.buckets.get(index).map(|v| v.pi == -1).unwrap_or(false)
    }

    fn value_elem_ref(val: &CsetValue<T>) -> &T {
        &val.elem
    }

    fn value_elem(val: &CsetValue<T>) -> T
    where
        T: Copy,
    {
        val.elem
    }

    fn value_pi(val: &CsetValue<T>) -> i32 {
        val.pi
    }

    fn bytes_compare(a: &[u8], b: &[u8], size: usize) -> bool {
        a.get(..size) == b.get(..size)
    }

    fn get_bytes_of_value(val: &T) -> &[u8] {
        // Use a safe approach: we need to get bytes of T
        // For now, we'll use a helper that works with the reference
        // This is a limitation - we can't safely get bytes of arbitrary T without unsafe
        // But we can use the fact that we're only called with references we control
        unsafe { std::slice::from_raw_parts(val as *const T as *const u8, std::mem::size_of::<T>()) }
    }

    fn matches(&self, vector_ref: &Vec<CsetValue<T>>, ref_bytes: &[u8], value: &T, index: usize) -> bool {
        match self.compare {
            Some(compare) => {
                let elem_ref = Self::value_elem_ref(&vector_ref[index]);
                compare(elem_ref, value)
            }
            None => {
                let elem_ref = Self::value_elem_ref(&vector_ref[index]);
                let elem_bytes = Self::get_bytes_of_value(elem_ref);
                Self::bytes_compare(elem_bytes, ref_bytes, std::mem::size_of::<T>())
            }
        }
    }

    fn h2hash(&self, ref_bytes: &[u8], value: &T) -> XXHU64 {
        if let Some(custom_hasher) = self.custom_hasher {
            custom_hasher(value, |bytes| xxh64_endian_align_h(bytes, bytes.len(), CSET_DEFAULT_SEED))
        } else {
            let hash = xxh64_endian_align_h(ref_bytes, std::mem::size_of::<T>(), self.seed) | 1;
            hash
        }
    }

    fn h1hash(&self, ref_bytes: &[u8], value: &T) -> XXHU64 {
        if let Some(custom_hasher) = self.custom_hasher {
            custom_hasher(value, |bytes| xxh64_endian_align(bytes, bytes.len(), CSET_DEFAULT_SEED))
        } else {
            xxh64_endian_align(ref_bytes, std::mem::size_of::<T>(), self.seed)
        }
    }

    fn double_hash_index(ha1: XXHU64, ha2: XXHU64, i: usize, cap: usize) -> usize {
        ((ha1 as usize) + (i * (ha2 as usize))) % cap
    }

    // Public methods
    pub fn new() -> Self
    where
        T: Default,
    {
        let mut buckets = Vec::new();
        cset_vector__init_with_cap(&mut buckets, CSET_INITIAL_CAP);
        if CSET_FORCE_INITIALIZE {
            for i in 0..buckets.len() {
                buckets[i].pi = 0;
            }
        }
        Cset {
            buckets,
            max_load_factor: CSET_MAX_LOAD_FACTOR,
            min_load_factor: CSET_MIN_LOAD_FACTOR,
            seed: CSET_DEFAULT_SEED,
            v: CsetValue { pi: 0, elem: T::default() },
            bucket_size: 0,
            compare: None,
            custom_hasher: None,
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

    pub fn index(&self, index: usize) -> T
    where
        T: Copy,
    {
        self.buckets[index].elem
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
        &mut self.buckets
    }

    pub fn get_temp_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        &mut self.temp_buckets
    }

    pub fn size(&self) -> i32 {
        self.bucket_size as i32
    }

    pub fn capacity(&self) -> i32 {
        self.buckets.capacity() as i32
    }

    pub fn add(&mut self, value: T) -> i32
    where
        T: Copy,
    {
        // Compute hash
        let ref_bytes = Self::get_bytes_of_value(&value);
        let h1 = self.h1hash(ref_bytes, &value);
        let mut found = false;
        let mut iteration = 1;
        let mut index = 0;
        let cap = self.buckets.capacity();
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_empty(index) || self.is_tombstone(index) {
                break;
            }
            if self.matches(&self.buckets, ref_bytes, &value, index) {
                found = true;
                break;
            }
        }
        if !found {
            // Ensure capacity
            if self.bucket_size >= cap {
                self.resize(cap * 2);
            }
            let index = Self::double_hash_index(h1, self.h2hash(ref_bytes, &value), iteration - 1, self.buckets.capacity());
            // Ensure the bucket exists
            if index >= self.buckets.len() {
                self.buckets.resize(index + 1, CsetValue { pi: 0, elem: T::default() });
            }
            self.buckets[index] = CsetValue { pi: iteration as i32, elem: value };
            self.bucket_size += 1;
        }
        0
    }

    pub fn remove(&mut self, value: T) -> i32
    where
        T: Copy,
    {
        let ref_bytes = Self::get_bytes_of_value(&value);
        let h1 = self.h1hash(ref_bytes, &value);
        let mut found = false;
        let mut iteration = 1;
        let cap = self.buckets.capacity();
        let mut found_index = 0;
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, &value);
            let index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_tombstone(index) {
                continue;
            }
            if self.is_empty(index) {
                break;
            }
            if self.matches(&self.buckets, ref_bytes, &value, index) {
                found = true;
                found_index = index;
                break;
            }
        }
        if found {
            self.buckets[found_index].pi = -1;
            self.bucket_size -= 1;
        }
        0
    }

    pub fn contains(&mut self, value: &T) -> bool {
        let ref_bytes = Self::get_bytes_of_value(value);
        let h1 = self.h1hash(ref_bytes, value);
        let mut iteration = 1;
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

    pub fn iter(&mut self) -> Vec<T>
    where
        T: Copy,
    {
        let mut result = Vec::new();
        for val in &self.buckets {
            if val.pi > 0 {
                result.push(val.elem);
            }
        }
        result
    }

    pub fn set_comparator(&mut self, compare: fn(&T, &T) -> bool) {
        self.compare = Some(compare);
    }

    pub fn set_hasher(&mut self, hasher: fn(&T, fn(&[u8]) -> u64) -> u64) {
        self.custom_hasher = Some(hasher);
    }

    pub fn clear(&mut self)
    where
        T: Default,
    {
        self.buckets.clear();
        self.bucket_size = 0;
        if CSET_FORCE_INITIALIZE {
            // Re-initialize with initial capacity
            cset_vector__init_with_cap(&mut self.buckets, CSET_INITIAL_CAP);
            for i in 0..self.buckets.len() {
                self.buckets[i].pi = 0;
            }
        }
    }

    pub fn intersect(&mut self, first: &Self, second: &Self)
    where
        T: Copy + Default,
    {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 && second.contains(&val.elem) {
                self.add(val.elem);
            }
        }
    }

    pub fn union(&mut self, first: &Self, second: &Self)
    where
        T: Copy + Default,
    {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
        for val in &second.buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
    }

    pub fn is_disjoint(&mut self, other: &Self) -> bool
    where
        T: Copy,
    {
        for val in &self.buckets {
            if val.pi > 0 && other.contains(&val.elem) {
                return false;
            }
        }
        true
    }

    pub fn difference(&mut self, first: &Self, second: &Self)
    where
        T: Copy + Default,
    {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 && !second.contains(&val.elem) {
                self.add(val.elem);
            }
        }
    }

    // Internal resize function
    fn resize(&mut self, new_cap: usize)
    where
        T: Copy + Default,
    {
        let mut temp = Vec::new();
        cset_vector__init_with_cap(&mut temp, new_cap);
        for i in 0..temp.len() {
            temp[i].pi = 0;
        }
        let old_buckets = std::mem::replace(&mut self.buckets, temp);
        self.bucket_size = 0; // reset size before reinserting
        for val in old_buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
    }
}
</replace>
</edit>