#!/usr/bin/env python3
"""
3mf_restamp.py — Apply process settings to an existing .3mf without changing geometry.

Reads a source .3mf, patches project_settings.config from a markdown settings file,
and writes a new .3mf that is byte-identical to the source except for the updated config.

CLI:
    python3 3mf_restamp.py \\
      --input source.3mf \\
      --settings settings.md \\
      [--output output_restamped.3mf]
"""

__version__ = "1.0.0"

import argparse
import copy
import json
import subprocess
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

# Import shared logic from the sibling module
sys.path.insert(0, str(Path(__file__).parent))
from make_bambu_3mf import (
    SETTING_KEY_MAP,
    apply_settings,
    load_preset,
    parse_settings_markdown,
    validate_settings,
)

import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Per-object metadata keys that are safe to keep in model_settings.config.
# All others are process overrides that cause Studio to show "Objects" view.
# ---------------------------------------------------------------------------
SAFE_OBJECT_METADATA_KEYS = {'name', 'extruder'}  # None (no key attr) is also safe (face_count)


def strip_object_process_overrides(model_settings_bytes: bytes) -> tuple[bytes, int]:
    """Remove per-object process overrides from model_settings.config XML.
    Returns (cleaned_bytes, count_stripped)."""
    root = ET.fromstring(model_settings_bytes)
    stripped = 0
    for obj in root.findall('object'):
        to_remove = [
            m for m in obj.findall('metadata')
            if m.get('key') not in SAFE_OBJECT_METADATA_KEYS and m.get('key') is not None
        ]
        for m in to_remove:
            obj.remove(m)
            stripped += 1
    if stripped:
        ET.indent(root, space='  ')
    xml_str = ET.tostring(root, encoding='unicode', xml_declaration=False)
    result = ('<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str).encode('utf-8')
    return result, stripped


# ---------------------------------------------------------------------------
# Filament-tab settings — applied to project_settings.config directly.
# These keys live as arrays (one entry per filament slot).
# ---------------------------------------------------------------------------
FILAMENT_SETTING_MAP = {
    "Nozzle temperature": ("nozzle_temperature", "array"),
    "Bed temperature": ("textured_plate_temp", "array"),
    # aliases used in some markdown files
    "Bed temp": ("textured_plate_temp", "array"),
}


def extract_filament_settings(md_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Split md_rows into (process_rows, filament_rows).
    Filament rows are those whose setting name matches a key in FILAMENT_SETTING_MAP.
    """
    process_rows = []
    filament_rows = []
    for row in md_rows:
        if row["setting"].strip() in FILAMENT_SETTING_MAP:
            filament_rows.append(row)
        else:
            process_rows.append(row)
    return process_rows, filament_rows


def apply_filament_settings(
    settings: dict, filament_rows: list[dict]
) -> tuple[dict, list[dict]]:
    """
    Apply filament-tab rows (nozzle temp, bed temp, etc.) directly into the
    project_settings dict. Returns (modified_dict, report_rows).
    """
    import copy
    from make_bambu_3mf import coerce_value, is_forbidden_key

    out = copy.deepcopy(settings)
    report = []

    for row in filament_rows:
        setting_name = row["setting"].strip()
        raw_new_val = row["new_val"].strip()

        if not raw_new_val:
            continue

        if setting_name not in FILAMENT_SETTING_MAP:
            log.warning(f"Unknown filament setting '{setting_name}' — SKIPPED")
            continue

        json_key, key_type = FILAMENT_SETTING_MAP[setting_name]

        if is_forbidden_key(json_key):
            log.warning(f"Key '{json_key}' is forbidden — SKIPPED")
            continue

        source_val = settings.get(json_key)
        old_val = out.get(json_key, "N/A")

        actual_key_type = key_type
        if source_val is not None:
            if isinstance(source_val, list):
                actual_key_type = "array"

        try:
            new_val = coerce_value(raw_new_val, actual_key_type, source_val)
        except Exception as e:
            log.warning(f"Could not coerce '{raw_new_val}' for '{json_key}': {e} — SKIPPED")
            report.append({
                "human_name": setting_name,
                "json_key": json_key,
                "old_value": old_val,
                "new_value": raw_new_val,
                "status": f"SKIPPED (coerce error: {e})",
            })
            continue

        out[json_key] = new_val
        report.append({
            "human_name": setting_name,
            "json_key": json_key,
            "old_value": old_val,
            "new_value": new_val,
            "status": "APPLIED",
        })

    return out, report


# ---------------------------------------------------------------------------
# Core restamp function
# ---------------------------------------------------------------------------
def restamp_3mf(
    input_path: str,
    settings_md: str | None,
    output_path: str,
    preset_rows: list[dict] | None = None,
) -> tuple[list[dict], dict, dict]:
    """
    Open source 3mf, apply settings from markdown, write new 3mf.
    Returns (report_rows, src_settings, updated_settings).

    preset_rows: optional preset settings to apply before md file rows.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    log.info(f"Input:    {input_path}")
    log.info(f"Settings: {settings_md}")
    log.info(f"Output:   {output_path}")

    # Open source zip
    with zipfile.ZipFile(input_path, "r") as src_zip:
        src_infos = src_zip.infolist()
        compression_map = {info.filename: info.compress_type for info in src_infos}

        # Locate project_settings.config — may be at root or under Metadata/
        config_candidates = [
            name for name in compression_map
            if name.endswith("project_settings.config")
        ]
        if not config_candidates:
            log.error("project_settings.config not found in source 3mf")
            sys.exit(1)
        config_name = config_candidates[0]
        log.info(f"Found settings at: {config_name}")

        src_settings_bytes = src_zip.read(config_name)
        src_settings = json.loads(src_settings_bytes)
        if not isinstance(src_settings, dict):
            log.error("project_settings.config is not a JSON dict")
            sys.exit(1)

        # Read and clean model_settings.config (strip per-object process overrides)
        model_settings_name = next(
            (n for n in compression_map if n.endswith('model_settings.config')), None
        )
        cleaned_model_settings_bytes = None
        if model_settings_name:
            raw_model_settings_bytes = src_zip.read(model_settings_name)
            cleaned_model_settings_bytes, n_stripped = strip_object_process_overrides(
                raw_model_settings_bytes
            )
            if n_stripped:
                log.info(f"Stripped {n_stripped} per-object process override(s) from {model_settings_name}")
            else:
                log.info(f"No per-object process overrides found in {model_settings_name}")

        # Parse the markdown (optional when preset-only)
        if settings_md:
            md_rows = parse_settings_markdown(settings_md)
            log.info(f"Parsed {len(md_rows)} rows from settings markdown")
        else:
            md_rows = []

        # Prepend preset rows so explicit settings override preset
        if preset_rows:
            log.info(f"Merging {len(preset_rows)} preset rows (overridden by explicit settings)")
            md_rows = preset_rows + md_rows

        # Split filament vs process rows
        process_rows, filament_rows = extract_filament_settings(md_rows)

        # Apply process settings
        updated_settings, process_report = apply_settings(
            src_settings, process_rows, "restamp", src_settings
        )

        # Apply filament settings
        updated_settings, filament_report = apply_filament_settings(
            updated_settings, filament_rows
        )

        all_report = process_report + filament_report

        # Force both profile keys to "Custom" so Studio doesn't load the named
        # system profile and override our embedded settings with its defaults.
        for profile_key in ('default_print_profile', 'print_settings_id'):
            if updated_settings.get(profile_key) != 'Custom':
                log.info(
                    f"Setting {profile_key} → Custom "
                    f"(was: {updated_settings.get(profile_key)})"
                )
                updated_settings[profile_key] = 'Custom'

        # Validate applied settings
        validation_warnings = validate_settings(updated_settings, "restamp")
        for w in validation_warnings:
            log.warning(f"Validation: {w}")

        # Serialize updated config
        updated_config_bytes = json.dumps(updated_settings, indent=2).encode("utf-8")

        # Build output zip
        out_buf = BytesIO()
        with zipfile.ZipFile(out_buf, "w") as out_zip:
            for info in src_infos:
                fname = info.filename
                data = src_zip.read(fname)

                if fname == config_name:
                    # Replace with updated config
                    zi = zipfile.ZipInfo(fname)
                    zi.compress_type = compression_map.get(fname, zipfile.ZIP_DEFLATED)
                    out_zip.writestr(zi, updated_config_bytes)
                elif fname == model_settings_name and cleaned_model_settings_bytes is not None:
                    # Replace with cleaned model_settings (per-object overrides stripped)
                    zi = zipfile.ZipInfo(fname)
                    zi.compress_type = compression_map.get(fname, zipfile.ZIP_DEFLATED)
                    out_zip.writestr(zi, cleaned_model_settings_bytes)
                else:
                    # Copy byte-for-byte with original compression
                    zi = zipfile.ZipInfo(fname)
                    zi.compress_type = compression_map.get(fname, zipfile.ZIP_STORED)
                    out_zip.writestr(zi, data)

    # Write output file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(out_buf.getvalue())

    log.info(f"Written: {output_path}")
    return all_report, src_settings, updated_settings


# ---------------------------------------------------------------------------
# Diff printer
# ---------------------------------------------------------------------------
def print_diff(src_settings: dict, updated_settings: dict) -> None:
    """Print a table of keys that actually changed between src and updated config."""
    changed = {}
    all_keys = set(src_settings.keys()) | set(updated_settings.keys())
    for key in sorted(all_keys):
        before = src_settings.get(key, "<missing>")
        after = updated_settings.get(key, "<missing>")
        if before != after:
            changed[key] = (before, after)

    if not changed:
        print("ACTUAL CONFIG DIFF: no keys changed")
        return

    print()
    print("ACTUAL CONFIG DIFF (keys that changed)")
    print("-" * 72)
    print(f"  {'Key':<38} {'Before':<20} {'After'}")
    print("-" * 72)
    for key, (before, after) in changed.items():
        before_str = str(before)[:19]
        after_str = str(after)[:19]
        print(f"  {key[:37]:<38} {before_str:<20} {after_str}")
    print()


# ---------------------------------------------------------------------------
# Slice preview via BambuStudio CLI
# ---------------------------------------------------------------------------
BAMBU_STUDIO_BIN = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"


def run_slice_preview(output_3mf_path: str) -> None:
    """Run BambuStudio --slice on the output file and print slice stats."""
    bin_path = Path(BAMBU_STUDIO_BIN)
    if not bin_path.exists():
        log.warning(f"BambuStudio binary not found at {BAMBU_STUDIO_BIN} — skipping slice preview")
        return

    log.info(f"Running slice preview: {BAMBU_STUDIO_BIN} --slice {output_3mf_path}")
    try:
        result = subprocess.run(
            [str(bin_path), "--slice", output_3mf_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        log.warning("Slice preview timed out after 120s")
        return
    except Exception as e:
        log.warning(f"Slice preview failed: {e}")
        return

    output = (result.stdout or "") + (result.stderr or "")

    print()
    print("SLICE PREVIEW")
    print("-" * 72)

    # Try to extract useful stats
    layer_match = None
    time_match = None
    filament_match = None

    import re
    for line in output.splitlines():
        if not layer_match and re.search(r"layer[s]?\s*[:=]?\s*(\d+)", line, re.IGNORECASE):
            layer_match = line.strip()
        if not time_match and re.search(r"(print\s+time|estimated|time\s*[:=])", line, re.IGNORECASE):
            time_match = line.strip()
        if not filament_match and re.search(r"(filament|material)\s*[:=]?\s*[\d.]+", line, re.IGNORECASE):
            filament_match = line.strip()

    if layer_match or time_match or filament_match:
        if layer_match:
            print(f"  Layers:   {layer_match}")
        if time_match:
            print(f"  Time:     {time_match}")
        if filament_match:
            print(f"  Filament: {filament_match}")
    else:
        # Fall back to raw output, truncated
        lines = output.splitlines()
        print(f"  (raw output — could not parse stats)")
        for line in lines[:40]:
            print(f"  {line}")
        if len(lines) > 40:
            print(f"  ... ({len(lines) - 40} more lines)")

    if result.returncode != 0:
        print(f"  [exit code {result.returncode}]")
    print()


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------
def print_report(report_rows: list[dict], input_path: str, output_path: str) -> None:
    applied = [r for r in report_rows if r["status"] == "APPLIED"]
    skipped = [r for r in report_rows if r["status"] != "APPLIED"]

    print()
    print("=" * 72)
    print("3MF RESTAMP — SETTINGS REPORT")
    print("=" * 72)
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")
    print()

    if applied:
        print(f"APPLIED ({len(applied)} settings)")
        print("-" * 72)
        print(f"  {'Setting':<30} {'JSON Key':<35} {'Old':<18} {'New'}")
        print("-" * 72)
        for r in applied:
            old_str = str(r["old_value"])
            if len(old_str) > 17:
                old_str = old_str[:14] + "..."
            new_str = str(r["new_value"])
            if len(new_str) > 25:
                new_str = new_str[:22] + "..."
            print(
                f"  {r['human_name'][:29]:<30} {r['json_key'][:34]:<35} "
                f"{old_str:<18} {new_str}"
            )
    else:
        print("No settings applied.")

    if skipped:
        print()
        print(f"SKIPPED ({len(skipped)} settings)")
        print("-" * 72)
        for r in skipped:
            print(f"  {r['human_name'][:29]:<30} {r['status']}")

    print()
    print(f"DONE — {len(applied)} settings applied, {len(skipped)} skipped.")
    print("=" * 72)
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Apply print settings from a markdown file to an existing .3mf "
            "without changing the geometry. Produces a new .3mf with updated "
            "project_settings.config and all other content byte-identical."
        )
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--input", required=True, help="Source .3mf file to modify.")
    parser.add_argument("--settings", default=None, help="Markdown settings file (optional when --preset is used).")
    parser.add_argument(
        "--output",
        default=None,
        help="Output .3mf path (default: <input_stem>_restamped.3mf in same directory).",
    )
    parser.add_argument(
        "--preset",
        default=None,
        help="Preset name to load from presets/<name>.md (applied before --settings, overridden by it).",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        default=False,
        help="Print a diff table of config keys that actually changed.",
    )
    parser.add_argument(
        "--slice-preview",
        action="store_true",
        default=False,
        help="Run BambuStudio CLI to slice the output file and print layer/time/filament stats.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        log.error(f"Input file not found: {input_path}")
        sys.exit(1)

    if not args.settings and not args.preset:
        log.error("At least one of --settings or --preset is required")
        sys.exit(1)

    settings_path = Path(args.settings) if args.settings else None
    if settings_path and not settings_path.exists():
        log.error(f"Settings file not found: {settings_path}")
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_restamped.3mf"

    # Load preset if specified
    preset_rows = None
    if args.preset:
        preset_rows = load_preset(args.preset)

    report_rows, src_settings, updated_settings = restamp_3mf(
        str(input_path),
        str(settings_path) if settings_path else None,
        str(output_path),
        preset_rows=preset_rows,
    )
    print_report(report_rows, str(input_path), str(output_path))

    if args.diff:
        print_diff(src_settings, updated_settings)

    if args.slice_preview:
        run_slice_preview(str(output_path))


if __name__ == "__main__":
    main()
