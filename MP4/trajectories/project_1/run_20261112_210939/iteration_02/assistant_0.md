<notes>
## Analysis
The tests are failing with overflow errors in `add()` method. Looking at the C code, the issue is that:
1. The `add` function in C doesn't resize before checking if the element exists - it checks load factor first
2. The `resize` function resets `bucket_size` to 0 and then re-adds elements, but the re-add logic is flawed
3. The `new()` function initializes buckets with `CSET_INITIAL_CAP` elements (all pi=0), but the C code uses `cset_vector__init_with_cap` which only reserves capacity, not sets size

## Key Issues
1. `new()` should create an empty vector, not pre-fill with zeroed elements
2. `add()` should check load factor BEFORE adding, not after
3. `resize()` logic is wrong - it should properly rehash all elements
4. The `bucket_size` should track actual elements, not be reset incorrectly

## Plan
1. Fix `new()` to create empty vector without pre-filling
2. Fix `add()` to check load factor before adding
3. Fix `resize()` to properly rehash elements
4. Fix `clear()` to properly reinitialize
5. Fix `contains()` to work with `&self`
6. Fix set operations to use `&self` for second parameter
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
</search>
<replace>
// Vector helper functions
fn cset_vector__init_with_cap<T>(tv: &mut Vec<CsetValue<T>>, ncap: usize) {
    tv.clear();
    tv.reserve(ncap);
    if CSET_FORCE_INITIALIZE {
        for _ in 0..ncap {
            tv.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
    }
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
</replace>
</edit>