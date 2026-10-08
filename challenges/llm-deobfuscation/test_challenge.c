#include <stdio.h>
#include <stdint.h>

extern const char* get_flag1(unsigned int seed);
extern const char* get_flag2(uint32_t magic_input);
extern const char* get_flag3(const char *password);

int main(void) {
    printf("=== Flag 1 (BCF) ===\n");
    printf("  Result: %s\n\n", get_flag1(42));

    printf("=== Flag 2 (MBA) ===\n");
    printf("  Wrong input:   %s\n", get_flag2(0x12345678));
    printf("  Correct input: %s\n\n", get_flag2(0xBAAAD0BF));

    printf("=== Flag 3 (CFF+RASP) ===\n");
    printf("  Wrong password:   %s\n", get_flag3("wrong"));
    printf("  Correct password: %s\n", get_flag3("quarkslab2026"));

    return 0;
}
