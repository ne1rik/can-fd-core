#!/usr/bin/env python3
"""Merge coverage databases from independent simulation runs."""

import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from canfd_kit.coverage import CANFDCoverage, CoverageReport


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-dir", default="coverage")
    ap.add_argument("--pattern", default="db_*.json")
    ap.add_argument("--out", default="coverage/merged")
    ap.add_argument("--min", type=float, default=95.0)
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.db_dir, args.pattern)))
    if not paths:
        print(f"no coverage databases matching {args.db_dir}/{args.pattern}", file=sys.stderr)
        return 2

    cov = CANFDCoverage()
    for p in paths:
        cov.load(p)
        print(f"merged {p}")

    rep = CoverageReport(cov)
    cov.save(args.out + "_db.json")
    rep.to_json(args.out + ".json")
    rep.to_file(args.out + ".md")

    print()
    print(f"POINTS  {rep.point_percentage:6.1f}%")
    print(f"CROSSES {rep.cross_percentage:6.1f}%")
    print(f"OVERALL {rep.overall_percentage:6.1f}%")
    miss = rep.uncovered()
    if miss:
        print("\nuncovered:")
        for k, v in miss.items():
            shown = v if len(v) <= 10 else v[:10] + [f"...+{len(v)-10}"]
            print(f"  {k}: {', '.join(shown)}")
    else:
        print("\nall legal bins hit")

    if rep.overall_percentage < args.min:
        print(f"\nFAIL: {rep.overall_percentage:.1f}% < {args.min:.1f}%", file=sys.stderr)
        return 1
    print(f"\nPASS: >= {args.min:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
