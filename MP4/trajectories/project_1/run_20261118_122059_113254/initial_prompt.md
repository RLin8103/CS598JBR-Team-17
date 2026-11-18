# Project: cset

Continue from the existing agent-generated implementation. Select a failure from the diagnostics, inspect the C and Rust, record your hypothesis in notes, and propose a focused edit. Use the next validation result to decide whether to revise it or inspect another failure.

## Workspace layout
crate (editable area: src/*.rs):
  .gitignore  (8 bytes)
  Cargo.lock  (148 bytes)
  Cargo.toml  (75 bytes)
  src/bin/test.rs  (6048 bytes)
  src/cset.rs  (19609 bytes)
  src/interfaces/cset.rs  (4944 bytes)
  src/lib.rs  (13 bytes)
c_source (read-only original C project):
  c_source/.gitignore  (20 bytes)
  c_source/License.txt  (1130 bytes)
  c_source/Makefile  (112 bytes)
  c_source/README.md  (10442 bytes)
  c_source/clib.json  (270 bytes)
  c_source/src/cset.h  (37399 bytes)
  c_source/tests/test.c  (9301 bytes)

## Toolchain and checks run after every iteration
- `cargo +nightly-2025-05-13 build --all-targets`
- `cargo +nightly-2025-05-13 test --no-fail-fast`
- `cargo +nightly-2025-05-13 clippy --all-targets --all-features -- -W clippy::<group>` for correctness, style, complexity and perf (reported separately)
- unsafe metrics: unsafe lines, unsafe calls, unsafe casts, pointer arithmetic

## Specification: Rust interface (do not change public items)
### src/interfaces/cset.rs (172 lines)
```rust
// Import necessary modules
use std::mem;
use std::ptr;
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
// Function Definitions
pub fn xxh_get64bits(mem_ptr: &mut XXHU8) -> XXHU64 {
    unimplemented!()
}
pub fn xxh_read_le64(mem_ptr: &mut XXHU8) -> XXHU64 {
    unimplemented!()
}
pub fn xxh_is_little_endian() -> bool {
    unimplemented!()
}
pub fn xxh_read_le64_align(mem_ptr: &mut XXHU8) -> XXHU64 {
    unimplemented!()
}
pub fn xxh_swap32(x: &mut  XXHU32) -> XXHU32 {
    unimplemented!()
}
pub fn xxh_read32(mem_ptr: &mut XXHU32) -> XXHU32 {
    unimplemented!()
}
pub fn xxh64_round(acc: XXHU64, input: XXHU64) -> XXHU64 {
    unimplemented!()
}
pub fn xxh64_merge_round(acc: XXHU64, val: XXHU64) -> XXHU64 {
    unimplemented!()
}
pub fn xxh_get_32bits(ptr: &mut XXHU32) -> XXHU32 {
    unimplemented!()
}
pub fn xxh_read_le32_align(ptr: &mut XXHU32) -> XXHU32 {
    unimplemented!()
}
pub fn xxh64_avalanche(mut h64: XXHU64) -> XXHU64 {
    unimplemented!()
}
pub fn xxh64_finalize(mut h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    unimplemented!()
}
pub fn xxh64_endian_align(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    unimplemented!()
}
pub fn xxh64_endian_align_h(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    unimplemented!()
}
pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    unimplemented!()
}
pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    unimplemented!()
}
pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    unimplemented!()
}
pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    unimplemented!()
}
pub struct  CsetValue<T> {
    pi: i32, 
    elem: T, 
}
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
    pub fn new() -> Cset<T> {
        unimplemented!()
    } 
    pub fn empty(&self) -> bool {
        unimplemented!()
    }
    pub fn tombstone(&self) -> bool {
        unimplemented!()
    }
    pub fn index(&self, index: usize) -> T {
        unimplemented!()
    }
    pub fn get_size(&self) -> usize {
        unimplemented!()
    }
    pub fn set_size(&mut self, new_size: usize) {
        unimplemented!()
    }
    pub fn get_seed(&self) -> u64 {
        unimplemented!()
    }
    pub fn set_seed(&mut self, seed: u64){
        unimplemented!()
    }
    pub fn get_max_load_factor(&self) -> f64 {
        unimplemented!()
    }
    pub fn set_max_load_factor(&mut self, new_factor: f64) {
        unimplemented!()
    }
    pub fn get_min_load_factor(&self) -> f64 {
        unimplemented!()
    }
    pub fn set_min_load_factor(&mut self, new_factor: f64) {
        unimplemented!()
    }
    pub fn get_buckets(&self) -> &Vec<CsetValue<T>> {
        unimplemented!()
    }
    pub fn get_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        unimplemented!()
    }
    pub fn get_temp_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        unimplemented!()
    }
    pub fn size(&self) -> i32 {
        unimplemented!()
    }
    pub fn capacity(&self) -> i32 {
        unimplemented!()
    }
    pub fn add(&mut self, value: T) -> i32 {
        unimplemented!()
    }
    pub fn remove(&mut self, value: T) -> i32 {
        unimplemented!()
    }
    pub fn contains(&mut self, value: &T) -> bool {
        unimplemented!()
    }
    pub fn iter(&mut self) -> Vec<T> {
        unimplemented!()
    }
    pub fn set_comparator(&mut self, compare: fn(&T, &T) -> bool) {
        unimplemented!()
    }
    pub fn clear(&mut self) {
        unimplemented!()
    }
    pub fn intersect(&mut self, first: &Self, second: &Self) {
        unimplemented!()
    }
    pub fn union(&mut self, first: &Self, second: &Self) {
        unimplemented!()
    }
    pub fn is_disjoint(&mut self, other: &Self) -> bool {
        unimplemented!()
    }
    pub fn difference(&mut self, first: &Self, second: &Self) {
        unimplemented!()
    }
}
```

## Tests (read-only, they are part of the specification)
Read benchmark source on demand using paths in the workspace tree.

## Source index
- `c_source/src/cset.h` (700 lines, included below)
- `c_source/tests/test.c` (453 lines, available via read)

## Original C source (this is the behaviour to preserve)
### c_source/src/cset.h (701 lines)
```c
#ifndef CSET_H
#define CSET_H

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* xxhash algorithm */

typedef uint64_t XXH64_hash_t;
typedef uint8_t xxh_u8;

typedef XXH64_hash_t xxh_u64;

#define XXH_FORCE_INLINE                                                       \
  static __inline__ __attribute__((always_inline, unused))

#define XXH_PRIME64_1                                                                         \
  0x9E3779B185EBCA87ULL /*!<                                                                  \
                           0b1001111000110111011110011011000110000101111010111100101010000111 \
                         */
#define XXH_PRIME64_2                                                                         \
  0xC2B2AE3D27D4EB4FULL /*!<                                                                  \
                           0b1100001010110010101011100011110100100111110101001110101101001111 \
                         */
#define XXH_PRIME64_3                                                                         \
  0x165667B19E3779F9ULL /*!<                                                                  \
                           0b0001011001010110011001111011000110011110001101110111100111111001 \
                         */
#define XXH_PRIME64_4                                                                         \
  0x85EBCA77C2B2AE63ULL /*!<                                                                  \
                           0b1000010111101011110010100111011111000010101100101010111001100011 \
                         */
#define XXH_PRIME64_5                                                                         \
  0x27D4EB2F165667C5ULL /*!<                                                                  \
                           0b0010011111010100111010110010111100010110010101100110011111000101 \
                         */

#define XXH_get64bits(p) XXH_readLE64_align(p)

XXH_FORCE_INLINE xxh_u64 XXH_readLE64(const void *memPtr) {
  const xxh_u8 *bytePtr = (const xxh_u8 *)memPtr;
  return bytePtr[0] | ((xxh_u64)bytePtr[1] << 8) | ((xxh_u64)bytePtr[2] << 16) |
         ((xxh_u64)bytePtr[3] << 24) | ((xxh_u64)bytePtr[4] << 32) |
         ((xxh_u64)bytePtr[5] << 40) | ((xxh_u64)bytePtr[6] << 48) |
         ((xxh_u64)bytePtr[7] << 56);
}

#ifndef XXH_CPU_LITTLE_ENDIAN
#if defined(_WIN32) || defined(__LITTLE_ENDIAN__) ||                           \
    (defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__)
#define XXH_CPU_LITTLE_ENDIAN 1
#elif defined(__BIG_ENDIAN__) ||                                               \
    (defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)
#define XXH_CPU_LITTLE_ENDIAN 0
#else
static int XXH_isLittleEndian(void) {
  const union {
    xxh_u32 u;
    xxh_u8 c[4];
  } one = {1};
  return one.c[0];
}
#define XXH_CPU_LITTLE_ENDIAN XXH_isLittleEndian()
#endif
#endif

XXH_FORCE_INLINE xxh_u64 XXH_readLE64_align(const void *ptr) {
  return XXH_readLE64(ptr);
}

#define XXH_rotl32(x, r) (((x) << (r)) | ((x) >> (32 - (r))))
#define XXH_rotl64(x, r) (((x) << (r)) | ((x) >> (64 - (r))))

typedef uint8_t xxh_u8;
typedef uint32_t XXH32_hash_t;
typedef uint32_t XXH32_hash_t;
typedef XXH32_hash_t xxh_u32;

static xxh_u32 XXH_swap32(xxh_u32 x) {
  return ((x << 24) & 0xff000000) | ((x << 8) & 0x00ff0000) |
         ((x >> 8) & 0x0000ff00) | ((x >> 24) & 0x000000ff);
}
static xxh_u32 XXH_read32(const void *memPtr) {
  xxh_u32 val;
  memcpy(&val, memPtr, sizeof(val));
  return val;
}

static xxh_u64 XXH64_round(xxh_u64 acc, xxh_u64 input) {
  acc += input * XXH_PRIME64_2;
  acc = XXH_rotl64(acc, 31);
  acc *= XXH_PRIME64_1;
  return acc;
}

static xxh_u64 XXH64_mergeRound(xxh_u64 acc, xxh_u64 val) {
  val = XXH64_round(0, val);
  acc ^= val;
  acc = acc * XXH_PRIME64_1 + XXH_PRIME64_4;
  return acc;
}

#define XXH_get32bits(p) XXH_readLE32_align(p)
XXH_FORCE_INLINE xxh_u32 XXH_readLE32(const void *ptr) {
  return XXH_CPU_LITTLE_ENDIAN ? XXH_read32(ptr) : XXH_swap32(XXH_read32(ptr));
}

XXH_FORCE_INLINE xxh_u32 XXH_readLE32_align(const void *ptr) {
  return XXH_readLE32(ptr);
}

static xxh_u64 XXH64_avalanche(xxh_u64 h64) {
  h64 ^= h64 >> 33;
  h64 *= XXH_PRIME64_2;
  h64 ^= h64 >> 29;
  h64 *= XXH_PRIME64_3;
  h64 ^= h64 >> 32;
  return h64;
}

static xxh_u64 XXH64_finalize(xxh_u64 h64, const xxh_u8 *ptr, size_t len) {
  len &= 31;
  while (len >= 8) {
    xxh_u64 const k1 = XXH64_round(0, XXH_get64bits(ptr));
    ptr += 8;
    h64 ^= k1;
    h64 = XXH_rotl64(h64, 27) * XXH_PRIME64_1 + XXH_PRIME64_4;
    len -= 8;
  }
  if (len >= 4) {
    h64 ^= (xxh_u64)(XXH_get32bits(ptr)) * XXH_PRIME64_1;
    ptr += 4;
    h64 = XXH_rotl64(h64, 23) * XXH_PRIME64_2 + XXH_PRIME64_3;
    len -= 4;
  }
  while (len > 0) {
    h64 ^= (*ptr++) * XXH_PRIME64_5;
    h64 = XXH_rotl64(h64, 11) * XXH_PRIME64_1;
    --len;
  }
  return XXH64_avalanche(h64);
}

XXH_FORCE_INLINE xxh_u64 XXH64_endian_align(const xxh_u8 *input, size_t len,
                                            xxh_u64 seed) {
  const xxh_u8 *bEnd = input ? input + len : NULL;
  xxh_u64 h64;

  if (len >= 32) {
    const xxh_u8 *const limit = bEnd - 32;
    xxh_u64 v1 = seed + XXH_PRIME64_1 + XXH_PRIME64_2;
    xxh_u64 v2 = seed + XXH_PRIME64_2;
    xxh_u64 v3 = seed + 0;
    xxh_u64 v4 = seed - XXH_PRIME64_1;

    do {
      v1 = XXH64_round(v1, XXH_get64bits(input));
      input += 8;
      v2 = XXH64_round(v2, XXH_get64bits(input));
      input += 8;
      v3 = XXH64_round(v3, XXH_get64bits(input));
      input += 8;
      v4 = XXH64_round(v4, XXH_get64bits(input));
      input += 8;
    } while (input <= limit);

    h64 = XXH_rotl64(v1, 1) + XXH_rotl64(v2, 7) + XXH_rotl64(v3, 12) +
          XXH_rotl64(v4, 18);
    h64 = XXH64_mergeRound(h64, v1);
    h64 = XXH64_mergeRound(h64, v2);
    h64 = XXH64_mergeRound(h64, v3);
    h64 = XXH64_mergeRound(h64, v4);

  } else {
    h64 = seed + XXH_PRIME64_5;
  }

  h64 += (xxh_u64)len;
  return XXH64_finalize(h64, input, len);
}

XXH_FORCE_INLINE xxh_u64 XXH64_endian_align_h(const xxh_u8 *input, size_t len,
                                              xxh_u64 seed) {
  const xxh_u8 *bEnd = input ? input + len : NULL;
  xxh_u64 h64;

  if (len >= 32) {
    const xxh_u8 *const limit = bEnd - 32;
    xxh_u64 v1 = seed + XXH_PRIME64_1 + XXH_PRIME64_2;
    xxh_u64 v2 = seed - XXH_PRIME64_2;
    xxh_u64 v3 = seed + XXH_PRIME64_3;
    xxh_u64 v4 = seed - XXH_PRIME64_1;

    do {
      v1 = XXH64_round(v1, XXH_get64bits(input));
      input += 8;
      v2 = XXH64_round(v2, XXH_get64bits(input));
      input += 8;
      v3 = XXH64_round(v3, XXH_get64bits(input));
      input += 8;
      v4 = XXH64_round(v4, XXH_get64bits(input));
      input += 8;
    } while (input <= limit);

    h64 = XXH_rotl64(v1, 1) + XXH_rotl64(v2, 7) + XXH_rotl64(v3, 12) +
          XXH_rotl64(v4, 18);
    h64 = XXH64_mergeRound(h64, v1);
    h64 = XXH64_mergeRound(h64, v2);
    h64 = XXH64_mergeRound(h64, v3);
    h64 = XXH64_mergeRound(h64, v4);

  } else {
    h64 = seed + XXH_PRIME64_1;
  }

  h64 += (xxh_u64)len;
  return XXH64_finalize(h64, input, len);
}

static XXH64_hash_t XXH64(const void *input, size_t len, XXH64_hash_t seed) {
  return XXH64_endian_align((const xxh_u8 *)input, len, seed);
}

static XXH64_hash_t XXH64_h(const void *input, size_t len, XXH64_hash_t seed) {
  return XXH64_endian_align_h((const xxh_u8 *)input, len, seed);
}

#ifndef CSET__FORCE_INITIALIZE
#define CSET__FORCE_INITIALIZE 1
#endif

#ifndef cset__INITIAL_CAP
#define cset__INITIAL_CAP 2
#endif

#ifndef cset__DEFAULT_SEED
#define cset__DEFAULT_SEED 2718182
#endif

#ifndef cset__MAX_LOAD_FACTOR
#define cset__MAX_LOAD_FACTOR 0.7
#endif

#ifndef cset__MIN_LOAD_FACTOR
#define cset__MIN_LOAD_FACTOR 0.2
#endif

#define cset__ref(cset) (&(cset))

#define cset__set_max_load_factor(cset, value)                                 \
  (((cset)->max_load_factor) = (value))
#define cset__set_min_load_factor(cset, value)                                 \
  (((cset)->min_load_factor) = (value))

#define cset__max_load_factor(cset) ((cset)->max_load_factor)
#define cset__min_load_factor(cset) ((cset)->min_load_factor)

#define cset__seed(cset) ((cset)->seed)
#define cset__set_seed(cset, value) (((cset)->seed) = (value))

#define cset__vector_buckets(cset) (((cset)->buckets))
#define cset__vector_buckets_ref(cset) (&((cset)->buckets))

#define cset__vector_temp_buckets_ref(cset) (&((cset)->temp_buckets))

#define cset__size(cset) ((cset)->bucket_size)
#define cset__set_size(cset, value) (((cset)->bucket_size) = value)

#define cset__cap(cset) cset_vector__cap(cset__vector_buckets_ref(cset))

#define cset__Value(cset_type_)                                                \
  typedef struct {                                                             \
    int pi;                                                                    \
    cset_type_ elem;                                                           \
  }

#define cset__value_elem_ref(val) (&((val)->elem))
#define cset__value_elem(val) ((val)->elem)

#define cset__value_pi(val) ((val)->pi)

typedef uint8_t cset__u8;
typedef uint64_t cset__u64;

#define cset__bytes_compare(self, other, size) (memcmp(self, other, size) == 0)

#define Cset(cset_type_)                                                       \
  cset__Value(cset_type_) cset_value_##cset_type_;                             \
  cset_Vector(cset_value_##cset_type_) buckets_##cset_type_;                   \
  typedef struct cset_##cset_type_ {                                           \
    buckets_##cset_type_ buckets;                                              \
    double max_load_factor;                                                    \
    double min_load_factor;                                                    \
    uint64_t seed;                                                             \
    cset_type_ v;                                                              \
    size_t bucket_size;                                                        \
    bool (*compare)(cset_type_ * self, cset_type_ *other);                     \
    cset__u64 (*customhasher)(cset_type_ * self,                               \
                              cset__u64 (*hash)(void *, size_t));              \
    buckets_##cset_type_ temp_buckets;                                         \
  }

#define cset__set_hash(cset, hasher) (((cset)->customhasher) = hasher)

#define cset__set_comparator(cset, comparator) (((cset)->compare) = comparator)

#define cset__init(cset)                                                       \
  do {                                                                         \
    cset__set_max_load_factor(cset, cset__MAX_LOAD_FACTOR);                    \
    cset__set_min_load_factor(cset, cset__MIN_LOAD_FACTOR);                    \
    cset__set_seed(cset, cset__DEFAULT_SEED);                                  \
    cset__set_size(cset, 0);                                                   \
    cset__set_comparator(cset, NULL);                                          \
    cset__set_hash(cset, NULL);                                                \
    cset_vector__init_with_cap(cset__vector_buckets_ref(cset),                 \
                               cset__INITIAL_CAP);                             \
    if (CSET__FORCE_INITIALIZE) {                                              \
      for (size_t i = 0; i < cset_vector__cap(cset__vector_buckets_ref(cset)); \
           i++) {                                                              \
        ((cset_vector__index(cset__vector_buckets_ref(cset), i))->pi) = 0;     \
      }                                                                        \
    }                                                                          \
  } while (0)

#define cset__empty(vector_ref, index)                                         \
  (((cset_vector__index(vector_ref, index))->pi) == 0)

#define cset__tombstone(vector_ref, index)                                     \
  (((cset_vector__index(vector_ref, index))->pi) == -1)

#define cset__index(cset, index)                                               \
  &(((cset_vector__index(cset__vector_buckets_ref(cset), index))->elem))

#define cset__matches(cset, vector_ref, ref, value, index)                     \
  ((cset)->compare)                                                            \
      ? (((cset)->compare)(                                                    \
            cset__value_elem_ref(cset_vector__index((vector_ref), (index))),   \
            (ref)))                                                            \
      : cset__bytes_compare(                                                   \
            cset__value_elem_ref(cset_vector__index((vector_ref), (index))),   \
            (ref), sizeof(value))

static cset__u64 cset__hash1_callback(void *memptr, size_t size) {
  return XXH64(memptr, size, cset__DEFAULT_SEED);
}

static cset__u64 cset__hash2_callback(void *memptr, size_t size) {
  return ((XXH64_h(memptr, size, cset__DEFAULT_SEED)) | 1);
}

#define cset__contains_(cset, ref, value, flag)                                \
  do {                                                                         \
    ((cset)->v) = value;                                                       \
    cset__u64 h1 = cset__h1hash(cset, ref, value);                             \
    size_t cap = cset__cap(cset);                                              \
    size_t iteration = 1;                                                      \
    size_t index = 0;                                                          \
    bool found = false;                                                        \
    for (;;) {                                                                 \
      /* break if we reach to the end */                                       \
      if ((iteration - 1) >= cset__cap(cset)) {                                \
        break;                                                                 \
      }                                                                        \
      cset__u64 h2 = cset__h2hash(cset, ref, value);                           \
      index = cset__double_hash_index(h1, h2, (iteration - 1), cap);           \
      iteration++;                                                             \
      if (cset__tombstone(cset__vector_buckets_ref(cset), index)) {            \
        continue;                                                              \
      }                                                                        \
      if (cset__empty(cset__vector_buckets_ref(cset), index)) {                \
        break;                                                                 \
      }                                                                        \
      bool matches = cset__matches(cset, cset__vector_buckets_ref(cset), ref,  \
                                   value, index);                              \
      if (matches) {                                                           \
        found = true;                                                          \
        break;                                                                 \
      }                                                                        \
    }                                                                          \
    (*(flag)) = found;                                                         \
  } while (0)

#define cset__contains(cset, value, flag)                                      \
  do {                                                                         \
    ((cset)->v) = value;                                                       \
    cset__contains_(cset, (&((cset)->v)), ((cset)->v), flag);                  \
  } while (0)

#define cset__h2hash(cset, ref, value)                                         \
  (((cset)->customhasher))                                                     \
      ? ((((cset)->customhasher))((ref), cset__hash2_callback))                \
      : ((XXH64_h((ref), sizeof(value), cset__seed(cset))) | 1)

#define cset__h1hash(cset, ref, value)                                         \
  (((cset)->customhasher))                                                     \
      ? ((((cset)->customhasher))(ref, cset__hash1_callback))                  \
      : (XXH64((ref), sizeof(value), (cset__seed(cset))))

#define cset__double_hash_index(ha1, ha2, i, cap)                              \
  (((ha1) + ((i) * (ha2))) % cap)

#define cset__add(cset, value)                                                 \
  do {                                                                         \
    double current_load_factor =                                               \
        ((double)(cset__size(cset)) / (cset__cap(cset)));                      \
    if (current_load_factor >= cset__max_load_factor(cset)) {                  \
      cset__resize(cset, (cset__cap(cset) * 2));                               \
    }                                                                          \
    ((cset)->v) = value;                                                       \
    cset__add_((cset), &((cset)->v), cset__vector_buckets_ref(cset),           \
               ((cset)->v));                                                   \
  } while (0)

#define cset__add_(cset, ref, vector_ref, value)                               \
  do {                                                                         \
    cset__u64 h1 = cset__h1hash(cset, ref, *ref);                              \
    bool found = false;                                                        \
    size_t iteration = 1;                                                      \
    size_t index;                                                              \
    size_t cap = cset_vector__cap(vector_ref);                                 \
    for (;;) {                                                                 \
      cset__u64 h2 = cset__h2hash(cset, ref, *ref);                            \
      index = cset__double_hash_index(h1, h2, (iteration - 1), cap);           \
      iteration++;                                                             \
      if (cset__empty(vector_ref, index) ||                                    \
          cset__tombstone(vector_ref, index)) {                                \
        break;                                                                 \
      }                                                                        \
      bool matches = cset__matches(cset, vector_ref, ref, value, index);       \
      if (matches) {                                                           \
        found = true;                                                          \
        break;                                                                 \
      }                                                                        \
    }                                                                          \
    if (!found) {                                                              \
      ((cset_vector__index(vector_ref, index))->elem) = value;                 \
      ((cset_vector__index(vector_ref, index))->pi) = iteration;               \
      cset__set_size(cset, (cset__size(cset)) + 1);                            \
    }                                                                          \
  } while (0)

#define cset__resize(cset, cap)                                                \
  do {                                                                         \
    size_t current_cap = cset__cap(cset);                                      \
    cset_vector__init_with_cap(&((cset)->temp_buckets), cap);                  \
    for (size_t i = 0;                                                         \
         i < cset_vector__cap(cset__vector_temp_buckets_ref(cset)); i++) {     \
      ((cset_vector__index(cset__vector_temp_buckets_ref(cset), i))->pi) = 0;  \
    }                                                                          \
    /* reset the size of cset */                                               \
    cset__set_size(cset, 0);                                                   \
    size_t current_index = 0;                                                  \
    for (;;) {                                                                 \
      if (current_index >= current_cap) {                                      \
        break;                                                                 \
      }                                                                        \
      int pi = cset__value_pi(cset_vector__index(                              \
          (cset__vector_buckets_ref(cset)), current_index));                   \
      if (pi == 0 || pi == -1) {                                               \
        current_index++;                                                       \
        continue;                                                              \
      }                                                                        \
      cset__add_(cset,                                                         \
                 cset__value_elem_ref(cset_vector__index(                      \
                     (cset__vector_buckets_ref(cset)), current_index)),        \
                 (&((cset)->temp_buckets)),                                    \
                 cset__value_elem(cset_vector__index(                          \
                     (cset__vector_buckets_ref(cset)), current_index)));       \
      current_index++;                                                         \
    }                                                                          \
    cset_vector__free(&((cset)->buckets));                                     \
    ((cset)->buckets) = ((cset)->temp_buckets);                                \
  } while (0)

#define cset__remove_(cset, ref, value, vector_ref)                            \
  do {                                                                         \
    cset__u64 h1 = cset__h1hash(cset, ref, value);                             \
    bool found = false;                                                        \
    size_t iteration = 1;                                                      \
    size_t index;                                                              \
    size_t cap = cset_vector__cap(vector_ref);                                 \
    for (;;) {                                                                 \
      if (((iteration)-1) >= cap)                                              \
        break;                                                                 \
      cset__u64 h2 = cset__h2hash(cset, ref, value);                           \
      index = cset__double_hash_index(h1, h2, (iteration - 1), cap);           \
      iteration++;                                                             \
      if (cset__tombstone(vector_ref, index)) {                                \
        continue;                                                              \
      }                                                                        \
      if (cset__empty(vector_ref, index)) {                                    \
        break;                                                                 \
      }                                                                        \
      bool matches = cset__matches(cset, vector_ref, ref, value, index);       \
      if (matches) {                                                           \
        found = true;                                                          \
        break;                                                                 \
      }                                                                        \
    }                                                                          \
    if (found) {                                                               \
      ((cset_vector__index(vector_ref, index))->pi) = -1;                      \
      cset__set_size(cset, (cset__size(cset)) - 1);                            \
    }                                                                          \
  } while (0)

#define cset__remove(cset, value)                                              \
  do {                                                                         \
    ((cset)->v) = value;                                                       \
    cset__remove_(cset, &((cset)->v), ((cset)->v),                             \
                  cset__vector_buckets_ref(cset));                             \
  } while (0)

#define cset__clear(cset)                                                      \
  do {                                                                         \
    cset__free(cset);                                                          \
    cset_vector__init_with_cap(cset__vector_buckets_ref(cset),                 \
                               cset__INITIAL_CAP);                             \
    cset__set_size(cset, 0);                                                   \
                                                                               \
    if (CSET__FORCE_INITIALIZE) {                                              \
      for (size_t i = 0; i < cset_vector__cap(cset__vector_buckets_ref(cset)); \
           i++) {                                                              \
        ((cset_vector__index(cset__vector_buckets_ref(cset), i))->pi) = 0;     \
      }                                                                        \
    }                                                                          \
  } while (0)

#define cset__free(cset) cset_vector__free(cset__vector_buckets_ref(cset))

#define cset__intersect(cset_res, cset_a, cset_b)                              \
  do {                                                                         \
    for (size_t i = 0; i < cset__cap(cset_a); i++) {                           \
      int pi = cset__value_pi(                                                 \
          cset_vector__index((cset__vector_buckets_ref(cset_a)), i));          \
      if (pi == 0 || pi == -1) {                                               \
        continue;                                                              \
      }                                                                        \
      bool contains = false;                                                   \
      cset__contains((cset_b),                                                 \
                     cset__value_elem((cset_vector__index(                     \
                         cset__vector_buckets_ref(cset_a), i))),               \
                     (&contains));                                             \
      if (contains) {                                                          \
        cset__add(cset_res, cset__value_elem((cset_vector__index(              \
                                cset__vector_buckets_ref(cset_a), i))));       \
      }                                                                        \
    }                                                                          \
  } while (0)

#define cset__union(cset_res, cset_a, cset_b)                                  \
  do {                                                                         \
    for (size_t i = 0; i < cset__cap(cset_a); i++) {                           \
      int pi = cset__value_pi(                                                 \
          cset_vector__index((cset__vector_buckets_ref(cset_a)), i));          \
      if (pi == 0 || pi == -1) {                                               \
        continue;                                                              \
      }                                                                        \
      cset__add(cset_res, cset__value_elem((cset_vector__index(                \
                              cset__vector_buckets_ref(cset_a), i))));         \
    }                                                                          \
    for (size_t i = 0; i < cset__cap(cset_b); i++) {                           \
      int pi = cset__value_pi(                                                 \
          cset_vector__index((cset__vector_buckets_ref(cset_b)), i));          \
      if (pi == 0 || pi == -1) {                                               \
        continue;                                                              \
      }                                                                        \
      cset__add(cset_res, cset__value_elem((cset_vector__index(                \
                              cset__vector_buckets_ref(cset_b), i))));         \
    }                                                                          \
  } while (0)

#define cset__is_disjoint(cset_a, cset_b, flag)                                \
  do {                                                                         \
    (*(flag)) = true;                                                          \
    for (size_t i = 0; i < cset__cap(cset_a); i++) {                           \
      int pi = cset__value_pi(                                                 \
          cset_vector__index((cset__vector_buckets_ref(cset_a)), i));          \
      if (pi == 0 || pi == -1) {                                               \
        continue;                                                              \
      }                                                                        \
      bool cset__contains_ = false;                                            \
      cset__contains((cset_b),                                                 \
                     cset__value_elem((cset_vector__index(                     \
                         cset__vector_buckets_ref(cset_a), i))),               \
                     (&cset__contains_));                                      \
      if (cset__contains_) {                                                   \
        (*(flag)) = false;                                                     \
        break;                                                                 \
      }                                                                        \
    }                                                                          \
  } while (0)

#define cset__difference(result, cset_a, cset_b)                               \
  do {                                                                         \
    for (size_t i = 0; i < cset__cap(cset_a); i++) {                           \
      int pi = cset__value_pi(                                                 \
          cset_vector__index((cset__vector_buckets_ref(cset_a)), i));          \
      if (pi == 0 || pi == -1) {                                               \
        continue;                                                              \
      }                                                                        \
      bool cset__contains_ = false;                                            \
      cset__contains((cset_b),                                                 \
                     cset__value_elem((cset_vector__index(                     \
                         cset__vector_buckets_ref(cset_a), i))),               \
                     (&cset__contains_));                                      \
      if (!cset__contains_) {                                                  \
        cset__add((result), cset__value_elem((cset_vector__index(              \
                                cset__vector_buckets_ref(cset_a), i))));       \
      }                                                                        \
    }                                                                          \
  } while (0)

#define Cset_iterator(cset_type_)                                              \
  typedef struct cset_iterator_##cset_type_ {                                  \
    cset_type_ *c;                                                             \
    size_t current_count;                                                      \
    size_t current_index;                                                      \
  }

#define cset_iterator__init(iterator, cset)                                    \
  do {                                                                         \
    ((iterator)->c) = (cset);                                                  \
    ((iterator)->current_count) = 0;                                           \
    ((iterator)->current_index) = 0;                                           \
  } while (0)

#define cset_iterator__done(iterator)                                          \
  (((iterator)->current_count) >= ((cset__size(((iterator)->c)))))

#define cset_iterator__next(iterator, buffer)                                  \
  do {                                                                         \
    for (;;) {                                                                 \
      int pi = cset__value_pi(                                                 \
          cset_vector__index((cset__vector_buckets_ref(((iterator)->c))),      \
                             (iterator)->current_index));                      \
      if (pi == 0 || pi == -1) {                                               \
        ((iterator)->current_index)++;                                         \
        continue;                                                              \
      }                                                                        \
      (buffer) = cset__value_elem_ref(                                         \
          cset_vector__index((cset__vector_buckets_ref(((iterator)->c))),      \
                             (iterator)->current_index));                      \
      ((iterator)->current_count)++;                                           \
      ((iterator)->current_index)++;                                           \
      break;                                                                   \
    }                                                                          \
  } while (0)

/* Vector required by cset */

#define cset_Vector(Type_)                                                     \
  typedef struct {                                                             \
    Type_ *e;                                                                  \
    size_t size;                                                               \
    size_t cap;                                                                \
    bool initialized;                                                          \
  }

#define cset_vector__init_with_cap(tv, ncap)                                   \
  do {                                                                         \
    ((tv)->size) = 0;                                                          \
    ((tv)->e) = NULL;                                                          \
    ((tv)->cap) = 0;                                                           \
    cset_vector__grow(tv, ncap);                                               \
    ((tv)->initialized) = true;                                                \
  } while (0)

#define cset_vector__grow(tv, ncap)                                            \
  do {                                                                         \
    size_t cap = ((tv)->cap);                                                  \
    void *mem = malloc(sizeof(*((tv)->e)) * ncap);                             \
    memcpy(mem, ((tv)->e), sizeof(*((tv)->e)) * cap);                          \
    free((tv)->e);                                                             \
    ((tv)->e) = mem;                                                           \
    ((tv)->cap) = ncap;                                                        \
  } while (0)

#define cset_vector__add(tv, value)                                            \
  do {                                                                         \
    size_t size = ((tv)->size);                                                \
    size_t cap = ((tv)->cap);                                                  \
    if (size >= cap) {                                                         \
      size_t new_cap = (cap == 0) ? 1 : (cap * 2);                             \
      cset_vector__grow(tv, new_cap);                                          \
    }                                                                          \
    (((tv)->e)[size]) = value;                                                 \
    ((tv)->size)++;                                                            \
  } while (0)

#define cset_vector__index(tv, i) &(((tv)->e)[i])

#define cset_vector__cap(tv) ((tv)->cap)

#define cset_vector__free(tv) (free((tv)->e))

#endif /* CSET_H */

```

## Current state of the editable Rust files
### src/cset.rs (612 lines)
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
    let h64 = if len >= 32 {
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
        let acc = v1
            .rotate_left(1)
            .wrapping_add(v2.rotate_left(7))
            .wrapping_add(v3.rotate_left(12))
            .wrapping_add(v4.rotate_left(18));
        let acc = xxh64_merge_round(acc, v1);
        let acc = xxh64_merge_round(acc, v2);
        let acc = xxh64_merge_round(acc, v3);
        xxh64_merge_round(acc, v4)
    } else {
        seed.wrapping_add(XXH_PRIME64_5)
    };
    let h64 = h64.wrapping_add(len as XXHU64);
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

## Baseline check result before your first edit
- compiles: True (0 errors)
- tests: 15 passed / 15 total (0 failed)
- unsafe metrics (builtin-approximation): lines=4, calls=3, casts=0, pointer_arithmetic=0
- validation: test_ok=True, clippy_ok=True, unsafe_valid=True
- clippy warnings: {"correctness": 0, "style": 0, "complexity": 0, "perf": 0}
- interface deviations (signatures that differ from src/interfaces/*.rs): 0
- untranslated bodies (`unimplemented!()`/`todo!()`): 0
- tokens used so far: 0

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
- src/cset.rs:257 [raw_pointer_decls] pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:263 [raw_pointer_decls] pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:318 [unsafe_calls] unsafe { std::ptr::read(std::ptr::from_ref(v)) }
- src/cset.rs:358 [unsafe_calls] unsafe { std::mem::zeroed() }

## Separate regression check
returncode=1 timed_out=False
{"tests::cset_hash_00": "ok", "tests::cset_hash_01": "ok", "tests::cset_hash_02": "ok", "tests::cset_hash_07": "ok", "tests::cset_hash_08": "ok", "tests::cset_hash_15": "ok", "tests::cset_hash_16": "ok", "tests::cset_hash_31": "ok", "tests::cset_hash_32": "ok", "tests::cset_hash_33": "ok", "tests::cset_hash_63": "ok", "tests::cset_hash_64": "ok", "tests::cset_hash_80": "ok", "tests::cset_hash_96": "ok", "tests::cset_hash_h_00": "FAILED", "tests::cset_hash_h_01": "FAILED", "tests::cset_hash_h_02": "FAILED", "tests::cset_hash_h_07": "FAILED", "tests::cset_hash_h_08": "FAILED", "tests::cset_hash_h_15": "FAILED", "tests::cset_hash_h_16": "FAILED", "tests::cset_hash_h_31": "FAILED", "tests::cset_hash_h_32": "ok", "tests::cset_hash_h_33": "ok", "tests::cset_hash_h_63": "ok", "tests::cset_hash_h_64": "ok", "tests::cset_hash_h_80": "ok", "tests::cset_hash_h_96": "ok", "tests::cset_padding_free_copy_generic": "ok"}
```
[tests::cset_hash_h_00]
thread 'tests::cset_hash_h_00' panicked at evaluation/harness/src/lib.rs:264:9:
input bytes 0..96, truncated to len:
len=0 seed=0: Rust=6089448738516538328, C=13315799867417602922
len=0 seed=2718182: Rust=11614518687002993724, C=9609742367336788117

[tests::cset_hash_h_01]
thread 'tests::cset_hash_h_01' panicked at evaluation/harness/src/lib.rs:264:9:
input bytes 0..96, truncated to len:
len=1 seed=0: Rust=1344935720564239988, C=11193626097507625299
len=1 seed=2718182: Rust=6594899528827042558, C=16585143914630977865

[tests::cset_hash_h_02]
thread 'tests::cset_hash_h_02' panicked at evaluation/harness/src/lib.rs:264:9:
input bytes 0..96, truncated to len:
len=2 seed=0: Rust=8617509540135573086, C=962134502339947765
len=2 seed=2718182: Rust=4971479887067988310, C=14547683834055110473

[tests::cset_hash_h_07]
thread 'tests::cset_hash_h_07' panicked at evaluation/harness/src/lib.rs:264:9:
input bytes 0..96, truncated to len:
len=7 seed=0: Rust=7584827969456509918, C=4249893767171937820
len=7 seed=2718182: Rust=12829040013170679280, C=1518540224581367784

[tests::cset_hash_h_08]
thread 'tests::cset_hash_h_08' panicked at evaluation/harness/src/lib.rs:264:9:
input bytes 0..96, truncated to len:
len=8 seed=0: Rust=9163211194136353357, C=3730646594863863303
len=8 seed=2718182: Rust=4170975662148065910, C=1811739754178317970

[tests::cset_hash_h_15]
thread 'tests::cset_hash_h_15' panicked at evaluation/harness/src/lib.rs:264:9:
input bytes 0..96, truncated to len:
len=15 seed=0: Rust=13813176779204586094, C=12756233403702556746
len=15 seed=2718182: Rust=2989575921063934098, C=17353067986731924435

[tests::cset_hash_h_16]
thread 'tests::cset_hash_h_16' panicked at evaluation/harness/src/lib.rs:264:9:
input bytes 0..96, truncated to len:
len=16 seed=0: Rust=15602599801977290796, C=14830457271042726377
len=16 seed=2718182: Rust=5130008953502153227, C=4311501666727977334

[tests::cset_hash_h_31]
thread 'tests::cset_hash_h_31' panicked at evaluation/harness/src/lib.rs:264:9:
input bytes 0..96, truncated to len:
len=31 seed=0: Rust=2122892477728805114, C=15169082307081493518
len=31 seed=2718182: Rust=6837672701383405910, C=15084038666174280388
```
