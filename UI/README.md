# UI — Connectome operator console

**Status:** v0 runnable (FlyWire load + slash palette). Not required for DSC correctness.  
**Feature:** [F012](../FEATURES/F012_connectome_operator_console.md)

Monitor and dialog only. Evolution / integrity live elsewhere.

## Setup

```bash
cd UI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

FlyWire data is **not** in git. Place packs per root [README.md](../README.md) → *Getting biological packs*.  
Minimum for UI test: `MODELS/fly/flywire_v783/proofread_connections_783.feather`

## Run

```bash
cd UI
source .venv/bin/activate
python -m console
```

Then:

```text
/load dsc
/tick 8
/load flywire
/status
/focus AL
/signal degree_entropy
/sample 16
/export
```

Press `/` to open the command palette above the input. Esc clears. `/quit` exits.

### Headless smoke (no TTY)

```bash
cd UI
source .venv/bin/activate
python -m console.smoke_flywire
```

## Layout
Banner · canvas · signal strips · summary · scrolling terminal · `/` palette · command input.

## Adapters
| Module | Status |
|--------|--------|
| `adapters/flywire_pack.py` | **v0** — load / focus / signals / export |
| `adapters/dsc_runtime.py` | scaffold — loads `MODEL/active/manifest.json` only |
| `male_cns` / `hemibrain` | stubs |

## Paths
| Path | Role |
|------|------|
| `MODEL/active/` | DSC under development |
| `MODELS/` | Biological packs (gitignored binaries) |
| `UI/exports/` | `/export` dumps (gitignored) |

## Live color + sampling
- Signal scale: **blue** (low) → **purple** (mid) → **red** (high).
- `/sample [hz]` sets live refresh rate (default **8**, try **16**). Range 1–30.
- Static packs (FlyWire) still *breathe*: node bars and edge highlight pulse each sample.

## Menu (Ctrl+P)

Ctrl+P opens **Menu** (Textual system commands). **Theme** remaps:

- panel chrome (banner, borders, backgrounds) via CSS variables
- signal scale (low → mid → high) for grid / bars / sparklines

DSC themes: `dsc-violet` (default), `dsc-ocean`, `dsc-ember`, `dsc-mono`. Built-in themes (nord, dracula, …) also drive signals from their secondary / accent / error colors.
