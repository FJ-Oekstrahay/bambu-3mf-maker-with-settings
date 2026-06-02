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
import json
import sys
import zipfile
from io import BytesIO
from pathlib import Path

# Import shared logic from the sibling module
sys.path.insert(0, str(Path(__file__).parent))
from make_bambu_3mf import (
    SETTING_KEY_MAP,
    apply_settings,
    parse_settings_markdown,
)

import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

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
def restamp_3mf(input_path: str, settings_md: str, output_path: str) -> list[dict]:
    """
    Open source 3mf, apply settings from markdown, write new 3mf.
    Returns combined report rows for all applied/skipped settings.
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

        # Parse the markdown
        md_rows = parse_settings_markdown(settings_md)
        log.info(f"Parsed {len(md_rows)} rows from settings markdown")

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
    return all_report


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
    parser.add_argument("--settings", required=True, help="Markdown settings file.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output .3mf path (default: <input_stem>_restamped.3mf in same directory).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        log.error(f"Input file not found: {input_path}")
        sys.exit(1)

    settings_path = Path(args.settings)
    if not settings_path.exists():
        log.error(f"Settings file not found: {settings_path}")
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_restamped.3mf"

    report_rows = restamp_3mf(str(input_path), str(settings_path), str(output_path))
    print_report(report_rows, str(input_path), str(output_path))


if __name__ == "__main__":
    main()
