import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio
import subprocess
import json


class SettingsPageComponent:
    """Settings page component"""

    def __init__(self):
        self.monitor_combo = None
        self.zoom_spin = None
        self.pan_x_spin = None
        self.pan_y_spin = None
        self.autopause_switch = None
        self.dark_switch = None
        self.username_entry = None

    def create_settings_page(self, config_manager, callbacks):
        """Create and return the settings page widget

        Args:
            config_manager: ConfigManager instance
            callbacks: Dict with callback functions:
                - on_monitor_changed
                - on_zoom_changed
                - on_pan_changed
                - on_autopause_changed
                - on_dark_mode_changed
                - on_username_changed
                - on_choose_avatar

        Returns:
            Gtk.Box containing the settings page
        """
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.add_css_class("content-area")

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.add_css_class("feeds-header")
        header.set_margin_bottom(12)

        title = Gtk.Label(label="Settings")
        title.add_css_class("feeds-title")
        title.set_halign(Gtk.Align.START)
        header.append(title)

        content.append(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        settings_box.set_margin_end(10)

        # Display Settings Section
        display_section = self._create_display_section(config_manager, callbacks)
        settings_box.append(display_section)

        # Appearance Section
        appearance_section = self._create_appearance_section(config_manager, callbacks)
        settings_box.append(appearance_section)

        # Profile Section
        profile_section = self._create_profile_section(config_manager, callbacks)
        settings_box.append(profile_section)

        scrolled.set_child(settings_box)
        content.append(scrolled)

        return content

    def _create_display_section(self, config_manager, callbacks):
        """Create display settings section"""
        section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section.add_css_class("settings-section")

        title = Gtk.Label(label="Display Settings")
        title.add_css_class("settings-title")
        title.set_halign(Gtk.Align.START)
        section.append(title)

        # Monitor Selection
        section.append(self._create_monitor_row(config_manager, callbacks))

        # Video Zoom
        section.append(self._create_zoom_row(config_manager, callbacks))

        # Pan X
        section.append(self._create_pan_x_row(config_manager, callbacks))

        # Pan Y
        section.append(self._create_pan_y_row(config_manager, callbacks))

        # Auto-Pause
        section.append(self._create_autopause_row(config_manager, callbacks))

        return section

    def _create_monitor_row(self, config_manager, callbacks):
        """Create monitor selection row"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        label = Gtk.Label(label="Monitor")
        label.add_css_class("control-label")
        row.append(label)
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        row.append(spacer)

        self.monitor_combo = Gtk.ComboBoxText()
        self.monitor_combo.append("*", "All Monitors")
        for mon in self._get_monitors():
            self.monitor_combo.append(mon, mon)
        self.monitor_combo.set_active_id(config_manager.get("monitor", "*"))
        self.monitor_combo.add_css_class("scale-dropdown")
        self.monitor_combo.connect("changed", callbacks["on_monitor_changed"])
        row.append(self.monitor_combo)
        return row

    def _create_zoom_row(self, config_manager, callbacks):
        """Create zoom row"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        label = Gtk.Label(label="Video Zoom")
        label.add_css_class("control-label")
        row.append(label)
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        row.append(spacer)

        self.zoom_spin = Gtk.SpinButton.new_with_range(-1.0, 2.0, 0.1)
        self.zoom_spin.set_value(config_manager.get("video_zoom", 0.0))
        self.zoom_spin.set_digits(1)
        self.zoom_spin.add_css_class("spin-entry")
        self.zoom_spin.connect("value-changed", callbacks["on_zoom_changed"])
        row.append(self.zoom_spin)
        return row

    def _create_pan_x_row(self, config_manager, callbacks):
        """Create pan X row"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        label = Gtk.Label(label="Pan X")
        label.add_css_class("control-label")
        row.append(label)
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        row.append(spacer)

        self.pan_x_spin = Gtk.SpinButton.new_with_range(-1.0, 1.0, 0.05)
        self.pan_x_spin.set_value(config_manager.get("video_pan_x", 0.0))
        self.pan_x_spin.set_digits(2)
        self.pan_x_spin.add_css_class("spin-entry")
        self.pan_x_spin.connect("value-changed", callbacks["on_pan_changed"])
        row.append(self.pan_x_spin)
        return row

    def _create_pan_y_row(self, config_manager, callbacks):
        """Create pan Y row"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        label = Gtk.Label(label="Pan Y")
        label.add_css_class("control-label")
        row.append(label)
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        row.append(spacer)

        self.pan_y_spin = Gtk.SpinButton.new_with_range(-1.0, 1.0, 0.05)
        self.pan_y_spin.set_value(config_manager.get("video_pan_y", 0.0))
        self.pan_y_spin.set_digits(2)
        self.pan_y_spin.add_css_class("spin-entry")
        self.pan_y_spin.connect("value-changed", callbacks["on_pan_changed"])
        row.append(self.pan_y_spin)
        return row

    def _create_autopause_row(self, config_manager, callbacks):
        """Create auto-pause row"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        label = Gtk.Label(label="Auto-Pause")
        label.add_css_class("control-label")
        row.append(label)
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        row.append(spacer)

        self.autopause_switch = Gtk.Switch()
        self.autopause_switch.set_active(config_manager.get("auto_pause", False))
        self.autopause_switch.connect("state-set", callbacks["on_autopause_changed"])
        row.append(self.autopause_switch)
        return row

    def _create_appearance_section(self, config_manager, callbacks):
        """Create appearance settings section"""
        section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section.add_css_class("settings-section")

        title = Gtk.Label(label="Appearance")
        title.add_css_class("settings-title")
        title.set_halign(Gtk.Align.START)
        section.append(title)

        dark_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        dark_label = Gtk.Label(label="Dark Mode")
        dark_label.add_css_class("control-label")
        dark_row.append(dark_label)
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        dark_row.append(spacer)

        self.dark_switch = Gtk.Switch()
        self.dark_switch.set_active(config_manager.get("dark_mode", True))
        self.dark_switch.connect("state-set", callbacks["on_dark_mode_changed"])
        dark_row.append(self.dark_switch)
        section.append(dark_row)

        return section

    def _create_profile_section(self, config_manager, callbacks):
        """Create profile settings section"""
        section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section.add_css_class("settings-section")

        title = Gtk.Label(label="Profile")
        title.add_css_class("settings-title")
        title.set_halign(Gtk.Align.START)
        section.append(title)

        # Username
        name_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        name_label = Gtk.Label(label="Username")
        name_label.add_css_class("control-label")
        name_row.append(name_label)
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        name_row.append(spacer)

        self.username_entry = Gtk.Entry()
        self.username_entry.set_text(config_manager.get("username", "Snow"))
        self.username_entry.add_css_class("url-entry")
        self.username_entry.set_max_width_chars(15)
        self.username_entry.connect("changed", callbacks["on_username_changed"])
        name_row.append(self.username_entry)
        section.append(name_row)

        # Avatar
        avatar_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        avatar_label = Gtk.Label(label="Avatar")
        avatar_label.add_css_class("control-label")
        avatar_row.append(avatar_label)
        spacer2 = Gtk.Box()
        spacer2.set_hexpand(True)
        avatar_row.append(spacer2)

        avatar_btn = Gtk.Button(label="Choose Image")
        avatar_btn.add_css_class("folder-button")
        avatar_btn.connect("clicked", callbacks["on_choose_avatar"])
        avatar_row.append(avatar_btn)
        section.append(avatar_row)

        return section

    def _get_monitors(self):
        """Get available monitors using hyprctl"""
        monitors = []
        try:
            result = subprocess.run(
                ["hyprctl", "monitors", "-j"], capture_output=True, text=True
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for mon in data:
                    monitors.append(mon.get("name", ""))
        except Exception:
            pass
        return monitors
