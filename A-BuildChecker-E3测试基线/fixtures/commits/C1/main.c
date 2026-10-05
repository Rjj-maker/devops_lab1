#include <stdio.h>
#include "config.h"
#include "feature.h"

int main(void) {
    printf("%d\n", BASE + FEATURE + MODE);
    return 0;
}
