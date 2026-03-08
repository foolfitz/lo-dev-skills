#!/usr/bin/env python3
"""Parse and filter SAL_LOG output.

Usage:
    python parse_sal_log.py < logfile.txt
    python parse_sal_log.py --area sw.core < logfile.txt
    python parse_sal_log.py --level warn < logfile.txt
    python parse_sal_log.py --file docnew.cxx < logfile.txt
    python parse_sal_log.py --stats < logfile.txt
    cat logfile.txt | python parse_sal_log.py --area sw --level warn
"""

import argparse
import re
import sys
from collections import Counter, defaultdict


# SAL_LOG output format:
# warn:sw.core:12345:7f8a:sw/source/core/doc/docnew.cxx:234: message
LOG_PATTERN = re.compile(
    r'^(?:(\d{4}-\d{2}-\d{2}:\d{2}:\d{2}:\d{2}\.\d{3})\s+)?'  # optional timestamp
    r'(?:(\d+\.\d{3})\s+)?'  # optional relative timer
    r'(info|warn|debug):'    # level
    r'([^:]*?):'             # area
    r'(\d+):'                # PID
    r'([0-9a-f]+):'          # TID
    r'([^:]+):'              # file
    r'(\d+):\s'              # line
    r'(.*)'                  # message
)


def parse_line(line: str) -> dict | None:
    """Parse a single SAL_LOG line into components."""
    m = LOG_PATTERN.match(line.strip())
    if not m:
        return None
    return {
        "timestamp": m.group(1),
        "relative": m.group(2),
        "level": m.group(3),
        "area": m.group(4),
        "pid": m.group(5),
        "tid": m.group(6),
        "file": m.group(7),
        "line": int(m.group(8)),
        "message": m.group(9),
        "raw": line.strip(),
    }


def matches_filter(entry: dict, args) -> bool:
    """Check if a log entry matches the given filters."""
    if args.area and not entry["area"].startswith(args.area):
        return False
    if args.level and entry["level"] != args.level:
        return False
    if args.file and args.file not in entry["file"]:
        return False
    if args.grep and args.grep.lower() not in entry["message"].lower():
        return False
    return True


def print_stats(entries: list[dict]):
    """Print statistics about log entries."""
    level_counts = Counter(e["level"] for e in entries)
    area_counts = Counter(e["area"] for e in entries)
    file_counts = Counter(e["file"] for e in entries)

    print(f"Total entries: {len(entries)}\n")

    print("By level:")
    for level, count in level_counts.most_common():
        print(f"  {level}: {count}")

    print(f"\nTop 20 areas (of {len(area_counts)}):")
    for area, count in area_counts.most_common(20):
        print(f"  {area}: {count}")

    print(f"\nTop 20 source files (of {len(file_counts)}):")
    for filepath, count in file_counts.most_common(20):
        print(f"  {filepath}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Parse and filter SAL_LOG output"
    )
    parser.add_argument("--area", help="Filter by area prefix (e.g., sw.core)")
    parser.add_argument("--level", choices=["info", "warn", "debug"],
                        help="Filter by log level")
    parser.add_argument("--file", help="Filter by source file substring")
    parser.add_argument("--grep", help="Filter by message substring (case-insensitive)")
    parser.add_argument("--stats", action="store_true",
                        help="Show statistics instead of filtered output")
    parser.add_argument("--compact", action="store_true",
                        help="Compact output: area:file:line message")
    parser.add_argument("input", nargs="?", type=argparse.FileType("r"),
                        default=sys.stdin, help="Log file (default: stdin)")

    args = parser.parse_args()

    entries = []
    unparsed = 0

    for line in args.input:
        entry = parse_line(line)
        if entry:
            entries.append(entry)
        else:
            unparsed += 1

    if args.stats:
        filtered = [e for e in entries if matches_filter(e, args)]
        if args.area or args.level or args.file or args.grep:
            print(f"Filtered ({len(filtered)} of {len(entries)} entries):\n")
        print_stats(filtered if (args.area or args.level or args.file or args.grep) else entries)
        if unparsed:
            print(f"\n({unparsed} lines could not be parsed)")
        return

    for entry in entries:
        if matches_filter(entry, args):
            if args.compact:
                print(f"{entry['level']}:{entry['area']}:{entry['file']}:{entry['line']} {entry['message']}")
            else:
                print(entry["raw"])

    if unparsed and not any([args.area, args.level, args.file, args.grep]):
        print(f"\n({unparsed} lines could not be parsed)", file=sys.stderr)


if __name__ == "__main__":
    main()
