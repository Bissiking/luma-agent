# Changelog

## 0.5.2 - 2026-03-01
- Added richer Windows disk metadata in metrics collection (`core/metrics.py`).
- Added `device`, `drive_type`, and `display_name` for disk entries.
- Added Windows volume fallback naming when no user label exists.
- Kept cross-platform compatibility (non-Windows returns empty/None for Windows-specific fields).

## 0.5.1 - 2026-02-09
- Previous release.
