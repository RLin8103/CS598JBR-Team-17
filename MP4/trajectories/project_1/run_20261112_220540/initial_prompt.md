# Project: cset

Translate the C project `cset` to Rust. The Rust crate already exists in your workspace. The module files declared by `src/lib.rs` are copies of the interface stubs, with `unimplemented!()` bodies that you must replace by real implementations.

## Workspace layout
crate (editable area: src/*.rs):
  .gitignore  (8 bytes)
  Cargo.lock  (148 bytes)
  Cargo.toml  (75 bytes)
  src/bin/test.rs  (6048 bytes)
  src/cset.rs  (18276 bytes)
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
### src/bin/test.rs (221 lines)
```rust
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

## Original C source (this is the behaviour to preserve)
### c_source/Makefile (8 lines)
```
.PHONY: test

test: tests/test.c
	@$(CC) $^ -o $@ -g -lm
	echo "Running test..."
	@./$@
	echo "Test completed."

```

### c_source/README.md (434 lines)
```
# Typesafe & Fast as fuck Set in C
![](https://i.imgur.com/4JE58Ew.png)

### Key Features
* Extremely fast non-cryptographic hash algorithm [XXHash](https://cyan4973.github.io/xxHash/)
* Complete Typesafe APIs
* **Double Hashing** to avoid both Primary & Secondary clustering
* **Robinhood Hash**(*in progress*) for near constant time access
* Iterators for streaming usecase
* Allows **Custom Hash** & **Custom Comparator**
* Single header file to rule them all 🚀 🚀 🚀

Go to this [blogpost](https://robus.dev/typesafe-and-fast-as-fk-set-in-c) for more information and motivation for writing Set from scratch.

### Getting Started
```c
#include <stdio.h>
#include "cset.h"

// Declare Cset of int type
Cset(int) cset_int_t;
// Declare Cset iterator of `cset_int_t` type
Cset_iterator(cset_int_t) cset_iterator_int_t;

int main() {
    // Instance of cset_int_t
    cset_int_t cset_int;

    // Initialize
    cset__init(&cset_int);

    // Add elements
    cset__add(&cset_int, 1);
    cset__add(&cset_int, 2);
    cset__add(&cset_int, 2); // Duplicate

    size_t size = cset__size(&cset_int);
    printf("Size of set is: %ld\n", size);

    // Iteration
    cset_iterator_int_t cset_iterator_int;

    // Initialize iterator with cset_int
    cset_iterator__init(&cset_iterator_int, &cset_int);

    // Traverse
    for(;;) {
      if (cset_iterator__done(&cset_iterator_int)) break;

      int* buffer;
      cset_iterator__next(&cset_iterator_int, buffer);

      printf("Got: %d\n", *buffer);
    }
}
```

###
### Installation
Simply copy paste `cset.h` in your source directly or you can use [Clib](https://github.com/clibs/clib) package manager for installation
```sh
clib install robusgauli/cset
```

### APIs
* `cset__add(cset, value)`: *no return*
Add element to set.
    ```c
    #include "cset.h"

    Cset(char) cset_char_t;

    int main() {
      cset_char_t cset_char;
      cset__init(&cset_char);

      // Add elements to set
      cset__add(&cset_char, 'a');
      cset__add(&cset_char, 'b');
    }

    cset__free(&cset_int);
    ```

* `cset__remove(cset, value)`: *no return*
Removes element from the set.

    ```c
    #include <assert.h>
    #include "cset.h"

    Cset(int) cset_int_t;

    int main() {
      cset_int_t cset_int;
      cset__init(&cset_int);

      cset__add(&cset_int, 34);
      assert(cset__size(&cset_int) == 1);

      // Remove element from the set
      cset__remove(&cset_int, 34);
      assert(cset__size(&cset_int) == 0);

      cset__free(&cset_int);
    }
    ```
* `cset__size(cset)`: *returns `size_t`*
Returns the size of set.
    ```c
    #include <assert.h>
    #include "cset.h"

    Cset(int) cset_int_t;

    int main() {
      cset_int_t cset_int;
      cset__init(&cset_int);

      cset__add(&cset_int, 34);
      cset__add(&cset_int, 25);
      cset__add(&cset_int, 56);

      size_t size = cset__size(&cset_int);
      printf("Size: %ld\n", size);

      cset__free(&cset_int);
    }
    ```
* `cset__clear(cset)`: *no return*
Removes all the elements from the set.
    ```c
    #include <assert.h>
    #include "cset.h"

    Cset(int) cset_int_t;

    int main() {
      cset_int_t cset_int;
      cset__init(&cset_int);

      cset__add(&cset_int, 34);
      cset__add(&cset_int, 25);
      cset__add(&cset_int, 56);

      // Clear the set
      cset__clear(&cset_int);
      assert(cset__size(&cset_int) == 0);

      cset__free(&cset_int);
    }
    ```

* `cset__contains(cset, value, flag)`: *no return*
Test whether an element is in set.
    ```c
    #include <assert.h>
    #include "cset.h"

    Cset(int) cset_int_t;

    int main() {
      cset_int_t cset_int;
      cset__init(&cset_int);

      cset__add(&cset_int, 34);
      cset__add(&cset_int, 25);
      cset__add(&cset_int, 56);

      // Positive membership test
      bool contains = false;
      cset__contains(&cset_int, 34, &contains);
      assert(contains == true);

      // Negative membershi test
      cset__contains(&cset_int, 100, &contains);
      assert(contains == false);

      cset__free(&cset_int);
    }
    ```
* `cset__set_comparator` & `cset__set_hash()`: *no return*

   **NOTE:** Both **Custom Comparator and Hash** must be implemented.

    These above methods allows us to use custom hashing and comparator for complex structs. Please go through this [link](https://stackoverflow.com/questions/2265503/why-do-i-need-to-override-the-equals-and-hashcode-methods-in-java) for why we need to implement both functions for correctness.

    ```c
    #include <assert.h>
    #include "cset.h"

    typedef struct {
      int x;
      int y;
    } Node;

    // Custom comparator
    bool custom_comparator(Node* self, Node* other) {
      return (self -> x) == (other -> x);
    }
    // Custom hash function
    // It takes pointer to Node and function as an arguments
    cset__u64 custom_hash(Node* self, cset__u64 (*hash)(void*, size_t)) {
      // VVIP: Hash function requires pointer to data and the size in bytes
      return hash(&(self -> x), sizeof(self -> x));
    }

    Cset(Node) cset_node_t;

    int main() {
      cset_node_t cset_node;
      cset__init(&cset_node);
      cset__set_hash(&cset_node, custom_hash);
      cset__set_comparator(&cset_node, custom_comparator);

      cset__add(&cset_node, ((Node){.x=4,.y=5}));
      // Duplicate because our custom comparator and hash uses `x`
      // instead of whole struct for hash
      cset__add(&cset_node, ((Node){.x=4,.y=4}));

      assert(cset__size(&cset_node) == 1);

      cset__add(&cset_node, ((Node){.x=1, .y=2}));
      assert(cset__size(&cset_node) == 2);

      // Removed because our comparator uses `x` i.e 1 which already exists
      cset__remove(&cset_node, ((Node){.x=1, .y=45}));
      assert(cset__size(&cset_node) == 1);

      cset__free(&cset_node);
    }
    ```

* `cset__free`: *no return*
Frees up heap allocation

    ```c
    #include "cset.h"

    Cset(int) cset_int_t;

    int main() {
      cset_int_t cset_int;
      cset__init(&cset_int);

      cset__add(&cset_int, 34);

      // Free up the memory
      cset__free(&cset_int);
    }
    ```

### APIS for Iteration

* `Cset_iterator(type)`
    Creates Iterator type definition for a given cset type.

* `cset_iterator__init(iter, cset)`: *no return*
    Initializes iterator `iter` with `cset`.
  ```c
  #include "cset.h"

  Cset(int) cset_int_t;
  // 1. Define iterator type for `cset_int_t`
  Cset_iterator(cset_int_t) cset_iterator_int_t;

  int main() {
    cset_int_t cset_int;
    cset__init(&cset_int);

    cset_iterator_int_t cset_int_iterator;
    // 2. Initialize iterator with `cset_int`
    cset_iterator__init(&cset_int_iterator, &cset_int);
  }
  ```

* `cset__done(iter)`: *returns `bool`*
    Returns whether the iteration is complete or not.
  ```c
  #include <assert.h>
  #include "cset.h"

  Cset(int) cset_int_t;
  Cset_iterator(cset_int_t) cset_iterator_int_t;

  int main() {
    cset_int_t cset_int;
    cset__init(&cset_int);

    cset__add(&cset_int, 34);
    cset__add(&cset_int, 56);

    cset_iterator_int_t cset_int_iterator;
    cset_iterator__init(&cset_int_iterator, &cset_int);

    // Checks whether the iteration is complete or not
    bool done = cset_iterator__done(&cset_int_iterator);
    assert(done == false);
  }
  ```

* `cset__next(iter, buffer)`: *no return*

    Yields pointer to next element into buffer. Note: buffer must be pointer type.

  ```c
  #include <assert.h>
  #include "cset.h"


  Cset(int) cset_int_t;
  Cset_iterator(cset_int_t) cset_iterator_int_t;

  int main() {
    cset_int_t cset_int;
    cset__init(&cset_int);

    cset__add(&cset_int, 34);
    cset__add(&cset_int, 56);

    cset_iterator_int_t cset_int_iterator;
    cset_iterator__init(&cset_int_iterator, &cset_int);

    for (;;) {
      if (cset_iterator__done(&cset_int_iterator)) break;

      // Yields pointer to next element into buffer
      int* buffer;
      cset_iterator__next(&cset_int_iterator, buffer);

      printf("Got: %d\n", *buffer);
    }

    cset__free(&cset_int);
  }
  ```

### APIS for basic set operations

* `cset__intersection(result, a, b)`: *no return*
Puts the intersection of two sets `a` and `b` in `result`.

  ```c
  #include <assert.h>
  #include "cset.h"

  Cset(int) cset_int_t;

  int main() {
    cset_int_t cset_int_a;
    cset_int_t cset_int_b;

    cset__init(&cset_int_a);
    cset__init(&cset_int_b);

    // Add elements to cset_int_a
    cset__add(&cset_int_a, 12);
    cset__add(&cset_int_a, 13);
    cset__add(&cset_int_a, 14);

    // Add elements to cset_int_b
    cset__add(&cset_int_b, 12);
    cset__add(&cset_int_b, 13);
    cset__add(&cset_int_b, 16);

    cset_int_t result;
    cset__init(&result);

    // Perform intersection between cset_int_a and cset_int_b
    cset__intersect(&result, &cset_int_a, &cset_int_b);

    assert(cset__size(&result) == 2);

    cset__free(&cset_int_a);
    cset__free(&cset_int_b);
    cset__free(&result);
  }
  ```

* `cset__union(result, a, b)`: *no return*
Puts all the elements that are in either set into `result`

  ```c
  #include <assert.h>
  #include "cset.h"

  Cset(int) cset_int_t;
  Cset_iterator(cset_int_t) cset_iterator_int_t;

  int main() {
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

    // Perform union between `cset_int_a` and `cset_int_b`
    cset__union(&cset_result, &cset_int_a, &cset_int_b);

    // Size of the `cset_result` set must be 5 with elements { 34, 25, 12, 1, 4 }
    assert(cset__size(&cset_result) == 5);

    cset__add(&cset_int_b, 100);
    cset__union(&cset_result, &cset_int_a, &cset_int_b);
    // Size of the `cset_result` set must be 6 as we added new elements to `cset_int_b`
    assert(cset__size(&cset_result) == 6);

    cset__free(&cset_int_a);
    cset__free(&cset_int_b);
    cset__free(&cset_result);
  }
  ```

### License

Copyright © 2020-20121 Robus, LLC. This source code is licensed under the MIT license found in
the [LICENSE.txt]
The documentation to the project is licensed under the [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)
license.


---
Made with ♥ by Robus Gauli ([@robusgauli]

```

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

### c_source/tests/test.c (454 lines)
```c
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

## Current state of the editable Rust files
### src/cset.rs (581 lines)
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
    let bytes = unsafe { std::slice::from_raw_parts(mem_ptr as *const u8, 4) };
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

## Baseline check result before your first edit
- compiles: False (1 errors)
- tests: 0 passed / 0 total (0 failed)
- unsafe metrics (builtin-approximation): lines=15, calls=15, casts=12, pointer_arithmetic=0
- clippy warnings: n/a (needs a successful build)
- tokens used so far: 0 / 2000000

## cargo build errors
```
   Compiling cset v0.1.0 (/mnt/c/VSCodeProjects/CS598JBR-Team-17/MP4/translations/project_1)
error[E0606]: casting `&mut u32` as `*const u8` is invalid
  --> src/cset.rs:48:53
   |
48 |     let bytes = unsafe { std::slice::from_raw_parts(mem_ptr as *const u8, 4) };
   |                                                     ^^^^^^^^^^^^^^^^^^^^

warning: value assigned to `index` is never read
   --> src/cset.rs:445:17
    |
445 |         let mut index = 0usize;
    |                 ^^^^^
    |
    = help: maybe it is overwritten before being read?
    = note: `#[warn(unused_assignments)]` on by default

For more information about this error, try `rustc --explain E0606`.
warning: `cset` (lib test) generated 1 warning
error: could not compile `cset` (lib test) due to 1 previous error; 1 warning emitted
warning: build failed, waiting for other jobs to finish...
warning: `cset` (lib) generated 1 warning (1 duplicate)
error: could not compile `cset` (lib) due to 1 previous error; 1 warning emitted

```

## unsafe metrics (builtin-approximation)
{"unsafe_lines": 15, "unsafe_calls": 15, "unsafe_casts": 12, "pointer_arithmetic": 0, "unsafe_blocks": 15, "unsafe_fns": 0, "raw_pointer_decls": 2, "ffi_calls": 0, "transmute_uses": 0, "manual_alloc_ops": 0, "files_with_forbid_unsafe_code": 0, "files_analysed": 2}
Where:
- src/cset.rs:27 [unsafe_calls] let bytes = unsafe { std::slice::from_raw_parts(mem_ptr as *const u8, 8) };
- src/cset.rs:48 [unsafe_calls] let bytes = unsafe { std::slice::from_raw_parts(mem_ptr as *const u8, 4) };
- src/cset.rs:192 [raw_pointer_decls] pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:196 [unsafe_calls] let slice = unsafe { std::slice::from_raw_parts(input, len) };
- src/cset.rs:201 [raw_pointer_decls] pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:205 [unsafe_calls] let slice = unsafe { std::slice::from_raw_parts(input, len) };
- src/cset.rs:211 [unsafe_calls] let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
- src/cset.rs:217 [unsafe_calls] let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
- src/cset.rs:274 [unsafe_calls] let elem_bytes = unsafe { std::slice::from_raw_parts(elem_ref as *const T as *const u8, std::mem::size_of::<T>()) };
- src/cset.rs:319 [unsafe_calls] buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
- src/cset.rs:326 [unsafe_calls] v: CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } },
- src/cset.rs:404 [unsafe_calls] self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
- src/cset.rs:413 [unsafe_calls] let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
- src/cset.rs:440 [unsafe_calls] let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
- src/cset.rs:475 [unsafe_calls] let ref_bytes = unsafe { std::slice::from_raw_parts(value as *const T as *const u8, std::mem::size_of::<T>()) };
- src/cset.rs:519 [unsafe_calls] self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
- src/cset.rs:570 [unsafe_calls] self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
Do not add new unsafe code while fixing this. Replace raw-pointer helpers with safe code over slices/`Vec`/iterators; keep unsafe, if a signature truly forces it, confined to that one function.

Start by studying the C code, the interface and the tests, then write your first implementation. Cover every function and type in the interface.
