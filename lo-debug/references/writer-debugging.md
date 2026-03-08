# Writer-Specific Debugging

## Layout Dump (F12 / Shift-F12)

In `DBG_UTIL` builds, with `SW_DEBUG=1` environment variable:

```bash
SW_DEBUG=1 ./instdir/program/soffice
```

Then in Writer:
- **F12** — Dumps layout to `layout.xml` in current directory
- **Shift-F12** — Dumps document node tree to `nodes.xml`

These XML files show the internal structure and are invaluable for debugging layout issues.

### Using Layout Dump in Tests

```cpp
CPPUNIT_TEST_FIXTURE(Test, testMyLayout)
{
    createSwDoc("test.odt");

    xmlDocUniquePtr pLayout = parseLayoutDump();

    // Assert page count
    assertXPath(pLayout, "//page", 2);

    // Assert text content in specific frame
    assertXPath(pLayout, "//page[1]//body/txt[1]", "text", "Hello");

    // Assert position
    assertXPath(pLayout, "//page[1]//body/txt[1]/infos/bounds", "top", "284");
}
```

## Debug Output Functions

**Header:** `sw/inc/dbgoutsw.hxx`
**Implementation:** `sw/source/core/doc/dbgoutsw.cxx`

GDB-callable functions for inspecting Writer internals:

```gdb
# In GDB, call these to inspect objects
call dbg_out(pNode)          # SwNode
call dbg_out(*pTextAttr)     # SwTextAttr
call dbg_out(rPaM)           # SwPaM (cursor range)
call dbg_out(*pItem)         # SfxPoolItem
call dbg_out(rPos)           # SwPosition
call dbg_out(*pNumRule)      # SwNumRule
call dbg_out(*pUndo)         # SwUndo
```

**Available functions:**

| Function | Type | Shows |
|----------|------|-------|
| `dbg_out(SwNode&)` | Node | Node type, index, text content |
| `dbg_out(SwTextAttr&)` | Text attribute | Attribute type, range, value |
| `dbg_out(SfxPoolItem&)` | Item | Item type and value |
| `dbg_out(SwPosition&)` | Position | Node index, content index |
| `dbg_out(SwPaM&)` | Cursor | Start/end positions |
| `dbg_out(SwNodeNum&)` | Numbering | Number rule and level |
| `dbg_out(SwNumRule&)` | Number rule | Format, levels |
| `dbg_out(SwUndo&)` | Undo | Undo type, description |

## Layout Protocol

**Header:** `sw/source/core/inc/dbg_lay.hxx`

In `DBG_UTIL` builds, records frame layout operations:

```cpp
// Macro usage (active only in DBG_UTIL)
PROTOCOL(pFrame, PROT::MakeAll, DbgAction::Start, nullptr)
PROTOCOL_ENTER(pFrame, PROT::MakeAll, DbgAction::Start, nullptr)
```

**Protocol flags (`PROT`):**

| Flag | Records |
|------|---------|
| `PROT::FileInit` | File initialization |
| `PROT::MakeAll` | Frame formatting |
| `PROT::MoveFwd` | Forward movement |
| `PROT::MoveBack` | Backward movement |
| `PROT::Grow` | Frame growing |
| `PROT::Shrink` | Frame shrinking |
| `PROT::Section` | Section handling |
| `PROT::Leaf` | Leaf (page) operations |

## Writer-Specific Environment Variables

| Variable | Purpose |
|----------|---------|
| `SW_DEBUG=1` | Enable F12/Shift-F12 layout/node dumps |
| `SW_DEBUG_WRITERFILTER=1` | Enable WriterFilter debug output (dbgutil) |
| `SW_DEBUG_HTML_PASTE_TO=<file>` | Dump HTML paste input to file |
| `SW_DEBUG_RTF_PASTE_TO=<file>` | Dump RTF paste output to file |
| `SW_DEBUG_RTF_PASTE_FROM=<file>` | Read RTF paste from file (replay) |
| `SW_DEBUG_MAILMERGE_DOCS=<path>` | Save mail merge intermediate documents |

## Writer Test Helpers

From `SwModelTestBase` (used in `sw/qa/extras/`):

```cpp
// Get paragraph by 1-based index, optionally check text
uno::Reference<text::XTextRange> para = getParagraph(2, "Expected text");

// Get shape by 1-based index
uno::Reference<drawing::XShape> shape = getShape(1);

// Get property from UNO object
bool isLandscape = getProperty<bool>(xStyle, "IsLandscape");
sal_Int32 width = getProperty<sal_Int32>(xStyle, "Width");

// Get style families
auto xStyles = getStyles("PageStyles");
auto xStyle = xStyles->getByName("Standard");

// Parse exported file for XPath checks
save("writer8");  // or "Office Open XML Text"
xmlDocUniquePtr pXml = parseExport("content.xml");
assertXPath(pXml, "//text:p", 5);  // 5 paragraphs
assertXPath(pXml, "//text:p[1]", "text-style-name", "Standard");

// Parse layout dump
xmlDocUniquePtr pLayout = parseLayoutDump();
assertXPath(pLayout, "//page", 2);
```

## UNO Object Inspection

### Development Tools (Built-in)

LibreOffice includes built-in UNO object inspector:

**Location:** `include/sfx2/devtools/`

Access via **View > Development Tools** in the UI. Features:
- Inspect any UNO object's properties, methods, interfaces
- Navigate object hierarchies
- View component context

### Xray Tool (Basic Macro)

For interactive UNO exploration via Basic:

```basic
' In Basic IDE (Tools > Macros > Edit)
GlobalScope.BasicLibraries.LoadLibrary("XrayTool")

' Inspect the document
xray ThisComponent

' Inspect a specific object
xray ThisComponent.StyleFamilies.PageStyles.getByName("Default Style")
```

Install from: Download `XrayTool52_en.sxw`, open in Writer, click Install.
