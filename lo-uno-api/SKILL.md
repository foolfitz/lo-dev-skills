---
name: lo-uno-api
description: Guide for developing UNO APIs in LibreOffice. Use when creating/modifying UNO IDL interfaces, structs, enums, services, or listeners in offapi/. Also for implementing UNO services in C++, registering in .component XML, or working with gb_UnoApi build rules.
---

# UNO API Development Guide for LibreOffice

## Overview

UNO (Universal Network Objects) is LibreOffice's component model. Developing a new UNO API involves five steps:

1. **Write IDL** — Define the interface/struct/enum/service in `.idl` file under `offapi/com/sun/star/`
2. **Register in build** — Add the IDL to `offapi/UnoApi_offapi.mk` using the correct `gb_UnoApi_add_idlfiles*` macro
3. **Implement C++** — Create a C++ class implementing the interface using `cppu::WeakImplHelper` or similar
4. **Register service** — Add a `<implementation>` entry in the module's `.component` XML file
5. **Build & test** — Run `make offapi && make <module>` to compile and verify

## Decision Tree

| I want to create... | IDL syntax | Reference | Script |
|---------------------|-----------|-----------|--------|
| A new interface with methods | `published interface XFoo : XInterface { ... };` | [idl-syntax.md](./references/idl-syntax.md#interface) | `gen_idl.py --type interface` |
| A data struct | `published struct FooEvent : EventObject { ... };` | [idl-syntax.md](./references/idl-syntax.md#struct) | `gen_idl.py --type struct` |
| An enumeration | `published enum FooStyle { ... };` | [idl-syntax.md](./references/idl-syntax.md#enum) | `gen_idl.py --type enum` |
| A service (instantiable) | `published service Foo : XFoo;` | [idl-syntax.md](./references/idl-syntax.md#service) | `gen_idl.py --type service` |
| An event listener | `published interface XFooListener : XEventListener { ... };` | [idl-syntax.md](./references/idl-syntax.md#listener) | `gen_idl.py --type listener` |

## Step-by-Step Workflow

### Step 1: Write the IDL File

Use `scripts/gen_idl.py` to generate a template:

```bash
python scripts/gen_idl.py --type interface --module com.sun.star.awt --name XMyWidget
```

Place the file under `offapi/com/sun/star/<module>/`. See [idl-syntax.md](./references/idl-syntax.md) for complete syntax reference.

Key rules:
- Use `published` keyword for all public API types
- Parameter directions: `[in]`, `[out]`, `[inout]`
- Use fully qualified type names: `com::sun::star::uno::XInterface`
- Module nesting: `module com { module sun { module star { module awt { ... }; }; }; };`

### Step 2: Register in Build System

Add the IDL path to `offapi/UnoApi_offapi.mk`. Choose the correct macro:

| Macro | Generates | Use for |
|-------|-----------|---------|
| `gb_UnoApi_add_idlfiles` | `.hpp` + `.hdl` | Interfaces, structs, enums (types used in C++ headers) |
| `gb_UnoApi_add_idlfiles_nohdl` | `.hpp` only | Services (no `.hdl` needed) |
| `gb_UnoApi_add_idlfiles_noheader` | Nothing | Types only used by other IDL files |

Entries must be in **alphabetical order** within each module block.

Validate with: `python scripts/check_build_registration.py --idl-path com/sun/star/awt/XMyWidget.idl`

See [build-registration.md](./references/build-registration.md) for details.

### Step 3: Implement in C++

Choose the implementation pattern based on your needs:

| Pattern | Base class | When to use |
|---------|-----------|-------------|
| Simple service | `cppu::WeakImplHelper<XServiceInfo, XMyInterface>` | Most services |
| VCL-backed | `cppu::ImplInheritanceHelper<VCLXWindow, XMyInterface>` | UI components needing VCL access |
| Listener multiplexer | `ListenerMultiplexerBase<XMyListener>` | Event dispatch to multiple listeners |

See [cpp-implementation.md](./references/cpp-implementation.md) for complete templates.

### Step 4: Register the Service

Add an `<implementation>` element to your module's `.component` XML:

```xml
<implementation name="com.sun.star.awt.comp.MyWidget"
    constructor="com_sun_star_awt_comp_MyWidget_get_implementation">
  <service name="com.sun.star.awt.MyWidget"/>
</implementation>
```

The constructor function name is derived from the implementation name by replacing `.` with `_` and appending `_get_implementation`.

Validate with: `python scripts/validate_component.py --component toolkit/util/tk.component`

See [build-registration.md](./references/build-registration.md#component-xml) for details.

### Step 5: Build and Test

```bash
# Build IDL headers
make offapi

# Build the implementing module
make toolkit  # or sw, sc, sd, etc.

# Run module tests
make CppunitTest_toolkit_a11y
```

## Common Pitfalls

1. **Forgetting `published`** — Without `published`, the type is module-internal and cannot be used by extensions or external code.

2. **Wrong build macro** — Using `gb_UnoApi_add_idlfiles` for a service generates an unnecessary `.hdl` file. Use `gb_UnoApi_add_idlfiles_nohdl` for services.

3. **Missing `SolarMutexGuard`** — Any method that accesses VCL objects must acquire `SolarMutexGuard` first. Forgetting this causes threading crashes.

4. **Constructor naming mismatch** — The constructor function name in `.component` XML must exactly match the `extern "C"` function name in C++. Convention: replace dots with underscores.

5. **Forgetting XServiceInfo** — Every service implementation should implement `css::lang::XServiceInfo`. Use `cppu::supportsService()` helper.

6. **Wrong `#include` form** — UNO generated headers use `<>` form: `#include <com/sun/star/awt/XMyWidget.hpp>`.

7. **Not adding source file to Library_*.mk** — The C++ implementation file must be listed in the module's `Library_*.mk` build file.

8. **Alphabetical ordering** — IDL entries in `UnoApi_offapi.mk` must be alphabetically sorted within each module block. The build system doesn't enforce this, but code review will reject unordered entries.

## Reference Index

| File | Purpose |
|------|---------|
| [references/idl-syntax.md](./references/idl-syntax.md) | Complete IDL syntax with real LO examples |
| [references/cpp-implementation.md](./references/cpp-implementation.md) | C++ implementation patterns and templates |
| [references/build-registration.md](./references/build-registration.md) | Build system macros and service registration |
| [references/common-base-interfaces.md](./references/common-base-interfaces.md) | Quick reference for commonly-used UNO interfaces |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/gen_idl.py` | Generate IDL template files |
| `scripts/check_build_registration.py` | Verify IDL is registered in UnoApi_offapi.mk |
| `scripts/validate_component.py` | Validate .component XML consistency |
