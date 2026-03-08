#!/usr/bin/env python3
"""Find and list SAL_LOG areas used in LibreOffice source code.

Usage:
    python find_log_areas.py --module sw          # Areas in Writer module
    python find_log_areas.py --area sw.core       # Find all uses of area "sw.core"
    python find_log_areas.py --check-registered   # Find unregistered areas
    python find_log_areas.py --list-registered    # List all registered areas
"""

import argparse
import os
import re
import sys
from collections import defaultdict


def find_lo_root(start_dir: str = ".") -> str | None:
    d = os.path.abspath(start_dir)
    while True:
        if os.path.isfile(os.path.join(d, "offapi", "UnoApi_offapi.mk")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def parse_registered_areas(lo_root: str) -> set[str]:
    """Parse include/sal/log-areas.dox for registered log areas."""
    dox_path = os.path.join(lo_root, "include", "sal", "log-areas.dox")
    areas = set()

    if not os.path.isfile(dox_path):
        return areas

    with open(dox_path, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r'\s*@li\s+@c\s+(\S+)', line)
            if m:
                areas.add(m.group(1))

    return areas


def find_areas_in_file(filepath: str) -> list[tuple[int, str, str]]:
    """Find SAL_LOG macro calls in a file.

    Returns list of (line_number, macro_name, area_string).
    """
    results = []
    pattern = re.compile(
        r'\b(SAL_INFO|SAL_INFO_IF|SAL_WARN|SAL_WARN_IF|'
        r'DBG_UNHANDLED_EXCEPTION|TOOLS_WARN_EXCEPTION|'
        r'TOOLS_WARN_EXCEPTION_IF|TOOLS_INFO_EXCEPTION)\s*\(\s*'
        r'"([^"]*)"'
    )

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                for m in pattern.finditer(line):
                    results.append((i, m.group(1), m.group(2)))
    except OSError:
        pass

    return results


def find_areas_in_module(lo_root: str, module: str) -> dict[str, list[tuple[str, int, str]]]:
    """Find all log areas used in a module.

    Returns dict mapping area -> [(filepath, line, macro)]
    """
    areas: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
    module_dir = os.path.join(lo_root, module)

    if not os.path.isdir(module_dir):
        print(f"Error: Module directory not found: {module_dir}", file=sys.stderr)
        sys.exit(1)

    for dirpath, _, filenames in os.walk(module_dir):
        for fname in filenames:
            if fname.endswith((".cxx", ".cpp", ".hxx", ".hpp")):
                fpath = os.path.join(dirpath, fname)
                for line_num, macro, area in find_areas_in_file(fpath):
                    rel_path = os.path.relpath(fpath, lo_root)
                    areas[area].append((rel_path, line_num, macro))

    return dict(sorted(areas.items()))


def find_area_usage(lo_root: str, area: str, search_dirs: list[str] | None = None) -> list[tuple[str, int, str]]:
    """Find all uses of a specific log area."""
    results = []

    if search_dirs is None:
        # Search common source directories
        search_dirs = []
        for entry in os.scandir(lo_root):
            if entry.is_dir() and not entry.name.startswith("."):
                src_dir = os.path.join(entry.path, "source")
                inc_dir = os.path.join(entry.path, "inc")
                if os.path.isdir(src_dir):
                    search_dirs.append(src_dir)
                if os.path.isdir(inc_dir):
                    search_dirs.append(inc_dir)
        # Also search include/
        include_dir = os.path.join(lo_root, "include")
        if os.path.isdir(include_dir):
            search_dirs.append(include_dir)

    for search_dir in search_dirs:
        for dirpath, _, filenames in os.walk(search_dir):
            for fname in filenames:
                if fname.endswith((".cxx", ".cpp", ".hxx", ".hpp")):
                    fpath = os.path.join(dirpath, fname)
                    for line_num, macro, found_area in find_areas_in_file(fpath):
                        if found_area == area:
                            rel_path = os.path.relpath(fpath, lo_root)
                            results.append((rel_path, line_num, macro))

    return sorted(results)


def main():
    parser = argparse.ArgumentParser(
        description="Find and analyze SAL_LOG areas in LibreOffice"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--module", help="List areas used in a module (e.g., sw, sc, vcl)")
    group.add_argument("--area", help="Find all uses of a specific area (e.g., sw.core)")
    group.add_argument("--check-registered", action="store_true",
                       help="Find areas used in code but not registered in log-areas.dox")
    group.add_argument("--list-registered", action="store_true",
                       help="List all registered areas from log-areas.dox")

    parser.add_argument("--lo-root", default=None, help="LibreOffice source root")

    args = parser.parse_args()

    lo_root = args.lo_root or find_lo_root()
    if not lo_root:
        print("Error: Cannot find LO source root. Use --lo-root.", file=sys.stderr)
        sys.exit(1)

    if args.list_registered:
        areas = sorted(parse_registered_areas(lo_root))
        print(f"Registered areas ({len(areas)}):")
        for area in areas:
            print(f"  {area}")

    elif args.module:
        areas = find_areas_in_module(lo_root, args.module)
        print(f"Log areas in module '{args.module}' ({len(areas)} areas):\n")
        for area, usages in areas.items():
            print(f"  {area} ({len(usages)} uses)")
            for filepath, line, macro in usages[:3]:
                print(f"    {filepath}:{line} [{macro}]")
            if len(usages) > 3:
                print(f"    ... and {len(usages) - 3} more")

    elif args.area:
        results = find_area_usage(lo_root, args.area)
        if results:
            print(f"Uses of area '{args.area}' ({len(results)} total):\n")
            for filepath, line, macro in results:
                print(f"  {filepath}:{line} [{macro}]")
        else:
            print(f"No uses of area '{args.area}' found.")

    elif args.check_registered:
        registered = parse_registered_areas(lo_root)
        print(f"Checking areas in common modules against {len(registered)} registered areas...\n")

        unregistered: dict[str, int] = defaultdict(int)
        modules = ["sw", "sc", "sd", "vcl", "sfx2", "toolkit", "framework", "svx"]

        for module in modules:
            module_dir = os.path.join(lo_root, module)
            if not os.path.isdir(module_dir):
                continue
            areas = find_areas_in_module(lo_root, module)
            for area in areas:
                if area not in registered:
                    unregistered[area] += len(areas[area])

        if unregistered:
            print(f"UNREGISTERED areas ({len(unregistered)}):")
            for area, count in sorted(unregistered.items()):
                print(f"  {area} ({count} uses)")
            print(f"\nAdd these to include/sal/log-areas.dox")
        else:
            print("All areas are registered.")


if __name__ == "__main__":
    main()
