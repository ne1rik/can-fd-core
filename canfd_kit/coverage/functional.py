"""CAN FD functional coverage: bins, crosses, persistence, merge.

Cross cells that the protocol makes impossible are declared `illegal` and
excluded from the denominator, so coverage cannot be padded or penalised by
dead combinations.
"""

from dataclasses import dataclass, field
from typing import List
import json


@dataclass
class CoverageBin:
    name: str
    description: str
    expected: int = 1
    actual: int = 0

    @property
    def hit(self) -> bool:
        return self.actual >= self.expected

    @property
    def percentage(self) -> float:
        if self.expected == 0:
            return 100.0
        return min(100.0, (self.actual / self.expected) * 100)


@dataclass
class CoverageGroup:
    name: str
    description: str
    bins: List[CoverageBin]

    @property
    def covered_bins(self) -> int:
        return sum(1 for b in self.bins if b.hit)

    @property
    def total_bins(self) -> int:
        return len(self.bins)

    @property
    def percentage(self) -> float:
        return (self.covered_bins / self.total_bins * 100) if self.total_bins else 100.0

    def sample(self, value) -> bool:
        for b in self.bins:
            if b.name == str(value):
                b.actual += 1
                return True
        return False

    def merge(self, other: "CoverageGroup"):
        idx = {b.name: b for b in self.bins}
        for b in other.bins:
            if b.name in idx:
                idx[b.name].actual += b.actual


@dataclass
class CoverageCross:
    name: str
    description: str
    group1: CoverageGroup
    group2: CoverageGroup
    hits: dict = field(default_factory=dict)
    illegal: tuple = ()          # tuple of (str, str) protocol-impossible cells

    @property
    def _illegal(self):
        return {tuple(x) for x in self.illegal}

    def sample(self, v1, v2):
        key = (str(v1), str(v2))
        self.hits[key] = self.hits.get(key, 0) + 1

    @property
    def expected_bins(self) -> int:
        return self.group1.total_bins * self.group2.total_bins - len(self._illegal)

    @property
    def covered_bins(self) -> int:
        ill = self._illegal
        return sum(1 for k, v in self.hits.items() if v > 0 and tuple(k) not in ill)

    @property
    def illegal_hits(self) -> int:
        ill = self._illegal
        return sum(1 for k, v in self.hits.items() if v > 0 and tuple(k) in ill)

    @property
    def percentage(self) -> float:
        return (self.covered_bins / self.expected_bins * 100) if self.expected_bins else 100.0

    def merge(self, other: "CoverageCross"):
        for k, v in other.hits.items():
            key = tuple(k)
            self.hits[key] = self.hits.get(key, 0) + v


class CANFDCoverage:
    """CAN FD functional coverage collector."""

    SCHEMA = 2

    def __init__(self):
        self.dlc = CoverageGroup("dlc", "Data Length Code",
            [CoverageBin(str(i), f"DLC={i}") for i in range(16)])

        self.brs = CoverageGroup("brs", "Bit Rate Switch", [
            CoverageBin("0", "BRS=0"), CoverageBin("1", "BRS=1")])

        self.crc_width = CoverageGroup("crc_width", "CRC field width", [
            CoverageBin("17", "CRC-17 (payload <= 16B)"),
            CoverageBin("21", "CRC-21 (payload > 16B)")])

        self.data_pattern = CoverageGroup("data_pattern", "Payload pattern", [
            CoverageBin("zeros", "All zeros"),
            CoverageBin("ones", "All ones"),
            CoverageBin("alternating", "0xAA/0x55"),
            CoverageBin("ramp", "Sequential ramp"),
            CoverageBin("random", "Pseudo-random")])

        self.id_range = CoverageGroup("id_range", "Identifier buckets", [
            CoverageBin("0x000", "ID=0x000"),
            CoverageBin("0x001-0x1FF", "ID 0x001-0x1FF"),
            CoverageBin("0x200-0x3FF", "ID 0x200-0x3FF"),
            CoverageBin("0x400-0x5FF", "ID 0x400-0x5FF"),
            CoverageBin("0x600-0x7FF", "ID 0x600-0x7FF")])

        self.stuff_density = CoverageGroup("stuff_density", "Dynamic stuff count", [
            CoverageBin("none", "0"), CoverageBin("low", "1-5"),
            CoverageBin("medium", "6-20"), CoverageBin("high", ">20")])

        self.error_type = CoverageGroup("error_type", "Injected fault", [
            CoverageBin("none", "No fault"),
            CoverageBin("payload_flip", "Payload bit flip"),
            CoverageBin("crc_flip", "CRC bit flip"),
            CoverageBin("stuff_flip", "Dynamic stuff bit flip"),
            CoverageBin("sc_flip", "Stuff count bit flip")])

        self.cross_dlc_brs = CoverageCross(
            "dlc_x_brs", "DLC x BRS", self.dlc, self.brs)

        self.cross_id_pattern = CoverageCross(
            "id_x_pattern", "ID bucket x payload pattern", self.id_range, self.data_pattern)

        # DLC=0 carries no payload, so a payload bit flip is impossible there.
        self.cross_error_dlc = CoverageCross(
            "error_x_dlc", "Fault type x DLC", self.error_type, self.dlc,
            illegal=(("payload_flip", "0"),))

        # dlc_x_crc intentionally absent: DLC determines CRC width by ISO
        # (0..10 -> CRC-17, 11..15 -> CRC-21). 16 of 32 cells are dead.

        self.groups = [self.dlc, self.brs, self.crc_width, self.data_pattern,
                       self.id_range, self.stuff_density, self.error_type]
        self.crosses = [self.cross_dlc_brs, self.cross_id_pattern, self.cross_error_dlc]

    # ---------- classification ----------

    @staticmethod
    def classify_pattern(data) -> str:
        if not data or all(b == 0x00 for b in data):
            return "zeros"
        if all(b == 0xFF for b in data):
            return "ones"
        if all(b == (0xAA if i % 2 == 0 else 0x55) for i, b in enumerate(data)):
            return "alternating"
        if all(b == (i & 0xFF) for i, b in enumerate(data)):
            return "ramp"
        return "random"

    @staticmethod
    def classify_id(fid: int) -> str:
        if fid == 0x000:
            return "0x000"
        if fid <= 0x1FF:
            return "0x001-0x1FF"
        if fid <= 0x3FF:
            return "0x200-0x3FF"
        if fid <= 0x5FF:
            return "0x400-0x5FF"
        return "0x600-0x7FF"

    @staticmethod
    def classify_stuff(count: int) -> str:
        if count == 0:
            return "none"
        if count <= 5:
            return "low"
        if count <= 20:
            return "medium"
        return "high"

    @staticmethod
    def classify_crc_width(dlc: int) -> str:
        from can_fd_reference import dlc_len
        return "21" if dlc_len(dlc) > 16 else "17"

    def sample_frame(self, fid, dlc, data, brs, stuff_count, error="none"):
        pat = self.classify_pattern(data)
        idb = self.classify_id(fid)
        cw = self.classify_crc_width(dlc)

        self.dlc.sample(dlc)
        self.brs.sample(int(brs))
        self.crc_width.sample(cw)
        self.data_pattern.sample(pat)
        self.id_range.sample(idb)
        self.stuff_density.sample(self.classify_stuff(stuff_count))
        self.error_type.sample(error)

        self.cross_dlc_brs.sample(dlc, int(brs))
        self.cross_id_pattern.sample(idb, pat)
        self.cross_error_dlc.sample(error, dlc)

    # ---------- persistence ----------

    def to_dict(self) -> dict:
        return {
            "schema": self.SCHEMA,
            "groups": {g.name: {b.name: b.actual for b in g.bins} for g in self.groups},
            "crosses": {c.name: {f"{k[0]}|{k[1]}": v for k, v in c.hits.items()}
                        for c in self.crosses},
        }

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)

    def load(self, path: str):
        with open(path) as f:
            data = json.load(f)
        if data.get("schema") != self.SCHEMA:
            raise ValueError(f"{path}: schema {data.get('schema')} != {self.SCHEMA}")
        gidx = {g.name: g for g in self.groups}
        for gname, bins in data.get("groups", {}).items():
            if gname not in gidx:
                continue
            bidx = {b.name: b for b in gidx[gname].bins}
            for bname, n in bins.items():
                if bname in bidx:
                    bidx[bname].actual += n
        cidx = {c.name: c for c in self.crosses}
        for cname, hits in data.get("crosses", {}).items():
            if cname not in cidx:
                continue
            for key, n in hits.items():
                a, b = key.split("|", 1)
                cidx[cname].hits[(a, b)] = cidx[cname].hits.get((a, b), 0) + n
        return self


class CoverageReport:
    def __init__(self, cov: CANFDCoverage):
        self.cov = cov

    @property
    def point_percentage(self) -> float:
        t = sum(g.total_bins for g in self.cov.groups)
        c = sum(g.covered_bins for g in self.cov.groups)
        return (c / t * 100) if t else 100.0

    @property
    def cross_percentage(self) -> float:
        t = sum(x.expected_bins for x in self.cov.crosses)
        c = sum(x.covered_bins for x in self.cov.crosses)
        return (c / t * 100) if t else 100.0

    @property
    def overall_percentage(self) -> float:
        """Points and crosses weighted by bin count. Crosses are NOT ignored."""
        t = sum(g.total_bins for g in self.cov.groups) + \
            sum(x.expected_bins for x in self.cov.crosses)
        c = sum(g.covered_bins for g in self.cov.groups) + \
            sum(x.covered_bins for x in self.cov.crosses)
        return (c / t * 100) if t else 100.0

    def uncovered(self) -> dict:
        out = {}
        for g in self.cov.groups:
            miss = [b.name for b in g.bins if not b.hit]
            if miss:
                out[g.name] = miss
        for x in self.cov.crosses:
            ill = x._illegal
            miss = []
            for b1 in x.group1.bins:
                for b2 in x.group2.bins:
                    k = (b1.name, b2.name)
                    if k in ill:
                        continue
                    if x.hits.get(k, 0) == 0:
                        miss.append(f"{k[0]} x {k[1]}")
            if miss:
                out[x.name] = miss
        return out

    def to_dict(self) -> dict:
        return {
            "overall": round(self.overall_percentage, 1),
            "points": round(self.point_percentage, 1),
            "crosses_pct": round(self.cross_percentage, 1),
            "groups": {g.name: {"covered": g.covered_bins, "total": g.total_bins,
                                "percentage": round(g.percentage, 1),
                                "bins": {b.name: b.actual for b in g.bins}}
                       for g in self.cov.groups},
            "crosses": {x.name: {"covered": x.covered_bins, "expected": x.expected_bins,
                                 "percentage": round(x.percentage, 1),
                                 "illegal_hits": x.illegal_hits}
                        for x in self.cov.crosses},
            "uncovered": self.uncovered(),
        }

    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)

    def to_markdown(self) -> str:
        L = ["# CAN FD Functional Coverage", "",
             f"**Overall: {self.overall_percentage:.1f}%** "
             f"(points {self.point_percentage:.1f}%, crosses {self.cross_percentage:.1f}%)", "",
             "## CoverPoints", "", "| Group | Covered | Total | % |", "|---|---|---|---|"]
        for g in self.cov.groups:
            L.append(f"| {g.name} | {g.covered_bins} | {g.total_bins} | {g.percentage:.1f}% |")
        L += ["", "## CoverCrosses", "", "| Cross | Covered | Legal | % |", "|---|---|---|---|"]
        for x in self.cov.crosses:
            L.append(f"| {x.name} | {x.covered_bins} | {x.expected_bins} | {x.percentage:.1f}% |")
        miss = self.uncovered()
        L += ["", "## Uncovered", ""]
        if not miss:
            L.append("None — all legal bins hit.")
        else:
            for k, v in miss.items():
                shown = v if len(v) <= 12 else v[:12] + [f"... +{len(v)-12} more"]
                L.append(f"- **{k}**: {', '.join(shown)}")
        return "\n".join(L) + "\n"

    def to_file(self, path: str):
        with open(path, "w") as f:
            f.write(self.to_markdown())
