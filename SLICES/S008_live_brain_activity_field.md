# S008 — Live FlyWire BRAIN MAP activity field

**Status:** complete (2026-09-13)  
**Feature:** F019  
**Source:** https://github.com/dealer1943/FlyBrains

## What shipped
- `BrainField` — soma-projected energy with decay + neighbor bleed + region glyph paint
- `FlyActivityEngine` — offline tick: region drive + spatial kNN recruitment
- FlyWire adapter: `/stim`, `/pulse`, `/rest`; `sample_frame` ticks the field
- Biology pane uses live markup when FlyWire is loaded
- Assets: `UI/assets/biology/flywire_layout.npz`, `flywire_knn8.npz`

## Try
```
/load flywire
/stim optic 0.4
/pulse taste
/rest
```

## OpenWorm addendum
- Anatomical C. elegans layout (anterior→posterior; amphid / ring / command / cords / tail)
- Graph propagation on White 1986 edges (`WormActivityEngine`)
- Same `/stim` `/pulse` `/rest` verbs; biology pane title `WORM MAP`
