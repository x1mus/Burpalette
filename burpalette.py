# -*- coding: utf-8 -*-
# Burpalette - Burp Suite Extension
# Replaces Burp's saturated HTTP history highlight colors with customizable
# pastel equivalents. Provides a settings tab for live color editing.
#
# Extension type : Python
# Python env     : Jython 2.7

from burp import IBurpExtender, IExtensionStateListener, ITab
from java.awt import Color, GridBagLayout, GridBagConstraints, Insets, Dimension, Font
from java.awt import BorderLayout, FlowLayout
from javax.swing import (JPanel, JLabel, JSpinner, SpinnerNumberModel, JButton,
						 JScrollPane, SwingUtilities, UIManager, BorderFactory,
						 Box, BoxLayout, JComponent)
from javax.swing.border import EmptyBorder
import javax.swing.plaf as plaf

EXTENSION_NAME    = "Burpalette"
EXTENSION_VERSION = "1.0.0"

# Confirmed slot -> color name (slot = HighlightColor.ordinal() - 1)
SLOT_ORDER = ["RED", "ORANGE", "YELLOW", "GREEN", "CYAN", "BLUE", "PINK", "MAGENTA", "GRAY"]

# Default pastel colors (hand-picked)
PASTEL_DEFAULTS = {
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

# Original Burp defaults (for restore on unload / reset button)
BURP_DEFAULTS = {
	"RED":     ((255, 100, 100), (255, 255, 255)),
	"ORANGE":  ((255, 200, 100), (0,   0,   0)),
	"YELLOW":  ((255, 255, 100), (0,   0,   0)),
	"GREEN":   ((100, 255, 100), (0,   0,   0)),
	"CYAN":    ((100, 255, 255), (0,   0,   0)),
	"BLUE":    ((100, 100, 255), (255, 255, 255)),
	"PINK":    ((255, 200, 200), (0,   0,   0)),
	"MAGENTA": ((255, 100, 255), (0,   0,   0)),
	"GRAY":    ((180, 180, 180), (0,   0,   0)),
}

TEXT_COLOR = (0, 0, 0)


class ColorRow(object):
	"""One row in the settings panel: label + R/G/B spinners + swatch + preview."""

	def __init__(self, name, rgb):
		self.name = name
		self._r_model = SpinnerNumberModel(rgb[0], 0, 255, 1)
		self._g_model = SpinnerNumberModel(rgb[1], 0, 255, 1)
		self._b_model = SpinnerNumberModel(rgb[2], 0, 255, 1)

		self._swatch  = JPanel()
		self._swatch.setPreferredSize(Dimension(48, 28))
		self._swatch.setMinimumSize(Dimension(48, 28))
		self._swatch.setBorder(BorderFactory.createLineBorder(Color(180, 180, 180), 1))

		self._preview = JLabel(name)
		self._preview.setPreferredSize(Dimension(80, 28))
		self._preview.setMinimumSize(Dimension(80, 28))
		self._preview.setHorizontalAlignment(JLabel.CENTER)
		self._preview.setOpaque(True)
		self._preview.setBorder(BorderFactory.createLineBorder(Color(180, 180, 180), 1))
		font = self._preview.getFont()
		self._preview.setFont(Font(font.getName(), Font.BOLD, 11))

		# Wire up live updates
		for model in (self._r_model, self._g_model, self._b_model):
			model.addChangeListener(self._on_change)

		self._update_swatch()

	def _on_change(self, event):
		self._update_swatch()

	def _update_swatch(self):
		r, g, b = self.get_rgb()
		color = Color(r, g, b)
		self._swatch.setBackground(color)
		self._preview.setBackground(color)
		# Pick black or white text based on luminance
		lum = 0.299 * r + 0.587 * g + 0.114 * b
		self._preview.setForeground(Color.BLACK if lum > 160 else Color.WHITE)
		self._swatch.repaint()
		self._preview.repaint()

	def get_rgb(self):
		return (
			int(self._r_model.getValue()),
			int(self._g_model.getValue()),
			int(self._b_model.getValue()),
		)

	def set_rgb(self, r, g, b):
		self._r_model.setValue(r)
		self._g_model.setValue(g)
		self._b_model.setValue(b)
		self._update_swatch()

	def build_spinner(self, model):
		s = JSpinner(model)
		s.setPreferredSize(Dimension(64, 28))
		s.setMinimumSize(Dimension(64, 28))
		# Limit editor columns
		editor = s.getEditor()
		try:
			editor.getTextField().setColumns(3)
		except Exception:
			pass
		return s

	def add_to_panel(self, panel, gbc, row):
		"""Add this color row's components to a GridBagLayout panel."""
		gbc.gridy   = row
		gbc.weightx = 0
		gbc.fill    = GridBagConstraints.NONE

		# Name label
		gbc.gridx  = 0
		gbc.insets = Insets(4, 8, 4, 12)
		label = JLabel(self.name)
		label.setPreferredSize(Dimension(72, 28))
		font = label.getFont()
		label.setFont(Font(font.getName(), Font.BOLD, 12))
		panel.add(label, gbc)

		# R spinner
		gbc.gridx  = 1
		gbc.insets = Insets(4, 2, 4, 2)
		panel.add(self.build_spinner(self._r_model), gbc)

		# G spinner
		gbc.gridx = 2
		panel.add(self.build_spinner(self._g_model), gbc)

		# B spinner
		gbc.gridx = 3
		panel.add(self.build_spinner(self._b_model), gbc)

		# Swatch
		gbc.gridx  = 4
		gbc.insets = Insets(4, 10, 4, 4)
		panel.add(self._swatch, gbc)

		# Preview label
		gbc.gridx  = 5
		gbc.insets = Insets(4, 4, 4, 8)
		panel.add(self._preview, gbc)


class BurpaletteTab(ITab):
	"""Swing panel registered as a Burp Suite tab."""

	def __init__(self, extension):
		self._ext   = extension
		self._rows  = {}
		self._panel = self._build_panel()

	def getTabCaption(self):
		return EXTENSION_NAME

	def getUiComponent(self):
		return self._panel

	def _build_panel(self):
		outer = JPanel(BorderLayout())
		outer.setBorder(EmptyBorder(20, 24, 20, 24))

		inner = JPanel(GridBagLayout())
		gbc   = GridBagConstraints()

		# ── Header row ──────────────────────────────────────────────────────
		gbc.gridy   = 0
		gbc.weightx = 0
		gbc.fill    = GridBagConstraints.NONE
		gbc.anchor  = GridBagConstraints.WEST

		headers = ["Color", "R", "G", "B", "Swatch", "Preview"]
		insets_map = [
			Insets(0, 8, 8, 12),
			Insets(0, 2, 8, 2),
			Insets(0, 2, 8, 2),
			Insets(0, 2, 8, 2),
			Insets(0, 10, 8, 4),
			Insets(0, 4, 8, 8),
		]
		for col, (h, ins) in enumerate(zip(headers, insets_map)):
			gbc.gridx  = col
			gbc.insets = ins
			lbl = JLabel(h)
			lbl.setFont(Font(lbl.getFont().getName(), Font.BOLD, 11))
			lbl.setForeground(Color(120, 120, 120))
			inner.add(lbl, gbc)

		# ── Color rows ───────────────────────────────────────────────────────
		gbc.anchor = GridBagConstraints.WEST
		for i, name in enumerate(SLOT_ORDER):
			rgb = PASTEL_DEFAULTS[name]
			row = ColorRow(name, rgb)
			self._rows[name] = row
			row.add_to_panel(inner, gbc, i + 1)

		# ── Spacer col to push everything left ───────────────────────────────
		gbc.gridx   = 6
		gbc.gridy   = 0
		gbc.weightx = 1.0
		gbc.fill    = GridBagConstraints.HORIZONTAL
		gbc.insets  = Insets(0, 0, 0, 0)
		inner.add(JLabel(""), gbc)

		# ── Button bar ───────────────────────────────────────────────────────
		btn_panel = JPanel(FlowLayout(FlowLayout.LEFT, 8, 0))
		btn_panel.setBorder(EmptyBorder(16, 0, 0, 0))

		btn_apply  = JButton("Apply")
		btn_pastel = JButton("Reset to Burpalette defaults")
		btn_burp   = JButton("Reset to Burp defaults")

		btn_apply.addActionListener(lambda e: self._apply())
		btn_pastel.addActionListener(lambda e: self._reset_pastel())
		btn_burp.addActionListener(lambda e: self._reset_burp())

		btn_panel.add(btn_apply)
		btn_panel.add(btn_pastel)
		btn_panel.add(btn_burp)

		# ── Hint label ───────────────────────────────────────────────────────
		hint = JLabel("Changes take effect immediately in HTTP history after clicking Apply.")
		hint.setFont(Font(hint.getFont().getName(), Font.PLAIN, 11))
		hint.setForeground(Color(130, 130, 130))
		hint_panel = JPanel(FlowLayout(FlowLayout.LEFT, 0, 0))
		hint_panel.setBorder(EmptyBorder(6, 0, 0, 0))
		hint_panel.add(hint)

		# ── Assemble ─────────────────────────────────────────────────────────
		content = JPanel()
		content.setLayout(BoxLayout(content, BoxLayout.Y_AXIS))
		content.add(inner)
		content.add(btn_panel)
		content.add(hint_panel)

		outer.add(content, BorderLayout.NORTH)
		return outer

	def _apply(self):
		for slot, name in enumerate(SLOT_ORDER):
			r, g, b = self._rows[name].get_rgb()
			bg_key   = "Colors.ui.highlight.{}.background".format(slot)
			text_key = "Colors.ui.highlight.{}.text".format(slot)
			UIManager.put(bg_key,   plaf.ColorUIResource(r, g, b))
			UIManager.put(text_key, plaf.ColorUIResource(
				TEXT_COLOR[0], TEXT_COLOR[1], TEXT_COLOR[2]))
		self._ext.log("Colors applied.")

	def _reset_pastel(self):
		for name in SLOT_ORDER:
			r, g, b = PASTEL_DEFAULTS[name]
			self._rows[name].set_rgb(r, g, b)
		self._apply()

	def _reset_burp(self):
		for name in SLOT_ORDER:
			(r, g, b), _ = BURP_DEFAULTS[name]
			self._rows[name].set_rgb(r, g, b)
		self._apply()


class BurpExtender(IBurpExtender, IExtensionStateListener):

	def registerExtenderCallbacks(self, callbacks):
		self._callbacks = callbacks
		self._stdout    = callbacks.getStdout()
		self._stderr    = callbacks.getStderr()

		callbacks.setExtensionName(EXTENSION_NAME)
		callbacks.registerExtensionStateListener(self)

		self.log("=== {} v{} loading ===".format(EXTENSION_NAME, EXTENSION_VERSION))

		def setup():
			self._tab = BurpaletteTab(self)
			callbacks.addSuiteTab(self._tab)
			# Apply pastel defaults on load
			self._tab._apply()
			self.log("Tab registered. Reopen HTTP history tab to see changes.")

		SwingUtilities.invokeLater(setup)

	def extensionUnloaded(self):
		def restore():
			for slot, name in enumerate(SLOT_ORDER):
				(r, g, b), (tr, tg, tb) = BURP_DEFAULTS[name]
				UIManager.put("Colors.ui.highlight.{}.background".format(slot),
							  plaf.ColorUIResource(r, g, b))
				UIManager.put("Colors.ui.highlight.{}.text".format(slot),
							  plaf.ColorUIResource(tr, tg, tb))
		SwingUtilities.invokeLater(restore)
		self.log("Unloaded. Original Burp colors restored.")

	def log(self, msg):
		self._stdout.write("[{}] {}\n".format(EXTENSION_NAME, msg))
		self._stdout.flush()

	def err(self, msg):
		self._stderr.write("[{}] {}\n".format(EXTENSION_NAME, msg))
		self._stderr.flush()
