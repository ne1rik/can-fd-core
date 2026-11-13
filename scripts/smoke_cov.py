"""Smoke probe for cocotb-coverage: import, sample a coverpoint, read it back.

Exit 0 = usable, exit 1 = unusable. Prints exactly one summary line so the
shell harness can drop it into the report verbatim.
"""

import sys


def main():
    try:
        import cocotb_coverage
        from cocotb_coverage.coverage import CoverPoint, coverage_db
    except Exception as exc:
        print(f"IMPORT_FAIL: {type(exc).__name__}: {exc}")
        return 1

    ver = getattr(cocotb_coverage, "__version__", "unknown")

    try:
        @CoverPoint("smoke.dlc", xf=lambda d: d, bins=list(range(16)))
        def sample(d):
            pass

        for d in range(16):
            sample(d)

        item = coverage_db["smoke.dlc"]
        size = item.size
        cov = item.coverage
        if size != 16:
            print(f"API_FAIL: size={size}, expected 16")
            return 1
        print(f"OK version={ver} coverpoint=smoke.dlc bins={size} coverage={cov:.1f}%")
        return 0
    except Exception as exc:
        print(f"API_FAIL: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
