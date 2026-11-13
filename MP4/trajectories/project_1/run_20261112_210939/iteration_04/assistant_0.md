<notes>
## Analysis
Looking at the test failures more carefully:
1. `test_cset_init` expects capacity=2 but gets 4 - the vector's capacity is 4 after reserving 2 (Rust's Vec grows exponentially)
2. The C code's `cset__cap` returns the actual capacity, and `cset_vector__init_with_cap` with `ncap=2` should result in capacity 2

The issue is that `cset_vector__init_with_cap` uses `reserve()` which may reserve more than requested. The C code uses `malloc` which allocates exactly the requested size.

I need to rewrite the implementation to properly manage the vector size and capacity to match the C behavior exactly.

## Plan
1. Rewrite `cset_vector__init_with_cap` to actually set the size to ncap with zeroed elements
2. Rewrite `new()` to properly initialize the vector
3. Rewrite `add()` to properly handle the double hashing and load factor check
4. Rewrite `resize()` to properly rehash elements
5. Fix all the helper functions to work correctly
</notes>

<edit path="src/cset.rs">
<search>
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

fn cset_vector__index<T>(tv: &[CsetValue<T>], i: usize) -> &CsetValue<T> {
    &tv[i]
}

fn cset_vector__cap<T>(tv: &Vec<CsetValue<T>>) -> usize {
    tv.capacity()
}

fn cset_vector__free<T>(tv: &mut Vec<CsetValue<T>>) {
    tv.clear();
    tv.shrink_to_fit();
}
</search>
<replace>
// Vector helper functions
fn cset_vector__init_with_cap<T>(tv: &mut Vec<CsetValue<T>>, ncap: usize) {
    tv.clear();
    tv.reserve_exact(ncap);
    for _ in 0..ncap {
        tv.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
    }
}

fn cset_vector__grow<T>(tv: &mut Vec<CsetValue<T>>, ncap: usize) {
    let current_cap = tv.capacity();
    if current_cap < ncap {
        tv.reserve_exact(ncap - current_cap);
        for _ in current_cap..ncap {
            tv.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
    }
}

fn cset_vector__add<T>(tv: &mut Vec<CsetValue<T>>, value: CsetValue<T>) {
    tv.push(value);
}

fn cset_vector__index<T>(tv: &[CsetValue<T>], i: usize) -> &CsetValue<T> {
    &tv[i]
}

fn cset_vector__cap<T>(tv: &Vec<CsetValue<T>>) -> usize {
    tv.capacity()
}

fn cset_vector__free<T>(tv: &mut Vec<CsetValue<T>>) {
    tv.clear();
    tv.shrink_to_fit();
}
</replace>
</edit>