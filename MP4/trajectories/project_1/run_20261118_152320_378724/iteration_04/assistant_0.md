The remaining four unsafe sites are each forced by the frozen interface, as the previous notes explain. Removing them needs one of the human decisions (a)–(d), so I won't attempt further reductions. This reply records the blocker in a doc comment so the code matches the notes. It does not change behaviour.

<edit path="src/cset.rs">
<search>
    // Placeholder element for slots that are never read (pi == 0 or -1).
</search>
<replace>
    // Placeholder element for slots that are never read (pi == 0 or -1).
    // OPEN (needs human decision): removing this unsafe requires `T: Default`
    // on `impl<T> Cset<T>`, which the frozen interface does not allow.
</replace>
</edit>

<notes>
Status: 15/15 tests pass, Clippy clean, 0 interface deviations, 4 unsafe lines.
Blocked on a human decision; no further safe reduction is possible under the frozen interface:
- raw_bytes (xxh64, xxh64_h take *const u8): needs from_raw_parts.
- alias_mut (&self -> &mut Vec): needs interior mutability or &mut self.
- copy_of (ptr::read, index/iter without Clone): owned T from &T.
- placeholder (mem::zeroed, new() without Default): UB for &U, Box, NonNull.
Also: the one-byte view_bytes limitation means callbacks hash only one byte for size > 1.
Options (a)-(d) are listed in the previous notes. Awaiting approval before any further change.
The #[allow] attributes are suppressions for the frozen signatures and are kept deliberately.
</notes>