#!/usr/bin/env python3
"""Compare two minpt_bvh stats files per-pixel.

Checks: image hash, and per-pixel rays / depth / nan (must match between
scene-semantics-preserving runs); nodes / tris may differ (that is the
acceleration-structure effect being measured).
"""
import sys


def load(path):
    meta, rows = {}, []
    with open(path) as f:
        for line in f:
            t = line.split()
            if not t or t[0] == "#":
                continue
            if len(t) == 2:
                meta[t[0]] = t[1]
            elif len(t) == 7:
                rows.append(tuple(int(v) for v in t))
    return meta, rows


def main(pa, pb):
    ma, ra = load(pa)
    mb, rb = load(pb)
    print(f"A: {pa}  (mode={ma['mode']})")
    print(f"B: {pb}  (mode={mb['mode']})")
    assert len(ra) == len(rb), "pixel count mismatch"

    same_img = ma["img_hash"] == mb["img_hash"]
    print(f"img_hash   A={ma['img_hash']}  B={mb['img_hash']}  "
          f"{'MATCH' if same_img else 'DIFFER'}")

    # per-pixel fields: x y rays nodes tris depth nan
    fields = {"rays": 2, "nodes": 3, "tris": 4, "depth": 5, "nan": 6}
    for name, idx in fields.items():
        diffs = [(a, b) for a, b in zip(ra, rb) if a[idx] != b[idx]]
        ta = sum(r[idx] for r in ra)
        tb = sum(r[idx] for r in rb)
        ratio = (tb / ta) if ta else float("nan")
        print(f"{name:6s}  total A={ta:<10d} B={tb:<10d} B/A={ratio:.4f}  "
              f"per-pixel diffs={len(diffs)}")
        if diffs and name in ("rays", "depth", "nan"):
            x, y = diffs[0][0][0], diffs[0][0][1]
            print(f"  first diff at pixel ({x},{y}): "
                  f"A={diffs[0][0][idx]} B={diffs[0][1][idx]}")

    ok = (same_img
          and all(a[2] == b[2] for a, b in zip(ra, rb))
          and all(a[5] == b[5] for a, b in zip(ra, rb))
          and all(a[6] == b[6] for a, b in zip(ra, rb)))
    print("VERDICT:", "CONSISTENT (semantics preserved)"
          if ok else "MISMATCH — scene semantics changed!")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
