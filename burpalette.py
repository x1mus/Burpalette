# -*- coding: utf-8 -*-
# Burpalette - Burp Suite Extension
# Replaces Burp's saturated HTTP history highlight colors with softer pastel
# equivalents, and ensures all highlighted row text is black for readability.
#
# Extension type : Python
# Tested on      : Burp Suite Professional / Community 2024.x+
# Python env     : Jython 2.7

from burp import IBurpExtender, IExtensionStateListener
from java.awt import Color
from javax.swing import SwingUtilities, UIManager
import javax.swing.plaf as plaf

EXTENSION_NAME    = "Burpalette"
EXTENSION_VERSION = "1.0.0"

# Confirmed slot -> color name mapping (slot = HighlightColor.ordinal() - 1):
#   slot 0 = RED     slot 1 = ORANGE   slot 2 = YELLOW
#   slot 3 = GREEN   slot 4 = CYAN     slot 5 = BLUE
#   slot 6 = PINK    slot 7 = MAGENTA  slot 8 = GRAY
SLOT_TO_NAME = {
    0: "RED",
    1: "ORANGE",
    2: "YELLOW",
    3: "GREEN",
    4: "CYAN",
    5: "BLUE",
    6: "PINK",
    7: "MAGENTA",
    8: "GRAY",
}

# Custom background colors (hand-picked)
PASTEL_BG = {
    "RED":     (255, 153, 153),
    "ORANGE":  (255, 200, 150),
    "YELLOW":  (255, 250, 150),
    "GREEN":   (168, 230, 168),
    "CYAN":    (168, 230, 230),
    "BLUE":    (180, 210, 255),
    "PINK":    (255, 210, 220),
    "MAGENTA": (230, 185, 255),
    "GRAY":    (210, 210, 210),
}

# Original Burp colors restored on unload
ORIGINAL_BG = {
    0: ((255, 100, 100), (255, 255, 255)),  # RED     - white text
    1: ((255, 200, 100), (0,   0,   0)),    # ORANGE
    2: ((255, 255, 100), (0,   0,   0)),    # YELLOW
    3: ((100, 255, 100), (0,   0,   0)),    # GREEN
    4: ((100, 255, 255), (0,   0,   0)),    # CYAN
    5: ((100, 100, 255), (255, 255, 255)),  # BLUE    - white text
    6: ((255, 200, 200), (0,   0,   0)),    # PINK
    7: ((255, 100, 255), (0,   0,   0)),    # MAGENTA
    8: ((180, 180, 180), (0,   0,   0)),    # GRAY
}

TEXT_RGB = (0, 0, 0)


class BurpExtender(IBurpExtender, IExtensionStateListener):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._stdout    = callbacks.getStdout()
        self._stderr    = callbacks.getStderr()

        callbacks.setExtensionName(EXTENSION_NAME)
        callbacks.registerExtensionStateListener(self)

        self._log("=== {} v{} loading ===".format(EXTENSION_NAME, EXTENSION_VERSION))
        SwingUtilities.invokeLater(self._apply_colors)

    # IExtensionStateListener
    def extensionUnloaded(self):
        SwingUtilities.invokeLater(self._restore_original_colors)
        self._log("Unloaded. Original colors restored.")

    def _apply_colors(self):
        patched = 0
        for slot, name in sorted(SLOT_TO_NAME.items()):
            bg_key   = "Colors.ui.highlight.{}.background".format(slot)
            text_key = "Colors.ui.highlight.{}.text".format(slot)
            rgb = PASTEL_BG.get(name)
            if rgb is None:
                continue
            try:
                old_bg   = UIManager.get(bg_key)
                old_text = UIManager.get(text_key)
                UIManager.put(bg_key,   plaf.ColorUIResource(rgb[0], rgb[1], rgb[2]))
                UIManager.put(text_key, plaf.ColorUIResource(TEXT_RGB[0], TEXT_RGB[1], TEXT_RGB[2]))
                self._log("  slot {} [{:7s}]  bg: {} -> rgb{}  text: {} -> black".format(
                    slot, name, self._rgb_str(old_bg), rgb, self._rgb_str(old_text)))
                patched += 1
            except Exception as e:
                self._err("  ERROR slot {} [{}]: {}".format(slot, name, e))
        self._log("Done: {} slots patched. Reopen HTTP history tab.".format(patched))

    def _restore_original_colors(self):
        for slot, (bg, text) in ORIGINAL_BG.items():
            try:
                UIManager.put("Colors.ui.highlight.{}.background".format(slot),
                              plaf.ColorUIResource(bg[0],   bg[1],   bg[2]))
                UIManager.put("Colors.ui.highlight.{}.text".format(slot),
                              plaf.ColorUIResource(text[0], text[1], text[2]))
            except Exception as e:
                self._err("  RESTORE ERROR slot {}: {}".format(slot, e))

    @staticmethod
    def _rgb_str(color):
        if color is None:
            return "None"
        try:
            return "rgb({},{},{})".format(
                color.getRed(), color.getGreen(), color.getBlue())
        except Exception:
            return str(color)

    def _log(self, msg):
        self._stdout.write("[{}] {}\n".format(EXTENSION_NAME, msg))
        self._stdout.flush()

    def _err(self, msg):
        self._stderr.write("[{}] {}\n".format(EXTENSION_NAME, msg))
        self._stderr.flush()
