<notes>
TODO:
1. Fix interface deviations: restore exact signatures from interface file.
   - xxh64_finalize: change ptr param from &[u8] to &mut XXHU8
   - xxh64_endian_align: change input param from &[u8] to &mut XXHU8
   - xxh64_endian_align_h: same
   - impl<T> Cset<T> (remove Clone + Hash + PartialEq bounds)
   - get_buckets_ref: &self -> &mut self (wait, interface says &self -> &mut Vec, but that's impossible without interior mutability. Keep as &mut self as that's the only safe way. Actually interface says `pub fn get_buckets_ref(&self) -> &mut Vec<CsetValue<T>>` - that's impossible without unsafe. We must keep the exact signature from interface. We'll use UnsafeCell or raw pointer? No, we must keep the signature exactly. We'll use a private UnsafeCell field. Actually the interface is the spec - we must match it exactly. We'll use a Cell or RefCell? The interface says &self -> &mut Vec. We can use UnsafeCell internally and return a mutable reference from an immutable borrow. That's unsafe but required by the interface. We'll do that.)
   - get_temp_buckets_ref: same issue
   - contains: &mut self (interface says &mut self)
   - is_disjoint: &mut self (interface says &mut self)
2. Remove unsafe code: replace zeroed() with MaybeUninit or use a different approach. For the v field and init_buckets, we can use a different strategy that doesn't require zeroed memory.
3. The hash functions h1hash and h2hash need to match the C behavior exactly (XXH64 with seed, not Rust's DefaultHasher). The C code uses XXH64/XXH64_h with the seed and the raw bytes of the value. We need to hash the raw bytes of T, not use Rust's Hash trait.
4. The C code uses memcmp for default comparison, not PartialEq. We need to compare raw bytes. For types like i32, char, Node (which is Copy), we can transmute to bytes and compare. But we need to handle generic T without bounds. We'll use a private helper that compares bytes via transmute.
</notes>