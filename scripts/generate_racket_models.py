#!/usr/bin/env python3
"""Build one .glb per racket from its livery (models/rackets/liveries/<id>.json).

The geometry matches the app's low-poly racket (tennis-life/tool/generate_models.py):
same head, throat, shaft and handle measurements, so the connector positions used
by the app keep working. The livery decides where each color sits.

    python3 -m venv .venv && .venv/bin/pip install trimesh numpy shapely mapbox_earcut matplotlib
    .venv/bin/python scripts/generate_racket_models.py [--preview]
"""

import argparse
import json
import math
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from trimesh.visual.material import PBRMaterial

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "models" / "rackets"
LIVERIES = OUT / "liveries"
PREVIEWS = OUT / "previews"
RACKETS = ROOT / "data" / "rackets.json"

CY, RX, RY, FR = 0.52, 0.125, 0.16, 0.011
THROAT_TOP = CY - RY
LEFT_ARM = ([-0.06, THROAT_TOP + 0.012, 0], [-0.008, 0.25, 0])
RIGHT_ARM = ([0.06, THROAT_TOP + 0.012, 0], [0.008, 0.25, 0])

ROLES = ("main", "second", "third", "fourth")
# Material names: the app recolors "frame" with the user's color, so the dominant role keeps that name.
ROLE_MATERIAL = {"main": "frame", "second": "frame_black", "third": "frame_white", "fourth": "frame_accent"}
FINISHES = {"gloss": (0.3, 0.0), "satin": (0.5, 0.0), "matte": (0.78, 0.0), "metallic": (0.32, 0.6)}


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def material(name, hex_color, rough, metal=0.0):
    m = PBRMaterial(
        baseColorFactor=[c / 255 for c in rgb(hex_color)] + [1.0],
        roughnessFactor=rough,
        metallicFactor=metal,
    )
    m.name = name
    return m


def tube(points, radius, sections=14):
    pts = np.asarray(points, dtype=float)
    return trimesh.creation.sweep_polygon(Point(0, 0).buffer(radius, quad_segs=max(2, sections // 4)), pts)


def cyl(a, b, r, sections=24):
    return trimesh.creation.cylinder(radius=r, segment=[a, b], sections=sections)


def extrude(poly, depth, z0=0.0):
    m = trimesh.creation.extrude_polygon(poly, depth)
    m.apply_translation([0, 0, z0 - depth / 2])
    return m


def head_arc(a0, a1, r, n, offset=0.0, z=0.0):
    t = np.radians(np.linspace(a0, a1, n))
    return np.c_[(RX + offset) * np.cos(t), CY + (RY + offset) * np.sin(t), np.full_like(t, z)]


def along(seg, f0, f1):
    a, b = np.asarray(seg[0]), np.asarray(seg[1])
    return a + (b - a) * f0, a + (b - a) * f1


# ---------------------------------------------------------------- stencils

def _strokes(lines, width):
    return unary_union([LineString(pts).buffer(width / 2, cap_style=2, join_style=2) for pts in lines])


def stencil_shape(shape):
    """Brand mark on the string bed, in head coordinates (meters)."""
    c = CY
    w = 0.018
    shapes = {
        "babolat": unary_union([
            Polygon([(-0.005, c - 0.12), (0.035, c - 0.12), (0.115, c + 0.03), (0.075, c + 0.03)]),
            Polygon([(0.05, c - 0.12), (0.075, c - 0.12), (0.125, c - 0.03), (0.1, c - 0.03)]),
        ]),
        "wilson": _strokes([[(-0.075, c + 0.05), (-0.04, c - 0.06), (0.0, c + 0.03), (0.04, c - 0.06), (0.075, c + 0.05)]], w),
        "head": _strokes([[(-0.07, c + 0.0), (0.07, c + 0.0)], [(-0.07, c - 0.045), (-0.07, c + 0.045)], [(0.07, c - 0.045), (0.07, c + 0.045)]], w),
        "yonex": _strokes([[(-0.055, c + 0.07), (0.0, c + 0.0)], [(0.055, c + 0.07), (0.0, c + 0.0)], [(0.0, c + 0.0), (0.0, c - 0.08)]], w),
        "tecnifibre": _strokes([[(-0.065, c + 0.06), (0.065, c + 0.06)], [(0.0, c + 0.06), (0.0, c - 0.08)]], w),
        "dunlop": _strokes([[(-0.06, c + 0.06), (0.0, c - 0.02), (0.06, c + 0.06)], [(-0.06, c + 0.0), (0.0, c - 0.08), (0.06, c + 0.0)]], w),
        "prince": _strokes([[(-0.03, c - 0.08), (-0.03, c + 0.07), (0.035, c + 0.07), (0.05, c + 0.04), (0.035, c + 0.01), (-0.03, c + 0.01)]], w),
        "volkl": _strokes([[(-0.06, c + 0.07), (0.0, c - 0.08), (0.06, c + 0.07)]], w),
    }
    return shapes.get(shape)


# ---------------------------------------------------------------- build

def build(livery):
    palette = {r: livery["palette"].get(r) or livery["palette"]["main"] for r in ROLES}
    rough, metal = FINISHES[livery.get("finish", "gloss")]
    parts = {r: [] for r in ROLES}

    def add(role, mesh):
        parts[role if role in ROLES else "main"].append(mesh)

    for seg in livery["head"]:
        a0, a1 = float(seg["from"]), float(seg["to"])
        if a1 <= a0:
            continue
        n = max(4, int((a1 - a0) / 3))
        add(seg["role"], tube(head_arc(a0, a1, FR, n), FR))

    add(livery.get("bumper", "second"), tube(head_arc(62, 118, FR, 24, offset=0.006), 0.0075))

    throat = livery.get("throat", {})
    add(throat.get("left", "main"), cyl(*LEFT_ARM, 0.0095))
    add(throat.get("right", "main"), cyl(*RIGHT_ARM, 0.0095))
    add(throat.get("bridge", "main"), cyl([-0.045, THROAT_TOP + 0.004, 0], [0.045, THROAT_TOP + 0.004, 0], 0.006))

    for g in livery.get("throatGraphics", []):
        arms = {"left": [LEFT_ARM], "right": [RIGHT_ARM], "both": [LEFT_ARM, RIGHT_ARM]}[g.get("side", "right")]
        f0, f1 = float(g["from"]), float(g["to"])
        for arm in arms:
            if g.get("style") == "blocks":
                step = (f1 - f0) / 5
                for i in range(5):
                    s = f0 + i * step
                    add(g["role"], cyl(*along(arm, s, s + step * 0.72), 0.0099, 10))
            else:
                add(g["role"], cyl(*along(arm, f0, f1), 0.0099, 12))

    add(livery.get("shaft", "main"), cyl([0, 0.19, 0], [0, 0.26, 0], 0.013))
    add(livery.get("collar", "second"), cyl([0, 0.185, 0], [0, 0.198, 0], 0.0185, sections=8))
    add(livery.get("cap", "second"), cyl([0, -0.012, 0], [0, 0.0, 0], 0.0195, sections=8))
    add(livery.get("capBand", "main"), cyl([0, 0.0, 0], [0, 0.006, 0], 0.0188, sections=8))

    grommets = []
    for a in np.linspace(0, 360, 44, endpoint=False):
        p = head_arc(a, a, FR, 1)[0]
        for z in (FR * 0.92, -FR * 0.92):
            g = trimesh.creation.icosphere(subdivisions=0, radius=0.0022)
            g.apply_translation([p[0], p[1], z])
            grommets.append(g)

    strings = []
    for x in np.linspace(-RX + 0.016, RX - 0.016, 16):
        h = RY * math.sqrt(max(0.0, 1 - (x / RX) ** 2)) - 0.004
        strings.append(cyl([x, CY - h, 0], [x, CY + h, 0], 0.0016, 6))
    for y in np.linspace(-RY + 0.018, RY - 0.018, 19):
        w = RX * math.sqrt(max(0.0, 1 - (y / RY) ** 2)) - 0.004
        strings.append(cyl([-w, CY + y, 0], [w, CY + y, 0], 0.0016, 6))

    handle = cyl([0, 0.0, 0], [0, 0.19, 0], 0.0175, sections=8)
    t = np.linspace(0, 2 * math.pi, 16, endpoint=False)
    wraps = trimesh.util.concatenate([
        tube(np.vstack([c := np.c_[0.0182 * np.cos(t), np.full_like(t, y), 0.0182 * np.sin(t)], c[:1]]), 0.0011, sections=6)
        for y in np.linspace(0.025, 0.17, 8)
    ])

    scene = trimesh.Scene()

    def put(name, meshes, mat):
        if not meshes:
            return
        mesh = trimesh.util.concatenate(meshes) if isinstance(meshes, list) else meshes
        mesh.visual = trimesh.visual.TextureVisuals(material=mat)
        scene.add_geometry(mesh, geom_name=name)

    for role in ROLES:
        put(ROLE_MATERIAL[role], parts[role], material(ROLE_MATERIAL[role], palette[role], rough, metal if role == "main" else 0.0))

    grommet_role = livery.get("grommets", "second")
    put("grommets", grommets, material("grommets", palette.get(grommet_role, palette["second"]), 0.6))
    put("strings", strings, material("strings", livery.get("strings", "#E6E6DE"), 0.6))

    st = livery.get("stencil") or {}
    poly = stencil_shape(st.get("shape", "none"))
    if poly is not None:
        bed = Polygon(head_arc(0, 360, 0, 64)[:, :2]).buffer(-0.008)
        clipped = bed.intersection(poly)
        geoms = getattr(clipped, "geoms", [clipped])
        meshes = [extrude(g, 0.0008, z0=z) for g in geoms if g.area > 0 for z in (0.0019, -0.0019)]
        put("stencil", meshes, material("stencil", st.get("color", "#F5F7FA"), 0.7))

    put("handle", [handle], material("handle", livery.get("grip", "#181A1E"), 0.85))
    put("wraps", [wraps], material("wraps", livery.get("wraps", livery.get("grip", "#282A2E")), 0.9))

    scene.metadata["extras"] = {"racketId": livery["id"]}
    return scene


# ---------------------------------------------------------------- preview

def render_preview(scene, path, title):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    polys, colors, depth = [], [], []
    light = np.array([0.35, 0.45, 0.82])
    light /= np.linalg.norm(light)
    for geom in scene.geometry.values():
        base = np.array(geom.visual.material.baseColorFactor[:3], dtype=float)
        if base.max() > 1:
            base = base / 255
        tri = geom.triangles
        normals = geom.face_normals
        shade = 0.45 + 0.55 * np.clip(normals @ light, 0, 1)
        for t_, s in zip(tri, shade):
            if t_[:, 2].mean() < -0.0005 and abs(t_[:, 2]).max() < 0.004:
                continue
            polys.append(t_[:, :2])
            colors.append(np.clip(base * s, 0, 1))
            depth.append(t_[:, 2].mean())
    order = np.argsort(depth)
    fig, ax = plt.subplots(figsize=(3, 6), dpi=120)
    ax.add_collection(PolyCollection([polys[i] for i in order], facecolors=[colors[i] for i in order], edgecolors="none"))
    ax.set_xlim(-0.16, 0.16)
    ax.set_ylim(-0.03, 0.71)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8)
    fig.savefig(path, bbox_inches="tight", facecolor="#F7F8F6")
    plt.close(fig)


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="also render front-view PNGs to models/rackets/previews")
    parser.add_argument("ids", nargs="*", help="only these racket ids")
    args = parser.parse_args()

    rackets = json.loads(RACKETS.read_text())["items"]
    if args.ids:
        rackets = [r for r in rackets if r["id"] in args.ids]
    if args.preview:
        PREVIEWS.mkdir(exist_ok=True)

    index, missing = [], []
    for r in rackets:
        path = LIVERIES / f"{r['id']}.json"
        if not path.exists():
            missing.append(r["id"])
            continue
        livery = json.loads(path.read_text())
        scene = build(livery)
        out = OUT / f"{r['id']}.glb"
        out.write_bytes(scene.export(file_type="glb"))
        if args.preview:
            render_preview(scene, PREVIEWS / f"{r['id']}.png", f"{r['brand']} {r['model']}")
        index.append({
            "id": r["id"],
            "brand": r["brand"],
            "model": r["model"],
            "file": f"models/rackets/{out.name}",
            "year": livery.get("year"),
            "finish": livery.get("finish"),
            "palette": livery["palette"],
            "notes": livery.get("notes"),
        })
        print(f"  {out.name}")

    if not args.ids:
        (OUT / "index.json").write_text(json.dumps({"schemaVersion": 2, "items": index}, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(index)} models written")
    if missing:
        print(f"missing liveries: {', '.join(missing)}")


if __name__ == "__main__":
    main()
