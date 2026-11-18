# Project: cset

Continue from the existing agent-generated implementation. Select a failure from the diagnostics, inspect the C and Rust, record your hypothesis in notes, and propose a focused edit. Use the next validation result to decide whether to revise it or inspect another failure.

## Workspace layout
crate (editable area: src/*.rs):
  .gitignore  (8 bytes)
  Cargo.lock  (148 bytes)
  Cargo.toml  (75 bytes)
  src/bin/test.rs  (6048 bytes)
  src/cset.rs  (19564 bytes)
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

#define XXH_get64
... [truncated; use <read> for the rest]
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
### src/cset.rs (611 lines)
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
- tokens used so far: 0 / 1000000

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
- src/cset.rs:256 [raw_pointer_decls] pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:262 [raw_pointer_decls] pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
- src/cset.rs:317 [unsafe_calls] unsafe { std::ptr::read(std::ptr::from_ref(v)) }
- src/cset.rs:357 [unsafe_calls] unsafe { std::mem::zeroed() }

## Separate regression check
$ /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/.venv/bin/python /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/src/run_regressions.py --project-id 1 --output /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/trajectories/project_1/run_20261118_114859_292068/additional_checks/1
returncode=1 timed_out=False
{"tests::cset_hash_00": "FAILED", "tests::cset_hash_01": "FAILED", "tests::cset_hash_02": "FAILED", "tests::cset_hash_07": "FAILED", "tests::cset_hash_08": "FAILED", "tests::cset_hash_15": "FAILED", "tests::cset_hash_16": "FAILED", "tests::cset_hash_31": "FAILED", "tests::cset_hash_32": "ok", "tests::cset_hash_33": "ok", "tests::cset_hash_63": "ok", "tests::cset_hash_64": "ok", "tests::cset_hash_80": "ok", "tests::cset_hash_96": "ok", "tests::cset_padding_free_copy_generic": "ok"}
```
[tests::cset_hash_00]
thread 'tests::cset_hash_00' panicked at src/lib.rs:253:9:
input bytes 0..96, truncated to len:
len=0 seed=0: Rust=13934714534406826450/6089448738516538328, C=17241709254077376921/13315799867417602922
len=0 seed=2718182: Rust=1088256915903631556/11614518687002993724, C=17164995725320669776/9609742367336788117
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

[tests::cset_hash_01]
thread 'tests::cset_hash_01' panicked at src/lib.rs:253:9:
input bytes 0..96, truncated to len:
len=1 seed=0: Rust=400611822795326115/1344935720564239988, C=16804241149081757544/11193626097507625299
len=1 seed=2718182: Rust=8168549641978686410/6594899528827042558, C=12030735130094489608/16585143914630977865

[tests::cset_hash_02]
thread 'tests::cset_hash_02' panicked at src/lib.rs:253:9:
input bytes 0..96, truncated to len:
len=2 seed=0: Rust=5578343508417602773/8617509540135573086, C=5216751715308240086/962134502339947765
len=2 seed=2718182: Rust=15723073577781726320/4971479887067988310, C=6839953705013005250/14547683834055110473

[tests::cset_hash_07]
thread 'tests::cset_hash_07' panicked at src/lib.rs:253:9:
input bytes 0..96, truncated to len:
len=7 seed=0: Rust=12527556425796954294/7584827969456509918, C=1498682999415010002/4249893767171937820
len=7 seed=2718182: Rust=8104809122016315627/12829040013170679280, C=15642697405811612460/1518540224581367784

[tests::cset_hash_08]
thread 'tests::cset_hash_08' panicked at src/lib.rs:253:9:
input bytes 0..96, truncated to len:
len=8 seed=0: Rust=14795519122527122261/9163211194136353357, C=9820687458478070669/3730646594863863303
len=8 seed=2718182: Rust=9499085504836072429/4170975662148065910, C=9136710207871035179/1811739754178317970

[tests::cset_hash_15]
thread 'tests::cset_hash_15' panicked at src/lib.rs:253:9:
input bytes 0..96, truncated to len:
len=15 seed=0: Rust=12282353933906490625/13813176779204586094, C=12198270006012390445/12756233403702556746
len=15 seed=2718182: Rust=7039273967639289272/2989575921063934098, C=12026005270239508466/17353067986731924435

[tests::cset_hash_16]
thread 'tests::cset_hash_16' panicked at src/lib.rs:253:9:
input bytes 0..96, truncated to len:
len=16 seed=0: Rust=4644812539751331808/15602599801977290796, C=4951407828574235127/14830457271042726377
len=16 seed=2718182: Rust=7312387820323049382/5130008953502153227, C=13836727961620331567/4311501666727977334

[tests::cset_hash_31]
thread 'tests::cset_hash_31' panicked at src/lib.rs:253:9:
input bytes 0..96, truncated to len:
len=31 seed=0: Rust=17127477829281814866/2122892477728805114, C=14071165763202158305/15169082307081493518
len=31 seed=2718182: Rust=5533785400843060160/6837672701383405910, C=15171138851224130528/15084038666174280388
```
