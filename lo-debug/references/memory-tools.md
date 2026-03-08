# Memory Debugging Tools Reference

## AddressSanitizer (ASAN)

Detects memory errors: buffer overflows, use-after-free, double-free, memory leaks.

### Building with ASAN

```bash
CC="gcc -fsanitize=address" CXX="g++ -fsanitize=address" \
    ./configure --enable-debug
make
```

Or with Clang:
```bash
CC="clang -fsanitize=address" CXX="clang++ -fsanitize=address" \
    ./configure --enable-debug
make
```

**Note:** Compiler plugins are automatically disabled when sanitizers are detected (they conflict with sanitizer instrumentation).

### Runtime Options

```bash
# Detect leaks at exit
export ASAN_OPTIONS="detect_leaks=1"

# Customize stack trace depth
export ASAN_OPTIONS="malloc_context_size=30"

# Disable specific check
export ASAN_OPTIONS="detect_stack_use_after_return=0"
```

### Running Tests with ASAN

```bash
# Tests run normally — ASAN is always active once built
make CppunitTest_sw_core

# ASAN errors cause test failure with detailed output
```

## UndefinedBehaviorSanitizer (UBSAN)

Detects undefined behavior: integer overflow, null pointer dereference, type mismatches.

### Building with UBSAN

```bash
CC="gcc -fsanitize=undefined" CXX="g++ -fsanitize=undefined" \
    ./configure --enable-debug
make
```

### Suppressions

**File:** `solenv/sanitizers/ubsan-suppressions`

```bash
export UBSAN_OPTIONS="suppressions=/path/to/LO-core/solenv/sanitizers/ubsan-suppressions"
```

## Valgrind Memcheck

### Running with Valgrind

```bash
# Individual test
make CppunitTest_sw_core VALGRIND=memcheck

# With GDB server (for interactive debugging of found issues)
make CppunitTest_sw_core VALGRIND=memcheck VALGRIND_GDB=1
```

Valgrind memcheck runs with these flags:
- `--tool=memcheck`
- `--num-callers=50` — deep backtraces
- `--error-exitcode=1` — fail test on error
- `G_SLICE=always-malloc` — disable GLib allocator caching
- `GLIBCXX_FORCE_NEW=1` — disable libstdc++ allocator caching

### Valgrind Suppressions

**File:** `solenv/sanitizers/valgrind-suppressions`

Known false positives are suppressed. Add new suppressions if needed:

```
{
   <suppression_name>
   Memcheck:Leak
   match-leak-kinds: reachable
   fun:malloc
   fun:_ZN...
}
```

### Valgrind in Code

**Header check:** `#if defined HAVE_VALGRIND_HEADERS`

```cpp
#include <valgrind/memcheck.h>

// Check if running under Valgrind
if (RUNNING_ON_VALGRIND) {
    // Skip expensive operations or use alternate code path
}

// Mark memory as defined/undefined
VALGRIND_MAKE_MEM_DEFINED(ptr, size);
VALGRIND_MAKE_MEM_UNDEFINED(ptr, size);
```

## Build-Time Memory Debug Flags

### MALLOC_CHECK_ (glibc)

Automatically set by `make debugrun` and test targets on Linux:

```bash
MALLOC_CHECK_=2      # Abort on heap corruption
MALLOC_PERTURB_=153  # Fill freed memory with pattern (detects use-after-free)
```

### macOS Malloc Debugging

Set by test targets on macOS:
```bash
MallocScribble=1     # Fill freed memory with 0x55
MallocPreScribble=1  # Fill allocated memory with 0xAA
```

## Comparison: When to Use What

| Tool | Detects | Overhead | Best for |
|------|---------|----------|----------|
| ASAN | Buffer overflow, use-after-free, double-free, leaks | ~2x slowdown | Development builds, CI |
| UBSAN | Integer overflow, null deref, type punning | Minimal | Always-on in debug |
| Valgrind memcheck | Leaks, uninitialized reads, invalid access | ~20x slowdown | Deep investigation |
| `MALLOC_CHECK_` | Heap corruption | Minimal | Quick sanity check |

**Recommendation:** Use ASAN for daily development (fast, catches most issues). Use Valgrind when ASAN misses something or for leak analysis.

## Callgrind (Performance)

Not a memory tool, but often used alongside:

```bash
# Run performance tests with callgrind
make perfcheck

# Individual test with callgrind
make CppunitTest_sw_core VALGRIND=callgrind
```

Callgrind options used:
- `--dump-instr=yes`
- `--instr-atstart=no` (start instrumentation manually)
- `--simulate-cache=yes`
- `--collect-bus=yes`
- `--branch-sim=yes`

Analyze results with `kcachegrind`.
