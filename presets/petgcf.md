# PETG-CF — Baseline Preset
## Bambu A1 Mini · PETG-CF (Carbon Fiber Reinforced)

> Baseline for PETG-CF. Higher temps, moderate speeds, no support by default.
> Override with --settings for part-specific structural requirements.

---

## Summary of All Changes

| Tab | Setting | Default | Value | Notes |
|---|---|---|---|---|
| Filament | Nozzle temperature | 220 | 265 | PETG-CF requires high nozzle temp |
| Filament | Bed temperature | 45 | 70 | PETG-CF needs warm bed |
| Speed | Initial layer speed | 20 | 25 | Slightly slower first layer for adhesion |
| Speed | Outer wall | 200 | 100 | PETG-CF surface quality at 100 mm/s |
| Speed | Inner wall | 300 | 200 | Inner walls can be faster |
| Speed | Sparse infill | 270 | 250 | PETG-CF flows well at high speed |
| Filament | Fan speed (general) | 70 | 50 | Moderate cooling for PETG-CF layer bonding |
| Filament | Fan speed (first layer) | 0 | 0 | Never cool first layer |
| Strength | Wall loops | 2 | 3 | Standard structural shell |
| Strength | Sparse infill density | 15% | 20% | Slightly denser for structural parts |
| Strength | Sparse infill pattern | Grid | gyroid | Isotropic strength |
| Support | Enable support | 1 | 0 | No support by default — orient parts to avoid |
| Support | Support type | normal | normal | Normal support if enabled |
| Support | Threshold angle | 30 | 45 | Standard overhang threshold |
