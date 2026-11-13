<notes>
## Plan

Fix the following compiler errors:
1. Fix enum casting in psbt_type_tostr using match instead of as
2. Fix unused variable warning in psbt_init by prefixing with underscore
3. Fix mutable reference issue in psbt_read handler
</notes>

<edit path="src/psbt.rs">
<search>
/// Return a string for a record type and scope.
pub fn psbt_type_tostr(record_type: u8, scope: PsbtScope) -> &'static str {
    match scope {
        PsbtScope::Global => psbt_global_type_tostr(PsbtGlobalType::UnsignedTx),
        PsbtScope::Inputs => psbt_input_type_tostr(record_type as PsbtInputType),
        PsbtScope::Outputs => psbt_output_type_tostr(record_type as PsbtOutputType),
    }
}
</search>
<replace>
/// Return a string for a record type and scope.
pub fn psbt_type_tostr(record_type: u8, scope: PsbtScope) -> &'static str {
    match scope {
        PsbtScope::Global => psbt_global_type_tostr(PsbtGlobalType::UnsignedTx),
        PsbtScope::Inputs => {
            match record_type {
                0 => psbt_input_type_tostr(PsbtInputType::NonWitnessUtxo),
                1 => psbt_input_type_tostr(PsbtInputType::WitnessUtxo),
                2 => psbt_input_type_tostr(PsbtInputType::PartialSig),
                3 => psbt_input_type_tostr(PsbtInputType::SighashType),
                4 => psbt_input_type_tostr(PsbtInputType::RedeemScript),
                5 => psbt_input_type_tostr(PsbtInputType::WitnessScript),
                6 => psbt_input_type_tostr(PsbtInputType::Bip32Derivation),
                7 => psbt_input_type_tostr(PsbtInputType::FinalScriptSig),
                8 => psbt_input_type_tostr(PsbtInputType::FinalScriptWitness),
                _ => "UNKNOWN_INPUT_TYPE",
            }
        }
        PsbtScope::Outputs => {
            match record_type {
                0 => psbt_output_type_tostr(PsbtOutputType::RedeemScript),
                1 => psbt_output_type_tostr(PsbtOutputType::WitnessScript),
                2 => psbt_output_type_tostr(PsbtOutputType::Bip32Derivation),
                _ => "UNKNOWN_OUTPUT_TYPE",
            }
        }
    }
}
</replace>
</edit>