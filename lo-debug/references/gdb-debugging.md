# GDB Debugging Reference

## make debugrun

Launches LibreOffice under GDB with proper environment setup.

```bash
make debugrun
```

**What it does** (defined in `solenv/gbuild/platform/unxgcc.mk`):
1. Sources `instdir/program/ooenv` for environment variables
2. Launches `gdb instdir/program/soffice.bin`
3. Sets arguments: `--norestore --nologo --accept=pipe,name=$USER;urp;`
4. Adds auto-load safe path for LO pretty printers
5. Sets `MALLOC_CHECK_=2` and `MALLOC_PERTURB_=153` for memory debugging

### GDB Session Tips

```gdb
# Set breakpoint on a specific function
break SwDoc::SetTextFormatColl

# Break on all C++ exceptions
catch throw

# Break on specific exception type
catch throw css::uno::RuntimeException

# Print UNO string (with pretty printer)
print aString

# Backtrace all threads
thread apply all bt

# Continue after breakpoint
continue
```

## GDB Pretty Printers

**Location:** `solenv/gdb/libreoffice/`

LibreOffice provides GDB pretty printers for common types:

| Module | File | Types |
|--------|------|-------|
| SAL | `sal.py` | `OUString`, `OString`, `sal_Bool` |
| CPPU | `cppu.py` | `css::uno::Reference`, `css::uno::Any`, `css::uno::Sequence` |
| Tools | `tl.py` | `Color`, `Rectangle`, `BigInt` |
| basegfx | `basegfx.py` | `B2DPoint`, `B2DVector`, `B2DRange` |
| VCL | `vcl.py` | VCL types |
| Writer | `sw.py` | Writer-specific types |
| SVL | `svl.py` | SVL types |

### Installing Pretty Printers

```bash
# Install to INSTDIR (auto-loaded by make debugrun)
./solenv/bin/install-gdb-printers -i ./instdir -a ./instdir
```

The `make debugrun` command automatically sets `add-auto-load-safe-path` to load these.

### Manual GDB Configuration

If not using `make debugrun`, add to `~/.gdbinit`:

```gdb
add-auto-load-safe-path /path/to/LO-core/instdir
```

## Core Dump Analysis

**Script:** `solenv/bin/gdb-core-bt.sh`

```bash
# Analyze core dump
solenv/bin/gdb-core-bt.sh /path/to/soffice.bin /core/directory $exit_code
```

The script:
1. Finds core files in the given directory
2. Uses `coredumpctl` on systemd systems
3. Generates full backtraces with `thread apply all backtrace full`
4. Outputs register info

### Enabling Core Dumps

```bash
ulimit -c unlimited
./instdir/program/soffice
# Core file generated on crash
```

## Exception Tracing

**Script:** `solenv/bin/gdbtrycatchtrace-stdout`

Catches all C++ throw/catch and logs backtraces:

```bash
# Automatic (for tests)
make CppunitTest_sw_core DEBUGCPPUNIT=TRUE

# Manual
gdb -nx --batch --command=solenv/bin/gdbtrycatchtrace-stdout ./instdir/program/soffice.bin
```

The script sets:
```gdb
set pagination off
catch throw
catch catch
run
bt
quit
```

Output goes to stdout (or `gdbtrace.log` for the non-stdout variant).

## Signal Handling

**Implementation:** `sal/osl/unx/signal.cxx`

LibreOffice installs custom signal handlers for:

| Signal | Default Action | Purpose |
|--------|---------------|---------|
| `SIGSEGV` | Abort + backtrace | Segmentation fault |
| `SIGBUS` | Abort + backtrace | Bus error |
| `SIGABRT` | Abort + backtrace | Abort signal |
| `SIGFPE` | Abort + backtrace | Floating point exception |
| `SIGILL` | Abort + backtrace | Illegal instruction |
| `SIGTRAP` | Abort + backtrace | Trap (breakpoint) |

The signal handler generates a backtrace of up to 256 frames using `osl::detail::backtraceAsString()`.

## Backtrace API

**Header:** `include/sal/backtrace.hxx`

```cpp
#include <sal/backtrace.hxx>

// Capture backtrace (returns unique_ptr<BacktraceState>)
auto bt = sal::backtrace_get(20);  // max 20 frames

// Convert to readable string
OUString trace = sal::backtrace_to_string(bt.get());
SAL_DEBUG("Stack: " << trace);
```

## Debugger Detection

**Header:** `include/comphelper/debuggerinfo.hxx`

```cpp
#include <comphelper/debuggerinfo.hxx>

if (comphelper::isDebuggerAttached()) {
    // Slow path OK — debugger is watching
}
```

Supported platforms:
- **Windows:** `IsDebuggerPresent()`
- **macOS:** `sysctl` with `P_TRACED` flag
- **Linux:** reads `/proc/self/status` for `TracerPid`

Only available in `DBG_UTIL` builds.
