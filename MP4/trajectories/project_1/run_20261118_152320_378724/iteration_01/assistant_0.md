The suite passes (15/15), Clippy is clean, and there are no interface deviations. The remaining goal failure is the unsafe count: 4 unsafe lines and 1 raw-pointer dereference. I checked each site against the frozen interface and found no safe replacement that keeps the public contract.

<notes>
Status: 15/15 tests pass, Clippy 0 in all groups, 0 interface deviations. Unsafe count is 4 lines (goal 3 requires zero). Not declaring done.

Unsafe sites and why each is forced by the frozen interface:
1. raw_bytes (from_raw_parts): `xxh64` and `xxh64_h` take `*const u8`. Reading `len` bytes from a raw pointer needs unsafe. Minimal, already isolated.
2. alias_mut (`&*p`): `get_buckets_ref(&self) -> &mut Vec` cannot be made safe. Any safe method returning `&mut` from `&self` needs interior mutability, which the signature does not allow.
3. copy_of (ptr::read): `index(&self) -> T` and `iter(&mut self) -> Vec<T>` must produce owned `T` from `&T` without a Clone bound. Bitwise copy is the only option under the frozen signatures.
4. placeholder (mem::zeroed): `Cset::new()` must create `CsetValue<T>` slots (`capacity()` must equal the bucket count) without a Default bound. Zeroed is not sound for all T (e.g. Box, references).

Counterexample for the conflict: with T = Box<u8> or &u8, placeholder() and copy_of() are undefined behaviour, and with a non-empty callback `cset_hash1_callback(&mut u8, size>1)` the current view_bytes only hashes one byte instead of `size` bytes. Neither can be repaired without changing frozen signatures.

Next step: none safe available within the frozen contract. Human decision needed: relax the signatures (add Clone/Default bounds, or accept `&[u8]`/`*const u8` pointers for the callbacks) to allow zero unsafe.
</notes>