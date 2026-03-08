# Profiling Reference

## Chrome Trace Events

**Header:** `include/comphelper/traceevent.hxx`
**ProfileZone:** `include/comphelper/profilezone.hxx`

LibreOffice can generate Chrome DevTools-compatible trace events for performance analysis.

### Enabling Trace Recording

**Via environment variable (DBG_UTIL builds only):**
```bash
export TRACE_EVENT_RECORDING=1
./instdir/program/soffice
```

**Via UNO API (programmatically):**
```cpp
#include <comphelper/traceevent.hxx>

comphelper::TraceEvent::startRecording();
// ... do work ...
OUString json = comphelper::TraceEvent::getRecordingAndClear();
comphelper::TraceEvent::stopRecording();
```

### ProfileZone — Scope-Based Profiling

```cpp
#include <comphelper/profilezone.hxx>

void MyFunction()
{
    comphelper::ProfileZone zone("MyFunction");
    // Everything in this scope is measured
    // Duration recorded when zone goes out of scope
}
```

ProfileZone features:
- Scope-based (RAII) — automatically records on destruction
- Nesting-aware with validation
- Outputs Chrome trace format `X` (complete) events
- Zero overhead when recording is disabled (`s_bRecording` is static)

### Instant Events

```cpp
#include <comphelper/traceevent.hxx>

// Mark a point in time
comphelper::TraceEvent::addInstantEvent("DocumentLoaded");
```

### Analyzing Trace Output

The JSON output is in Chromium Trace Event Format. To view:

1. Save JSON to a file
2. Open Chrome/Chromium
3. Navigate to `chrome://tracing`
4. Load the JSON file

The trace shows a timeline with nested function calls, durations, and thread information.

## Callgrind Integration

**Header:** `include/test/callgrind.hxx`
**Implementation:** `test/source/callgrind.cxx`

For fine-grained CPU profiling of specific code sections.

### In Test Code

```cpp
#include <test/callgrind.hxx>

void MyTest::testPerformance()
{
    // Start profiling
    callgrindStart();

    // Code to profile
    doExpensiveOperation();

    // Stop and dump stats
    callgrindDump("expensive_operation");
}
```

### Via Make

```bash
# Run all performance tests
make perfcheck

# Single test with callgrind
make CppunitTest_sw_core VALGRIND=callgrind
```

Callgrind options:
```
--tool=callgrind
--dump-instr=yes          # Instruction-level profiling
--instr-atstart=no        # Don't profile startup
--simulate-cache=yes      # Cache simulation
--collect-bus=yes         # Bus event counting
--branch-sim=yes          # Branch prediction simulation
```

### Analyzing Callgrind Output

```bash
# View with KCachegrind (GUI)
kcachegrind callgrind.out.<pid>

# Or command-line summary
callgrind_annotate callgrind.out.<pid>
```

## perf (Linux)

For system-level profiling:

```bash
# Record
perf record -g ./instdir/program/soffice --norestore document.odt

# Report
perf report

# Flame graph
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg
```

### With Tests

```bash
# Profile a specific test
perf record -g make CppunitTest_sw_core CPPUNIT_TEST_NAME="testPerf"
perf report
```

## Comparison

| Tool | Type | Granularity | Overhead | Output |
|------|------|-------------|----------|--------|
| ProfileZone / TraceEvent | Instrumented | Function-level | Low (when recording) | Chrome trace JSON |
| Callgrind | Simulation | Instruction-level | ~50x | KCachegrind format |
| perf | Sampling | System-wide | Low | perf.data |

**Recommendations:**
- **ProfileZone** for understanding high-level flow and finding which phase is slow
- **Callgrind** for precise CPU cycle counting and cache analysis
- **perf** for production-like profiling with minimal overhead
