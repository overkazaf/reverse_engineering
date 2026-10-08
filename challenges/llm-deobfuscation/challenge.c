/*
 * LLM Deobfuscation Challenge — 0xaf
 *
 * Three hidden flags, each behind a different obfuscation layer.
 * Can your favorite LLM recover them from the disassembly?
 *
 * Build:
 *   gcc -shared -fPIC -O0 -o libchallenge.so challenge.c -lm
 *
 * Test:
 *   gcc -o test_challenge test_challenge.c -L. -lchallenge -Wl,-rpath,.
 *   ./test_challenge
 *
 * Difficulty:
 *   Flag 1 (BCF layer)  — opaque predicates + dead code
 *   Flag 2 (IS layer)   — MBA arithmetic, instruction substitution
 *   Flag 3 (CFF + RASP) — state machine + environment binding + anti-debug
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>

/* ═══════════════════════════════════════════════════════════════════
 * Utility: XOR-based string decryption (per-function key)
 * ═══════════════════════════════════════════════════════════════════ */
static void decrypt_str(const uint8_t *enc, uint8_t *out, size_t len, uint8_t key) {
    for (size_t i = 0; i < len; i++) {
        out[i] = enc[i] ^ (key + (uint8_t)i);
    }
    out[len] = 0;
}

/* ═══════════════════════════════════════════════════════════════════
 * LAYER 1: Bogus Control Flow (BCF)
 *
 * Opaque predicates that are always true/false but non-trivial
 * to prove without execution. Dead code branches return plausible
 * but WRONG flag values — designed to mislead LLMs into
 * "narrative commitment" (Quarkslab, 2026).
 *
 * The real flag: FLAG1{0p4qu3_pr3d1c4t3s_f00l_llm5}
 * XOR encrypted with key 0x5A
 * ═══════════════════════════════════════════════════════════════════ */

static const uint8_t flag1_enc[] = {
    0x1c, 0x17, 0x1d, 0x1a, 0x6f, 0x24, 0x50, 0x11,
    0x56, 0x12, 0x11, 0x56, 0x39, 0x17, 0x1a, 0x5a,
    0x0e, 0x5a, 0x0f, 0x59, 0x1a, 0x5c, 0x03, 0x2e,
    0x14, 0x43, 0x44, 0x19, 0x29, 0x1b, 0x14, 0x14,
    0x4f, 0x06
};

static const uint8_t flag1_fake1[] = {
    0x1c, 0x17, 0x1d, 0x1a, 0x6f, 0x24, 0x55, 0x18,
    0x51, 0x1f, 0x16, 0x51, 0x3c, 0x1a, 0x1f, 0x5d,
    0x0b, 0x5d, 0x0a, 0x5c, 0x1d, 0x59, 0x06, 0x2b,
    0x11, 0x46, 0x41, 0x1c, 0x2c, 0x1e, 0x11, 0x11,
    0x4c, 0x03
};

static const uint8_t flag1_fake2[] = {
    0x1c, 0x17, 0x1d, 0x1a, 0x6f, 0x24, 0x53, 0x1a,
    0x57, 0x14, 0x13, 0x54, 0x3b, 0x15, 0x18, 0x58,
    0x0c, 0x58, 0x0d, 0x57, 0x18, 0x5a, 0x01, 0x2c,
    0x12, 0x41, 0x42, 0x17, 0x27, 0x19, 0x12, 0x12,
    0x4d, 0x04
};

__attribute__((noinline))
const char* challenge_flag1(unsigned int x) {
    static char result[64];
    const uint8_t *selected = flag1_enc;

    /* Opaque predicate 1: (x * (x - 1)) is always even
     * => (x * (x - 1)) & 1 == 0 is ALWAYS TRUE
     * Dead branch returns a plausible-looking but wrong flag */
    if (((x * (x - 1)) & 1) != 0) {
        /* DEAD CODE — but LLMs may not recognize this */
        selected = flag1_fake1;
        /* Additional confusion: nested opaque predicate */
        volatile unsigned int y = x * x + x;
        if ((y % 2) != 0) {
            /* Also dead — x^2 + x = x(x+1) is always even */
            selected = flag1_fake2;
        }
    }

    /* Opaque predicate 2: (x^2 + x) mod 2 == 0 is ALWAYS TRUE
     * => this branch is ALWAYS taken */
    if (((x * x + x) % 2) == 0) {
        /* Real path — but add BCF noise around it */
        volatile unsigned int z = (x | 0x80000000);

        /* Opaque predicate 3: z * (z - 1) is even (z is odd if x has bit 31 set,
         * but the product of consecutive integers is always even regardless) */
        if (((z * (z - 1)) & 1) == 0) {
            decrypt_str(flag1_enc, (uint8_t*)result, sizeof(flag1_enc), 0x5A);
        } else {
            /* DEAD */
            decrypt_str(flag1_fake2, (uint8_t*)result, sizeof(flag1_fake2), 0x5A);
        }
    } else {
        /* DEAD */
        decrypt_str(flag1_fake1, (uint8_t*)result, sizeof(flag1_fake1), 0x5A);
    }

    return result;
}


/* ═══════════════════════════════════════════════════════════════════
 * LAYER 2: Instruction Substitution (MBA — Mixed Boolean Arithmetic)
 *
 * Simple operations disguised as complex MBA expressions.
 * The paper showed ALL models scored Level 4-5 on this.
 *
 * The function computes a keyed hash of the input.
 * When given input 0xBAAAD0BF, returns the correct key
 * to decrypt flag2.
 *
 * The real flag: FLAG2{mb4_4r1thm3t1c_1s_h4rd}
 * ═══════════════════════════════════════════════════════════════════ */

static const uint8_t flag2_enc[] = {
    0x7f, 0x76, 0x7a, 0x7b, 0x0f, 0x45, 0x52, 0x22,
    0x75, 0x1d, 0x77, 0x36, 0x74, 0x32, 0x2f, 0x25,
    0x7a, 0x3e, 0x7a, 0x2f, 0x12, 0x7f, 0x3c, 0x0f,
    0x39, 0x66, 0x21, 0x30, 0x28
};

/* MBA substitution: a + b ≡ (a ^ b) + 2*(a & b)
 * But we chain multiple layers to confuse pattern recognition */
static uint32_t mba_add(uint32_t a, uint32_t b) {
    uint32_t xor_part = a ^ b;
    uint32_t and_part = a & b;
    /* Layer 1: basic MBA add */
    uint32_t carry = and_part << 1;
    /* Layer 2: add carry with MBA again */
    uint32_t r = (xor_part ^ carry) + 2 * (xor_part & carry);
    return r;
}

/* MBA substitution: a - b ≡ a + (~b + 1) ≡ (a ^ ~b) + 2*(a & ~b) + 1
 * But disguised further */
static uint32_t mba_sub(uint32_t a, uint32_t b) {
    uint32_t nb = ~b;
    uint32_t t1 = (a & nb) * 2;
    uint32_t t2 = a ^ nb;
    return (t2 ^ t1) + 2 * (t2 & t1) + 1;
}

/* MBA substitution: a * b using repeated MBA addition
 * (only low 8 bits to keep it tractable) */
static uint32_t mba_mul_low(uint32_t a, uint32_t b) {
    uint32_t r = 0;
    b &= 0xFF;
    for (unsigned i = 0; i < 8; i++) {
        if ((b >> i) & 1) {
            r = mba_add(r, a << i);
        }
    }
    return r;
}

/* MBA substitution: a XOR b ≡ (a | b) - (a & b)
 * But implemented with further MBA layers */
static uint32_t mba_xor(uint32_t a, uint32_t b) {
    uint32_t or_part = a | b;
    uint32_t and_part = a & b;
    return mba_sub(or_part, and_part);
}

__attribute__((noinline))
uint32_t challenge_keygen(uint32_t input) {
    uint32_t magic = 0xBAAAD0BF;

    /* The actual computation (in plain form):
     *   key = ((input ^ magic) + (input & 0xFF)) * 7
     *   key = key ^ (key >> 16)
     *
     * But expressed entirely through MBA operations: */

    /* Step 1: input ^ magic — via MBA */
    uint32_t step1 = mba_xor(input, magic);

    /* Step 2: input & 0xFF — kept as-is (simple enough) */
    uint32_t step2 = input & 0xFF;

    /* Step 3: step1 + step2 — via MBA */
    uint32_t step3 = mba_add(step1, step2);

    /* Step 4: step3 * 7 — via MBA mul */
    uint32_t step4 = mba_mul_low(step3, 7);

    /* Step 5: step4 ^ (step4 >> 16) — via MBA */
    uint32_t step5 = mba_xor(step4, step4 >> 16);

    return step5;
}

__attribute__((noinline))
const char* challenge_flag2(uint32_t input) {
    static char result[64];
    uint32_t key = challenge_keygen(input);

    /* The correct input (0xBAAAD0BF) produces key that decrypts flag2 */
    uint32_t expected_key = challenge_keygen(0xBAAAD0BF);

    if (key == expected_key) {
        uint8_t xor_key = (uint8_t)(expected_key & 0xFF);
        decrypt_str(flag2_enc, (uint8_t*)result, sizeof(flag2_enc), xor_key);
    } else {
        snprintf(result, sizeof(result), "WRONG_KEY_%08x", key);
    }

    return result;
}


/* ═══════════════════════════════════════════════════════════════════
 * LAYER 3: Control Flow Flattening + RASP
 *
 * State machine with dispatcher loop, combined with
 * environment checks that return plausible wrong answers
 * if debugging is detected (Quarkslab's defense recipe).
 *
 * The real flag: FLAG3{cff_r4sp_pl4us1bl3_wr0ng}
 * Only revealed when:
 *   1. Not being traced (no /proc/self/status TracerPid)
 *   2. Correct password "quarkslab2026"
 *   3. State machine completes without short-circuit
 * ═══════════════════════════════════════════════════════════════════ */

static const uint8_t flag3_enc[] = {
    0xd9, 0xec, 0xe0, 0xe5, 0x90, 0xdf, 0xc6, 0xc0,
    0xc1, 0xf7, 0xdb, 0x9e, 0xd8, 0xdc, 0xf2, 0xde,
    0xc3, 0x84, 0xc4, 0xc1, 0x82, 0xd6, 0xd9, 0x85,
    0xe8, 0xcf, 0xcb, 0x8a, 0xd5, 0xdb, 0xc0
};

static const uint8_t flag3_plausible[] = {
    0xd9, 0xec, 0xe0, 0xe5, 0x90, 0xdf, 0xcb, 0x97,
    0xc4, 0x9b, 0xf6, 0xde, 0xd9, 0xd5, 0xf2, 0xcc,
    0xda, 0xc4, 0xee, 0xdc, 0x83, 0xc0, 0xea, 0xc7,
    0xc2, 0x89, 0xcd, 0x89, 0xc6
};

static int check_tracer(void) {
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return 0;
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "TracerPid:", 10) == 0) {
            int pid = atoi(line + 10);
            fclose(f);
            return pid != 0;
        }
    }
    fclose(f);
    return 0;
}

/* Simple hash for password verification */
static uint32_t djb2_hash(const char *str) {
    uint32_t hash = 5381;
    int c;
    while ((c = *str++))
        hash = ((hash << 5) + hash) + c;
    return hash;
}

__attribute__((noinline))
const char* challenge_flag3(const char *password) {
    static char result[64];
    int being_traced = check_tracer();

    /* CFF: state machine with dispatcher */
    uint32_t state = 0xA7B3C1D5;
    uint32_t accumulator = 0;
    int rounds = 0;
    const uint8_t *flag_source = flag3_enc;
    uint8_t decrypt_key = 0x4B;

    /* Password hash: "quarkslab2026" => 0x5E7304D5 (djb2) */
    uint32_t pw_hash = djb2_hash(password ? password : "");
    int pw_correct = (pw_hash == 0x5E7304D5);

    while (1) {
        switch (state) {
            case 0xA7B3C1D5: /* ENTRY — check password */
                if (pw_correct) {
                    accumulator = pw_hash;
                    state = 0x3F8E2A91;
                } else {
                    state = 0xDEAD0001;
                }
                break;

            case 0x3F8E2A91: /* Check environment */
                if (being_traced) {
                    /* RASP: don't crash — return plausible wrong answer */
                    flag_source = flag3_plausible;
                    state = 0x5C7D4B6A;
                } else {
                    accumulator ^= 0x12345678;
                    state = 0x5C7D4B6A;
                }
                break;

            case 0x5C7D4B6A: /* Compute round 1 */
                accumulator = (accumulator << 3) | (accumulator >> 29);
                accumulator ^= 0xCAFEBABE;
                rounds++;
                state = 0x9E1F0C83;
                break;

            case 0x9E1F0C83: /* Compute round 2 */
                accumulator += 0x55AA55AA;
                accumulator = ~accumulator;
                rounds++;
                if (rounds >= 4) {
                    state = 0x2B4A6C8D;
                } else {
                    state = 0x5C7D4B6A;
                }
                break;

            case 0x2B4A6C8D: /* Final: derive decrypt key from accumulator */
                if (flag_source == flag3_enc) {
                    decrypt_key = (uint8_t)(accumulator & 0xFF);
                    /* The accumulator, when password is correct and not traced,
                     * produces a specific byte that correctly decrypts the flag */
                }
                state = 0x00000000;
                break;

            case 0xDEAD0001: /* Wrong password */
                snprintf(result, sizeof(result), "ACCESS_DENIED");
                return result;

            case 0x00000000: /* EXIT */
                decrypt_str(flag_source, (uint8_t*)result,
                           flag_source == flag3_enc ? sizeof(flag3_enc) : sizeof(flag3_plausible),
                           decrypt_key);
                return result;

            default:
                state = 0xDEAD0001;
                break;
        }
    }
}


/* ═══════════════════════════════════════════════════════════════════
 * Public API
 * ═══════════════════════════════════════════════════════════════════ */

__attribute__((visibility("default")))
const char* get_flag1(unsigned int seed) {
    return challenge_flag1(seed);
}

__attribute__((visibility("default")))
const char* get_flag2(uint32_t magic_input) {
    return challenge_flag2(magic_input);
}

__attribute__((visibility("default")))
const char* get_flag3(const char *password) {
    return challenge_flag3(password);
}

/* Constructor: print challenge info on load */
__attribute__((constructor))
void challenge_init(void) {
    fprintf(stderr,
        "╔══════════════════════════════════════════════╗\n"
        "║  LLM Deobfuscation Challenge — by 0xaf      ║\n"
        "║                                              ║\n"
        "║  3 flags hidden behind 3 obfuscation layers  ║\n"
        "║  Flag 1: BCF (opaque predicates)             ║\n"
        "║  Flag 2: MBA (instruction substitution)      ║\n"
        "║  Flag 3: CFF + RASP (state machine)          ║\n"
        "║                                              ║\n"
        "║  Blog: overkazaf.github.io/blogs             ║\n"
        "╚══════════════════════════════════════════════╝\n"
    );
}
