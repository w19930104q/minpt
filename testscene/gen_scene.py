#!/usr/bin/env python3
"""Generate a fixed test scene for minpt BVH A/B comparison.

Cornell-box-like scene exercising: diffuse (Lambertian), perfect mirror
(illum 5), Fresnel glass (illum 7), anisotropic-capable glossy GGX, and an
area light. Deterministic output (no randomness).
"""
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scene.obj")
MTL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scene.mtl")

verts = []   # 1-based in OBJ
groups = []  # list of (material, [faces]) where face = tuple of vertex indices


def add_v(x, y, z):
    verts.append((x, y, z))
    return len(verts)


def add_quad(mtl, p1, p2, p3, p4):
    ids = [add_v(*p) for p in (p1, p2, p3, p4)]
    groups.append((mtl, [tuple(ids)]))


def add_sphere(mtl, cx, cy, cz, r, nseg=48, nring=24):
    base = len(verts)
    for i in range(nring + 1):
        th = math.pi * i / nring
        for j in range(nseg):
            ph = 2 * math.pi * j / nseg
            verts.append((cx + r * math.sin(th) * math.cos(ph),
                          cy + r * math.cos(th),
                          cz + r * math.sin(th) * math.sin(ph)))
    faces = []
    for i in range(nring):
        for j in range(nseg):
            a = base + i * nseg + j + 1
            b = base + i * nseg + (j + 1) % nseg + 1
            c = base + (i + 1) * nseg + (j + 1) % nseg + 1
            d = base + (i + 1) * nseg + j + 1
            if i > 0:
                faces.append((a, b, c))      # outward (CCW from outside)
            if i < nring - 1:
                faces.append((a, c, d))
    groups.append((mtl, faces))


# Box: x in [-1,1], y in [0,2], z in [-1,1], front open, normals inward.
add_quad("white", (-1, 0, -1), (-1, 0, 1), (1, 0, 1), (1, 0, -1))      # floor +y
add_quad("white", (-1, 2, -1), (1, 2, -1), (1, 2, 1), (-1, 2, 1))      # ceil  -y
add_quad("white", (-1, 0, -1), (1, 0, -1), (1, 2, -1), (-1, 2, -1))    # back  +z
add_quad("red",   (-1, 0, -1), (-1, 2, -1), (-1, 2, 1), (-1, 0, 1))    # left  +x
add_quad("green", (1, 0, -1), (1, 0, 1), (1, 2, 1), (1, 2, -1))        # right -x

# Area light on ceiling, normal pointing down (-y).
add_quad("light", (-0.35, 1.99, -0.35), (0.35, 1.99, -0.35),
                  (0.35, 1.99, 0.35), (-0.35, 1.99, 0.35))

# Spheres: mirror, glass, glossy.
add_sphere("mirror", -0.45, 0.50, 0.25, 0.50)
add_sphere("glass",   0.45, 0.50, -0.25, 0.50)
add_sphere("glossy",  0.20, 0.26, 0.60, 0.26)

with open(MTL, "w") as f:
    f.write("""newmtl white
Kd 0.72 0.72 0.72
Ns 10
illum 2

newmtl red
Kd 0.65 0.12 0.12
Ns 10
illum 2

newmtl green
Kd 0.12 0.65 0.12
Ns 10
illum 2

newmtl mirror
illum 5

newmtl glass
Ni 1.5
illum 7

newmtl glossy
Kd 0.10 0.10 0.10
Ks 0.90 0.90 0.90
Ns 100
illum 2

newmtl light
Kd 0 0 0
Ke 18 18 18
illum 2
""")

with open(OUT, "w") as f:
    f.write("mtllib scene.mtl\n")
    for x, y, z in verts:
        f.write(f"v {x:.9f} {y:.9f} {z:.9f}\n")
    for mtl, faces in groups:
        f.write(f"usemtl {mtl}\n")
        for fc in faces:
            f.write("f " + " ".join(str(i) for i in fc) + "\n")

ntri = sum(len(fc) * 2 for _, faces in groups for fc in faces)
print(f"wrote {OUT}: {len(verts)} verts, ~{ntri} tris (quads count as 2)")
