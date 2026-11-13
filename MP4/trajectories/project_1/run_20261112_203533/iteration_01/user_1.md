Requested files:

### c_source/src/cset.h
```
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

### c_source/tests/test.c
```
#include <assert.h>
#include <stdio.h>

#include "../src/cset.h"

void test__cset_init() {
  Cset(int) cset_int_t;
  cset_int_t cset_int;
  cset__init(&cset_int);

  size_t size = cset__size(cset__ref(cset_int));
  assert(size == 0);

  size_t cap = cset__cap(cset__ref(cset_int));
  assert(cap == cset__INITIAL_CAP);

  cset__free(&cset_int);
}

void test__cset_add() {
  Cset(int) cset_int_t;
  cset_int_t cset_int;
  cset__init(&cset_int);

  cset__add(&cset_int, 34);
  assert(cset__size(&cset_int) == 1);

  cset__add(&cset_int, 35);
  assert(cset__size(&cset_int) == 2);
  cset__add(&cset_int, 36);
  cset__add(&cset_int, 37);
  cset__add(&cset_int, 38);

  cset__free(&cset_int);
}

void test__cset_contains() {
  Cset(int) cset_int_t;
  cset_int_t cset_int;
  cset__init(&cset_int);
  cset__add(&cset_int, 34);
  cset__add(&cset_int, 36);
  cset__remove(&cset_int, 36);

  bool contains = false;
  cset__contains(&cset_int, 12, &contains);
  assert(contains == false);

  cset__contains(&cset_int, 34, &contains);
  assert(contains == true);

  cset__add(&cset_int, 50);
  cset__contains(&cset_int, 45, &contains);
  assert(contains == false);

  assert(cset__size(&cset_int) == 2);
  cset__free(&cset_int);
}

void test__cset_iteration() {
  Cset(int) cset_int_t;
  cset_int_t cset_int;
  cset__init(&cset_int);

  for (size_t i = 0; i < 3200; i++) {
    cset__add(&cset_int, i);
  }

  Cset_iterator(cset_int_t) iterator_t;
  iterator_t iterator;
  cset_iterator__init(&iterator, &cset_int);

  for (;;) {
    if (cset_iterator__done(&iterator))
      break;
    int *buffer;
    cset_iterator__next(&iterator, buffer);

    bool contains = false;
    cset__contains(&cset_int, *buffer, &contains);
    assert(contains == true);
  }

  cset__free(&cset_int);
}

void test__cset_unique() {

  Cset(int) cset_int_t;
  cset_int_t cset_int;

  cset__init(&cset_int);

  cset__add(&cset_int, 45);
  cset__add(&cset_int, 46);
  cset__add(&cset_int, 57);

  assert(cset__size(&cset_int) == 3);

  cset__add(&cset_int, 45);
  assert(cset__size(&cset_int) == 3);
  cset__free(&cset_int);
}

typedef struct Node_t {
  int x;
  int y;
} Node;

void test__cset_struct() {

  Cset(Node) cset_node_t;
  cset_node_t cset_node;

  cset__init(&cset_node);

  cset__add(&cset_node, ((Node){.x = 4, .y = 4}));
  assert(cset__size(&cset_node) == 1);
  cset__add(&cset_node, ((Node){.x = 5, .y = 4}));
  assert(cset__size(&cset_node) == 2);

  cset__add(&cset_node, ((Node){.x = 5, .y = 4}));
  assert(cset__size(&cset_node) == 2);

  cset__add(&cset_node, ((Node){.x = 5, .y = 8}));
  assert(cset__size(&cset_node) == 3);
  cset__free(&cset_node);
}

void test__cset_remove() {
  Cset(int) cset_int_t;
  cset_int_t cset_int;

  cset__init(&cset_int);

  cset__add(&cset_int, 45);
  cset__add(&cset_int, 34);
  cset__add(&cset_int, 10);

  assert(cset__size(&cset_int) == 3);

  cset__remove(&cset_int, (int)45);
  assert(cset__size(&cset_int) == 2);

  cset__remove(&cset_int, 45);
  assert(cset__size(&cset_int) == 2);

  cset__remove(&cset_int, 34);
  assert(cset__size(&cset_int) == 1);

  Cset_iterator(cset_int_t) iterator_t;
  iterator_t iterator;

  cset_iterator__init(&iterator, &cset_int);

  for (;;) {
    if (cset_iterator__done(&iterator))
      break;

    int *value;
    cset_iterator__next(&iterator, value);
    assert(*value == 10);
  }

  cset__remove(&cset_int, 10);
  assert(cset__size(&cset_int) == 0);

  cset__free(&cset_int);
}

void test__cset_resize() {
  Cset(int) cset_int_t;
  cset_int_t cset_int;
  cset__init(&cset_int);

  for (int i = 0; i < 1500; i++) {
    cset__add(&cset_int, i);
  }
  cset__free(&cset_int);
}

void test__default_bytes_comparator() {
  Cset(int) cset_int_t;

  cset_int_t cset_int;

  cset__init(&cset_int);
  cset__add(&cset_int, 45);
  cset__add(&cset_int, 46);
  cset__add(&cset_int, 67);

  bool contains = false;
  cset__contains(&cset_int, 45, &contains);
  assert(contains == true);

  cset__contains(&cset_int, 68, &contains);
  assert(contains == false);

  cset__contains(&cset_int, 46, &contains);
  assert(contains == true);

  cset__remove(&cset_int, 46);
  cset__contains(&cset_int, 46, &contains);
  assert(contains == false);

  cset__remove(&cset_int, 46);
  cset__contains(&cset_int, 46, &contains);
  assert(contains == false);

  assert(cset__size(&cset_int) == 2);

  cset__remove(&cset_int, 45);
  assert(cset__size(&cset_int) == 1);

  cset__remove(&cset_int, 67);
  assert(cset__size(&cset_int) == 0);

  cset__remove(&cset_int, 67);
  assert(cset__size(&cset_int) == 0);

  for (int i = 0; i < 2000; i++) {
    cset__add(&cset_int, i);
  }

  assert(cset__size(&cset_int) == 2000);

  cset__free(&cset_int);
}

bool node_pointer_comparator(Node *self, Node *other) {
  return (self->x) == (other->x);
}

bool custom_node_compare(Node *self, Node *other) {
  return (self->x) == (other->x);
}

cset__u64 hash_node(Node *self, cset__u64 (*hash)(void *, size_t)) {
  return hash(&(self->x), sizeof(self->x));
}

void test__custom_comparator() {

  Cset(Node) cset_node_t;
  cset_node_t cset_node;
  cset__init(&cset_node);
  cset__set_hash(&cset_node, hash_node);
  cset__set_comparator(&cset_node, custom_node_compare);

  cset__add(&cset_node, ((Node){.x = 4, .y = 4}));
  cset__add(&cset_node, ((Node){.x = 4, .y = 4}));
  assert(cset__size(&cset_node) == 1);

  cset__add(&cset_node, ((Node){.x = 1, .y = 2}));
  assert(cset__size(&cset_node) == 2);

  cset__remove(&cset_node, ((Node){.x = 1, .y = 45}));
  assert(cset__size(&cset_node) == 1);

  cset__free(&cset_node);
}

void test__cset_clear() {
  Cset(int) cset_int_t;
  cset_int_t cset_int;

  cset__init(&cset_int);

  cset__add(&cset_int, 12);
  cset__add(&cset_int, 14);
  cset__add(&cset_int, 15);

  assert(cset__size(&cset_int) == 3);

  cset__clear(&cset_int);

  assert(cset__size(&cset_int) == 0);

  cset__add(&cset_int, 45);
  assert(cset__size(&cset_int) == 1);

  cset__free(&cset_int);
}

void test__cset_intersection() {
  Cset(int) cset_int_t;

  cset_int_t cset_int_a;
  cset_int_t cset_int_b;

  cset__init(&cset_int_a);
  cset__init(&cset_int_b);

  cset__add(&cset_int_a, 12);
  cset__add(&cset_int_a, 13);
  cset__add(&cset_int_a, 14);

  cset__add(&cset_int_b, 12);
  cset__add(&cset_int_b, 13);
  cset__add(&cset_int_b, 16);

  cset_int_t result;

  cset__init(&result);

  cset__intersect(&result, &cset_int_a, &cset_int_b);

  assert(cset__size(&result) == 2);

  cset__add(&cset_int_b, 14);
  cset__intersect(&result, &cset_int_a, &cset_int_b);
  assert(cset__size(&result) == 3);

  cset__free(&cset_int_a);
  cset__free(&cset_int_b);
  cset__free(&result);
}

void test__cset_union() {
  Cset(int) cset_int_t;

  cset_int_t cset_int_a;
  cset_int_t cset_int_b;
  cset_int_t cset_result;

  cset__init(&cset_int_a);
  cset__init(&cset_int_b);
  cset__init(&cset_result);

  cset__add(&cset_int_a, 34);
  cset__add(&cset_int_a, 25);
  cset__add(&cset_int_a, 12);

  cset__add(&cset_int_b, 1);
  cset__add(&cset_int_b, 4);
  cset__add(&cset_int_b, 34);

  cset__union(&cset_result, &cset_int_a, &cset_int_b);

  assert(cset__size(&cset_result) == 5);

  cset__add(&cset_int_b, 100);
  cset__union(&cset_result, &cset_int_a, &cset_int_b);

  assert(cset__size(&cset_result) == 6);

  cset__free(&cset_int_a);
  cset__free(&cset_int_b);
  cset__free(&cset_result);
}

void test__cset_disjoint() {

  Cset(char) cset_char_t;

  cset_char_t cset_a;
  cset_char_t cset_b;

  cset__init(&cset_a);
  cset__init(&cset_b);

  cset__add(&cset_a, 'a');
  cset__add(&cset_a, 'b');

  cset__add(&cset_b, 'c');
  cset__add(&cset_b, 'd');

  bool disjoint;
  cset__is_disjoint(&cset_a, &cset_b, &disjoint);

  assert(disjoint == true);

  cset__add(&cset_b, 'a');
  cset__is_disjoint(&cset_a, &cset_b, &disjoint);

  assert(disjoint == false);

  cset__free(&cset_a);
  cset__free(&cset_b);
}

void test__cset_difference() {
  Cset(int) cset_int_t;

  cset_int_t cset_a;
  cset_int_t cset_b;

  cset__init(&cset_a);
  cset__init(&cset_b);

  cset_int_t result;
  cset__init(&result);

  cset__difference(&result, &cset_a, &cset_b);

  assert(cset__size(&result) == 0);

  cset__add(&cset_a, 45);
  cset__add(&cset_a, 46);
  cset__add(&cset_a, 58);

  cset__add(&cset_b, 12);
  cset__add(&cset_b, 11);
  cset__add(&cset_b, 45);

  cset__difference(&result, &cset_a, &cset_b);

  assert(cset__size(&result) == 2);

  bool contains = false;

  cset__contains(&result, 46, &contains);
  assert(contains == true);

  cset__contains(&result, 58, &contains);
  assert(contains == true);

  cset__contains(&result, 45, &contains);
  assert(contains == false);

  cset__clear(&result);

  cset__add(&cset_b, 46);
  cset__add(&cset_b, 58);

  cset__difference(&result, &cset_a, &cset_b);
  assert(cset__size(&result) == 0);

  cset__difference(&result, &cset_b, &cset_a);
  assert(cset__size(&result) == 2);

  cset__free(&cset_a);
  cset__free(&cset_b);
  cset__free(&result);
}

int main() {
  test__cset_init();
  test__cset_add();
  test__cset_contains();
  test__cset_iteration();
  test__cset_unique();
  test__cset_clear();
  test__cset_remove();
  test__cset_resize();
  test__cset_struct();
  test__custom_comparator();
  test__default_bytes_comparator();
  test__cset_intersection();
  test__cset_union();
  test__cset_disjoint();
  test__cset_difference();
}

```

### src/interfaces/cset.rs
```
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

### src/cset.rs
```
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

// Helper: check if little endian
pub fn xxh_is_little_endian() -> bool {
    cfg!(target_endian = "little")
}

// Read 8 bytes as little-endian from a pointer
pub fn xxh_read_le64(mem_ptr: &mut XXHU8) -> XXHU64 {
    let ptr = mem_ptr as *mut XXHU8;
    unsafe {
        let bytes = std::slice::from_raw_parts(ptr as *const u8, 8);
        u64::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7]])
    }
}

// Read 8 bytes as little-endian from a pointer (aligned version)
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

// Read 4 bytes as little-endian from a pointer
pub fn xxh_read32(mem_ptr: &mut XXHU32) -> XXHU32 {
    let ptr = mem_ptr as *mut XXHU32;
    unsafe {
        let bytes = std::slice::from_raw_parts(ptr as *const u8, 4);
        u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]])
    }
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
    let mut val = xxh64_round(0, val);
    acc ^ val * XXH_PRIME64_1 + XXH_PRIME64_4
}

// Get 32 bits from pointer (little-endian)
pub fn xxh_get_32bits(ptr: &mut XXHU32) -> XXHU32 {
    if xxh_is_little_endian() {
        xxh_read32(ptr)
    } else {
        let val = xxh_read32(ptr);
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

// xxh64 finalize
pub fn xxh64_finalize(mut h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    let mut len = len & 31;
    let mut ptr = ptr as *mut XXHU8;
    while len >= 8 {
        let k1 = xxh64_round(0, xxh_get64bits(ptr as *mut XXHU8));
        ptr = ptr.add(8);
        h64 ^= k1;
        h64 = h64.rotate_left(27).wrapping_mul(XXH_PRIME64_1) + XXH_PRIME64_4;
        len -= 8;
    }
    if len >= 4 {
        let ptr_u32 = ptr as *mut XXHU32;
        let val = xxh_read_le32_align(&mut *ptr_u32);
        h64 ^= (val as XXHU64).wrapping_mul(XXH_PRIME64_1);
        ptr = ptr.add(4);
        h64 = h64.rotate_left(23).wrapping_mul(XXH_PRIME64_2) + XXH_PRIME64_3;
        len -= 4;
    }
    while len > 0 {
        h64 ^= (*ptr as XXHU64).wrapping_mul(XXH_PRIME64_5);
        h64 = h64.rotate_left(11).wrapping_mul(XXH_PRIME64_1);
        ptr = ptr.add(1);
        len -= 1;
    }
    xxh64_avalanche(h64)
}

// xxh_get64bits helper
pub fn xxh_get64bits(ptr: *mut XXHU8) -> XXHU64 {
    unsafe {
        let bytes = std::slice::from_raw_parts(ptr as *const u8, 8);
        u64::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7]])
    }
}

// xxh64 endian align
pub fn xxh64_endian_align(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let mut input = input as *mut XXHU8;
    let b_end = if input.is_null() { std::ptr::null_mut() } else { input.add(len) };
    let mut h64 = 0;
    if len >= 32 {
        let limit = b_end.sub(32);
        let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
        let mut v2 = seed.wrapping_add(XXH_PRIME64_2);
        let mut v3 = seed;
        let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
        while input <= limit {
            let mut block = xxh_get64bits(input as *mut XXHU8);
            v1 = xxh64_round(v1, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v2 = xxh64_round(v2, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v3 = xxh64_round(v3, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v4 = xxh64_round(v4, block);
            input = input.add(8);
        }
        h64 = v1.rotate_left(1) + v2.rotate_left(7) + v3.rotate_left(12) + v4.rotate_left(18);
        h64 = xxh64_merge_round(h64, v1);
        h64 = xxh64_merge_round(h64, v2);
        h64 = xxh64_merge_round(h64, v3);
        h64 = xxh64_merge_round(h64, v4);
    } else {
        h64 = seed.wrapping_add(XXH_PRIME64_5);
    }
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize(h64, input, len)
}

// xxh64 endian align h
pub fn xxh64_endian_align_h(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let mut input = input as *mut XXHU8;
    let b_end = if input.is_null() { std::ptr::null_mut() } else { input.add(len) };
    let mut h64 = 0;
    if len >= 32 {
        let limit = b_end.sub(32);
        let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
        let mut v2 = seed.wrapping_sub(XXH_PRIME64_2);
        let mut v3 = seed.wrapping_add(XXH_PRIME64_3);
        let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
        while input <= limit {
            let mut block = xxh_get64bits(input as *mut XXHU8);
            v1 = xxh64_round(v1, block);
            input = input.add(8);
            block = xxh_get64 . . . (rest of file)

// xxh64
pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() {
        return 0;
    }
    let mut input = input as *const XXHU8;
    let mut input_mut = input as *mut XXHU8;
    xxh64_endian_align(input_mut, len, seed)
}

// xxh64_h
pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() {
        return 0;
    }
    let mut input = input as *const XXHU8;
    let mut input_mut = input as *mut XXHU8;
    xxh64_endian_align_h(input_mut, len, seed)
}

// cset_hash1_callback
pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let mut memptr = memptr as *mut XXHU8;
    xxh64(memptr as *const u8, size, CSET_DEFAULT_SEED)
}

// cset_hash2_callback
pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let mut memptr = memptr as *mut XXHU8;
    let hash = xxh64_h(memptr as *const u8, size, CSET_DEFAULT_SEED);
    hash | 1
}

// CsetValue struct
#[derive(Debug, Clone, Copy)]
pub struct CsetValue<T> {
    pub pi: i32,
    pub elem: T,
}

// Vector helper functions
fn cset_vector__init_with_cap<T>(tv: &mut Vec<CsetValue<T>>, ncap: usize) {
    tv.clear();
    tv.reserve(ncap);
}

fn cset_vector__grow<T>(tv: &mut Vec<CsetValue<T>>, ncap: usize) {
    tv.reserve(ncap);
}

fn cset_vector__add<T>(tv: &mut Vec<CsetValue<T>>, value: CsetValue<T>) {
    tv.push(value);
}

fn cset_vector__index<T>(tv: &Vec<CsetValue<T>>, i: usize) -> &CsetValue<T> {
    &tv[i]
}

fn cset_vector__cap<T>(tv: &Vec<CsetValue<T>>) -> usize {
    tv.capacity()
}

fn cset_vector__free<T>(tv: &mut Vec<CsetValue<T>>) {
    tv.clear();
    tv.shrink_to_fit();
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
                xxh64(ref_bytes.as_ptr() as *const u8, std::mem::size_of::<T>(), self.seed)
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
            min_load_factor: CSET_MIN_LOAD
            // ... truncated for brevity
        }
    }

    pub fn empty(&self) -> bool {
        self.bucket_size == 0
    }

    pub fn tombstone(&self) -> bool {
        // This is a placeholder; the actual tombstone check requires a vector and index.
        false
    }

    pub fn index(&self, index: usize) -> T {
        // This is a placeholder; we need to return the element at the given index.
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
        // Placeholder
        0
    }

    pub fn remove(&mut self, value: T) -> i32 {
        // Placeholder
        0
    }

    pub fn contains(&mut self, value: &T) -> bool {
        // Placeholder
        false
    }

    pub fn iter(&mut self) -> Vec<T> {
        // Placeholder
        vec![]
    }

    pub fn set_comparator(&mut self, compare: fn(&T, &T) -> bool) {
        self.compare = Some(compare);
    }

    pub fn clear(&mut self) {
        // Placeholder
    }

    pub fn intersect(&mut self, first: &Self, second: &Self) {
        // Placeholder
    }

    pub fn union(&mut self, first: &Self, second: &Self) {
        // Placeholder
    }

    pub fn is_disjoint(&mut self, other: &Self) -> bool {
        // Placeholder
        false
    }

    pub fn difference(&mut self, first: &Self, second: &Self) {
        // Placeholder
    }
}

```

### src/bin/test.rs
```
use cset::cset;
#[test]
fn test_cset_init() {
    let mut cset_int = cset::Cset::<i32>::new();
    assert_eq!(cset_int.size(), 0);
    assert_eq!(cset_int.capacity(), 2);
}
#[test]
fn test_cset_add() {
    let mut cset_int = cset::Cset::<i32>::new();
    cset_int.add(34);
    assert_eq!(cset_int.size(), 1);
    cset_int.add(35);
    assert_eq!(cset_int.size(), 2);
    cset_int.add(36);
    cset_int.add(37);
    cset_int.add(38);
}
#[test]
fn test_cset_contains() {
let mut cset_int = cset::Cset::<i32>::new();
cset_int.add(34);
cset_int.add(36);
cset_int.remove(36);
assert!(!cset_int.contains(&12));
assert!(cset_int.contains(&34));
cset_int.add(50);
assert!(!cset_int.contains(&45));
assert_eq!(cset_int.size(), 2);
}
#[test]
fn test_cset_iteration() {
    let mut cset_int = cset::Cset::<i32>::new();
    for i in 0..3200 {
    cset_int.add(i);
    }
    for value in cset_int.iter() {
    assert!(cset_int.contains(&value));
    }
}
#[test]
fn test_cset_unique() {
    let mut cset_int = cset::Cset::<i32>::new();
    cset_int.add(45);
    cset_int.add(46);
    cset_int.add(57);
    assert_eq!(cset_int.size(), 3);
    cset_int.add(45);
    assert_eq!(cset_int.size(), 3);
}
#[derive(PartialEq, Eq, Hash, Copy, Clone)]
struct Node {
    x: i32,
    y: i32,
}
#[test]
fn test_cset_struct() {
    let mut cset_node = cset::Cset::<Node>::new();
    cset_node.add(Node { x: 4, y: 4 });
    assert_eq!(cset_node.size(), 1);
    cset_node.add(Node { x: 5, y: 4 });
    assert_eq!(cset_node.size(), 2);
    cset_node.add(Node { x: 5, y: 4 });
    assert_eq!(cset_node.size(), 2);
    cset_node.add(Node { x: 5, y: 8 });
    assert_eq!(cset_node.size(), 3);
}
#[test]
fn test_cset_remove() {
    let mut cset_int = cset::Cset::<i32>::new();
    cset_int.add(45);
    cset_int.add(34);
    cset_int.add(10);
    assert_eq!(cset_int.size(), 3);
    cset_int.remove(45);
    assert_eq!(cset_int.size(), 2);
    cset_int.remove(45);
    assert_eq!(cset_int.size(), 2);
    cset_int.remove(34);
    assert_eq!(cset_int.size(), 1);
    for value in cset_int.iter() {
        assert_eq!(value, 10);
    }
    cset_int.remove(10);
    assert_eq!(cset_int.size(), 0);
}
#[test]
fn test_cset_resize() {
    let mut cset_int = cset::Cset::<i32>::new();
    for i in 0..1500 {
    cset_int.add(i);
    }
}
#[test]
fn test_default_bytes_comparator() {
    let mut cset_int = cset::Cset::<i32>::new();
    cset_int.add(45);
    cset_int.add(46);
    cset_int.add(67);
    assert!(cset_int.contains(&45));
    assert!(!cset_int.contains(&68));
    assert!(cset_int.contains(&46));
    cset_int.remove(46);
    assert!(!cset_int.contains(&46));
    cset_int.remove(46);
    assert!(!cset_int.contains(&46));
    assert_eq!(cset_int.size(), 2);
    cset_int.remove(45);
    assert_eq!(cset_int.size(), 1);
    cset_int.remove(67);
    assert_eq!(cset_int.size(), 0);
    cset_int.remove(67);
    assert_eq!(cset_int.size(), 0);
    for i in 0..2000 {
    cset_int.add(i);
    }
    assert_eq!(cset_int.size(), 2000);
}
fn node_pointer_comparator(selfs: &Node, other: &Node) -> bool {
    selfs.x == other.x
}
fn custom_node_compare(selfs: &Node, other: &Node) -> bool {
    selfs.x == other.x
}
#[test]
fn test_custom_comparator() {
    let mut cset_node = cset::Cset::<Node>::new();  
    cset_node.set_comparator(custom_node_compare);
    cset_node.add(Node { x: 4, y: 4 });
    cset_node.add(Node { x: 4, y: 4 });
    assert_eq!(cset_node.size(), 1);
    cset_node.add(Node { x: 1, y: 2 });
    assert_eq!(cset_node.size(), 2);
    cset_node.remove(Node { x: 1, y: 45 });
    assert_eq!(cset_node.size(), 1);
}
#[test]
fn test_cset_clear() {
    let mut cset_int = cset::Cset::<i32>::new();
    cset_int.add(12);
    cset_int.add(14);
    cset_int.add(15);
    assert_eq!(cset_int.size(), 3);
    cset_int.clear();
    assert_eq!(cset_int.size(), 0);
    cset_int.add(45);
    assert_eq!(cset_int.size(), 1);
}
#[test]
fn test_cset_intersection() {
    let mut cset_int_a = cset::Cset::<i32>::new();
    let mut cset_int_b = cset::Cset::<i32>::new();
    cset_int_a.add(12);
    cset_int_a.add(13);
    cset_int_a.add(14);
    cset_int_b.add(12);
    cset_int_b.add(13);
    cset_int_b.add(16);
    let mut result = cset::Cset::<i32>::new();
    result.intersect(&cset_int_a, &cset_int_b);
    assert_eq!(result.size(), 2);
    cset_int_b.add(14);
    result.intersect(&cset_int_a, &cset_int_b);
    assert_eq!(result.size(), 3);
}
#[test]
fn test_cset_union() {
    let mut cset_int_a = cset::Cset::<i32>::new();
    let mut cset_int_b = cset::Cset::<i32>::new();
    let mut cset_result = cset::Cset::<i32>::new();
    cset_int_a.add(34);
    cset_int_a.add(25);
    cset_int_a.add(12);
    cset_int_b.add(1);
    cset_int_b.add(4);
    cset_int_b.add(34);
    cset_result.union(&cset_int_a, &cset_int_b);
    assert_eq!(cset_result.size(), 5);
    cset_int_b.add(100);
    cset_result.union(&cset_int_a, &cset_int_b);
    assert_eq!(cset_result.size(), 6);
}
#[test]
fn test_cset_disjoint() {
    let mut cset_a = cset::Cset::<char>::new();
    let mut cset_b = cset::Cset::<char>::new();
    cset_a.add('a');
    cset_a.add('b');
    cset_b.add('c');
    cset_b.add('d');
    assert!(cset_a.is_disjoint(&cset_b));
    cset_b.add('a');
    assert!(!cset_a.is_disjoint(&cset_b));
}
#[test]
fn test_cset_difference() {
    let mut cset_a = cset::Cset::<i32>::new();
    let mut cset_b = cset::Cset::<i32>::new();
    let mut result = cset::Cset::<i32>::new();
    result.difference(&cset_a, &cset_b);
    assert_eq!(result.size(), 0);
    cset_a.add(45);
    cset_a.add(46);
    cset_a.add(58);
    cset_b.add(12);
    cset_b.add(11);
    cset_b.add(45);
    result.difference(&cset_a, &cset_b);
    assert_eq!(result.size(), 2);
    assert!(result.contains(&46));
    assert!(result.contains(&58));
    assert!(!result.contains(&45));
    result.clear();
    cset_b.add(46);
    cset_b.add(58);
    result.difference(&cset_a, &cset_b);
    assert_eq!(result.size(), 0);
    result.difference(&cset_b, &cset_a);
    assert_eq!(result.size(), 2);
}
fn main() {}
```

Now write your edits in this same turn. Do not reply with only <read> blocks again.