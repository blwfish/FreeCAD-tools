# Gap Proportions - Visual Guide

## Based on Gordonsville Depot 1970 Photo

### Observations

From the reference photo analysis:

1. **Border thickness**: ~1/9 of letter height → 0.5mm in HO scale
2. **Horizontal gap** (left/right): Approximately 3× border thickness → 1.5mm
3. **Vertical gap** (top/bottom): Approximately 1.5× border thickness → 0.75mm

### Why Different Gaps?

This is standard practice in sign design:
- **Horizontal**: More generous to handle long station names gracefully
- **Vertical**: Tighter to maintain compact vertical profile
- **Result**: Sign appears balanced, not too tall and narrow

### Proportions

```
16" letters at full scale = 4.67mm in HO scale

Border:     0.5mm (fixed)
Gap H:      1.5mm (3× border)
Gap V:      0.75mm (1.5× border)

Ratio:      Gap H : Gap V = 2:1
```

### ASCII Art Comparison

**Old way (equal gaps - v1.1.x):**
```
┌─────────────────────────────────────┐
│ 0.5mm border                        │
│  ┌───────────────────────────────┐  │
│  │ 1.0mm gap all around          │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  G O R D O N S V I L L E│  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```
Problem: Sign looks slightly cramped horizontally

**New way (separate gaps - v1.2.0):**
```
┌─────────────────────────────────────────┐
│ 0.5mm border                            │
│  ┌───────────────────────────────────┐  │
│  │ H:1.5mm   │ V:0.75mm             │  │
│  │           ├──────────────────────┤  │
│  │  G O R D O N S V I L L E         │  │
│  │           └──────────────────────┘  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```
Result: Sign proportions match prototype photo

### Measurements from Photo

Assuming 16" letters (actual specification):

| Element | Full Scale | HO Scale (1:87) | Notes |
|---------|-----------|-----------------|-------|
| Letter height | 16" | 4.67mm | Specification |
| Border width | ~1.8" | 0.53mm | ~1/9 of letter |
| Gap horizontal | ~5" | 1.46mm | ~3× border |
| Gap vertical | ~2.5" | 0.73mm | ~1.5× border |

### Default Parameters (Rounded)

```python
borderThickness = 0.5mm        # Match prototype
borderGapHorizontal = 1.5mm    # Generous horizontal
borderGapVertical = 0.75mm     # Tighter vertical
```

### Example: "GORDONSVILLE"

With these parameters:
- Text width: ~35mm (varies with font)
- Text height: ~4.67mm
- Sign width: 1.0 + 3.0 + 35 = 39mm
- Sign height: 1.0 + 1.5 + 4.67 = 7.17mm

Matches the elongated horizontal proportion visible in the photo!

### Customization

Users can override in Skeleton spreadsheet:

```
Cell B4: borderGapHorizontal (default 1.5)
Cell B5: borderGapVertical (default 0.75)
```

For shorter names, you might want:
- Equal gaps: H=1.0, V=1.0
- More square signs: H=1.0, V=1.5

For longer names:
- Current defaults work well: H=1.5, V=0.75
- Or even more horizontal: H=2.0, V=0.75
