---
name: lo-debug
description: Guide for debugging LibreOffice development. Use when diagnosing crashes, adding logging, running tests under debugger, profiling performance, analyzing core dumps, or working with SAL_LOG, GDB, Valgrind, sanitizers, or loplugins in the LibreOffice codebase.
---

# LibreOffice Debugging Guide

## Overview

LibreOffice has a comprehensive debugging infrastructure. This guide covers:

1. **Logging** — SAL_LOG framework for runtime output
2. **Build modes** — Debug/dbgutil builds with extra checks
3. **GDB integration** — Pretty printers, debugrun, exception tracing
4. **Test debugging** — Running individual tests under GDB/Valgrind/RR
5. **Memory tools** — AddressSanitizer, Valgrind memcheck
6. **Profiling** — Chrome trace events, callgrind, ProfileZone
7. **Loplugins** — Compile-time static analysis
8. **Writer-specific** — Layout dumps, debug output functions

## Decision Tree

| I want to... | Go to |
|--------------|-------|
| Add log output to code | [logging.md](./references/logging.md) |
| Run LO under GDB | [gdb-debugging.md](./references/gdb-debugging.md) |
| Debug a failing test | [test-debugging.md](./references/test-debugging.md) |
| Find a memory leak/corruption | [memory-tools.md](./references/memory-tools.md) |
| Profile slow code | [profiling.md](./references/profiling.md) |
| Catch bugs at compile time | [loplugins.md](./references/loplugins.md) |
| Debug Writer layout/nodes | [writer-debugging.md](./references/writer-debugging.md) |

## Quick Reference

### Build for Debugging

```bash
# Full debug build (debug info + assertions + extra checks)
./autogen.sh  # with --enable-debug --enable-dbgutil in autogen.input
make

# Just debug symbols (no extra checks, ABI compatible)
./autogen.sh  # with --enable-debug only
make
```

Key configure flags:

| Flag | Effect | ABI Compatible? |
|------|--------|-----------------|
| `--enable-debug` | Debug info (`-g`), no optimization, assertions | Yes |
| `--enable-dbgutil` | Extra runtime checks, `DBG_UTIL` defined, object counting | **No** |
| `--enable-assert-always-abort` | `assert()` always aborts (even release) | Yes |
| `--enable-compiler-plugins` | Clang loplugin checks at compile time | Yes |
| `--enable-split-debug` | Split debug symbols to separate files | Yes |

### Run Under Debugger

```bash
# Interactive GDB session
make debugrun

# Run specific test under GDB
make CppunitTest_sw_rtfexport6 CPPUNITTRACE="gdb --args"
```

### Add Logging

```cpp
#include <sal/log.hxx>

SAL_INFO("sw.core", "Processing node: " << nNodeIdx);
SAL_WARN("sw.core", "Unexpected state: " << nState);
SAL_DEBUG("temp debug: " << value);  // temporary, never commit
```

Control at runtime:
```bash
export SAL_LOG="+INFO.sw.core+WARN"
./instdir/program/soffice
```

### Debug a Single Test

```bash
# Run one test method
CPPUNIT_TEST_NAME="testTdf91074" make CppunitTest_sw_rtfexport6

# Under GDB
make CppunitTest_sw_rtfexport6 CPPUNITTRACE="gdb --args" CPPUNIT_TEST_NAME="testTdf91074"

# With exception tracing
make CppunitTest_sw_rtfexport6 DEBUGCPPUNIT=TRUE

# Record/replay with rr
make CppunitTest_sw_rtfexport6 RR=1
```

### Memory Debugging

```bash
# Valgrind memcheck
make CppunitTest_sw_rtfexport6 VALGRIND=memcheck

# Build with AddressSanitizer
CC="gcc -fsanitize=address" CXX="g++ -fsanitize=address" ./configure --enable-debug
```

## Common Pitfalls

1. **SAL_DEBUG left in committed code** — `SAL_DEBUG` is for temporary use only. Use `SAL_INFO` or `SAL_WARN` with a proper area for code that will be committed.

2. **Missing log area in log-areas.dox** — When adding a new SAL_LOG area (e.g., `"sw.md"`), register it in `include/sal/log-areas.dox`. The `sallogareas` loplugin enforces this.

3. **Forgetting SolarMutexGuard in debug checks** — `DBG_TESTSOLARMUTEX()` only works in `DBG_UTIL` builds. Don't rely on it for production assertions.

4. **dbgutil vs debug confusion** — `--enable-debug` only adds debug symbols. `--enable-dbgutil` enables `DBG_UTIL` macro and extra checks but is **ABI incompatible** — don't mix dbgutil and non-dbgutil libraries.

5. **SAL_LOG unset** — Default is `+WARN` (warnings only). Set `SAL_LOG="+INFO.your.area"` explicitly to see info messages.

6. **CPPUNITTRACE with wrong syntax** — Must be `CPPUNITTRACE="gdb --args"` (with `--args`), not just `CPPUNITTRACE=gdb`.

## Reference Index

| File | Content |
|------|---------|
| [references/logging.md](./references/logging.md) | SAL_LOG framework, exception logging, assertion macros |
| [references/gdb-debugging.md](./references/gdb-debugging.md) | GDB pretty printers, debugrun, core dumps |
| [references/test-debugging.md](./references/test-debugging.md) | CppUnit, UITest, PythonTest debugging |
| [references/memory-tools.md](./references/memory-tools.md) | Valgrind, ASAN, UBSAN integration |
| [references/profiling.md](./references/profiling.md) | Trace events, callgrind, ProfileZone |
| [references/loplugins.md](./references/loplugins.md) | Clang compiler plugin system |
| [references/writer-debugging.md](./references/writer-debugging.md) | Writer layout dumps, debug output functions |
