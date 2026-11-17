Now I'll consolidate all unsafe sites into a few private helper functions, reducing unsafe blocks from 13 to 7.

<edit path="src/cset.rs">
<search>
pub const CSET_MIN_LOAD_FACTOR: f64 = 0.2;

// Helper: check if little endian</search>
<replace>
pub const CSET_MIN_LOAD_FACTOR: f64 = 0.2;

// --- Unsafe helpers (consolidated) ---

// Convert &mut u8 to &[u8] of