#include <inttypes.h>
#include <stdio.h>
#include "../../subjects/project_1/c_source/src/cset.h"

int main(void) {
    uint8_t data[96];
    for (size_t i = 0; i < sizeof(data); ++i) data[i] = (uint8_t)i;
    const size_t lengths[] = {0, 1, 2, 7, 8, 15, 16, 31, 32, 33, 63, 64, 80, 96};
    const uint64_t seeds[] = {0, 2718182};
    for (size_t i = 0; i < sizeof(lengths) / sizeof(lengths[0]); ++i)
        for (size_t j = 0; j < sizeof(seeds) / sizeof(seeds[0]); ++j)
            printf("%zu %" PRIu64 " %" PRIu64 " %" PRIu64 "\n", lengths[i], seeds[j],
                   XXH64(data, lengths[i], seeds[j]), XXH64_h(data, lengths[i], seeds[j]));
    return 0;
}
