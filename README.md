# Burpalette

A Burp Suite extension that replaces the default saturated HTTP history highlight
colors with softer pastel equivalents, making it easier to work with highlighted
requests during long testing sessions.

All highlighted row text is also forced to **black**, fixing the readability
issues with Burp's default white-on-red and white-on-blue rows.

---

## Features

- Replaces all 9 Burp highlight colors (Red, Orange, Yellow, Green, Cyan, Blue,
  Pink, Magenta, Gray) with hand-picked pastel equivalents
- Forces highlighted row text to black for maximum readability
- Restores original Burp colors cleanly on extension unload
- No network requests, no dependencies beyond Jython

## Color mapping

| Highlight | Original (approx.) | Burpalette color   |
|-----------|--------------------|--------------------|
| Red       | rgb(255,100,100)   | rgb(255,153,153)   |
| Orange    | rgb(255,200,100)   | rgb(255,200,150)   |
| Yellow    | rgb(255,255,100)   | rgb(255,250,150)   |
| Green     | rgb(100,255,100)   | rgb(168,230,168)   |
| Cyan      | rgb(100,255,255)   | rgb(168,230,230)   |
| Blue      | rgb(100,100,255)   | rgb(180,210,255)   |
| Pink      | rgb(255,200,200)   | rgb(255,210,220)   |
| Magenta   | rgb(255,100,255)   | rgb(230,185,255)   |
| Gray      | rgb(180,180,180)   | rgb(210,210,210)   |

---

## Requirements

- Burp Suite Professional or Community Edition (2022.x or later recommended)
- Jython 2.7 standalone JAR configured in Burp's Python environment
  (**Extensions → Options → Python environment**)

## Installation

### From the BApp Store
1. In Burp, go to **Extensions → BApp Store**.
2. Search for **Burpalette** and click **Install**.

### Manual installation
1. Download `burpalette.py`.
2. In Burp, go to **Extensions → Installed → Add**.
3. Set **Extension type** to **Python**.
4. Select `burpalette.py` and click **Next**.

After loading, reopen the **HTTP history** tab (Proxy → HTTP history) to see
the updated colors.

## Customizing colors

Open `burpalette.py` and edit the `PASTEL_BG` dictionary near the top
of the file. Each entry is an `(R, G, B)` tuple.

```python
PASTEL_BG = {
    "RED":     (255, 153, 153),   # ← change these values
    ...
}
```

Reload the extension after saving for changes to take effect.

## Unloading

When the extension is unloaded via **Extensions → Installed**, the original
Burp highlight colors are automatically restored.

---

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.

## Author

Maximilien Laenen
Claude
