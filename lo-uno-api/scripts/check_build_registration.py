#!/usr/bin/env python3
"""Verify that an IDL file is correctly registered in UnoApi_offapi.mk.

Usage:
    python check_build_registration.py --idl-path com/sun/star/awt/XMyWidget.idl
    python check_build_registration.py --idl-path com/sun/star/awt/XMyWidget.idl --lo-root /path/to/LO-core
"""

import argparse
import os
import re
import sys


def find_lo_root(start_dir: str = ".") -> str | None:
    """Find the LibreOffice source root by looking for offapi/UnoApi_offapi.mk."""
    d = os.path.abspath(start_dir)
    while True:
        if os.path.isfile(os.path.join(d, "offapi", "UnoApi_offapi.mk")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def parse_makefile(mk_path: str) -> dict[str, list[tuple[str, str]]]:
    """Parse UnoApi_offapi.mk and return registered IDL entries.

    Returns:
        dict mapping "module_dir/TypeName" to list of (macro_name, module_dir) tuples
    """
    with open(mk_path, "r", encoding="utf-8") as f:
        content = f.read()

    entries: dict[str, list[tuple[str, str]]] = {}

    # Match patterns like:
    # $(eval $(call gb_UnoApi_add_idlfiles,offapi,com/sun/star/awt,\
    #     TypeName \
    # ))
    pattern = re.compile(
        r'\$\(eval \$\(call (gb_UnoApi_add_idlfiles\w*),offapi,([^,]+),\\\n'
        r'((?:\t[^\)]+\\\n)*\t[^\)]+\n)'
        r'\)\)',
        re.MULTILINE,
    )

    for m in pattern.finditer(content):
        macro = m.group(1)
        module_dir = m.group(2).strip()
        names_block = m.group(3)

        # Extract type names
        names = []
        for line in names_block.strip().split("\n"):
            name = line.strip().rstrip("\\").strip()
            if name:
                names.append(name)

        for name in names:
            key = f"{module_dir}/{name}"
            if key not in entries:
                entries[key] = []
            entries[key].append((macro, module_dir))

    return entries


def suggest_macro(idl_path: str, lo_root: str) -> str:
    """Analyze the IDL file content to suggest the correct macro."""
    full_path = os.path.join(lo_root, "offapi", idl_path)
    if not os.path.isfile(full_path):
        return "gb_UnoApi_add_idlfiles"

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Single-interface service pattern: "service Name : XInterface;"
    if re.search(r'published\s+service\s+\w+\s*:', content):
        return "gb_UnoApi_add_idlfiles_nohdl"

    # Accumulation-based service
    if re.search(r'published\s+service\s+\w+\s*\{', content):
        return "gb_UnoApi_add_idlfiles_nohdl"

    # Default for interfaces, structs, enums
    return "gb_UnoApi_add_idlfiles"


def check_alphabetical_order(entries: dict[str, list[tuple[str, str]]], module_dir: str, mk_path: str) -> list[str]:
    """Check if entries in a module block are alphabetically sorted."""
    warnings = []

    with open(mk_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all blocks for this module
    pattern = re.compile(
        r'\$\(eval \$\(call (gb_UnoApi_add_idlfiles\w*),offapi,' + re.escape(module_dir) + r',\\\n'
        r'((?:\t[^\)]+\\\n)*\t[^\)]+\n)'
        r'\)\)',
        re.MULTILINE,
    )

    for m in pattern.finditer(content):
        macro = m.group(1)
        names_block = m.group(2)
        names = []
        for line in names_block.strip().split("\n"):
            name = line.strip().rstrip("\\").strip()
            if name:
                names.append(name)

        sorted_names = sorted(names, key=str.casefold)
        if names != sorted_names:
            # Find first out-of-order entry
            for i in range(1, len(names)):
                if names[i].casefold() < names[i - 1].casefold():
                    warnings.append(
                        f"In {macro} block for {module_dir}: "
                        f"'{names[i]}' should come before '{names[i-1]}' (alphabetical order)"
                    )
                    break

    return warnings


def main():
    parser = argparse.ArgumentParser(
        description="Verify IDL registration in UnoApi_offapi.mk"
    )
    parser.add_argument(
        "--idl-path",
        required=True,
        help="IDL path relative to offapi/, e.g. com/sun/star/awt/XMyWidget.idl",
    )
    parser.add_argument(
        "--lo-root",
        default=None,
        help="LibreOffice source root (auto-detected if not specified)",
    )

    args = parser.parse_args()

    # Find LO root
    lo_root = args.lo_root
    if lo_root is None:
        lo_root = find_lo_root()
    if lo_root is None:
        print("Error: Cannot find LibreOffice source root. Use --lo-root.", file=sys.stderr)
        sys.exit(1)

    mk_path = os.path.join(lo_root, "offapi", "UnoApi_offapi.mk")
    if not os.path.isfile(mk_path):
        print(f"Error: {mk_path} not found.", file=sys.stderr)
        sys.exit(1)

    # Normalize IDL path
    idl_path = args.idl_path
    if idl_path.endswith(".idl"):
        idl_path = idl_path[:-4]  # Remove .idl extension
    # Remove leading offapi/ if present
    if idl_path.startswith("offapi/"):
        idl_path = idl_path[len("offapi/"):]

    # Extract module dir and type name
    parts = idl_path.rsplit("/", 1)
    if len(parts) != 2:
        print(f"Error: Invalid IDL path format: {args.idl_path}", file=sys.stderr)
        sys.exit(1)

    module_dir, type_name = parts

    # Parse makefile
    entries = parse_makefile(mk_path)

    # Check registration
    key = f"{module_dir}/{type_name}"
    if key in entries:
        for macro, mod in entries[key]:
            print(f"REGISTERED: {type_name} in {module_dir}")
            print(f"  Macro: {macro}")

        # Suggest correct macro
        suggested = suggest_macro(f"{idl_path}.idl", lo_root)
        actual_macros = {m for m, _ in entries[key]}
        if len(actual_macros) == 1 and suggested not in actual_macros:
            actual = list(actual_macros)[0]
            print(f"\n  WARNING: Currently using '{actual}', but '{suggested}' may be more appropriate.")
            print(f"  Suggestion based on IDL content analysis.")
    else:
        print(f"NOT REGISTERED: {type_name} in {module_dir}")
        suggested = suggest_macro(f"{idl_path}.idl", lo_root)
        print(f"\n  Suggested macro: {suggested}")
        print(f"\n  Add to offapi/UnoApi_offapi.mk:")
        print(f"  $(eval $(call {suggested},offapi,{module_dir},\\")
        print(f"      {type_name} \\")
        print(f"  ))")
        print(f"\n  Or add '{type_name}' to an existing {suggested} block for {module_dir}")

    # Check alphabetical order
    warnings = check_alphabetical_order(entries, module_dir, mk_path)
    if warnings:
        print(f"\n  ORDERING WARNINGS:")
        for w in warnings:
            print(f"    - {w}")


if __name__ == "__main__":
    main()
