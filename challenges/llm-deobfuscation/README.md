# LLM Deobfuscation Challenge

Based on research from:
- [Deconstructing Obfuscation](https://arxiv.org/abs/2505.19887) (Tkachenko et al., 2025)
- [Defeating AI-Assisted RE](https://blog.quarkslab.com/defeating-ai-assisted-reverse-engineering-or-at-least-trying-to.html) (Quarkslab, 2026)

## The Challenge

`libchallenge.so` contains **3 hidden flags**, each protected by a different obfuscation layer drawn from real-world techniques that academic research has shown to challenge LLMs:

| Flag | Obfuscation Layer | Difficulty | What Makes LLMs Fail |
|------|-------------------|------------|---------------------|
| Flag 1 | **BCF** — Opaque predicates + dead code | Medium | Predicate misinterpretation, narrative commitment to fake branches |
| Flag 2 | **MBA** — Mixed Boolean Arithmetic substitution | Hard | Arithmetic transformation errors, constant fabrication |
| Flag 3 | **CFF + RASP** — State machine + anti-debug | Very Hard | Control flow misinterpretation, environment-blind analysis |

## Rules

1. Feed the **disassembly** (not the source) to your LLM of choice
2. Ask it to recover the 3 flags
3. Compare results with the ground truth
4. Report which flags your LLM got right in the [Issues](https://github.com/overkazaf/reverse_engineering/issues)

## Quick Start

```bash
# Disassemble with objdump
objdump -d libchallenge.so > challenge.asm

# Or use Ghidra/IDA for better analysis
# Then feed the decompiled output to your LLM

# Verify your answers
gcc -o test test_challenge.c -L. -lchallenge -Wl,-rpath,.
./test
```

## Build from Source

```bash
gcc -shared -fPIC -O0 -o libchallenge.so challenge.c
gcc -o test_challenge test_challenge.c -L. -lchallenge -Wl,-rpath,.
```

## Blog Post

Read the full analysis: [当 LLM 学会拆炸弹](https://overkazaf.github.io/blogs/posts/llm-deobfuscation-quarkslab-framework/)

## Scoreboard

| Model | Flag 1 (BCF) | Flag 2 (MBA) | Flag 3 (CFF+RASP) | Notes |
|-------|:---:|:---:|:---:|-------|
| *Your model here* | | | | *Submit via Issues* |

---

*Challenge by [0xaf](https://github.com/overkazaf) — DRM Security @ NetEase*
