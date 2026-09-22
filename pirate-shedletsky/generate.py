#!/usr/bin/env python3
"""
generate.py — builds a solid, low-poly "Pirate Shedletsky" Roblox figure
(classic R6 blocky proportions: yellow skin, black torso, blue legs, black
tricorn-style pirate hat) as binary STL files, from scratch. No downloaded
model — every part is a box primitive.

Outputs (this directory):
    shedletsky_body_solid.stl   — head + torso + arms + legs, one fused mesh
    shedletsky_hat.stl          — pirate hat (brim + band + crown), separate piece
    shedletsky_got_root_plaque.stl — thin flat plaque for the "got root?" shirt text

Body and hat are separate STLs on purpose: the hat has a wide overhanging
brim that's easier to print flat (no supports) and easier to paint before
gluing on than if fused to the head.

Coordinate system per part: X = left-right, Y = front-back, Z = up (0 = the
part's own resting face — the STL packer re-normalizes min-Z to 0 anyway).
"""

import struct
from pathlib import Path

OUT_DIR = Path(__file__).parent


def box_triangles(cx, cy, cz, dx, dy, dz):
    """Axis-aligned box centered at (cx,cy,cz), full extents dx,dy,dz. Returns 12 triangles."""
    x0, x1 = cx - dx / 2, cx + dx / 2
    y0, y1 = cy - dy / 2, cy + dy / 2
    z0, z1 = cz - dz / 2, cz + dz / 2
    v = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),  # bottom 0-3
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),  # top 4-7
    ]
    faces = [
        (0, 1, 2), (0, 2, 3),   # bottom
        (4, 6, 5), (4, 7, 6),   # top
        (0, 5, 1), (0, 4, 5),   # -Y side
        (1, 6, 2), (1, 5, 6),   # +X side
        (2, 7, 3), (2, 6, 7),   # +Y side
        (3, 4, 0), (3, 7, 4),   # -X side
    ]
    return [(v[a], v[b], v[c]) for a, b, c in faces]


def write_binary_stl(path: Path, triangles: list) -> int:
    """Write a binary STL. Returns triangle count."""
    with open(path, "wb") as f:
        header = b"generate.py - pirate shedletsky - box primitives"
        f.write(header[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(triangles)))
        for v0, v1, v2 in triangles:
            ux, uy, uz = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
            wx, wy, wz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
            nx = uy * wz - uz * wy
            ny = uz * wx - ux * wz
            nz = ux * wy - uy * wx
            length = (nx ** 2 + ny ** 2 + nz ** 2) ** 0.5 or 1.0
            nx, ny, nz = nx / length, ny / length, nz / length
            f.write(struct.pack("<3f", nx, ny, nz))
            for v in (v0, v1, v2):
                f.write(struct.pack("<3f", *v))
            f.write(struct.pack("<H", 0))
    return len(triangles)


# ---------------------------------------------------------------------------
# BODY — legs, torso, arms, head. Overlaps of ~1mm at every joint so the
# fused mesh welds solid (no visible seam gaps, no risk of a shell-only
# connection at part boundaries).
# ---------------------------------------------------------------------------
def build_body():
    tris = []

    LEG_W, LEG_D, LEG_H = 12, 12, 30
    leg_z = LEG_H / 2
    tris += box_triangles(-5.85, 0, leg_z, LEG_W, LEG_D, LEG_H)  # left leg
    tris += box_triangles(5.85, 0, leg_z, LEG_W, LEG_D, LEG_H)   # right leg

    TORSO_W, TORSO_D, TORSO_H = 26, 14, 30
    torso_bottom = LEG_H - 1  # 1mm overlap into legs
    torso_z = torso_bottom + TORSO_H / 2
    tris += box_triangles(0, 0, torso_z, TORSO_W, TORSO_D, TORSO_H)
    torso_top = torso_bottom + TORSO_H

    ARM_W, ARM_D, ARM_H = 10, 10, 32
    arm_z = torso_top - ARM_H / 2  # shoulders flush with top of torso
    arm_x = TORSO_W / 2 + ARM_W / 2 - 1  # 1mm overlap into torso
    tris += box_triangles(-arm_x, 0, arm_z, ARM_W, ARM_D, ARM_H)  # left arm
    tris += box_triangles(arm_x, 0, arm_z, ARM_W, ARM_D, ARM_H)   # right arm

    HEAD_W, HEAD_D, HEAD_H = 20, 16, 18
    head_bottom = torso_top - 1  # 1mm overlap into torso
    head_z = head_bottom + HEAD_H / 2
    tris += box_triangles(0, 0, head_z, HEAD_W, HEAD_D, HEAD_H)
    head_top = head_bottom + HEAD_H

    total_height = head_top  # feet at z=0
    return tris, total_height


# ---------------------------------------------------------------------------
# HAT — simplified blocky pirate tricorn: wide flat brim, a band, a crown.
# Standalone piece, own local frame (brim rests on the print bed).
# ---------------------------------------------------------------------------
def build_hat():
    tris = []

    BRIM_W, BRIM_D, BRIM_H = 34, 26, 3
    brim_z = BRIM_H / 2
    tris += box_triangles(0, 0, brim_z, BRIM_W, BRIM_D, BRIM_H)

    BAND_W, BAND_D, BAND_H = 22, 16, 2
    band_bottom = BRIM_H - 0.5
    band_z = band_bottom + BAND_H / 2
    tris += box_triangles(0, 0, band_z, BAND_W, BAND_D, BAND_H)
    band_top = band_bottom + BAND_H

    CROWN_W, CROWN_D, CROWN_H = 20, 14, 10
    crown_bottom = band_top - 0.5
    crown_z = crown_bottom + CROWN_H / 2
    tris += box_triangles(0, 0, crown_z, CROWN_W, CROWN_D, CROWN_H)
    crown_top = crown_bottom + CROWN_H

    return tris, crown_top


# ---------------------------------------------------------------------------
# PLAQUE — thin flat rectangle for the "got root?" shirt graphic, glued to
# the torso front after printing. Hand-letter, paint-pen, or printed sticker.
# ---------------------------------------------------------------------------
def build_plaque():
    PLAQUE_W, PLAQUE_D, PLAQUE_H = 20, 10, 1.2
    tris = box_triangles(0, 0, PLAQUE_H / 2, PLAQUE_W, PLAQUE_D, PLAQUE_H)
    return tris, PLAQUE_H


def main():
    body_tris, body_h = build_body()
    hat_tris, hat_h = build_hat()
    plaque_tris, plaque_h = build_plaque()

    body_path = OUT_DIR / "shedletsky_body_solid.stl"
    hat_path = OUT_DIR / "shedletsky_hat.stl"
    plaque_path = OUT_DIR / "shedletsky_got_root_plaque.stl"

    n1 = write_binary_stl(body_path, body_tris)
    n2 = write_binary_stl(hat_path, hat_tris)
    n3 = write_binary_stl(plaque_path, plaque_tris)

    print(f"{body_path.name}: {n1} triangles, body height {body_h:.1f} mm (feet to top of head)")
    print(f"{hat_path.name}: {n2} triangles, hat height {hat_h:.1f} mm")
    print(f"{plaque_path.name}: {n3} triangles, plaque {plaque_h:.1f} mm thick")


if __name__ == "__main__":
    main()
