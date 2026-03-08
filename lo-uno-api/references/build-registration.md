# Build System & Service Registration

## UnoApi_offapi.mk — Registering IDL Files

IDL files must be registered in `offapi/UnoApi_offapi.mk` to be compiled. There are three macros:

### gb_UnoApi_add_idlfiles

Generates both `.hpp` and `.hdl` header files.

**Use for:** Interfaces, structs, enums — any type that needs to be used in C++ code.

```makefile
$(eval $(call gb_UnoApi_add_idlfiles,offapi,com/sun/star/awt,\
	GradientStyle \
	PaintEvent \
	XGraphics2 \
	XPaintListener \
))
```

**What it generates:**
- `com/sun/star/awt/XGraphics2.hpp` — Full C++ type definition
- `com/sun/star/awt/XGraphics2.hdl` — Forward declaration header

### gb_UnoApi_add_idlfiles_nohdl

Generates only `.hpp` (no `.hdl`).

**Use for:** Services — they don't need forward declarations.

```makefile
$(eval $(call gb_UnoApi_add_idlfiles_nohdl,offapi,com/sun/star/awt,\
	AsyncCallback \
	Toolkit \
))
```

### gb_UnoApi_add_idlfiles_noheader

Generates no headers at all.

**Use for:** Types only referenced by other IDL files, never directly used in C++.

### Ordering Rules

Within each `gb_UnoApi_add_idlfiles*` block for a given module, entries must be in **alphabetical order**:

```makefile
$(eval $(call gb_UnoApi_add_idlfiles,offapi,com/sun/star/awt,\
	ActionEvent \
	AdjustmentEvent \
	DeviceCapability \
	...
	XWindowListener \
))
```

### Adding a New IDL

1. Determine the correct macro (see table above)
2. Find the block for your module (e.g., `com/sun/star/awt`)
3. Add your type name in alphabetical order
4. If no block exists for your module, create one following the pattern

## .component XML — Service Registration {#component-xml}

Each module that provides UNO services has a `.component` file (e.g., `toolkit/util/tk.component`).

### XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component loader="com.sun.star.loader.SharedLibrary" environment="@CPPU_ENV@"
    xmlns="http://openoffice.org/2010/uno-components">
  <implementation name="com.sun.star.awt.comp.AsyncCallback"
      constructor="com_sun_star_awt_comp_AsyncCallback_get_implementation">
    <service name="com.sun.star.awt.AsyncCallback"/>
  </implementation>
</component>
```

### Element Reference

| Element/Attribute | Description |
|-------------------|-------------|
| `<implementation name="...">` | Unique implementation name (typically `com.sun.star.module.comp.Name`) |
| `constructor="..."` | Name of the `extern "C"` constructor function in C++ |
| `<service name="...">` | UNO service name that this implementation provides |

### Constructor Naming Convention

The constructor function name is derived from the implementation name:

```
Implementation name:  com.sun.star.awt.comp.AsyncCallback
Constructor function: com_sun_star_awt_comp_AsyncCallback_get_implementation
```

Rule: Replace all `.` with `_`, append `_get_implementation`.

### Multiple Services

An implementation can provide multiple services:

```xml
<implementation name="com.sun.star.comp.embed.HatchWindowFactory"
    constructor="com_sun_star_comp_embed_HatchWindowFactory_get_implementation">
  <service name="com.sun.star.comp.embed.HatchWindowFactory"/>
  <service name="com.sun.star.embed.HatchWindowFactory"/>
</implementation>
```

### Common .component File Locations

| Module | Component file |
|--------|---------------|
| toolkit | `toolkit/util/tk.component` |
| sw (Writer) | `sw/util/sw.component` |
| sc (Calc) | `sc/util/sc.component` |
| sd (Draw/Impress) | `sd/util/sd.component` |
| sfx2 | `sfx2/util/sfx.component` |
| vcl | `vcl/vcl.component` |

## Library_*.mk — Adding C++ Source Files

When you create a new C++ implementation file, you must add it to the module's library build file.

### Example: toolkit

File: `toolkit/Library_tk.mk`

```makefile
$(eval $(call gb_Library_add_exception_objects,tk,\
    toolkit/source/awt/asynccallback \
    toolkit/source/awt/vclxgraphics \
    ...
))
```

**Note:** Path is relative to the repository root, without file extension.

### Incremental Build

After modifying build files:

```bash
# Rebuild just the IDL headers
make offapi

# Rebuild a specific module
make toolkit

# Build without running tests (faster)
make toolkit build-nocheck
```

## Complete Checklist

When adding a new UNO service:

- [ ] IDL file created under `offapi/com/sun/star/<module>/`
- [ ] IDL registered in `offapi/UnoApi_offapi.mk` (correct macro, alphabetical order)
- [ ] C++ implementation file created in module's source directory
- [ ] C++ file added to `Library_*.mk`
- [ ] Constructor function name matches between C++ and `.component` XML
- [ ] `<implementation>` entry added to `.component` file
- [ ] Implementation name is unique across all `.component` files
- [ ] `XServiceInfo` implemented with correct service name
- [ ] `make offapi && make <module>` succeeds
