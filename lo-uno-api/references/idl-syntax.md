# IDL Syntax Reference

## UNO Type System Basics

| UNO Type | IDL Keyword | C++ Type |
|----------|-------------|----------|
| `void` | `void` | `void` |
| `boolean` | `boolean` | `sal_Bool` |
| `byte` | `byte` | `sal_Int8` |
| `short` | `short` | `sal_Int16` |
| `unsigned short` | `unsigned short` | `sal_uInt16` |
| `long` | `long` | `sal_Int32` |
| `unsigned long` | `unsigned long` | `sal_uInt32` |
| `hyper` | `hyper` | `sal_Int64` |
| `unsigned hyper` | `unsigned hyper` | `sal_uInt64` |
| `float` | `float` | `float` |
| `double` | `double` | `double` |
| `char` | `char` | `sal_Unicode` |
| `string` | `string` | `OUString` |
| `type` | `type` | `css::uno::Type` |
| `any` | `any` | `css::uno::Any` |
| `sequence<T>` | `sequence<T>` | `css::uno::Sequence<T>` |

## File Structure

Every IDL file follows this structure:

```idl
/* -*- Mode: C++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
/*
 * This file is part of the LibreOffice project.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

module com { module sun { module star { module <module> {

// type definition here

}; }; }; };

/* vim:set shiftwidth=4 softtabstop=4 expandtab: */
```

## Interface

An interface defines a set of methods that an implementation must provide.

**Syntax:**
```idl
published interface XName : BaseInterface
{
    ReturnType methodName( [in] ParamType1 param1, [out] ParamType2 param2 )
        raises (com::sun::star::uno::RuntimeException);
};
```

**Parameter directions:**
- `[in]` — Input parameter (caller provides value)
- `[out]` — Output parameter (callee fills value)
- `[inout]` — Bidirectional parameter

**Real example** (`offapi/com/sun/star/awt/XGraphics2.idl`):
```idl
published interface XGraphics2: com::sun::star::awt::XGraphics
{
    /** clears the given rectangle on the device
        @since LibreOffice 4.1
     */
    void clear( [in] Rectangle aRect );

    /** draws a com::sun::star::graphic::XGraphic in the output device. */
    void drawImage( [in] long nX,
                    [in] long nY,
                    [in] long nWidth,
                    [in] long nHeight,
                    [in] short nStyle,
                    [in] ::com::sun::star::graphic::XGraphic aGraphic );
};
```

**Key points:**
- Interfaces typically start with `X` prefix
- Inherit from `com::sun::star::uno::XInterface` (or a derived interface)
- Methods can `raises` specific exceptions
- Use `@since LibreOffice X.Y` in doc comments for new additions

## Struct

A struct defines a data type with named fields.

**Syntax:**
```idl
published struct Name : OptionalBaseStruct
{
    Type1 Field1;
    Type2 Field2;
};
```

**Real example** (`offapi/com/sun/star/awt/PaintEvent.idl`):
```idl
/** specifies the paint event for a component. */
published struct PaintEvent: com::sun::star::lang::EventObject
{
    /** contains the rectangle area which needs to be repainted. */
    com::sun::star::awt::Rectangle UpdateRect;

    /** contains the number of paint events that follows this event. */
    short Count;
};
```

**Key points:**
- Event structs typically inherit from `com::sun::star::lang::EventObject`
- `EventObject` provides a `Source` field of type `XInterface`
- Fields are public (no access specifiers in IDL)

## Enum

An enumeration defines a fixed set of named values.

**Syntax:**
```idl
published enum Name
{
    VALUE1,
    VALUE2,
    VALUE3
};
```

**Real example** (`offapi/com/sun/star/awt/GradientStyle.idl`):
```idl
/** specify the style of color dispersion. */
published enum GradientStyle
{
    LINEAR,
    AXIAL,
    RADIAL,
    ELLIPTICAL,
    SQUARE,
    RECT
};
```

**Key points:**
- No explicit integer values (assigned sequentially starting from 0)
- Last value has no trailing comma
- Maps to C++ `enum` in the generated header

## Service

A service declares that an implementation provides a specific interface. There are two forms:

### Single-interface service (modern, preferred)

**Syntax:**
```idl
published service Name : XInterface;
```

**Real example** (`offapi/com/sun/star/awt/Toolkit.idl`):
```idl
/** describes a toolkit that creates windows on a screen. */
published service Toolkit : XToolkit2;
```

### Accumulation-based service (legacy)

**Syntax:**
```idl
published service Name
{
    service OtherService;
    interface XFoo;
    [optional] interface XBar;
    [property] type PropName;
};
```

**Key points:**
- Modern code should use single-interface services
- Single-interface services use `gb_UnoApi_add_idlfiles_nohdl` (no `.hdl` generated)
- The service IDL defines what interface to use; the C++ class implements it

## Listener

A listener is an interface for receiving event notifications. It follows a specific pattern.

**Syntax:**
```idl
published interface XFooListener: com::sun::star::lang::XEventListener
{
    void eventMethod( [in] FooEvent e );
};
```

**Real example** (`offapi/com/sun/star/awt/XPaintListener.idl`):
```idl
/** makes it possible to receive paint events. */
published interface XPaintListener: com::sun::star::lang::XEventListener
{
    /** is invoked when a region of the window became invalid. */
    void windowPaint( [in] com::sun::star::awt::PaintEvent e );
};
```

**Key points:**
- Always inherits from `com::sun::star::lang::XEventListener`
- `XEventListener` provides `disposing()` method for cleanup
- Event methods take a single event struct parameter
- Typically paired with a corresponding event struct (e.g., `PaintEvent`)
- Naming: `XFooListener` with methods like `fooHappened(FooEvent e)`

## Constants Group

For defining named constants:

```idl
published constants ImageDrawMode
{
    const short NONE = 0;
    const short HIGHLIGHT = 1;
    const short DECOLOR = 2;
    const short SEMITRANSPARENT = 4;
};
```

## Common Import Patterns

IDL files don't use `#include`. Instead, types are referenced by fully qualified name. The UNOIDL compiler resolves references automatically from registered API sets.

When referencing types from the same module, you can use short names:
```idl
// Inside module com::sun::star::awt
void paint( [in] PaintEvent e );  // PaintEvent is in same module
```

When referencing types from other modules, use fully qualified names:
```idl
void setSource( [in] com::sun::star::lang::EventObject e );
```
