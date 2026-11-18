/* Byte-oriented defined-behavior comparisons only. No transaction parsing:
 * tx.c dereferences potentially unaligned u32/u64 pointers. No Base62 62/63
 * indices, short C destinations, or inconsistent C allocation lengths. */
#include <stdio.h>
#include <string.h>
#include "../../subjects/project_2/c_source/psbt.h"
#include "../../subjects/project_2/c_source/base64.h"
#include "../../subjects/project_2/c_source/compactsize.h"

static void bytes(const char *label, const unsigned char *data, size_t n) {
    printf("%s ", label);
    for (size_t i = 0; i < n; ++i) printf("%02x", data[i]);
    putchar('\n');
}

int main(void) {
    unsigned char out[32] = {0};
    size_t len = 0;
    enum psbt_result r = psbt_decode("70736274ffNOT_HEX", 10, out, sizeof(out), &len);
    if (r != PSBT_OK) return 1;
    bytes("hex_prefix", out, len);
    unsigned char raw[] = {0x12, 0x34, 0xff};
    r = psbt_encode_raw(raw, 2, PSBT_ENCODING_HEX, out, sizeof(out), &len);
    if (r != PSBT_OK) return 2;
    bytes("raw_prefix", out, len);
    unsigned char psbt[] = {'p','s','b','t',0xff};
    if (!base64_encode(psbt, sizeof(psbt), out, sizeof(out), &len)) return 3;
    bytes("base64", out, len + 1);
    unsigned char safe62[] = {0xf4, 0, 0};
    if (!base62_encode(safe62, sizeof(safe62), out, sizeof(out), &len)) return 4;
    bytes("base62", out, len + 1);
    printf("unknown_global %s\n", psbt_type_tostr(0x99, PSBT_SCOPE_GLOBAL));
    memset(out, 0xaa, sizeof(out));
    compactsize_write(out, 253);
    bytes("compactsize_253_c", out, 3);
    return 0;
}
