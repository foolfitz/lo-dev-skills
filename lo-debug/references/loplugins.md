# Loplugins — Clang Compiler Plugin System

**Location:** `compilerplugins/`
**Documentation:** `compilerplugins/README.md`

## Overview

Loplugins are Clang-based compiler plugins that catch bugs and enforce coding standards at compile time. They run automatically during compilation when enabled.

## Enabling

```bash
# Automatically enabled with dbgutil (if Clang headers available)
./configure --enable-dbgutil

# Explicit enablement
./configure --enable-compiler-plugins

# Requires Clang 18.1.8+ headers
```

## Two Types of Plugins

### 1. Compile Checks (Automatic)

Run during normal compilation, emit warnings with `[loplugin:name]` prefix:

```
sw/source/core/doc/docnew.cxx:234: error: [loplugin:includeform] ...
```

**Key compile check plugins:**

| Plugin | Catches |
|--------|---------|
| `includeform` | Wrong `#include` form (`""` vs `<>`) |
| `sallogareas` | Invalid SAL_LOG area names (not in log-areas.dox) |
| `unusedvariablemore` | Extended unused variable detection |
| `deadcode` | Unreachable code paths |
| `unreffun` | Unreferenced functions |
| `redundantcast` | Unnecessary casts |
| `simplifybool` | Boolean expression simplification |
| `nullptr` | Using `0` or `NULL` instead of `nullptr` |
| `passstuffbyref` | Pass-by-value when pass-by-ref is better |
| `stringconstant` | String literal improvements |
| `cppunitassertequals` | Should use `CPPUNIT_ASSERT_EQUAL` instead of `CPPUNIT_ASSERT` |

### 2. Rewriters (Manual)

Code refactoring tools invoked explicitly:

```bash
# Run a specific rewriter on all code
make COMPILER_PLUGIN_TOOL=removenullpointers FORCE_COMPILE=all UPDATE_FILES=all

# Warnings-only mode (dry run)
make COMPILER_PLUGIN_WARNINGS_ONLY=X

# Rewrite specific module only
make sw.build COMPILER_PLUGIN_TOOL=removenullpointers FORCE_COMPILE=sw UPDATE_FILES=all
```

## Common Plugin Warnings and Fixes

### includeform

```
error: [loplugin:includeform] use "" not <> for include of sal/config.h
```

**Rule:** Use `""` only when the included file is in the same directory. Use `<>` for everything else (including UNO headers).

### sallogareas

```
error: [loplugin:sallogareas] unknown log area "sw.myarea"
```

**Fix:** Add the area to `include/sal/log-areas.dox`:
```
@li @c sw.myarea
```

### cppunitassertequals

```
warning: [loplugin:cppunitassertequals] rather use CPPUNIT_ASSERT_EQUAL
```

**Fix:** Change `CPPUNIT_ASSERT(a == b)` to `CPPUNIT_ASSERT_EQUAL(a, b)`.

## Creating Custom Plugins

Plugins live in `compilerplugins/clang/`:

1. Create `compilerplugins/clang/myplugin.cxx`
2. Inherit from `loplugin::FilteringPlugin<MyPlugin>` or `loplugin::FilteringRewritePlugin<MyPlugin>`
3. Override `VisitFunctionDecl`, `VisitCallExpr`, etc. (Clang AST visitors)
4. Register with `loplugin::Plugin::Registration<MyPlugin> myplugin("myplugin");`

The plugin is automatically compiled and loaded — no build system changes needed.

## Disabling Plugins

```bash
# Disable all plugins for a build
./configure --disable-compiler-plugins

# Disable specific plugin warnings in code (rare, avoid if possible)
// SAL_LOPLUGIN_ANNOTATE("noclippy:pluginname")
```

## Interaction with Sanitizers

Compiler plugins are **automatically disabled** when sanitizer flags (`-fsanitize=*`) are detected in CC/CXX. This avoids conflicts between plugin instrumentation and sanitizer instrumentation.
