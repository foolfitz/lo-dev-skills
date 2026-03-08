# Logging Framework Reference

## SAL_LOG — The Primary Logging System

**Header:** `include/sal/log.hxx`
**Implementation:** `sal/osl/all/log.cxx`

### Logging Macros

| Macro | Purpose | Persists in code? |
|-------|---------|-------------------|
| `SAL_INFO(area, stream)` | Info-level log | Yes |
| `SAL_INFO_IF(cond, area, stream)` | Conditional info | Yes |
| `SAL_WARN(area, stream)` | Warning-level log | Yes |
| `SAL_WARN_IF(cond, area, stream)` | Conditional warning | Yes |
| `SAL_DEBUG(stream)` | Temporary debug output | **No — never commit** |
| `SAL_DEBUG_IF(cond, stream)` | Conditional debug | **No — never commit** |
| `SAL_DEBUG_BACKTRACE(stream, depth)` | Debug with stack trace | **No — never commit** |

### Usage

```cpp
#include <sal/log.hxx>

// Info messages — for tracing normal operation
SAL_INFO("sw.core", "Loading document: " << sURL);
SAL_INFO("sw.filter.md", "Parsing heading level " << nLevel);

// Warnings — for unexpected but handled conditions
SAL_WARN("sw.core", "Node not found: " << nNodeIdx);
SAL_WARN_IF(pNode == nullptr, "sw.core", "Null node at index " << i);

// Temporary debug — NEVER commit this
SAL_DEBUG("value = " << value);
SAL_DEBUG_BACKTRACE("reached here", 10);  // 10 frames deep
```

### Log Area Naming Convention

Areas use dot-separated segments matching `[0-9a-z]+`:

```
<module>.<submodule>.<detail>
```

Examples: `sw.core`, `sw.filter.md`, `vcl.gdi`, `toolkit.awt`, `sc.core`

**Important:** New areas must be registered in `include/sal/log-areas.dox`. The `sallogareas` loplugin enforces this at compile time.

### Runtime Control via SAL_LOG

```bash
# Default (unset) — warnings only
export SAL_LOG="+WARN"

# All info and warnings for a specific area
export SAL_LOG="+INFO.sw.core+WARN"

# Everything from sw, but not sw.filter
export SAL_LOG="+INFO.sw-INFO.sw.filter"

# All messages with timestamps
export SAL_LOG="+INFO+WARN+TIMESTAMP"

# All messages with relative timer (seconds since start)
export SAL_LOG="+INFO+WARN+RELATIVETIMER"

# Make matching messages fatal (abort)
export SAL_LOG="+FATAL+WARN.sw.core"

# Redirect to file (appends PID if path ends with -)
export SAL_LOG_FILE=/tmp/lo-debug.log-

# Use syslog
export SAL_LOG_SYSLOG=1
```

**Matching rules:**
- `+INFO.sw` matches `SAL_INFO("sw", ...)`, `SAL_INFO("sw.core", ...)`, etc.
- `-INFO.sw.filter` excludes `sw.filter` and its children
- Longest matching prefix wins
- If both `+` and `-` match at same length, `+` wins

### Compile-Time Control

The macros `SAL_LOG_INFO` and `SAL_LOG_WARN` must be defined at compile time to enable the respective log levels. Debug builds (`--enable-debug`) define both.

In release builds, `SAL_INFO` and `SAL_WARN` calls compile to no-ops unless explicitly enabled.

### Output Format

```
<timestamp> <level>:<area>:<PID>:<TID>:<file>:<line>: <message>
```

Example:
```
warn:sw.core:12345:7f8a:sw/source/core/doc/docnew.cxx:234: Node not found: 42
```

## Exception Logging

**Header:** `include/comphelper/diagnose_ex.hxx`

### DBG_UNHANDLED_EXCEPTION

Reports a caught UNO exception. Must be called as the **first thing** in a catch block:

```cpp
try {
    doSomething();
} catch (const css::uno::Exception&) {
    DBG_UNHANDLED_EXCEPTION("sw.core");
    // or with explanatory message:
    DBG_UNHANDLED_EXCEPTION("sw.core", "while loading document");
}
```

### TOOLS_WARN_EXCEPTION / TOOLS_INFO_EXCEPTION

Log exception with a custom message:

```cpp
try {
    doSomething();
} catch (const css::uno::Exception&) {
    TOOLS_WARN_EXCEPTION("sw.core", "Failed to process node");
    // Output: "Failed to process node com.sun.star.uno.RuntimeException: ..."
}
```

### exceptionToString

Convert exception to loggable string:

```cpp
try {
    doSomething();
} catch (const css::uno::Exception&) {
    css::uno::Any ex(cppu::getCaughtException());
    SAL_WARN("sw.core", "Error: " << exceptionToString(ex));
}
```

### ENSURE_OR_THROW / ENSURE_OR_RETURN

Assert-and-throw/return macros:

```cpp
// Assert + throw IllegalArgumentException
ENSURE_ARG_OR_THROW(pNode != nullptr, "node must not be null");

// Assert + throw RuntimeException
ENSURE_OR_THROW(bInitialized, "not initialized");

// Assert + return value
ENSURE_OR_RETURN(pDoc != nullptr, "no document", false);
ENSURE_OR_RETURN_FALSE(pDoc != nullptr, "no document");
ENSURE_OR_RETURN_VOID(pDoc != nullptr, "no document");
```

## Legacy Assertion Macros

**Header:** `include/osl/diagnose.h` — **Deprecated, use SAL_WARN instead**

| Macro | Maps to | Purpose |
|-------|---------|---------|
| `OSL_ASSERT(c)` | `SAL_WARN` | Assert condition |
| `OSL_ENSURE(c, msg)` | `SAL_WARN` | Assert with message |
| `OSL_FAIL(msg)` | `SAL_WARN` | Always-fail assertion |
| `OSL_VERIFY(c)` | `OSL_ASSERT` | Assert, always evaluates `c` |

**Header:** `include/tools/debug.hxx`

| Macro | Purpose |
|-------|---------|
| `DBG_ASSERT(c, msg)` | Assert (maps to SAL_WARN) |
| `DBG_TESTSOLARMUTEX()` | Assert SolarMutex is held (dbgutil only) |
| `DBG_TESTNOTSOLARMUTEX()` | Assert SolarMutex is NOT held (dbgutil only) |

## SAL_WHERE and SAL_STREAM Helpers

```cpp
// Create "file:line" string for exception messages
throw css::uno::RuntimeException("error at " SAL_WHERE);

// Create string from stream expression
OUString msg = SAL_STREAM("value=" << n << " state=" << s);
```
