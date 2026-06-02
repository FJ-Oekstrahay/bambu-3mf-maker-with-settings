#!/usr/bin/env python3
"""
make_bambu_3mf.py — Multi-plate Bambu Studio .3mf builder with programmatic process settings.

Reads a source .3mf file, patches per-plate process settings from a markdown
settings table (or key=value pairs on the CLI), and writes a new .3mf ready
to open in Bambu Studio. Solves the problem of scripting precise per-material
settings (temperatures, speeds, wall counts, etc.) without using Bambu Studio's GUI.

CLI:
    python make_bambu_3mf.py \\
      --source input.3mf \\
      --plate 1 --material "PETG-CF" --objects 6,8 --settings petgcf.md \\
      --plate 2 --material "TPU 95A" --objects 2,4 --settings tpu.md \\
      --output output.3mf
"""

__version__ = "1.0.0"

import argparse
import copy
import difflib
import json
import logging
import re
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Verified JSON key lookup table (from spec — do NOT expand by guessing)
# ---------------------------------------------------------------------------
SETTING_KEY_MAP = {
    # Quality
    "Elephant foot compensation": ("elefant_foot_compensation", "string"),
    "Bridge flow": ("bridge_flow", "string"),
    "Avoid crossing wall": ("reduce_crossing_wall", "integer"),
    "Layer height": ("layer_height", "string"),
    "Initial layer height": ("initial_layer_print_height", "string"),
    "Seam position": ("seam_position", "string"),
    "Arc fitting": ("enable_arc_fitting", "string"),
    "X-Y hole compensation": ("xy_hole_compensation", "string"),
    "Ironing type": ("ironing_type", "string"),
    "Order of walls": ("wall_sequence", "string"),
    "Print infill first": ("is_infill_first", "string"),
    "Resolution": ("resolution", "string"),
    "Slice gap closing radius": ("slice_closing_radius", "string"),
    # Strength
    "Wall loops": ("wall_loops", "string"),
    "Detect thin wall": ("detect_thin_wall", "string"),
    "Bottom shell layers": ("bottom_shell_layers", "string"),
    "Bottom shell thickness": ("bottom_shell_thickness", "string"),
    "Top shell thickness": ("top_shell_thickness", "string"),
    "Top surface pattern": ("top_surface_pattern", "string"),
    "Bottom surface pattern": ("bottom_surface_pattern", "string"),
    "Sparse infill density": ("sparse_infill_density", "string"),
    "Sparse infill pattern": ("sparse_infill_pattern", "string"),
    "Length of sparse infill anchor": ("sparse_infill_anchor", "string"),
    "Skin infill density": ("skin_infill_density", "string"),
    "Skeleton infill density": ("skeleton_infill_density", "string"),
    "Skin infill depth": ("skin_infill_depth", "string"),
    # Speed — single-element array of strings
    "Travel speed": ("travel_speed", "array"),
    "Initial layer speed": ("initial_layer_speed", "array"),
    "Initial layer infill": ("initial_layer_infill_speed", "array"),
    "Outer wall": ("outer_wall_speed", "array"),
    "Inner wall": ("inner_wall_speed", "array"),
    "Small perimeters": ("small_perimeter_speed", "array"),
    "Sparse infill": ("sparse_infill_speed", "array"),
    "Internal solid infill": ("internal_solid_infill_speed", "array"),
    "Top surface": ("top_surface_speed", "array"),
    "Bridge": ("bridge_speed", "array"),
    "Gap infill": ("gap_infill_speed", "array"),
    "Support": ("support_speed", "array"),
    "Support interface": ("support_interface_speed", "array"),
    "Initial layer": ("initial_layer_acceleration", "array"),
    # Acceleration — single-element array of strings
    "Normal printing": ("default_acceleration", "array"),
    "Normal printing accel": ("default_acceleration", "array"),
    "Travel accel": ("travel_acceleration", "array"),
    "Travel": ("travel_acceleration", "array"),
    "Initial layer travel accel": ("initial_layer_travel_acceleration", "array"),
    "Initial layer travel": ("initial_layer_travel_acceleration", "array"),
    "Initial layer accel": ("initial_layer_acceleration", "array"),
    "Outer wall accel": ("outer_wall_acceleration", "array"),
    "Outer wall acceleration": ("outer_wall_acceleration", "array"),
    "Top surface accel": ("top_surface_acceleration", "array"),
    "Top surface acceleration": ("top_surface_acceleration", "array"),
    "Inner wall accel": ("inner_wall_acceleration", "array"),
    "Inner wall acceleration": ("inner_wall_acceleration", "array"),
    # Others — Bed adhesion
    "Skirt loops": ("skirt_loops", "string"),
    "Skirt height": ("skirt_height", "string"),
    "Brim type": ("brim_type", "string"),
    "Brim width": ("brim_width", "string"),
    "Brim-object gap": ("brim_object_gap", "string"),
    # Others — Prime tower
    "Enable prime tower": ("enable_prime_tower", "string"),
    "Enable": ("enable_prime_tower", "string"),  # "Enable" in Prime Tower section
    "Prime tower": ("enable_prime_tower", "string"),  # fallback alias
    # Others — Special mode
    "Print sequence": ("print_sequence", "string"),
    "Slicing mode": ("slicing_mode", "string"),
    "Spiral vase": ("spiral_mode", "string"),
    "Fuzzy skin": ("fuzzy_skin", "string"),
    # Support
    "Enable support": ("enable_support", "string"),
    "Support type": ("support_type", "string"),
    "Threshold angle": ("support_threshold_angle", "string"),
    "Support threshold angle": ("support_threshold_angle", "string"),
    "Support on build plate only": ("support_on_build_plate_only", "string"),
    "Raft layers": ("raft_layers", "string"),
    # Retraction (filament-tab but sometimes referenced in process docs)
    "Retraction length": ("retraction_length", "string"),
    "Retraction speed": ("retraction_speed", "string"),
    "Retraction distance": ("retraction_length", "string"),
    # Temperature — scalar spec value written as 6-element array (one per filament slot)
    "Nozzle temperature": ("nozzle_temperature", "array"),
    "Bed temperature": ("textured_plate_temp", "array"),
    # Abbreviated aliases used in summary tables
    "Infill density": ("sparse_infill_density", "string"),
    "Top shell layers": ("top_shell_layers", "string"),
    "Elephant foot comp": ("elefant_foot_compensation", "string"),
    "Normal accel": ("default_acceleration", "array"),
    "Bed temp": ("textured_plate_temp", "array"),
    "Nozzle temp": ("nozzle_temperature", "array"),
    "Brim": ("brim_type", "string"),
}

# Keys we must NEVER touch regardless of what the markdown says
FORBIDDEN_KEY_FRAGMENTS = [
    "machine_max",
    "machine_",
    "printer_",
    "extruder_count",
    "bed_exclude",
    "printable_area",
    "upward_compatible",
    "head_wrap",
    "start_end_point",
    "change_filament_gcode",
    "start_gcode",
    "end_gcode",
]


def is_forbidden_key(key: str) -> bool:
    return any(fragment in key for fragment in FORBIDDEN_KEY_FRAGMENTS)


# ---------------------------------------------------------------------------
# Markdown parser — extract ⚠️-marked rows from the summary table
# ---------------------------------------------------------------------------
def parse_settings_markdown(md_path: str) -> list[dict]:
    """
    Return a list of dicts with keys: tab, setting, default_val, new_val, reason.
    Only rows whose Setting column contains ⚠️ in the body, or rows from the
    summary table at the bottom (which marks all ⚠️ rows).

    We use the summary table (last table with columns Tab/Setting/Default/*/Reason)
    as the authoritative source because the spec says:
      "The ⚠️-marked settings in the markdown are the only changes from Bambu defaults."
    The summary table collects them all in one place.
    """
    text = Path(md_path).read_text(encoding="utf-8")

    # Find "Summary of All Changes" section
    summary_match = re.search(
        r"## Summary of All Changes.*?(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE
    )
    if not summary_match:
        log.warning(f"No summary table found in {md_path}; trying inline ⚠️ scan")
        return _parse_inline_warning_rows(text)

    summary_text = summary_match.group(0)
    rows = []

    # Parse markdown table rows  |Tab|Setting|Default|Value|Reason|
    for line in summary_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 4:
            continue
        # Skip header / separator rows
        if cols[0].lower() in ("tab", "") or set(cols[0]) <= {"-", " "}:
            continue
        tab = cols[0].strip()
        setting = cols[1].strip()
        default_val = cols[2].strip()
        new_val = cols[3].strip() if len(cols) > 3 else ""
        reason = cols[4].strip() if len(cols) > 4 else ""
        rows.append(
            {
                "tab": tab,
                "setting": setting,
                "default_val": default_val,
                "new_val": new_val,
                "reason": reason,
            }
        )

    log.info(f"Parsed {len(rows)} ⚠️ settings from summary table in {md_path}")

    return rows


def _parse_inline_warning_rows(text: str) -> list[dict]:
    """Fallback: scan all table rows containing ⚠️."""
    rows = []
    for line in text.splitlines():
        if "⚠️" not in line:
            continue
        if not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 2:
            continue
        rows.append(
            {
                "tab": "",
                "setting": cols[0].strip().replace("⚠️", "").strip(),
                "default_val": cols[2].strip() if len(cols) > 2 else "",
                "new_val": cols[3].strip() if len(cols) > 3 else "",
                "reason": "",
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Value coercion helpers
# ---------------------------------------------------------------------------
def _strip_unit(val: str) -> str:
    """Remove trailing unit annotations: mm/s, mm/s², mm, %, mm² etc."""
    # Remove bold markers
    val = val.replace("**", "").strip()
    # Remove common unit suffixes (order matters — longer first)
    for unit in ["mm/s²", "mm/s", " mm²", " mm", " %", "°C", " °", "°"]:
        if val.endswith(unit):
            val = val[: -len(unit)].strip()
    # Handle "45%" → "45%" (keep % if it's the value itself, like for density)
    return val.strip()


def coerce_value(raw_val: str, key_type: str, source_val):
    """
    Convert a raw string value from markdown to the correct Python type
    for writing into JSON, guided by key_type and the source value.

    key_type: "string" | "array" | "integer"
    source_val: what's currently in the source JSON (for type-fidelity fallback)
    """
    # Checkbox values
    checkbox_map = {"☑": "1", "☐": "0", "✓": "1", "✗": "0"}
    for ch, num in checkbox_map.items():
        if raw_val.strip() == ch:
            raw_val = num
            break

    # Strip units from numeric values (but preserve % in density strings)
    clean = _strip_unit(raw_val)

    if key_type == "integer":
        try:
            return int(float(clean))
        except (ValueError, TypeError):
            # checkbox was already handled above
            return int(clean)

    if key_type == "array":
        # Strip % from percentage values for speed (they're stored as plain numbers)
        numeric = clean.rstrip("%").strip()
        # If the source is a multi-element array (e.g. nozzle_temperature has 6 slots),
        # repeat the value to match the expected length rather than returning a 1-element list.
        if isinstance(source_val, list) and len(source_val) > 1:
            return [numeric] * len(source_val)
        return [numeric]

    # "string" type — may have % appended (e.g. sparse_infill_density "45%")
    # Check the source to see if it ends with %
    if isinstance(source_val, str) and source_val.endswith("%"):
        # Preserve the % suffix
        if not clean.endswith("%"):
            clean = clean + "%"
    return clean


def bool_str_to_value(val_str: str, key_type: str) -> int | str:
    """Convert ☑/☐ to 1/0 respecting integer vs string type."""
    m = {"☑": 1, "☐": 0}
    for ch, n in m.items():
        if ch in val_str:
            if key_type == "integer":
                return n
            return str(n)
    return val_str


# ---------------------------------------------------------------------------
# Apply settings to a settings dict
# ---------------------------------------------------------------------------
def apply_settings(
    settings: dict,
    md_rows: list[dict],
    material_name: str,
    source_settings: dict,
) -> tuple[dict, list[dict]]:
    """
    Deep-copy settings, apply ⚠️ rows, return (modified_dict, report_rows).
    Never touches forbidden keys.
    """
    out = copy.deepcopy(settings)
    report = []

    for row in md_rows:
        setting_name = row["setting"].strip()
        raw_new_val = row["new_val"].strip()

        # Skip rows with no new value — blank cells mean "no change"
        if not raw_new_val:
            continue

        # Look up the JSON key
        if setting_name in SETTING_KEY_MAP:
            json_key, key_type = SETTING_KEY_MAP[setting_name]
        else:
            # Fallback: normalize the setting name directly to a candidate config key
            # lowercase, replace spaces/hyphens with underscores, strip trailing
            # unit annotations like "(mm)", "(°C)", colons, etc.
            normalized = setting_name.lower().strip()
            normalized = re.sub(r"\s*\(.*?\)\s*$", "", normalized)  # strip "(mm)", "(°C)"
            normalized = re.sub(r":$", "", normalized)              # strip trailing colon
            normalized = re.sub(r"[\s\-]+", "_", normalized)        # spaces/hyphens → _
            normalized = re.sub(r"[^\w]", "", normalized)            # drop remaining non-word chars

            if normalized in out:
                # Infer type from the current value in the settings dict
                existing = out[normalized]
                if isinstance(existing, list):
                    key_type = "array"
                elif isinstance(existing, int) and not isinstance(existing, bool):
                    key_type = "integer"
                else:
                    key_type = "string"
                json_key = normalized
                log.info(
                    f"[{material_name}] '{setting_name}' not in lookup table — "
                    f"resolved via normalization to '{json_key}'"
                )
            else:
                suggestions = difflib.get_close_matches(
                    normalized,
                    list(SETTING_KEY_MAP.keys()) + list(out.keys()),
                    n=3,
                    cutoff=0.6,
                )
                if suggestions:
                    log.warning(
                        f"[{material_name}] Unknown setting '{setting_name}' — did you mean: {suggestions}?"
                    )
                else:
                    log.warning(
                        f"[{material_name}] Unknown setting '{setting_name}' — "
                        f"not in lookup table and normalized key '{normalized}' not found in config, SKIPPED"
                    )
                report.append(
                    {
                        "human_name": setting_name,
                        "json_key": "N/A",
                        "old_value": "N/A",
                        "new_value": raw_new_val,
                        "status": "SKIPPED (not in lookup table)",
                    }
                )
                continue

        # Never touch forbidden keys
        if is_forbidden_key(json_key):
            log.warning(
                f"[{material_name}] Key '{json_key}' is forbidden (hardware/machine setting), SKIPPED"
            )
            report.append(
                {
                    "human_name": setting_name,
                    "json_key": json_key,
                    "old_value": out.get(json_key, "N/A"),
                    "new_value": raw_new_val,
                    "status": "SKIPPED (forbidden key)",
                }
            )
            continue

        # Get the source value for type reference
        source_val = source_settings.get(json_key)
        old_val = out.get(json_key, "N/A")

        # If the key isn't in the source, infer type from key_type
        # Determine actual type from source value if present
        actual_key_type = key_type
        if source_val is not None:
            if isinstance(source_val, list):
                actual_key_type = "array"
            elif isinstance(source_val, int) and not isinstance(source_val, bool):
                actual_key_type = "integer"
            else:
                actual_key_type = "string"

        try:
            new_val = coerce_value(raw_new_val, actual_key_type, source_val)
        except Exception as e:
            log.warning(
                f"[{material_name}] Could not coerce '{raw_new_val}' for '{json_key}': {e} — SKIPPED"
            )
            report.append(
                {
                    "human_name": setting_name,
                    "json_key": json_key,
                    "old_value": old_val,
                    "new_value": raw_new_val,
                    "status": f"SKIPPED (coerce error: {e})",
                }
            )
            continue

        out[json_key] = new_val
        report.append(
            {
                "human_name": setting_name,
                "json_key": json_key,
                "old_value": old_val,
                "new_value": new_val,
                "status": "APPLIED",
            }
        )

    # Verify travel_speed was not changed
    if out.get("travel_speed") != source_settings.get("travel_speed"):
        log.warning("travel_speed was modified — resetting to source value!")
        out["travel_speed"] = source_settings.get("travel_speed", ["700"])

    return out, report


# ---------------------------------------------------------------------------
# Preset loader
# ---------------------------------------------------------------------------
def load_preset(preset_name: str) -> list[dict]:
    """
    Load preset rows from presets/<preset_name>.md relative to this script's directory.
    Returns parsed md_rows (same format as parse_settings_markdown).
    """
    script_dir = Path(__file__).parent
    preset_path = script_dir / "presets" / f"{preset_name}.md"
    if not preset_path.exists():
        log.error(f"Preset '{preset_name}' not found at {preset_path}")
        sys.exit(1)
    log.info(f"Loading preset: {preset_path}")
    return parse_settings_markdown(str(preset_path))


# ---------------------------------------------------------------------------
# Settings validation
# ---------------------------------------------------------------------------
def validate_settings(settings_dict: dict, material_name: str = "") -> list[str]:
    """
    Check settings_dict for common misconfigurations.
    Returns a list of warning strings (empty if all OK).
    """
    warnings = []

    # 1. Hollow shell (0% infill) with only 1 wall loop — will be very fragile
    density_raw = settings_dict.get("sparse_infill_density", "")
    if isinstance(density_raw, list):
        density_raw = density_raw[0] if density_raw else ""
    density_str = str(density_raw).strip().rstrip("%").strip()
    try:
        density_val = float(density_str)
    except (ValueError, TypeError):
        density_val = None

    wall_loops_raw = settings_dict.get("wall_loops", "")
    if isinstance(wall_loops_raw, list):
        wall_loops_raw = wall_loops_raw[0] if wall_loops_raw else ""
    try:
        wall_loops_val = int(str(wall_loops_raw).strip())
    except (ValueError, TypeError):
        wall_loops_val = None

    if density_val is not None and density_val == 0 and wall_loops_val is not None and wall_loops_val <= 1:
        warnings.append(
            "hollow shell with only 1 wall loop will be fragile — "
            "consider adding more wall loops (wall_loops >= 2)"
        )

    # 2. Speed > 200 mm/s with TPU material
    if material_name and "tpu" in material_name.lower():
        speed_keys = [
            "outer_wall_speed", "inner_wall_speed", "sparse_infill_speed",
            "internal_solid_infill_speed", "top_surface_speed", "bridge_speed",
            "gap_infill_speed",
        ]
        for key in speed_keys:
            val = settings_dict.get(key)
            if val is None:
                continue
            if isinstance(val, list):
                val = val[0] if val else None
            if val is None:
                continue
            try:
                speed_val = float(str(val).strip())
                if speed_val > 200:
                    warnings.append(
                        f"speed > 200 mm/s ({key}={speed_val}) with TPU may cause under-extrusion or jams"
                    )
            except (ValueError, TypeError):
                pass

    return warnings


# ---------------------------------------------------------------------------
# model_settings.config modifier — split objects across plates
# ---------------------------------------------------------------------------
def build_model_settings(
    source_model_settings_xml: bytes,
    plates: list[dict],
) -> bytes:
    """
    Rebuild model_settings.config XML with multiple plates.

    plates = [
        {"plate_num": 1, "objects": [6, 8], "material": "PETG-CF"},
        {"plate_num": 2, "objects": [2, 4], "material": "TPU 95A"},
    ]

    Preserves all <object> blocks exactly.
    Reads identify_id values from the original plate's model_instances.
    """
    # Parse original
    root = ET.fromstring(source_model_settings_xml)

    # Collect all existing object elements (preserve exactly)
    object_elems = [child for child in root if child.tag == "object"]

    # Collect identify_id map from original plate model_instances
    identify_id_map = {}  # object_id -> identify_id
    for plate_elem in root.iter("plate"):
        for mi in plate_elem.iter("model_instance"):
            oid = None
            iid = None
            for m in mi.iter("metadata"):
                if m.get("key") == "object_id":
                    oid = int(m.get("value"))
                if m.get("key") == "identify_id":
                    iid = m.get("value")
            if oid is not None and iid is not None:
                identify_id_map[oid] = iid

    # Get the original plate metadata (thumbnail paths etc.)
    orig_plate_meta = {}
    for plate_elem in root.iter("plate"):
        for m in plate_elem.iter("metadata"):
            orig_plate_meta[m.get("key")] = m.get("value")
        break  # only need first plate's metadata structure

    # Get assemble element if present
    assemble_elem = root.find("assemble")

    # Build new root
    new_root = ET.Element("config")

    # Re-append all object elements
    for obj_elem in object_elems:
        new_root.append(obj_elem)

    # Build new plate elements
    for plate_info in plates:
        plate_num = plate_info["plate_num"]
        objects = plate_info["objects"]

        plate_elem = ET.SubElement(new_root, "plate")

        def add_meta(key, value):
            m = ET.SubElement(plate_elem, "metadata")
            m.set("key", key)
            m.set("value", str(value))

        add_meta("plater_id", str(plate_num))
        add_meta("plater_name", "")
        add_meta("locked", "false")
        add_meta("filament_map_mode", orig_plate_meta.get("filament_map_mode", "Auto For Flush"))
        # filament_maps: read from the source template — space-separated slot indices.
        # Default "1 1 1 1 1 1" matches the 6-slot A1 mini AMS Lite; if the template was
        # saved by 2.7.1.57 with a different slot count, orig_plate_meta will have the
        # correct value. Do NOT hardcode slot count here.
        add_meta("filament_maps", orig_plate_meta.get("filament_maps", "1 1 1 1 1 1"))
        add_meta("filament_volume_maps", orig_plate_meta.get("filament_volume_maps", "0 0 0 0"))
        add_meta("thumbnail_file", f"Metadata/plate_{plate_num}.png")
        add_meta("thumbnail_no_light_file", f"Metadata/plate_no_light_{plate_num}.png")
        add_meta("top_file", f"Metadata/top_{plate_num}.png")
        add_meta("pick_file", f"Metadata/pick_{plate_num}.png")

        for oid in objects:
            mi = ET.SubElement(plate_elem, "model_instance")
            oid_m = ET.SubElement(mi, "metadata")
            oid_m.set("key", "object_id")
            oid_m.set("value", str(oid))
            iid_m = ET.SubElement(mi, "metadata")
            iid_m.set("key", "instance_id")
            iid_m.set("value", "0")
            identify_m = ET.SubElement(mi, "metadata")
            identify_m.set("key", "identify_id")
            identify_m.set("value", identify_id_map.get(oid, str(oid * 10)))

    # Re-append assemble block if present
    if assemble_elem is not None:
        new_root.append(assemble_elem)

    # Serialize with declaration
    ET.indent(new_root, space="  ")
    xml_bytes = ET.tostring(new_root, encoding="unicode", xml_declaration=False)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes).encode("utf-8")


# ---------------------------------------------------------------------------
# Main build function
# ---------------------------------------------------------------------------
def build_3mf(
    source_path: str,
    plates_config: list[dict],
    output_path: str,
) -> list[dict]:
    """
    Build the output .3mf.

    plates_config: list of dicts with keys:
        plate_num (int), material (str), objects (list[int]), settings_md (str)

    Returns verification report rows.
    """
    src = zipfile.ZipFile(source_path, "r")
    src_infos = {info.filename: info for info in src.infolist()}

    # Record compression methods
    compression_map = {
        info.filename: info.compress_type for info in src.infolist()
    }

    # Load source project_settings.config (must be a dict)
    src_settings_bytes = src.read("Metadata/project_settings.config")
    src_settings = json.loads(src_settings_bytes)
    assert isinstance(src_settings, dict), "source project_settings.config is not a dict!"

    # Load source model_settings.config
    src_model_settings_bytes = src.read("Metadata/model_settings.config")

    # Load 3dmodel.model (byte-preserve)
    model_bytes = src.read("3D/3dmodel.model")

    # Parse settings markdowns and build per-plate settings
    per_plate_settings = {}  # plate_num -> (settings_dict, report_rows)
    all_report_rows = []

    for plate in plates_config:
        plate_num = plate["plate_num"]
        material = plate["material"]
        md_path = plate["settings_md"]

        log.info(f"Plate {plate_num} ({material}): parsing {md_path}")
        md_rows = parse_settings_markdown(md_path) if md_path else []

        # Prepend preset rows so explicit settings override preset values
        preset_rows = plate.get("preset_rows", [])
        if preset_rows:
            log.info(f"Plate {plate_num}: merging {len(preset_rows)} preset rows (overridden by explicit settings)")
            md_rows = preset_rows + md_rows

        plate_settings, report = apply_settings(
            src_settings, md_rows, material, src_settings
        )
        per_plate_settings[plate_num] = plate_settings
        all_report_rows.extend(
            [{"plate": plate_num, "material": material, **r} for r in report]
        )

        # Validate applied settings
        validation_warnings = validate_settings(plate_settings, material)
        for w in validation_warnings:
            log.warning(f"[Plate {plate_num} / {material}] Validation: {w}")

    # Build model_settings.config
    new_model_settings_bytes = build_model_settings(
        src_model_settings_bytes, plates_config
    )

    # Determine PNG files for plate 1 (to copy to plate 2)
    plate1_pngs = {
        "plate": src.read("Metadata/plate_1.png"),
        "plate_no_light": src.read("Metadata/plate_no_light_1.png"),
        "top": src.read("Metadata/top_1.png"),
        "pick": src.read("Metadata/pick_1.png"),
        "plate_small": src.read("Metadata/plate_1_small.png"),
    }

    # Build plate_N.json files (minimal metadata stubs for extra plates)
    # Plate 1 json already exists; create stub for plate 2+
    src_plate1_json = json.loads(src.read("Metadata/plate_1.json"))

    def make_plate_json(plate_num: int) -> bytes:
        stub = {
            "bbox_all": src_plate1_json.get("bbox_all", []),
            "bbox_objects": [],
            "bed_type": src_plate1_json.get("bed_type", "textured_plate"),
            "filament_colors": [],
            "filament_ids": [],
            "first_extruder": 0,
            "first_layer_time": 0,
            "is_seq_print": False,
            "nozzle_diameter": src_plate1_json.get("nozzle_diameter", 0.4),
            "version": src_plate1_json.get("version", 2),
        }
        return json.dumps(stub, indent=2).encode("utf-8")

    # -----------------------------------------------------------------------
    # Write output zip
    # -----------------------------------------------------------------------
    out_buf = BytesIO()
    with zipfile.ZipFile(out_buf, "w") as out_zip:

        # Files to copy verbatim from source (except ones we override)
        override_files = {
            "Metadata/project_settings.config",
            "Metadata/model_settings.config",
        }
        # Add per-plate process_settings files (new)
        # Add per-plate thumbnails for new plates

        for info in src.infolist():
            fname = info.filename
            if fname in override_files:
                continue
            if fname.endswith(".png"):
                # Copy with original STORED compression
                data = src.read(fname)
                out_zip.writestr(
                    zipfile.ZipInfo(fname), data
                    # ZipInfo default is STORED
                )
                continue
            # Everything else: copy with original compression method
            data = src.read(fname)
            zi = zipfile.ZipInfo(fname)
            zi.compress_type = compression_map.get(fname, zipfile.ZIP_DEFLATED)
            out_zip.writestr(zi, data)

        # Write 3dmodel.model (byte-identical — already copied above since not in override_files)
        # Actually it was already handled above. Let's verify it went through.

        # Write overridden project_settings.config = copy of plate 1 settings (conservative)
        project_cfg_bytes = json.dumps(
            per_plate_settings[plates_config[0]["plate_num"]], indent=2
        ).encode("utf-8")
        zi = zipfile.ZipInfo("Metadata/project_settings.config")
        zi.compress_type = zipfile.ZIP_DEFLATED
        out_zip.writestr(zi, project_cfg_bytes)

        # Write model_settings.config
        zi = zipfile.ZipInfo("Metadata/model_settings.config")
        zi.compress_type = zipfile.ZIP_DEFLATED
        out_zip.writestr(zi, new_model_settings_bytes)

        # Write process_settings_N.config for each plate
        for plate in plates_config:
            plate_num = plate["plate_num"]
            cfg = per_plate_settings[plate_num]
            cfg_bytes = json.dumps(cfg, indent=2).encode("utf-8")
            fname = f"Metadata/process_settings_{plate_num}.config"
            zi = zipfile.ZipInfo(fname)
            zi.compress_type = zipfile.ZIP_DEFLATED
            out_zip.writestr(zi, cfg_bytes)

        # Write extra plate PNGs (copies of plate 1) for plates > 1
        for plate in plates_config:
            plate_num = plate["plate_num"]
            if plate_num == 1:
                continue
            # thumbnail copies
            for kind, src_key in [
                ("plate", "plate"),
                ("plate_no_light", "plate_no_light"),
                ("top", "top"),
                ("pick", "pick"),
            ]:
                fname = f"Metadata/{kind}_{plate_num}.png"
                if fname not in [i.filename for i in src.infolist()]:
                    zi = zipfile.ZipInfo(fname)
                    zi.compress_type = zipfile.ZIP_STORED  # PNGs are STORED
                    out_zip.writestr(zi, plate1_pngs[kind])
            # plate_N_small.png
            fname_small = f"Metadata/plate_{plate_num}_small.png"
            if fname_small not in [i.filename for i in src.infolist()]:
                zi = zipfile.ZipInfo(fname_small)
                zi.compress_type = zipfile.ZIP_STORED
                out_zip.writestr(zi, plate1_pngs["plate_small"])

            # plate_N.json stub
            fname_json = f"Metadata/plate_{plate_num}.json"
            if fname_json not in [i.filename for i in src.infolist()]:
                zi = zipfile.ZipInfo(fname_json)
                zi.compress_type = zipfile.ZIP_DEFLATED
                out_zip.writestr(zi, make_plate_json(plate_num))

    src.close()

    # Write output file
    with open(output_path, "wb") as f:
        f.write(out_buf.getvalue())

    log.info(f"Written: {output_path}")
    return all_report_rows


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
def verify_output(
    output_path: str,
    source_path: str,
    plates_config: list[dict],
) -> list[tuple[str, bool, str]]:
    """Run structural checks. Returns list of (check_name, passed, detail)."""
    checks = []

    # 1. Valid zip
    try:
        z = zipfile.ZipFile(output_path, "r")
        checks.append(("Valid zip", True, ""))
    except Exception as e:
        checks.append(("Valid zip", False, str(e)))
        return checks

    # 2. 3dmodel.model byte-identical to source
    try:
        src_z = zipfile.ZipFile(source_path, "r")
        src_model = src_z.read("3D/3dmodel.model")
        out_model = z.read("3D/3dmodel.model")
        identical = src_model == out_model
        checks.append(("3dmodel.model byte-identical to source", identical, ""))
        src_z.close()
    except Exception as e:
        checks.append(("3dmodel.model byte-identical to source", False, str(e)))

    # 3. project_settings.config is a JSON dict
    try:
        data = z.read("Metadata/project_settings.config")
        obj = json.loads(data)
        is_dict = isinstance(obj, dict)
        checks.append(("project_settings.config is JSON dict", is_dict, type(obj).__name__))
    except Exception as e:
        checks.append(("project_settings.config is JSON dict", False, str(e)))

    # 4. process_settings_N.config for each plate is a JSON dict with expected settings
    for plate in plates_config:
        plate_num = plate["plate_num"]
        fname = f"Metadata/process_settings_{plate_num}.config"
        try:
            data = z.read(fname)
            obj = json.loads(data)
            is_dict = isinstance(obj, dict)
            checks.append(
                (f"process_settings_{plate_num}.config is JSON dict", is_dict, type(obj).__name__)
            )
        except Exception as e:
            checks.append((f"process_settings_{plate_num}.config is JSON dict", False, str(e)))

    # 5. model_settings.config is valid XML with two <plate> blocks and correct object IDs
    try:
        data = z.read("Metadata/model_settings.config")
        root = ET.fromstring(data)
        plate_elems = [c for c in root if c.tag == "plate"]
        plate_count_ok = len(plate_elems) == len(plates_config)
        checks.append(
            (
                f"model_settings.config has {len(plates_config)} plate block(s)",
                plate_count_ok,
                f"found {len(plate_elems)}",
            )
        )

        # Check each plate has the right object IDs
        for plate_info, plate_elem in zip(plates_config, plate_elems):
            expected_oids = set(plate_info["objects"])
            actual_oids = set()
            for mi in plate_elem.iter("model_instance"):
                for m in mi.iter("metadata"):
                    if m.get("key") == "object_id":
                        actual_oids.add(int(m.get("value")))
            ok = expected_oids == actual_oids
            checks.append(
                (
                    f"Plate {plate_info['plate_num']} has correct object IDs {sorted(expected_oids)}",
                    ok,
                    f"found {sorted(actual_oids)}",
                )
            )
    except Exception as e:
        checks.append(("model_settings.config valid XML", False, str(e)))

    # 6. Compression methods match original for files present in both
    try:
        src_z = zipfile.ZipFile(source_path, "r")
        src_compress = {info.filename: info.compress_type for info in src_z.infolist()}
        out_compress = {info.filename: info.compress_type for info in z.infolist()}
        mismatches = []
        for fname, src_ct in src_compress.items():
            if fname in out_compress and out_compress[fname] != src_ct:
                mismatches.append(
                    f"{fname}: expected {src_ct} got {out_compress[fname]}"
                )
        checks.append(
            (
                "Compression methods match original",
                len(mismatches) == 0,
                "; ".join(mismatches) if mismatches else "",
            )
        )
        src_z.close()
    except Exception as e:
        checks.append(("Compression methods match original", False, str(e)))

    z.close()
    return checks


# ---------------------------------------------------------------------------
# Verification report printer
# ---------------------------------------------------------------------------
def print_verification_report(
    report_rows: list[dict],
    checks: list[tuple[str, bool, str]],
    output_path: str,
) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append("BAMBU 3MF GENERATOR — VERIFICATION REPORT")
    lines.append("=" * 72)
    lines.append("")

    # Settings applied/skipped
    lines.append("SETTINGS APPLICATION")
    lines.append("-" * 72)
    lines.append(
        f"{'Plate':<6} {'Setting':<30} {'JSON Key':<35} {'Old':<20} {'New':<20} {'Status'}"
    )
    lines.append("-" * 72)
    for row in report_rows:
        lines.append(
            f"{row.get('plate','')!s:<6} {row['human_name'][:29]:<30} {row['json_key'][:34]:<35} "
            f"{str(row['old_value'])[:19]:<20} {str(row['new_value'])[:19]:<20} {row['status']}"
        )

    lines.append("")
    lines.append("STRUCTURAL CHECKS")
    lines.append("-" * 72)
    for check_name, passed, detail in checks:
        status = "PASS" if passed else "FAIL"
        detail_str = f" — {detail}" if detail else ""
        lines.append(f"  [{status}] {check_name}{detail_str}")

    lines.append("")
    all_passed = all(p for _, p, _ in checks)
    lines.append(f"OVERALL: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")
    lines.append("=" * 72)

    report_text = "\n".join(lines)
    print(report_text)

    # Save to file
    report_path = str(Path(output_path).parent / "verification_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    log.info(f"Verification report saved: {report_path}")
    return report_text


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Build a Bambu Studio multi-plate .3mf file with programmatic process settings. "
            "Reads a source .3mf, applies per-plate settings from markdown tables, "
            "and writes a new .3mf with patched project/process configs."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example (two plates):\n"
            "  python make_bambu_3mf.py \\\n"
            "    --source input.3mf \\\n"
            "    --plate 1 --material 'PETG-CF' --objects 6,8 --settings petgcf.md \\\n"
            "    --plate 2 --material 'TPU 95A' --objects 2,4 --settings tpu.md \\\n"
            "    --output output.3mf"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to the source .3mf file to use as a template.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output .3mf file to write.",
    )

    # Plate groups: --plate N --material X --objects A,B --settings file.md
    # We collect them manually because argparse doesn't handle repeating groups well
    args, remaining = parser.parse_known_args(argv)

    # Parse repeating plate groups from remaining
    plates = []
    i = 0
    while i < len(remaining):
        if remaining[i] == "--plate":
            plate_num = int(remaining[i + 1])
            i += 2
            material = None
            objects = None
            settings_md = None
            preset_name = None
            while i < len(remaining) and remaining[i] not in ("--plate", "--source", "--output"):
                if remaining[i] == "--material":
                    material = remaining[i + 1]
                    i += 2
                elif remaining[i] == "--objects":
                    objects = [int(x) for x in remaining[i + 1].split(",")]
                    i += 2
                elif remaining[i] == "--settings":
                    settings_md = remaining[i + 1]
                    i += 2
                elif remaining[i] == "--preset":
                    preset_name = remaining[i + 1]
                    i += 2
                else:
                    i += 1
            plate_entry = {
                "plate_num": plate_num,
                "material": material,
                "objects": objects,
                "settings_md": settings_md,
            }
            if preset_name:
                plate_entry["preset_rows"] = load_preset(preset_name)
            plates.append(plate_entry)
        else:
            i += 1

    if not plates:
        parser.error("At least one --plate group is required.")

    return args, plates


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv=None):
    args, plates_config = parse_args(argv)

    log.info(f"Source: {args.source}")
    log.info(f"Output: {args.output}")
    for p in plates_config:
        log.info(f"  Plate {p['plate_num']}: {p['material']} objects={p['objects']} settings={p['settings_md']}")

    report_rows = build_3mf(args.source, plates_config, args.output)
    checks = verify_output(args.output, args.source, plates_config)
    print_verification_report(report_rows, checks, args.output)

    # Exit non-zero if any check failed
    if not all(p for _, p, _ in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
