#!/usr/bin/env python3
"""
stl_to_bambu_3mf.py — STL + settings markdown → Bambu Studio .3mf generator.

Ingests one material's STL file(s) plus one settings markdown and emits one
Bambu Studio .3mf (A1 mini, 0.4 nozzle) that loads and slices correctly.
Single material, single plate. Run once per material.

NOTE: This tool does NOT auto-orient objects. Objects import in STL orientation.
Orient them in Bambu Studio before slicing if needed.

CLI:
    python stl_to_bambu_3mf.py \\
      --stl path/a.stl --stl path/b.stl \\
      --settings bambu_a1_mini_PETGCF_QAV-S2_O4Pro_Mounts.md \\
      --material "PETG-CF" \\
      --plate-name "Mounts — PETG-CF" \\
      --output QAV-S2_O4Pro_Mounts_PETG-CF.3mf
"""

import argparse
import json
import logging
import re
import struct
import sys
import uuid
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np

# Import the settings engine from make_bambu_3mf — single source of truth
from make_bambu_3mf import (
    SETTING_KEY_MAP,
    FORBIDDEN_KEY_FRAGMENTS,
    is_forbidden_key,
    parse_settings_markdown,
    apply_settings,
    coerce_value,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# Default template 3MF — a valid A1 mini, 0.4 nozzle Bambu Studio project
DEFAULT_TEMPLATE = Path(__file__).parent / "QAV-S_2_Bardwell_-_O4_Pro_Insert_Left.3mf"

# A1 mini bed dimensions (mm)
BED_X = 180.0
BED_Y = 180.0
PART_GAP = 5.0  # mm gap between parts on the bed


# ---------------------------------------------------------------------------
# STL binary parser — no external deps beyond numpy
# ---------------------------------------------------------------------------
def parse_binary_stl(stl_path: str) -> tuple[np.ndarray, np.ndarray, int]:
    """
    Parse a binary STL file.

    Returns:
        vertices  — (N, 3) float32 array of unique vertices
        triangles — (T, 3) int32 array of vertex indices
        tri_count — number of triangles (for cross-check)
    """
    data = Path(stl_path).read_bytes()
    # 80-byte header, uint32 triangle count
    tri_count = struct.unpack_from("<I", data, 80)[0]

    # Each triangle: 12 floats (normal + 3 verts) + 2-byte attribute = 50 bytes
    expected_size = 84 + tri_count * 50
    if len(data) < expected_size:
        raise ValueError(
            f"{stl_path}: expected {expected_size} bytes, got {len(data)}"
        )

    # Parse all vertices (skip normals at offsets 0-11 per triangle)
    all_verts = []
    offset = 84
    for _ in range(tri_count):
        # Skip normal (12 bytes), read 3 vertices (36 bytes), skip attribute (2 bytes)
        v1 = struct.unpack_from("<3f", data, offset + 12)
        v2 = struct.unpack_from("<3f", data, offset + 24)
        v3 = struct.unpack_from("<3f", data, offset + 36)
        all_verts.append(v1)
        all_verts.append(v2)
        all_verts.append(v3)
        offset += 50

    raw_verts = np.array(all_verts, dtype=np.float32)  # (tri_count*3, 3)

    # Dedupe vertices using a dict for first-occurrence stable order
    rounded = np.round(raw_verts.astype(np.float64), decimals=5)

    seen: dict[tuple, int] = {}
    unique_list = []
    remap = np.empty(len(rounded), dtype=np.int32)

    for i, row in enumerate(rounded):
        key = (round(float(row[0]), 5), round(float(row[1]), 5), round(float(row[2]), 5))
        if key not in seen:
            seen[key] = len(unique_list)
            unique_list.append(row)
        remap[i] = seen[key]

    unique_verts = np.array(unique_list, dtype=np.float64)
    triangles = remap.reshape(-1, 3)

    return unique_verts, triangles, tri_count


# ---------------------------------------------------------------------------
# Mesh bounding box, auto-rotation, and placement
# ---------------------------------------------------------------------------
def mesh_bbox(verts: np.ndarray) -> tuple[float, float, float, float, float, float]:
    """Return (xmin, xmax, ymin, ymax, zmin, zmax)."""
    return (
        float(verts[:, 0].min()), float(verts[:, 0].max()),
        float(verts[:, 1].min()), float(verts[:, 1].max()),
        float(verts[:, 2].min()), float(verts[:, 2].max()),
    )



def arrange_on_bed(meshes: list[tuple[np.ndarray, np.ndarray]]) -> list[tuple[float, float, float]]:
    """
    Compute (tx, ty, tz) translation for each mesh so they rest on the bed
    (min Z = 0) and don't overlap, laid out left-to-right with wrapping.

    Returns list of (tx, ty, tz) per mesh.
    """
    placements = []
    cursor_x = PART_GAP
    cursor_y = PART_GAP
    row_max_y_extent = 0.0

    for verts, _ in meshes:
        xmin, xmax, ymin, ymax, zmin, zmax = mesh_bbox(verts)
        width = xmax - xmin    # extent in X
        depth = ymax - ymin    # extent in Y
        height = zmax - zmin   # extent in Z (unused for placement)

        # Wrap to next row if won't fit
        if cursor_x + width + PART_GAP > BED_X and placements:
            cursor_y += row_max_y_extent + PART_GAP
            cursor_x = PART_GAP
            row_max_y_extent = 0.0

        # Place: translate so xmin→cursor_x, ymin→cursor_y, zmin→0
        tx = cursor_x - xmin
        ty = cursor_y - ymin
        tz = -zmin

        placements.append((tx, ty, tz))
        cursor_x += width + PART_GAP
        row_max_y_extent = max(row_max_y_extent, depth)

    return placements


def center_on_bed(
    meshes: list[tuple[np.ndarray, np.ndarray]],
    placements: list[tuple[float, float, float]],
) -> list[tuple[float, float, float]]:
    """Shift all placements so the group is centered on the A1 mini bed."""
    min_x = min(mesh_bbox(v)[0] + tx for (v, _), (tx, _, _) in zip(meshes, placements))
    max_x = max(mesh_bbox(v)[1] + tx for (v, _), (tx, _, _) in zip(meshes, placements))
    min_y = min(mesh_bbox(v)[2] + ty for (v, _), (_, ty, _) in zip(meshes, placements))
    max_y = max(mesh_bbox(v)[3] + ty for (v, _), (_, ty, _) in zip(meshes, placements))
    offset_x = (BED_X - (max_x - min_x)) / 2.0 - min_x
    offset_y = (BED_Y - (max_y - min_y)) / 2.0 - min_y
    return [(tx + offset_x, ty + offset_y, tz) for tx, ty, tz in placements]


# ---------------------------------------------------------------------------
# 3MF geometry XML generation
# ---------------------------------------------------------------------------
_3MF_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
_BAMBU_NS = "http://schemas.bambulab.com/package/2021"
_PROD_NS = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"


def _gen_uuid() -> str:
    return str(uuid.uuid4())


def build_3dmodel_xml(
    stl_names: list[str],
    meshes: list[tuple[np.ndarray, np.ndarray]],
    placements: list[tuple[float, float, float]],
    object_ids: list[int],
) -> bytes:
    """
    Build the top-level 3D/3dmodel.model XML.
    Each STL becomes one top-level <object> directly containing a <mesh>.
    Build <item> references the object with its placement transform.
    """
    ET.register_namespace("", _3MF_NS)
    ET.register_namespace("BambuStudio", _BAMBU_NS)
    ET.register_namespace("p", _PROD_NS)

    nsmap = {
        "xmlns": _3MF_NS,
        "xml:lang": "en-US",
        "unit": "millimeter",
        f"xmlns:BambuStudio": _BAMBU_NS,
        f"xmlns:p": _PROD_NS,
        "requiredextensions": "p",
    }

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append(
        '<model unit="millimeter" xml:lang="en-US"'
        ' xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
        ' xmlns:BambuStudio="http://schemas.bambulab.com/package/2021"'
        ' xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"'
        ' requiredextensions="p">'
    )
    lines.append(' <metadata name="Application">BambuStudio-02.07.00.55</metadata>')
    lines.append(' <metadata name="BambuStudio:3mfVersion">1</metadata>')
    lines.append(' <resources>')

    for i, (oid, stl_name) in enumerate(zip(object_ids, stl_names)):
        obj_uuid = _gen_uuid()
        lines.append(f'  <object id="{oid}" p:UUID="{obj_uuid}" type="model">')
        # Mesh is embedded directly (no components indirection)
        # The mesh data goes in a separate object_N.model; here we just reference nothing
        # Actually per spec, simpler is fine: embed mesh directly in 3dmodel.model
        # But the template uses external object files — we follow the same pattern
        # to keep rels clean. However, the spec says "simpler scheme is valid."
        # We embed mesh inline in 3dmodel.model for simplicity.
        lines.append('   <mesh>')
        lines.append('    <vertices>')

        verts, tris = meshes[i]
        tx, ty, tz = placements[i]

        for v in verts:
            x = v[0] + tx
            y = v[1] + ty
            z = v[2] + tz
            lines.append(f'     <vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>')

        lines.append('    </vertices>')
        lines.append('    <triangles>')
        for tri in tris:
            lines.append(f'     <triangle v1="{tri[0]}" v2="{tri[1]}" v3="{tri[2]}"/>')
        lines.append('    </triangles>')
        lines.append('   </mesh>')
        lines.append('  </object>')

    lines.append(' </resources>')
    lines.append(' <build p:UUID="' + _gen_uuid() + '">')

    for i, (oid, (tx, ty, tz)) in enumerate(zip(object_ids, placements)):
        item_uuid = _gen_uuid()
        # Identity rotation + translation; mesh already translated in geometry
        # so transform here is identity (mesh coords already in bed space)
        lines.append(
            f'  <item objectid="{oid}" p:UUID="{item_uuid}"'
            f' transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"/>'
        )

    lines.append(' </build>')
    lines.append('</model>')

    return "\n".join(lines).encode("utf-8")


# ---------------------------------------------------------------------------
# model_settings.config generation
# ---------------------------------------------------------------------------
def build_model_settings_new(
    stl_names: list[str],
    object_ids: list[int],
    tri_counts: list[int],
    plate_name: str,
    template_plate_meta: dict | None = None,
) -> bytes:
    """
    Build model_settings.config XML for the new objects + a single named plate.

    template_plate_meta: dict of key->value from the source template's first <plate>
    element. Used to inherit filament_maps and related slot-count values so we stay
    compatible if the template was saved with a different AMS slot count (e.g. 32-slot
    AMS in Bambu Studio 2.7.1.57+). If None, falls back to 6-slot defaults.
    """
    tmpl = template_plate_meta or {}

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<config>')

    for i, (oid, stl_name, tri_count) in enumerate(
        zip(object_ids, stl_names, tri_counts)
    ):
        part_id = oid  # part id = object id (simple scheme)
        lines.append(f'  <object id="{oid}">')
        lines.append(f'    <metadata key="name" value="{stl_name}"/>')
        lines.append(f'    <metadata key="extruder" value="1"/>')
        lines.append(f'    <metadata face_count="{tri_count}"/>')
        lines.append(f'    <part id="{part_id}" subtype="normal_part">')
        lines.append(f'      <metadata key="name" value="{stl_name}"/>')
        lines.append(f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>')
        lines.append(f'      <metadata key="source_file" value="{stl_name}"/>')
        lines.append(f'      <metadata key="source_object_id" value="0"/>')
        lines.append(f'      <metadata key="source_volume_id" value="0"/>')
        lines.append(
            f'      <mesh_stat face_count="{tri_count}" edges_fixed="0"'
            f' degenerate_facets="0" facets_removed="0"'
            f' facets_reversed="0" backwards_edges="0"/>'
        )
        lines.append(f'    </part>')
        lines.append(f'  </object>')

    # Inherit slot-count-dependent values from the template so we don't hardcode
    # a 6-slot assumption. If the template was opened/saved by 2.7.1.57 with a
    # different AMS configuration, these values will carry through correctly.
    filament_map_mode = tmpl.get("filament_map_mode", "Auto For Flush")
    filament_maps = tmpl.get("filament_maps", "1 1 1 1 1 1")
    filament_volume_maps = tmpl.get("filament_volume_maps", "0 0 0 0")

    # Single plate
    lines.append('  <plate>')
    lines.append('    <metadata key="plater_id" value="1"/>')
    lines.append(f'    <metadata key="plater_name" value="{plate_name}"/>')
    lines.append('    <metadata key="locked" value="false"/>')
    lines.append(f'    <metadata key="filament_map_mode" value="{filament_map_mode}"/>')
    lines.append(f'    <metadata key="filament_maps" value="{filament_maps}"/>')
    lines.append(f'    <metadata key="filament_volume_maps" value="{filament_volume_maps}"/>')
    lines.append('    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>')
    lines.append('    <metadata key="thumbnail_no_light_file" value="Metadata/plate_no_light_1.png"/>')
    lines.append('    <metadata key="top_file" value="Metadata/top_1.png"/>')
    lines.append('    <metadata key="pick_file" value="Metadata/pick_1.png"/>')

    for i, oid in enumerate(object_ids):
        identify_id = 10000 + oid * 10
        lines.append('    <model_instance>')
        lines.append(f'      <metadata key="object_id" value="{oid}"/>')
        lines.append(f'      <metadata key="instance_id" value="0"/>')
        lines.append(f'      <metadata key="identify_id" value="{identify_id}"/>')
        lines.append('    </model_instance>')

    lines.append('  </plate>')
    lines.append('</config>')

    return "\n".join(lines).encode("utf-8")


# ---------------------------------------------------------------------------
# Filament-tab temperature extraction (not in summary table)
# ---------------------------------------------------------------------------
def extract_filament_temperatures(md_path: str) -> dict[str, str]:
    """
    Parse the Filament Tab Settings section for nozzle and bed temperatures.
    Returns dict with keys 'nozzle_temperature', 'textured_plate_temp' (values as strings).
    """
    text = Path(md_path).read_text(encoding="utf-8")
    result = {}

    # Find nozzle temperature
    nozzle_match = re.search(
        r"\|\s*Nozzle temperature\s*\|\s*\**(\d+)\**[°℃C]?", text
    )
    if nozzle_match:
        result["nozzle_temperature"] = nozzle_match.group(1)
        log.info(f"Filament tab: nozzle_temperature = {result['nozzle_temperature']}°C")

    # Find bed temperature — may be a range like "35–40°C", take the lower value
    bed_match = re.search(
        r"\|\s*Bed temperature\s*\|\s*\**(\d+)\**[–-]?(\d+)?[°℃C]?", text
    )
    if bed_match:
        result["textured_plate_temp"] = bed_match.group(1)
        log.info(f"Filament tab: textured_plate_temp = {result['textured_plate_temp']}°C")

    # Find fan speed — may be a range like "30–50%"
    fan_match = re.search(
        r"\|\s*Fan speed[^|]*\|\s*\**(\d+)[–-]?(\d+)?\**\s*%?", text
    )
    if fan_match:
        min_val = fan_match.group(1)
        max_val = fan_match.group(2) if fan_match.group(2) else min_val
        result["fan_min_speed"] = min_val
        result["fan_max_speed"] = max_val
        log.info(f"Filament tab: fan_min_speed = {min_val}%, fan_max_speed = {max_val}%")

    # Find max volumetric speed
    mvs_match = re.search(
        r"\|\s*Max volumetric speed\s*\|\s*\**(\d+(?:\.\d+)?)\**", text
    )
    if mvs_match:
        result["filament_max_volumetric_speed"] = mvs_match.group(1)
        log.info(f"Filament tab: filament_max_volumetric_speed = {result['filament_max_volumetric_speed']}")

    return result


def apply_filament_temperatures(
    settings: dict, filament_temps: dict[str, str]
) -> dict:
    """
    Apply nozzle and bed temperatures from filament tab to the settings dict.
    Both are 6-element arrays in project_settings.config.
    """
    import copy
    out = copy.deepcopy(settings)
    for key, str_val in filament_temps.items():
        if key in out:
            source_val = out[key]
            if isinstance(source_val, list):
                updated = list(source_val)
                updated[0] = str_val
                out[key] = updated
            else:
                out[key] = str_val
            log.info(f"Applied filament temp: {key} = {out[key]}")
    return out


# ---------------------------------------------------------------------------
# Main build function
# ---------------------------------------------------------------------------
def build_stl_3mf(
    stl_paths: list[str],
    settings_md: str,
    material: str,
    plate_name: str,
    template_path: str,
    output_path: str,
) -> dict:
    """
    Build the output .3mf from STLs + settings markdown.
    Returns a report dict with settings_report and structural info.
    """
    # --- Parse STLs ---
    log.info(f"Parsing {len(stl_paths)} STL file(s)...")
    meshes = []
    stl_names = []
    tri_counts = []
    for stl_path in stl_paths:
        log.info(f"  Parsing: {stl_path}")
        verts, tris, tri_count = parse_binary_stl(stl_path)
        xmin, xmax, ymin, ymax, zmin, zmax = mesh_bbox(verts)
        log.info(f"    -> {len(verts)} unique vertices, {len(tris)} triangles; "
                 f"dims {xmax-xmin:.1f} x {ymax-ymin:.1f} x {zmax-zmin:.1f} mm")
        meshes.append((verts, tris))
        stl_names.append(Path(stl_path).name)
        tri_counts.append(tri_count)

    # --- Arrange on bed, then center ---
    placements = arrange_on_bed(meshes)
    placements = center_on_bed(meshes, placements)
    log.info("Bed layout (centered):")
    for name, (tx, ty, tz) in zip(stl_names, placements):
        log.info(f"  {name}: translate ({tx:.2f}, {ty:.2f}, {tz:.2f})")

    # --- Object IDs: start at 2, step 2 (Bambu convention) ---
    object_ids = [2 + i * 2 for i in range(len(stl_paths))]

    # --- Load template ---
    log.info(f"Loading template: {template_path}")
    with zipfile.ZipFile(template_path, "r") as tmpl:
        tmpl_infos = {info.filename: info for info in tmpl.infolist()}
        compression_map = {info.filename: info.compress_type for info in tmpl.infolist()}

        # Source settings for type reference
        src_settings = json.loads(tmpl.read("Metadata/project_settings.config"))
        assert isinstance(src_settings, dict), "Template project_settings.config is not a dict"

        # Read template plate metadata (filament_maps, filament_map_mode, etc.)
        # so we can inherit slot-count-dependent values rather than hardcoding them.
        template_plate_meta: dict = {}
        try:
            from xml.etree import ElementTree as _ET
            _ms_xml = tmpl.read("Metadata/model_settings.config")
            _ms_root = _ET.fromstring(_ms_xml)
            for _plate in _ms_root.iter("plate"):
                for _m in _plate.iter("metadata"):
                    _k = _m.get("key")
                    _v = _m.get("value")
                    if _k and _v is not None:
                        template_plate_meta[_k] = _v
                break  # only need first plate
        except Exception as _e:
            log.warning(f"Could not read template plate metadata: {_e} — using defaults")

        # Files to copy verbatim
        verbatim_files = {
            "[Content_Types].xml",
            "Metadata/slice_info.config",
        }

        # Read verbatim files
        verbatim_data = {}
        for fname in verbatim_files:
            if fname in tmpl_infos:
                verbatim_data[fname] = (tmpl.read(fname), compression_map.get(fname, zipfile.ZIP_DEFLATED))

    # --- Parse and apply settings ---
    log.info(f"Parsing settings: {settings_md}")
    md_rows = parse_settings_markdown(settings_md)
    settings, report_rows = apply_settings(src_settings, md_rows, material, src_settings)

    # Apply filament-tab temperatures (not in summary table)
    filament_temps = extract_filament_temperatures(settings_md)
    if filament_temps:
        settings = apply_filament_temperatures(settings, filament_temps)

    # Update filament_settings_id to match the material being used.
    # If the template's slot 0 preset name doesn't match the material, Bambu may
    # reload that preset from its library and override our embedded values.
    # Using a custom name forces Bambu to use only what's in the file.
    if "filament_settings_id" in settings:
        fid = settings["filament_settings_id"]
        if isinstance(fid, list) and fid:
            fid[0] = f"Custom {material} @BBL A1M 0.4 nozzle"
            settings["filament_settings_id"] = fid
            log.info(f"Set filament_settings_id[0] = {fid[0]!r}")
    # Also mark the print preset as custom so Bambu doesn't reload the stock process profile
    settings["print_settings_id"] = f"Custom 0.20mm {material} @BBL A1M"

    # --- Generate geometry ---
    log.info("Generating 3dmodel.model...")
    model_xml = build_3dmodel_xml(stl_names, meshes, placements, object_ids)

    # --- Generate model_settings.config ---
    log.info("Generating model_settings.config...")
    model_settings_xml = build_model_settings_new(
        stl_names, object_ids, tri_counts, plate_name,
        template_plate_meta=template_plate_meta,
    )

    # --- Build minimal _rels/.rels (no thumbnail refs to files we don't include) ---
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        ' <Relationship Target="/3D/3dmodel.model" Id="rel-1"'
        ' Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        '</Relationships>\n'
    ).encode("utf-8")

    # --- Write output zip ---
    log.info(f"Writing: {output_path}")
    out_buf = BytesIO()
    with zipfile.ZipFile(out_buf, "w") as out_zip:

        # Verbatim files
        for fname, (data, compress_type) in verbatim_data.items():
            zi = zipfile.ZipInfo(fname)
            zi.compress_type = compress_type
            out_zip.writestr(zi, data)

        # _rels/.rels (minimal — no thumbnail refs)
        zi = zipfile.ZipInfo("_rels/.rels")
        zi.compress_type = zipfile.ZIP_DEFLATED
        out_zip.writestr(zi, rels_xml)

        # 3D/3dmodel.model
        zi = zipfile.ZipInfo("3D/3dmodel.model")
        zi.compress_type = zipfile.ZIP_DEFLATED
        out_zip.writestr(zi, model_xml)

        # project_settings.config
        settings_bytes = json.dumps(settings, indent=2).encode("utf-8")
        zi = zipfile.ZipInfo("Metadata/project_settings.config")
        zi.compress_type = zipfile.ZIP_DEFLATED
        out_zip.writestr(zi, settings_bytes)

        # model_settings.config
        zi = zipfile.ZipInfo("Metadata/model_settings.config")
        zi.compress_type = zipfile.ZIP_DEFLATED
        out_zip.writestr(zi, model_settings_xml)

        # filament_sequence.json — Bambu Studio uses this to recognize a project
        # file vs a geometry-only import. Without it, settings are ignored.
        filament_seq = json.dumps(
            {"plate_1": {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []}}
        ).encode("utf-8")
        zi = zipfile.ZipInfo("Metadata/filament_sequence.json")
        zi.compress_type = zipfile.ZIP_DEFLATED
        out_zip.writestr(zi, filament_seq)

        # cut_information.xml — expected by Bambu for each object
        cut_lines = ['<?xml version="1.0" encoding="utf-8"?>', "<objects>"]
        for oid in object_ids:
            cut_lines.append(f' <object id="{oid}">')
            cut_lines.append(f'  <cut_id id="0" check_sum="1" connectors_cnt="0"/>')
            cut_lines.append(" </object>")
        cut_lines.append("</objects>")
        cut_xml = "\n".join(cut_lines).encode("utf-8")
        zi = zipfile.ZipInfo("Metadata/cut_information.xml")
        zi.compress_type = zipfile.ZIP_DEFLATED
        out_zip.writestr(zi, cut_xml)

    with open(output_path, "wb") as f:
        f.write(out_buf.getvalue())

    log.info(f"Written: {output_path}")

    return {
        "settings_report": report_rows,
        "object_ids": object_ids,
        "stl_names": stl_names,
        "tri_counts": tri_counts,
        "plate_name": plate_name,
        "filament_temps_applied": filament_temps,
    }


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
def verify_stl_3mf(
    output_path: str,
    stl_paths: list[str],
    material: str,
    expected_settings: dict,
    expected_object_ids: list[int],
    plate_name_fragment: str,
) -> list[tuple[str, bool, str]]:
    """
    Structural verification. Returns list of (check_name, passed, detail).
    """
    checks = []

    # 1. Valid zip
    try:
        z = zipfile.ZipFile(output_path, "r")
        checks.append(("Valid zip", True, ""))
    except Exception as e:
        checks.append(("Valid zip", False, str(e)))
        return checks

    names_in_zip = {info.filename for info in z.infolist()}

    # 2. project_settings.config is a JSON dict
    try:
        data = z.read("Metadata/project_settings.config")
        obj = json.loads(data)
        is_dict = isinstance(obj, dict)
        checks.append(("project_settings.config is JSON dict", is_dict, type(obj).__name__))
    except Exception as e:
        checks.append(("project_settings.config is JSON dict", False, str(e)))
        obj = {}

    # 3. Expected settings values
    for key, expected_val in expected_settings.items():
        actual = obj.get(key, "MISSING")
        if isinstance(actual, list):
            # Check first element for arrays
            actual_check = actual[0] if actual else "EMPTY"
        else:
            actual_check = str(actual)
        match = str(actual_check) == str(expected_val)
        checks.append(
            (
                f"Setting {key}={expected_val}",
                match,
                f"got {actual_check!r}" if not match else "",
            )
        )

    # 4. model_settings.config is valid XML, one <plate>, plate_name contains material
    try:
        data = z.read("Metadata/model_settings.config")
        root = ET.fromstring(data)
        plate_elems = [c for c in root if c.tag == "plate"]
        checks.append(("model_settings.config valid XML", True, ""))
        checks.append(("model_settings.config has 1 plate", len(plate_elems) == 1, f"found {len(plate_elems)}"))

        if plate_elems:
            plate = plate_elems[0]
            plater_name = ""
            for m in plate.iter("metadata"):
                if m.get("key") == "plater_name":
                    plater_name = m.get("value", "")
            has_material = plate_name_fragment.lower() in plater_name.lower()
            checks.append(
                (
                    f"plater_name contains '{plate_name_fragment}'",
                    has_material,
                    f"plater_name={plater_name!r}",
                )
            )

            # Check model_instance count
            model_instances = list(plate.iter("model_instance"))
            checks.append(
                (
                    f"plate has {len(stl_paths)} model_instance(s)",
                    len(model_instances) == len(stl_paths),
                    f"found {len(model_instances)}",
                )
            )

            # Check object IDs match
            actual_oids = set()
            for mi in model_instances:
                for m in mi.iter("metadata"):
                    if m.get("key") == "object_id":
                        actual_oids.add(int(m.get("value")))
            expected_oids_set = set(expected_object_ids)
            checks.append(
                (
                    f"model_instance object_ids match {sorted(expected_oids_set)}",
                    actual_oids == expected_oids_set,
                    f"found {sorted(actual_oids)}",
                )
            )

    except Exception as e:
        checks.append(("model_settings.config valid XML", False, str(e)))

    # 5. 3dmodel.model parses as XML, objects/vertices/triangles > 0
    try:
        data = z.read("3D/3dmodel.model")
        mroot = ET.fromstring(data)
        ns = {"m": _3MF_NS}
        # Count objects
        resources = mroot.find("{%s}resources" % _3MF_NS)
        objs = list(resources.findall("{%s}object" % _3MF_NS)) if resources is not None else []
        checks.append(
            (
                f"3dmodel.model has {len(stl_paths)} object(s)",
                len(objs) == len(stl_paths),
                f"found {len(objs)}",
            )
        )
        for j, stl_path in enumerate(stl_paths):
            stl_name = Path(stl_path).name
            # Find corresponding object
            if j < len(objs):
                obj_elem = objs[j]
                mesh = obj_elem.find("{%s}mesh" % _3MF_NS)
                if mesh is not None:
                    verts_elem = mesh.find("{%s}vertices" % _3MF_NS)
                    tris_elem = mesh.find("{%s}triangles" % _3MF_NS)
                    v_count = len(list(verts_elem)) if verts_elem is not None else 0
                    t_count = len(list(tris_elem)) if tris_elem is not None else 0
                    checks.append(
                        (
                            f"Object {j+1} ({stl_name}) vertices>0",
                            v_count > 0,
                            f"count={v_count}",
                        )
                    )
                    # Triangle count should match source STL
                    # Re-read source STL tri count
                    _, _, src_tri_count = parse_binary_stl(stl_path)
                    checks.append(
                        (
                            f"Object {j+1} ({stl_name}) tri_count={src_tri_count}",
                            t_count == src_tri_count,
                            f"got {t_count}",
                        )
                    )
    except Exception as e:
        checks.append(("3dmodel.model XML parse", False, str(e)))

    # 6. No dangling rels
    try:
        rels_data = z.read("_rels/.rels")
        rels_root = ET.fromstring(rels_data)
        dangling = []
        for rel in rels_root:
            target = rel.get("Target", "").lstrip("/")
            if target and target not in names_in_zip:
                dangling.append(target)
        checks.append(
            (
                "No dangling _rels/.rels references",
                len(dangling) == 0,
                f"missing: {dangling}" if dangling else "",
            )
        )
    except Exception as e:
        checks.append(("_rels/.rels check", False, str(e)))

    z.close()
    return checks


# ---------------------------------------------------------------------------
# Verification report
# ---------------------------------------------------------------------------
def write_verification_report(
    output_path: str,
    results: list[dict],
    report_path: str,
):
    lines = []
    lines.append("=" * 72)
    lines.append("STL TO BAMBU 3MF — STRUCTURAL VERIFICATION REPORT")
    lines.append("=" * 72)
    lines.append("")
    lines.append(
        "NOTE: This report checks file structure only — not slicer acceptance."
    )
    lines.append(
        "Final validation requires loading each file in Bambu Studio."
    )
    lines.append(
        "This script cannot verify that files print correctly."
    )
    lines.append("")

    all_passed = True

    for result in results:
        output = result["output_path"]
        checks = result["checks"]
        settings_report = result.get("settings_report", [])

        lines.append(f"FILE: {output}")
        lines.append("-" * 72)

        if settings_report:
            lines.append("Settings applied:")
            for row in settings_report:
                status = row["status"]
                if "APPLIED" in status:
                    lines.append(
                        f"  APPLIED  {row['json_key']}: {row['old_value']!r} -> {row['new_value']!r}"
                    )
                elif "SKIPPED" in status:
                    lines.append(
                        f"  SKIPPED  {row['human_name']}: {status}"
                    )
            lines.append("")

        lines.append("Structural checks:")
        for check_name, passed, detail in checks:
            status = "PASS" if passed else "FAIL"
            detail_str = f" ({detail})" if detail else ""
            lines.append(f"  [{status}] {check_name}{detail_str}")
            if not passed:
                all_passed = False

        lines.append("")

    lines.append("=" * 72)
    lines.append(f"OVERALL: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")
    lines.append("=" * 72)

    report_text = "\n".join(lines)
    print(report_text)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    log.info(f"Verification report: {report_path}")

    return all_passed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Convert STL files + settings markdown into a Bambu Studio .3mf.\n"
            "Single material, single plate. Run once per material.\n"
            "\n"
            "NOTE: Objects import in STL orientation. Use Bambu Studio to"
            " re-orient if needed — this tool does not auto-orient."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--stl",
        action="append",
        metavar="PATH",
        help="STL file (repeatable; also accepts comma-separated paths)",
        required=False,
    )
    parser.add_argument(
        "--settings",
        required=False,
        metavar="PATH",
        help="Settings markdown file (e.g. bambu_a1_mini_PETGCF_*.md)",
    )
    parser.add_argument(
        "--material",
        required=False,
        metavar="NAME",
        help='Material name (e.g. "PETG-CF", "TPU 95A")',
    )
    parser.add_argument(
        "--plate-name",
        metavar="NAME",
        help='Plate name in Bambu Studio (default: material name). Should mention the material.',
    )
    parser.add_argument(
        "--output",
        required=False,
        default=None,
        metavar="PATH",
        help="Output .3mf file path (default: derived from first STL + material)",
    )
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE),
        metavar="PATH",
        help=f"Template .3mf file (default: {DEFAULT_TEMPLATE.name})",
    )
    parser.add_argument(
        "--print-template",
        action="store_true",
        help="Print SETTINGS_TEMPLATE.md to stdout and exit.",
    )

    args = parser.parse_args(argv)

    # --print-template exits before STL validation — return early here so main()
    # can handle it cleanly without crashing on missing --stl.
    if args.print_template:
        return args

    # Expand comma-separated STL paths
    stl_paths = []
    for entry in (args.stl or []):
        for part in entry.split(","):
            part = part.strip()
            if part:
                stl_paths.append(part)
    args.stl = stl_paths

    if not args.plate_name:
        args.plate_name = args.material

    return args


def main(argv=None):
    args = parse_args(argv)

    if args.print_template:
        template_path = Path(__file__).parent / "SETTINGS_TEMPLATE.md"
        if not template_path.exists():
            print(f"ERROR: SETTINGS_TEMPLATE.md not found at {template_path}", file=sys.stderr)
            sys.exit(1)
        print(template_path.read_text(encoding="utf-8"), end="")
        sys.exit(0)

    # Validate required args (not enforced at argparse level to allow --print-template)
    missing = [name for name, val in [("--stl", args.stl), ("--settings", args.settings), ("--material", args.material)] if not val]
    if missing:
        print(f"ERROR: the following arguments are required: {', '.join(missing)}", file=sys.stderr)
        sys.exit(2)

    if args.output is None:
        first_stl = Path(args.stl[0])
        mat_slug = args.material.replace(" ", "-")
        derived_name = f"{first_stl.stem}_{mat_slug}.3mf"
        args.output = str(first_stl.parent / derived_name)
        log.info(f"Derived output path: {args.output}")

    log.info(f"STLs: {args.stl}")
    log.info(f"Settings: {args.settings}")
    log.info(f"Material: {args.material}")
    log.info(f"Plate name: {args.plate_name}")
    log.info(f"Template: {args.template}")
    log.info(f"Output: {args.output}")

    report = build_stl_3mf(
        stl_paths=args.stl,
        settings_md=args.settings,
        material=args.material,
        plate_name=args.plate_name,
        template_path=args.template,
        output_path=args.output,
    )

    # Determine expected settings for verification
    # PETG-CF: outer_wall_speed=80, nozzle_temperature=265, elefant_foot=0.1, reduce_crossing_wall=1
    # TPU 95A: outer_wall_speed=30, nozzle_temperature=230, elefant_foot=0.1, reduce_crossing_wall=1
    # We read them from the applied settings dict (load the output and check)
    expected_settings = {}
    # Add temperature from what we extracted
    filament_temps = report.get("filament_temps_applied", {})
    if "nozzle_temperature" in filament_temps:
        expected_settings["nozzle_temperature"] = filament_temps["nozzle_temperature"]

    # Get outer_wall_speed, reduce_crossing_wall, and elefant_foot_compensation
    # from the settings report — only add to expected_settings if actually APPLIED
    for row in report["settings_report"]:
        if "APPLIED" not in row["status"]:
            continue
        new_val = row["new_value"]
        normalized = new_val[0] if isinstance(new_val, list) else str(new_val)
        if row["json_key"] == "outer_wall_speed":
            expected_settings["outer_wall_speed"] = normalized
        elif row["json_key"] == "reduce_crossing_wall":
            expected_settings["reduce_crossing_wall"] = normalized
        elif row["json_key"] == "elefant_foot_compensation":
            expected_settings["elefant_foot_compensation"] = normalized

    checks = verify_stl_3mf(
        output_path=args.output,
        stl_paths=args.stl,
        material=args.material,
        expected_settings=expected_settings,
        expected_object_ids=report["object_ids"],
        plate_name_fragment=args.material,
    )

    return {
        "output_path": args.output,
        "checks": checks,
        "settings_report": report["settings_report"],
    }


if __name__ == "__main__":
    result = main()
    output_dir = Path(result["output_path"]).parent
    report_path = str(output_dir / "stl_to_3mf_verification.txt")

    # Write combined report (will be overwritten per run; caller does both)
    all_passed = all(p for _, p, _ in result["checks"])
    if not all_passed:
        sys.exit(1)
