<p align="center">
  <img src="logo.png" alt="Burpalette logo" width="220"/>
</p>

<h1 align="center">Burpalette</h1>

<p align="center">
  A Burp Suite extension that replaces the default saturated HTTP history highlight
  colors with softer pastel equivalents. Colors are fully customizable directly
  within Burp via the <strong>Burpalette</strong> tab.<br><br>
  All highlighted row text is forced to <strong>black</strong>, fixing the readability issues
  with Burp's default white-on-red and white-on-blue rows.
</p>

---

## Features

- Replaces all 9 Burp highlight colors (Red, Orange, Yellow, Green, Cyan, Blue,
  Pink, Magenta, Gray) with hand-picked pastel equivalents
- **Live color editor** — dedicated Burp tab with R/G/B spinners, color swatch,
  and text preview per color
- Forces highlighted row text to black for maximum readability
- Apply button applies changes instantly without reloading the extension
- Reset to Burpalette defaults or original Burp colors in one click
- Restores original Burp colors cleanly on extension unload

## Default color mapping

| Highlight | Original (approx.)  | Burpalette default  |
|-----------|---------------------|---------------------|
| Red       | rgb(255, 100, 100)  | rgb(255, 153, 153)  |
| Orange    | rgb(255, 200, 100)  | rgb(255, 200, 150)  |
| Yellow    | rgb(255, 255, 100)  | rgb(255, 250, 150)  |
| Green     | rgb(100, 255, 100)  | rgb(168, 230, 168)  |
| Cyan      | rgb(100, 255, 255)  | rgb(168, 230, 230)  |
| Blue      | rgb(100, 100, 255)  | rgb(180, 210, 255)  |
| Pink      | rgb(255, 200, 200)  | rgb(255, 210, 220)  |
| Magenta   | rgb(255, 100, 255)  | rgb(230, 185, 255)  |
| Gray      | rgb(180, 180, 180)  | rgb(210, 210, 210)  |

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

After loading, a **Burpalette** tab appears in the Burp top bar, and HTTP
history highlights are updated immediately.

## Usage

1. Open the **Burpalette** tab in Burp.
2. Adjust R, G, B values for any highlight color using the spinners.
   The swatch and preview label update live as you type.
3. Click **Apply** to apply the new colors to HTTP history.
4. Use **Reset to Burpalette defaults** to restore the built-in pastel colors.
5. Use **Reset to Burp defaults** to restore Burp's original saturated colors.

## Unloading

When the extension is unloaded via **Extensions → Installed**, the original
Burp highlight colors are automatically restored.

---

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
