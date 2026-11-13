We need to implement the xxhash functions first. Let's start with the helper functions.

We'll edit src/cset.rs step by step. We'll replace the unimplemented stubs with proper implementations.

First, we need to fix the xxh_is_little_endian function. It currently uses cfg!(target_endian = "little") which is fine.

Second, we need to implement xxh_read_le64, xxh_read_le64_align, xxh_swap32, xxh_read32. These functions read from a pointer. We can implement them safely by using slices and unsafe blocks, but we need to keep unsafe minimal. However, the interface expects these functions to take &mut XXHU8 and &mut XXHU32 respectively. We can implement them by converting the reference to a raw pointer and then using std::slice::from_raw_parts with unsafe.

We'll also need to implement xxh_get64bits and xxh_get_32bits. The interface expects xxh_get64bits(ptr: *mut XXHU8) -> XXHU64 and xxh_get_32bits(ptr: &mut XXHU32) -> XXHU32. We can implement them similarly.

We'll also need to implement xxh64_round, xxh64_merge_round, xxh64_avalanche, xxh64_finalize, xxh64_endian_align, xxh64_endian_align_h, xxh64, xxh64_h, cset_hash1_callback, cset_hash2_callback.

We'll also need to implement the CsetValue struct and the vector helper functions.

We'll also need to implement the Cset struct and its methods.

Given the complexity, we should break the task into smaller steps. We'll start by implementing the xxhash functions, then the vector helpers, then the Cset struct.

We'll edit the file in multiple steps, each step focusing on a few functions.

Let's start with the xxhash functions. We'll replace the unimplemented stubs with proper implementations.

We'll edit src/cset.rs using <edit> blocks. We'll need to be careful to match the exact text.

First, let's look at the current content of src/cset.rs to see the exact lines we need to replace.

We'll open the file and read it.<read path="src/cset.rs"/>