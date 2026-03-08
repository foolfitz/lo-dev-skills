#!/usr/bin/env python3
"""Validate a .component XML file for consistency.

Checks:
- Constructor naming convention (dots to underscores + _get_implementation)
- Whether constructor functions exist in the source code (optional)
- Missing <service> elements
- XML well-formedness

Usage:
    python validate_component.py --component toolkit/util/tk.component
    python validate_component.py --component toolkit/util/tk.component --check-source
    python validate_component.py --component toolkit/util/tk.component --lo-root /path/to/LO-core
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


NS = "http://openoffice.org/2010/uno-components"


def find_lo_root(start_dir: str = ".") -> str | None:
    """Find the LibreOffice source root."""
    d = os.path.abspath(start_dir)
    while True:
        if os.path.isfile(os.path.join(d, "offapi", "UnoApi_offapi.mk")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def expected_constructor_name(impl_name: str) -> str:
    """Derive expected constructor function name from implementation name."""
    return impl_name.replace(".", "_") + "_get_implementation"


def validate_component(component_path: str, check_source: bool = False, lo_root: str | None = None):
    """Validate a .component XML file.

    Returns (errors, warnings) lists.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Parse XML
    try:
        tree = ET.parse(component_path)
    except ET.ParseError as e:
        errors.append(f"XML parse error: {e}")
        return errors, warnings

    root = tree.getroot()

    # Check root element
    expected_tag = f"{{{NS}}}component"
    if root.tag != expected_tag and root.tag != "component":
        # Handle both namespaced and non-namespaced
        pass

    # Iterate implementations
    impl_count = 0
    impl_names = set()

    for impl in root.iter():
        # Handle both namespaced and non-namespaced
        if impl.tag in (f"{{{NS}}}implementation", "implementation"):
            impl_count += 1
            impl_name = impl.get("name", "")
            constructor = impl.get("constructor", "")

            if not impl_name:
                errors.append(f"Implementation #{impl_count}: missing 'name' attribute")
                continue

            # Check for duplicate implementation names
            if impl_name in impl_names:
                errors.append(f"Duplicate implementation name: {impl_name}")
            impl_names.add(impl_name)

            # Check constructor naming convention
            if constructor:
                expected = expected_constructor_name(impl_name)
                if constructor != expected:
                    warnings.append(
                        f"Constructor naming mismatch for '{impl_name}':\n"
                        f"  Actual:   {constructor}\n"
                        f"  Expected: {expected}"
                    )

            # Check for <service> elements
            services = []
            for child in impl:
                if child.tag in (f"{{{NS}}}service", "service"):
                    service_name = child.get("name", "")
                    if service_name:
                        services.append(service_name)

            if not services:
                warnings.append(f"Implementation '{impl_name}' has no <service> elements")

            # Optional: check if constructor function exists in source
            if check_source and lo_root and constructor:
                found = _find_constructor_in_source(constructor, lo_root, component_path)
                if not found:
                    warnings.append(
                        f"Constructor function '{constructor}' not found in source code "
                        f"(searched near {component_path})"
                    )

    if impl_count == 0:
        errors.append("No <implementation> elements found")

    return errors, warnings


def _find_constructor_in_source(constructor: str, lo_root: str, component_path: str) -> bool:
    """Search for the constructor function in source files near the component file."""
    # Determine the module directory
    comp_path = Path(component_path)
    if comp_path.is_absolute():
        rel = comp_path.relative_to(lo_root)
    else:
        rel = comp_path

    # Component files are typically in <module>/util/
    # Source files are in <module>/source/
    module_dir = rel.parts[0] if len(rel.parts) > 0 else ""
    source_dir = os.path.join(lo_root, module_dir, "source")

    if not os.path.isdir(source_dir):
        return False  # Can't check

    # Search for the constructor function name in .cxx files
    pattern = re.compile(re.escape(constructor))
    for dirpath, _, filenames in os.walk(source_dir):
        for fname in filenames:
            if fname.endswith((".cxx", ".cpp", ".hxx", ".hpp")):
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        if pattern.search(f.read()):
                            return True
                except OSError:
                    continue

    # Also check include directory
    include_dir = os.path.join(lo_root, "include", module_dir)
    if os.path.isdir(include_dir):
        for dirpath, _, filenames in os.walk(include_dir):
            for fname in filenames:
                if fname.endswith((".hxx", ".hpp")):
                    fpath = os.path.join(dirpath, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            if pattern.search(f.read()):
                                return True
                    except OSError:
                        continue

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate .component XML file consistency"
    )
    parser.add_argument(
        "--component",
        required=True,
        help="Path to .component file, e.g. toolkit/util/tk.component",
    )
    parser.add_argument(
        "--check-source",
        action="store_true",
        help="Also search source code for constructor functions",
    )
    parser.add_argument(
        "--lo-root",
        default=None,
        help="LibreOffice source root (auto-detected if not specified)",
    )

    args = parser.parse_args()

    lo_root = args.lo_root
    if lo_root is None:
        lo_root = find_lo_root()

    # Resolve component path
    component_path = args.component
    if lo_root and not os.path.isfile(component_path):
        component_path = os.path.join(lo_root, args.component)

    if not os.path.isfile(component_path):
        print(f"Error: Component file not found: {args.component}", file=sys.stderr)
        sys.exit(1)

    errors, warnings = validate_component(
        component_path,
        check_source=args.check_source,
        lo_root=lo_root,
    )

    # Report results
    print(f"Validating: {component_path}")
    print()

    if not errors and not warnings:
        print("OK: No issues found.")
        sys.exit(0)

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        print()

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            for i, line in enumerate(w.split("\n")):
                prefix = "  - " if i == 0 else "    "
                print(f"{prefix}{line}")
        print()

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
