import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class SidebarComponent:
    """Sidebar navigation component"""

    def __init__(self):
        self.local_btn = None
        self.settings_btn = None

    def create_sidebar(self, on_switch_page):
        """Create and return the sidebar widget

        Args:
            on_switch_page: Callback function for page switching
        """
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar.add_css_class("sidebar")
        sidebar.set_size_request(130, -1)
        sidebar.set_vexpand(True)

        # Snowflake Logo Header
        header = self._create_header()
        sidebar.append(header)

        # Menu Label
        menu_label = Gtk.Label(label="Menu")
        menu_label.add_css_class("menu-label")
        menu_label.set_halign(Gtk.Align.START)
        menu_label.set_margin_start(12)
        menu_label.set_margin_top(10)
        sidebar.append(menu_label)

        # Local button
        self.local_btn = self._create_menu_item("folder-videos-symbolic", "Local", True)
        self.local_btn.connect("clicked", lambda b: on_switch_page("local"))
        sidebar.append(self.local_btn)

        # Settings button
        self.settings_btn = self._create_menu_item(
            "emblem-system-symbolic", "Settings", False
        )
        self.settings_btn.connect("clicked", lambda b: on_switch_page("settings"))
        sidebar.append(self.settings_btn)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        sidebar.append(spacer)

        # Branding
        branding = Gtk.Label(label="Snow")
        branding.add_css_class("app-branding")
        branding.set_halign(Gtk.Align.START)
        branding.set_margin_start(12)
        branding.set_margin_bottom(12)
        sidebar.append(branding)

        return sidebar

    def _create_header(self):
        """Create the sidebar header with logo"""
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header.add_css_class("sidebar-header")
        header.set_halign(Gtk.Align.CENTER)
        header.set_margin_top(15)
        header.set_margin_bottom(15)

        # Snowflake icon
        snow_icon = Gtk.Label(label="❄")
        snow_icon.add_css_class("snow-logo")
        header.append(snow_icon)

        # "Snow" text
        snow_label = Gtk.Label(label="Snow")
        snow_label.add_css_class("snow-title")
        header.append(snow_label)

        # "Engine" text
        engine_label = Gtk.Label(label="Engine")
        engine_label.add_css_class("snow-subtitle")
        header.append(engine_label)

        return header

    def _create_menu_item(self, icon_name, label_text, active=False):
        """Create a menu item button"""
        button = Gtk.Button()
        button.add_css_class("menu-item")
        if active:
            button.add_css_class("active")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.add_css_class("menu-icon")
        box.append(icon)

        label = Gtk.Label(label=label_text)
        box.append(label)

        button.set_child(box)
        return button

    def switch_page(self, page):
        """Update active page styling"""
        self.local_btn.remove_css_class("active")
        self.settings_btn.remove_css_class("active")

        if page == "local":
            self.local_btn.add_css_class("active")
        elif page == "settings":
            self.settings_btn.add_css_class("active")
