# Test Debugging Reference

## CppUnit Tests

### Running Tests

```bash
# Run a full test suite
make CppunitTest_sw_rtfexport6

# Run a single test method
CPPUNIT_TEST_NAME="testTdf91074" make CppunitTest_sw_rtfexport6

# Multiple test methods (space-separated)
CPPUNIT_TEST_NAME="testTdf91074 testTdf120754" make CppunitTest_sw_rtfexport6

# Suppress make output for cleaner test output
CPPUNIT_TEST_NAME="testTdf91074" make -sr CppunitTest_sw_rtfexport6
```

**How CPPUNIT_TEST_NAME works:** The `cppunittester` (`sal/cppunittester/cppunittester.cxx`) uses suffix matching — `"testFoo"` matches any test whose full name ends with `testFoo`.

### Debugging with GDB

```bash
# Interactive GDB session
make CppunitTest_sw_rtfexport6 CPPUNITTRACE="gdb --args"

# Combined: single test under GDB
make CppunitTest_sw_rtfexport6 CPPUNITTRACE="gdb --args" CPPUNIT_TEST_NAME="testTdf91074"

# With LLDB instead
make CppunitTest_sw_rtfexport6 CPPUNITTRACE="lldb --"
```

GDB is launched with:
- `-return-child-result` — return child's exit code
- `add-auto-load-safe-path $(INSTDIR)` — load pretty printers
- `MALLOC_CHECK_=2`, `MALLOC_PERTURB_=153` — memory debug flags (Linux)

### Exception Tracing

```bash
# Catch all C++ exceptions, log backtraces
make CppunitTest_sw_rtfexport6 DEBUGCPPUNIT=TRUE
```

Uses `solenv/bin/gdbtrycatchtrace-stdout` — catches throw/catch events and prints backtraces to stdout.

### Record and Replay

```bash
# Record with rr
make CppunitTest_sw_rtfexport6 RR=1

# Replay later
rr replay
```

[rr](https://rr-project.org/) records execution deterministically, allowing backward stepping and replay.

### Memory Checking

```bash
# Valgrind memcheck
make CppunitTest_sw_rtfexport6 VALGRIND=memcheck

# Valgrind with GDB server
make CppunitTest_sw_rtfexport6 VALGRIND=memcheck VALGRIND_GDB=1
```

Valgrind memcheck runs with:
- `--num-callers=50` — deep backtraces
- `--error-exitcode=1` — fail on errors
- `G_SLICE=always-malloc`, `GLIBCXX_FORCE_NEW=1` — disable allocator caches

### Environment Variables Summary

| Variable | Value | Effect |
|----------|-------|--------|
| `CPPUNIT_TEST_NAME` | `"testName"` | Run only matching test methods |
| `CPPUNITTRACE` | `"gdb --args"` | Run under specified debugger |
| `DEBUGCPPUNIT` | `TRUE` | Exception tracing via GDB script |
| `VALGRIND` | `memcheck` | Run under Valgrind memcheck |
| `VALGRIND_GDB` | `1` | Enable Valgrind GDB server |
| `RR` | `1` | Record with rr |

## UI Tests

### Running UI Tests

```bash
# Run a UI test suite
make UITest_sw_writer_tests

# Run specific test (by Python method name)
make UITest_sw_writer_tests UITEST_TEST_NAME="testTdf12345"
```

### Debugging UI Tests

```bash
# GDB for soffice.bin crashes
make UITest_sw_writer_tests UITESTTRACE=1

# Connect to already-running LibreOffice (interactive debugging)
make UITest_sw_writer_tests gb_UITest_DEBUGRUN=1
```

`UITESTTRACE=1` adds `--gdb` flag which launches GDB when soffice.bin crashes during the test.

`gb_UITest_DEBUGRUN=1` connects to an existing running LO instance instead of launching a new one — useful for stepping through UI code interactively.

## Python Tests

### Running and Debugging

```bash
# Run Python test
make PythonTest_connectivity

# Single test method
make PythonTest_connectivity PYTHON_TEST_NAME="testXYZ"

# Under GDB
make PythonTest_connectivity CPPUNITTRACE="gdb --args"

# With Valgrind
make PythonTest_connectivity VALGRIND=memcheck
```

## Test Categories and Make Targets

| Target | Description | Speed |
|--------|-------------|-------|
| `make check` | All tests (unit + slow + subsequent) | Slow |
| `make unitcheck` | Unit tests only | Fast |
| `make slowcheck` | Slow unit tests | Medium |
| `make subsequentcheck` | System/integration tests | Slow |
| `make perfcheck` | Performance tests (callgrind) | Very slow |
| `make screenshot` | Screenshot generation tests | Medium |
| `make CppunitTest_*` | Single CppUnit test | Fast |
| `make UITest_*` | Single UI test | Medium |
| `make PythonTest_*` | Single Python test | Medium |

## Writing Testable Code

### CppUnit Test Structure

```cpp
#include <cppunit/TestFixture.h>
#include <cppunit/extensions/HelperMacros.h>
#include <cppunit/plugin/TestPlugIn.h>

class MyTest : public CppUnit::TestFixture {
public:
    void testSomething();

    CPPUNIT_TEST_SUITE(MyTest);
    CPPUNIT_TEST(testSomething);
    CPPUNIT_TEST_SUITE_END();
};

void MyTest::testSomething()
{
    CPPUNIT_ASSERT_EQUAL(42, computeValue());
    CPPUNIT_ASSERT(condition);
    CPPUNIT_ASSERT_MESSAGE("failed because...", condition);
}

CPPUNIT_TEST_SUITE_REGISTRATION(MyTest);
CPPUNIT_PLUGIN_IMPLEMENT();
```

### Writer Filter Test Pattern

```cpp
CPPUNIT_TEST_FIXTURE(Test, testTdf91074)
{
    // Load test document
    createSwDoc("tdf91074.docx");

    // Assert document model via UNO
    uno::Reference<beans::XPropertySet> xStyle(
        getStyles("PageStyles")->getByName("Standard"), uno::UNO_QUERY);
    CPPUNIT_ASSERT_EQUAL(true, getProperty<bool>(xStyle, "IsLandscape"));

    // Or assert layout via XPath
    xmlDocUniquePtr pLayout = parseLayoutDump();
    assertXPath(pLayout, "//page", 2);

    // Or assert exported XML
    save("writer8");
    xmlDocUniquePtr pXml = parseExport("content.xml");
    assertXPath(pXml, "//text:p", "text-style-name", "Standard");
}
```

### Key Assertion Macros

| Macro | Purpose |
|-------|---------|
| `CPPUNIT_ASSERT(cond)` | Assert condition is true |
| `CPPUNIT_ASSERT_EQUAL(expected, actual)` | Assert equality (prints both values on failure) |
| `CPPUNIT_ASSERT_EQUAL_MESSAGE(msg, expected, actual)` | With custom message |
| `CPPUNIT_ASSERT_MESSAGE(msg, cond)` | Assert with custom message |
| `CPPUNIT_ASSERT_DOUBLES_EQUAL(expected, actual, delta)` | Float comparison |
| `CPPUNIT_ASSERT_THROW(expr, ExceptionType)` | Assert exception is thrown |

**Tip:** Prefer `CPPUNIT_ASSERT_EQUAL` over `CPPUNIT_ASSERT` for comparisons — it prints both expected and actual values on failure.

**Tip:** For `sal_Bool` returns from UNO, cast to `bool` before comparing:
```cpp
CPPUNIT_ASSERT_EQUAL(true, static_cast<bool>(xProp->getPropertyValue("IsLandscape")));
```
