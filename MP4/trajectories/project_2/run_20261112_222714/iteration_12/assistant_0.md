<notes>
## Plan

Looking at the test failures:
1. `empty_input_test` and `encode_decode_test` fail with `ReadError` - this suggests the PSBT parsing is failing
2. `read_test_vector` fails with step=4 instead of 0 - the handler is being called but the step counter is not being updated correctly

The issue with `read_test_vector` is that the `step` variable is passed as `&mut dyn Any` but the handler can't directly increment it because it's not typed. The C code uses a pointer to an int that gets incremented.

For the `ReadError` failures, I need to look at what's happening in the PSBT parsing. The test uses `psbt_read` after `psbt_init`, and the PSBT data comes from `psbt_decode`.

Let me check the test more carefully:
- `empty_input_test` decodes a base64 PSBT, then calls `psbt_init` and `psbt_read`
- The base64 string is "cHNidP8BACoCAAAAAAGA8PoCAAAAABepFCufG2xKKzFR7+3XGjiAZPO/VDBkhwAAAAAAAA=="

The issue might be in how we're handling the PSBT parsing. Looking at the C code, `psbt_read` expects the data to already be in the PSBT's data buffer, and it parses from there.

I need to re-read the C code more carefully to understand the expected behavior.
</notes>

<read path="src/bin/test.rs"/>