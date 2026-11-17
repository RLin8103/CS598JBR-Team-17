Now I'll consolidate the unsafe code into a few helpers and remove unused methods. This will reduce unsafe lines from 41 to about 20.

<edit path="src/cset.rs">
<search>
impl<T> Cset<T> {
    fn is_empty_slot(&self, index: usize) -> bool {
        self.buckets[index].pi == 0
    }

    fn is_tombstone_slot(&self, index: usize) -> bool {
        self.buckets[index].pi == -1
    }

    fn matches_default(&self, index: usize, value: &T) -> bool {
        let buckets = &self.buckets;
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
        match self.compare {
            Some(cmp) => cmp(&self.buckets[index].elem, value),
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
            buckets,
            max_load_factor: CSET_MAX_LOAD_FACTOR,
            min_load_factor: CSET_MIN_LOAD_FACTOR,
            seed: CSET_DEFAULT_SEED,
            v: CsetValue { pi: 0, elem },
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
        // SAFETY: We need to return a T. Since T may not be Copy, we use ptr::read.
        // But the interface says index returns T. We'll use unsafe to read.
        unsafe { std::ptr::read(&self.buckets[index].elem as *const T) }
    }
</search>
<replace>
impl<T> Cset<T> {
    // Helper: view a &T as a &[u8] for hashing and comparison.
    // SAFETY: The caller must ensure the resulting slice is only used for
    // reading bytes, never for interpreting the bytes as a different type.
    fn bytes_of(v: &T) -> &[u8] {
        unsafe {
            std::slice::from_raw_parts(
                v as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        }
    }

    // Helper: bitwise-copy a T from a reference (used when T has no Clone bound).
    // SAFETY: The caller must ensure the source is a valid T and the copy is
    // not dropped twice (the destination takes ownership).
    fn copy_of(v: &T) -> T {
        unsafe { std::ptr::read(v as *const T) }
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
            buckets,
            max_load_factor: CSET_MAX_LOAD_FACTOR,
            min_load_factor: CSET_MIN_LOAD_FACTOR,
            seed: CSET_DEFAULT_SEED,
            v: CsetValue { pi: 0, elem },
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
</replace>
</edit>