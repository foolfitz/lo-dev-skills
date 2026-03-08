# lo-dev-skills

[Claude Code](https://claude.ai/code) skills for LibreOffice core development.

These skills give Claude Code domain-specific knowledge about LibreOffice's build system, UNO component model, debugging infrastructure, and development conventions — enabling it to assist with LO development tasks accurately and efficiently.

## Skills

### lo-uno-api

Guide for developing UNO APIs in LibreOffice.

Covers the full lifecycle: writing IDL files, registering in the build system, implementing in C++, registering services, and building. Includes real examples extracted from the LO source tree.

**Triggers on:** Creating/modifying UNO IDL interfaces, structs, enums, services, or listeners in `offapi/`. Implementing UNO services in C++. Working with `.component` XML or `gb_UnoApi` build rules.

**Reference docs:**

| File | Content |
|------|---------|
| `references/idl-syntax.md` | IDL syntax for interfaces, structs, enums, services, listeners |
| `references/cpp-implementation.md` | C++ patterns: WeakImplHelper, VCL-backed, listener multiplexer, dispose |
| `references/build-registration.md` | `UnoApi_offapi.mk` macros, `.component` XML, `Library_*.mk` |
| `references/common-base-interfaces.md` | Quick reference for XInterface, XServiceInfo, XComponent, etc. |

**Scripts:**

| Script | Purpose |
|--------|---------|
| `scripts/gen_idl.py` | Generate IDL template files with correct license header and module nesting |
| `scripts/check_build_registration.py` | Verify IDL is registered in `UnoApi_offapi.mk` with the correct macro |
| `scripts/validate_component.py` | Validate `.component` XML for naming consistency |

### lo-debug

Guide for debugging LibreOffice development.

Covers logging (SAL_LOG), GDB integration, test debugging, memory tools, profiling, compiler plugins, and Writer-specific debugging facilities.

**Triggers on:** Diagnosing crashes, adding logging, running tests under GDB/Valgrind/rr, profiling performance, analyzing core dumps, or working with SAL_LOG, loplugins, or sanitizers.

**Reference docs:**

| File | Content |
|------|---------|
| `references/logging.md` | SAL_INFO/SAL_WARN macros, SAL_LOG env var syntax, exception logging |
| `references/gdb-debugging.md` | `make debugrun`, pretty printers, core dumps, backtrace API |
| `references/test-debugging.md` | CppUnit/UITest/PythonTest under GDB, Valgrind, rr |
| `references/memory-tools.md` | AddressSanitizer, UBSan, Valgrind memcheck |
| `references/profiling.md` | Chrome trace events, ProfileZone, callgrind, perf |
| `references/loplugins.md` | Clang compiler plugin system and common checks |
| `references/writer-debugging.md` | Layout dumps (F12), `dbg_out()` functions, Writer env vars |

**Scripts:**

| Script | Purpose |
|--------|---------|
| `scripts/find_log_areas.py` | Search, list, and validate SAL_LOG areas across modules |
| `scripts/parse_sal_log.py` | Parse and filter SAL_LOG output by area, level, or file |

## Installation

### Claude Code

Add the skill directories to your Claude Code settings (`.claude/settings.json`):

```json
{
  "skills": [
    "/path/to/lo-dev-skills/lo-uno-api",
    "/path/to/lo-dev-skills/lo-debug"
  ]
}
```

Or install per-project by adding to `.claude/settings.local.json` in your LO-core checkout.

### Standalone Scripts

The scripts under each skill's `scripts/` directory work standalone with Python 3.11+ and no external dependencies. They auto-detect the LO source root or accept `--lo-root`:

```bash
# Generate an IDL template
python lo-uno-api/scripts/gen_idl.py --type interface --module com.sun.star.awt --name XMyWidget

# Check if an IDL is registered in the build
python lo-uno-api/scripts/check_build_registration.py --idl-path com/sun/star/awt/Toolkit.idl

# List log areas used in a module
python lo-debug/scripts/find_log_areas.py --module sw

# Filter SAL_LOG output
SAL_LOG="+INFO.sw" ./instdir/program/soffice 2>&1 | python lo-debug/scripts/parse_sal_log.py --area sw.core
```

## Compatibility

- Developed against LibreOffice core (master branch, 2026)
- Scripts require Python 3.11+ (stdlib only, no pip dependencies)
- Reference material is based on LO's gbuild system, UNO IDL compiler, and SAL logging framework — these have been stable across many LO versions

## License

MPL-2.0 — same as LibreOffice.
