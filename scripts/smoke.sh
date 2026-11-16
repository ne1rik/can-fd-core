#!/usr/bin/env bash
# Dependency smoke harness for the CAN FD verification kit.
# Rule: no external dependency reaches the critical path before it passes here.
# Usage: bash scripts/smoke.sh
# Output: console table + docs/smoke_report.md ; exit 1 if any FAIL (WARN does not fail).

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1
mkdir -p docs

REPORT="docs/smoke_report.md"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ROWS="$TMP/rows.tsv"
: > "$ROWS"
FAILS=0
WARNS=0

row() {
    printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" >> "$ROWS"
    case "$1" in
        FAIL) FAILS=$((FAILS + 1)) ;;
        WARN) WARNS=$((WARNS + 1)) ;;
    esac
    return 0
}

have() { command -v "$1" >/dev/null 2>&1; }

# ---------- interpreters and build tools ----------
if have python3; then
    row PASS "python3" "$(python3 -c 'import sys;print(sys.version.split()[0])')" "interpreter"
else
    row FAIL "python3" "-" "not found"
fi

for t in make g++ git; do
    if have "$t"; then
        row PASS "$t" "$($t --version 2>&1 | head -1 | cut -c1-48)" "build tool"
    else
        row FAIL "$t" "-" "not found"
    fi
done

# ---------- simulator ----------
VLV="-"
if have verilator; then
    VLV="$(verilator --version 2>&1 | head -1)"
    row PASS "verilator" "$VLV" "simulator"
else
    row FAIL "verilator" "-" "not found"
fi

# ---------- python verification packages ----------
for m in cocotb pytest; do
    out="$(python3 -c "import $m,sys;print(getattr($m,'__version__','unknown'))" 2>&1)"
    if [ $? -eq 0 ]; then
        row PASS "$m" "$out" "python package"
    else
        row FAIL "$m" "-" "$(echo "$out" | tail -1 | cut -c1-60)"
    fi
done

# cocotb-coverage: real coverpoint round-trip, not just an import.
if out="$(python3 scripts/smoke_cov.py 2>&1)"; then
    row PASS "cocotb-coverage" "$(echo "$out" | sed -n 's/.*version=\([^ ]*\).*/\1/p')" "$out"
else
    row FAIL "cocotb-coverage" "-" "$(echo "$out" | tail -1 | cut -c1-90)"
fi

# ---------- Verilator coverage flags ----------
if have verilator; then
    for f in --coverage --coverage-line --coverage-toggle --coverage-user \
             --coverage-branch --coverage-expr --coverage-fsm; do
        if verilator -cc "$f" --top-module smoke_cov \
             -Mdir "$TMP/vl$(echo "$f" | tr -d '-')" \
             scripts/smoke_cov.sv > "$TMP/vl.log" 2>&1; then
            row PASS "verilator $f" "$VLV" "flag accepted"
        else
            row WARN "verilator $f" "$VLV" "flag rejected by this build"
        fi
    done
fi

# ---------- formal toolchain ----------
if have yosys; then
    row PASS "yosys" "$(yosys -V 2>&1 | head -1 | cut -c1-48)" "synthesis / formal front-end"
else
    row FAIL "yosys" "-" "not found"
fi

if have sby; then
    row PASS "sby" "$(sby --version 2>&1 | head -1)" "formal driver"
else
    row FAIL "sby" "-" "not found"
fi

for t in yosys-smtbmc yosys-abc z3 yices boolector; do
    if have "$t"; then
        row PASS "$t" "present" "formal engine / solver"
    else
        row WARN "$t" "absent" "may be required by the chosen engine"
    fi
done

# Real formal run.
if have sby; then
    if ( cd scripts && timeout 180 sby -f smoke_formal.sby ) > "$TMP/sby.log" 2>&1; then
        row PASS "formal run (smtbmc)" "-" "trivial proof completed"
    else
        row FAIL "formal run (smtbmc)" "-" "$(grep -iE 'error|not found|no such|unsupported' "$TMP/sby.log" | tail -1 | cut -c1-90)"
        cp "$TMP/sby.log" docs/smoke_formal_failure.log
    fi
fi

# ---------- waveform viewer ----------
if have gtkwave; then
    gv="$(timeout 15 gtkwave --version 2>&1 | head -1)"
    if echo "$gv" | grep -qi gtkwave; then
        row PASS "gtkwave" "$(echo "$gv" | cut -c1-48)" "waveform viewer"
    else
        row WARN "gtkwave" "present" "version probe inconclusive"
    fi
else
    row WARN "gtkwave" "absent" "optional for CI"
fi

# ---------- report ----------
{
    echo "# Dependency smoke report"
    echo
    echo "Generated: $(date -u '+%Y-%m-%d %H:%M UTC')"
    echo "Host: $(uname -srm)"
    if [ -r /etc/os-release ]; then
        echo "OS: $(. /etc/os-release; echo "$PRETTY_NAME")"
    fi
    echo
    echo "| Status | Component | Version | Note |"
    echo "|---|---|---|---|"
    while IFS=$'\t' read -r st comp ver note; do
        echo "| $st | $comp | $ver | $note |"
    done < "$ROWS"
    echo
    echo "FAIL=$FAILS WARN=$WARNS"
} > "$REPORT"

echo
printf '%-6s %-28s %-30s %s\n' "STATUS" "COMPONENT" "VERSION" "NOTE"
printf '%s\n' "--------------------------------------------------------------------------------------"
while IFS=$'\t' read -r st comp ver note; do
    printf '%-6s %-28s %-30s %s\n' "$st" "$(echo "$comp" | cut -c1-28)" "$(echo "$ver" | cut -c1-30)" "$(echo "$note" | cut -c1-60)"
done < "$ROWS"
echo
echo "FAIL=$FAILS WARN=$WARNS  -> $REPORT"

[ "$FAILS" -gt 0 ] && exit 1
exit 0
