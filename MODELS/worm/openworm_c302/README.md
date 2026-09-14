# openworm_c302

**What:** *C. elegans* whole-animal connectivity (White et al. 1986) as used by OpenWorm/c302.  
**Why:** Third offline comparison brain — small enough to load instantly, biological, between DSC and FlyWire.

## Obtain / refresh

```bash
curl -fsSL -o aconnectome_white_1986_whole.csv \
  https://raw.githubusercontent.com/openworm/c302/master/c302/data/aconnectome_white_1986_whole.csv
```

Then regenerate `edges.csv` / `edges_neural.csv` / `manifest.json` (or re-run the pack builder in `FEATURES/F017`).

## Files
| File | Role |
|------|------|
| `aconnectome_white_1986_whole.csv` | Upstream TSV |
| `edges_neural.csv` | UI default (muscles stripped) |
| `edges.csv` | All cells including muscle stubs |
| `manifest.json` | Stats + provenance |

## Console
`/load openworm`  (aliases: `worm`, `celegans`, `c302`)

Static graph only — no `/tick` / `/evolve` (same as FlyWire).
