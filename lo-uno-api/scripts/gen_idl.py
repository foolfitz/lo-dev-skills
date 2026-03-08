#!/usr/bin/env python3
"""Generate IDL template files for LibreOffice UNO API development.

Usage:
    python gen_idl.py --type interface --module com.sun.star.awt --name XMyWidget
    python gen_idl.py --type struct --module com.sun.star.awt --name MyEvent
    python gen_idl.py --type enum --module com.sun.star.awt --name MyStyle
    python gen_idl.py --type service --module com.sun.star.awt --name MyService
    python gen_idl.py --type listener --module com.sun.star.awt --name XMyListener

Options:
    --type       Type of IDL to generate: interface, struct, enum, service, listener
    --module     UNO module path (dot-separated), e.g. com.sun.star.awt
    --name       Type name (e.g. XMyWidget, MyEvent)
    --output-dir Output directory (default: current directory)
    --base       Base interface/struct (optional, has sensible defaults)
"""

import argparse
import os
import sys
from datetime import date

LICENSE_HEADER = """\
/* -*- Mode: C++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
/*
 * This file is part of the LibreOffice project.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
"""

VIM_MODELINE = "/* vim:set shiftwidth=4 softtabstop=4 expandtab: */"


def module_to_nesting(module: str) -> tuple[str, str]:
    """Convert dot-separated module to IDL module nesting.

    Returns (opening, closing) strings.
    """
    parts = module.split(".")
    opening = " ".join(f"module {p} {{" for p in parts)
    closing = " ".join("};" for _ in parts)
    return opening, closing


def module_to_fqn(module: str) -> str:
    """Convert dot-separated module to :: separated fully qualified name."""
    return "::".join(module.split("."))


def generate_interface(module: str, name: str, base: str | None) -> str:
    if base is None:
        base = "com::sun::star::uno::XInterface"
    opening, closing = module_to_nesting(module)
    return f"""{LICENSE_HEADER}

{opening}

/** TODO: Add description.

    @since LibreOffice {_lo_version()}
 */
published interface {name} : {base}
{{
    /** TODO: Add method description. */
    void exampleMethod( [in] string aParam );

}};

{closing}

{VIM_MODELINE}
"""


def generate_struct(module: str, name: str, base: str | None) -> str:
    if base is None:
        base = "com::sun::star::lang::EventObject"
    opening, closing = module_to_nesting(module)
    return f"""{LICENSE_HEADER}

{opening}

/** TODO: Add description.

    @since LibreOffice {_lo_version()}
 */
published struct {name} : {base}
{{
    /** TODO: Add field description. */
    string Data;

}};

{closing}

{VIM_MODELINE}
"""


def generate_enum(module: str, name: str, _base: str | None) -> str:
    opening, closing = module_to_nesting(module)
    return f"""{LICENSE_HEADER}

{opening}

/** TODO: Add description.

    @since LibreOffice {_lo_version()}
 */
published enum {name}
{{
    /** TODO: Add value description. */
    VALUE_ONE,

    /** TODO: Add value description. */
    VALUE_TWO

}};

{closing}

{VIM_MODELINE}
"""


def generate_service(module: str, name: str, base: str | None) -> str:
    if base is None:
        # Guess interface name from service name
        iface = "X" + name
        base = f"{module_to_fqn(module)}::{iface}"
    opening, closing = module_to_nesting(module)
    return f"""{LICENSE_HEADER}

{opening}

/** TODO: Add description.

    @since LibreOffice {_lo_version()}
 */
published service {name} : {base};

{closing}

{VIM_MODELINE}
"""


def generate_listener(module: str, name: str, base: str | None) -> str:
    if base is None:
        base = "com::sun::star::lang::XEventListener"
    opening, closing = module_to_nesting(module)

    # Derive event method name from listener name
    # XFooListener -> fooOccurred
    event_method = "eventOccurred"
    if name.startswith("X") and name.endswith("Listener"):
        core = name[1:-len("Listener")]
        if core:
            event_method = core[0].lower() + core[1:]

    return f"""{LICENSE_HEADER}

{opening}

/** TODO: Add description.

    @since LibreOffice {_lo_version()}
 */
published interface {name} : {base}
{{
    /** TODO: Add method description.

        @param e
            the event object
     */
    void {event_method}( [in] com::sun::star::lang::EventObject e );

}};

{closing}

{VIM_MODELINE}
"""


def _lo_version() -> str:
    """Return a reasonable LibreOffice version string for @since tags."""
    # Use current year to estimate LO version
    # LO releases roughly: year - 2016 + 5 = major version
    # This is approximate; developers should verify
    y = date.today().year
    major = y - 2016 + 5
    return f"{major}.0"


GENERATORS = {
    "interface": generate_interface,
    "struct": generate_struct,
    "enum": generate_enum,
    "service": generate_service,
    "listener": generate_listener,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate IDL template files for LibreOffice UNO API"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=GENERATORS.keys(),
        help="Type of IDL to generate",
    )
    parser.add_argument(
        "--module",
        required=True,
        help="UNO module path (dot-separated), e.g. com.sun.star.awt",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Type name, e.g. XMyWidget",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--base",
        default=None,
        help="Base interface/struct (fully qualified, :: separated)",
    )

    args = parser.parse_args()

    # Validate name conventions
    if args.type == "interface" and not args.name.startswith("X"):
        print(f"Warning: Interface names should start with 'X' (got '{args.name}')",
              file=sys.stderr)
    if args.type == "listener" and not args.name.startswith("X"):
        print(f"Warning: Listener names should start with 'X' (got '{args.name}')",
              file=sys.stderr)
    if args.type == "listener" and not args.name.endswith("Listener"):
        print(f"Warning: Listener names should end with 'Listener' (got '{args.name}')",
              file=sys.stderr)

    generator = GENERATORS[args.type]
    content = generator(args.module, args.name, args.base)

    # Determine output path
    module_path = args.module.replace(".", os.sep)
    output_dir = os.path.join(args.output_dir, module_path)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{args.name}.idl"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated: {output_path}")

    # Print registration hint
    macro = "gb_UnoApi_add_idlfiles"
    if args.type == "service":
        macro = "gb_UnoApi_add_idlfiles_nohdl"

    idl_path = f"{module_path.replace(os.sep, '/')}/{args.name}"
    module_dir = module_path.replace(os.sep, "/")
    print(f"\nRegister in offapi/UnoApi_offapi.mk:")
    print(f"  $(eval $(call {macro},offapi,{module_dir},\\")
    print(f"      {args.name} \\")
    print(f"  ))")


if __name__ == "__main__":
    main()
