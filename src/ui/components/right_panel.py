import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
import os


class RightPanelComponent:
    """Right panel component with preview and controls"""

    def __init__(self):
        self.preview_image_box = None
        self.title_label = None
        self.apply_btn = None
        self.scale_combo = None
        self.volume_slider = None
        self.audio_switch = None
        self.loop_switch = None
        self.url_entry = None
        self.status_label = None

    def create_right_panel(self, config_manager, callbacks):
        """Create and return the right panel widget

        Args:
            config_manager: ConfigManager instance
            callbacks: Dict with callback functions:
                - on_switch_page
                - on_apply_clicked
                - on_youtube_clicked
                - on_stop_clicked
                - on_scale_changed
                - on_volume_changed
                - on_audio_changed
                - on_loop_changed

        Returns:
            Gtk.ScrolledWindow containing the panel
        """
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_size_request(280, -1)

        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        panel.add_css_class("right-panel")
        panel.set_margin_start(12)
        panel.set_vexpand(True)

        # Top bar
        panel.append(self._create_top_bar(callbacks))

        # Preview card
        panel.append(self._create_preview_card(callbacks))

        # Controls box
        panel.append(self._create_controls_box(config_manager, callbacks))

        # YouTube section
        panel.append(self._create_youtube_section(callbacks))

        # Spacer
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        panel.append(spacer)

        # Footer
        panel.append(self._create_footer(callbacks))

        scrolled.set_child(panel)
        return scrolled

    def _create_top_bar(self, callbacks):
        """Create top bar with settings button"""
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        top_bar.set_margin_bottom(10)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top_bar.append(spacer)

        settings_btn = Gtk.Button()
        settings_btn.set_child(Gtk.Image.new_from_icon_name("emblem-system-symbolic"))
        settings_btn.add_css_class("icon-button")
        settings_btn.add_css_class("primary")
        settings_btn.connect(
            "clicked", lambda b: callbacks["on_switch_page"]("settings")
        )
        top_bar.append(settings_btn)

        return top_bar

    def _create_preview_card(self, callbacks):
        """Create preview card"""
        preview_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        preview_card.add_css_class("preview-card")
        preview_card.set_halign(Gtk.Align.CENTER)

        self.preview_image_box = Gtk.Box()
        self.preview_image_box.add_css_class("preview-image")
        self.preview_image_box.set_halign(Gtk.Align.CENTER)

        preview_card.append(self.preview_image_box)

        # Title and Apply in same row
        title_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_row.set_halign(Gtk.Align.CENTER)

        self.title_label = Gtk.Label(label="Select Video")
        self.title_label.add_css_class("preview-title")
        title_row.append(self.title_label)

        self.apply_btn = Gtk.Button(label="Apply")
        self.apply_btn.add_css_class("apply-btn")
        self.apply_btn.connect("clicked", callbacks["on_apply_clicked"])
        title_row.append(self.apply_btn)

        preview_card.append(title_row)
        return preview_card

    def _create_controls_box(self, config_manager, callbacks):
        """Create controls box"""
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        controls_box.set_margin_top(16)

        # Scale Row
        controls_box.append(self._create_scale_row(config_manager, callbacks))

        # Volume Row
        controls_box.append(self._create_volume_row(config_manager, callbacks))

        # Audio Row
        controls_box.append(self._create_audio_row(config_manager, callbacks))

        # Loop Row
        controls_box.append(self._create_loop_row(config_manager, callbacks))

        return controls_box

    def _create_scale_row(self, config_manager, callbacks):
        """Create scale control row"""
        scale_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        scale_icon = Gtk.Image.new_from_icon_name("zoom-fit-best-symbolic")
        scale_row.append(scale_icon)
        scale_label = Gtk.Label(label="Scale")
        scale_label.add_css_class("control-label")
        scale_row.append(scale_label)
        scale_spacer = Gtk.Box()
        scale_spacer.set_hexpand(True)
        scale_row.append(scale_spacer)

        self.scale_combo = Gtk.ComboBoxText()
        self.scale_combo.append("fill", "Fill")
        self.scale_combo.append("fit", "Fit")
        self.scale_combo.append("stretch", "Stretch")
        self.scale_combo.append("center", "Center")
        self.scale_combo.set_active_id(config_manager.get("scale_mode", "fill"))
        self.scale_combo.add_css_class("scale-dropdown")
        self.scale_combo.connect("changed", callbacks.get("on_scale_changed"))
        scale_row.append(self.scale_combo)
        return scale_row

    def _create_volume_row(self, config_manager, callbacks):
        """Create volume control row"""
        volume_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        volume_icon = Gtk.Image.new_from_icon_name("audio-volume-high-symbolic")
        volume_row.append(volume_icon)
        volume_label = Gtk.Label(label="Volume")
        volume_label.add_css_class("control-label")
        volume_row.append(volume_label)
        volume_spacer = Gtk.Box()
        volume_spacer.set_hexpand(True)
        volume_row.append(volume_spacer)

        self.volume_slider = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 100, 5
        )
        self.volume_slider.set_value(config_manager.get("volume", 50))
        self.volume_slider.set_size_request(100, -1)
        self.volume_slider.add_css_class("control-slider")
        self.volume_slider.connect("value-changed", callbacks.get("on_volume_changed"))
        volume_row.append(self.volume_slider)
        return volume_row

    def _create_audio_row(self, config_manager, callbacks):
        """Create audio toggle row"""
        audio_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        audio_icon = Gtk.Image.new_from_icon_name("audio-speakers-symbolic")
        audio_row.append(audio_icon)
        audio_label = Gtk.Label(label="Audio")
        audio_label.add_css_class("control-label")
        audio_row.append(audio_label)
        audio_spacer = Gtk.Box()
        audio_spacer.set_hexpand(True)
        audio_row.append(audio_spacer)

        self.audio_switch = Gtk.Switch()
        self.audio_switch.set_active(config_manager.get("enable_audio", True))
        self.audio_switch.connect("state-set", callbacks.get("on_audio_changed"))
        audio_row.append(self.audio_switch)
        return audio_row

    def _create_loop_row(self, config_manager, callbacks):
        """Create loop toggle row"""
        loop_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        loop_icon = Gtk.Image.new_from_icon_name("media-playlist-repeat-symbolic")
        loop_row.append(loop_icon)
        loop_label = Gtk.Label(label="Loop")
        loop_label.add_css_class("control-label")
        loop_row.append(loop_label)
        loop_spacer = Gtk.Box()
        loop_spacer.set_hexpand(True)
        loop_row.append(loop_spacer)

        self.loop_switch = Gtk.Switch()
        self.loop_switch.set_active(config_manager.get("loop", True))
        self.loop_switch.connect("state-set", callbacks.get("on_loop_changed"))
        loop_row.append(self.loop_switch)
        return loop_row

    def _create_youtube_section(self, callbacks):
        """Create YouTube section"""
        url_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        url_box.set_margin_top(16)

        url_label = Gtk.Label(label="YouTube URL")
        url_label.add_css_class("control-label")
        url_label.set_halign(Gtk.Align.START)
        url_box.append(url_label)

        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("Paste URL...")
        self.url_entry.add_css_class("url-entry")
        url_box.append(self.url_entry)

        yt_btn = Gtk.Button(label="▶ Play YouTube")
        yt_btn.add_css_class("play-button")
        yt_btn.set_margin_top(5)
        yt_btn.connect("clicked", callbacks["on_youtube_clicked"])
        url_box.append(yt_btn)

        return url_box

    def _create_footer(self, callbacks):
        """Create footer with status and controls"""
        footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer_box.add_css_class("panel-footer")

        # Left side - Snow branding
        snow_label = Gtk.Label(label="❄ Snow")
        snow_label.add_css_class("footer-brand")
        footer_box.append(snow_label)

        # Center spacer
        footer_spacer = Gtk.Box()
        footer_spacer.set_hexpand(True)
        footer_box.append(footer_spacer)

        # Right side - status and stop button
        self.status_label = Gtk.Label(label="● Stopped")
        self.status_label.add_css_class("status-stopped")
        footer_box.append(self.status_label)

        stop_btn = Gtk.Button(label="Stop")
        stop_btn.add_css_class("mini-stop-button")
        stop_btn.connect("clicked", callbacks["on_stop_clicked"])
        footer_box.append(stop_btn)

        return footer_box

    def set_preview_image(self, image_path):
        """Set preview image

        Args:
            image_path: Path to image file
        """
        # Clear existing children
        for child in list(self.preview_image_box):
            self.preview_image_box.remove(child)

        if not image_path or not os.path.exists(image_path):
            return

        try:
            # Load image with proper scaling
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
            orig_width = pixbuf.get_width()
            orig_height = pixbuf.get_height()

            # Scale to fit panel width (max ~180px) while keeping aspect ratio
            max_width = 180
            if orig_width > max_width:
                scale = max_width / orig_width
                new_width = max_width
                new_height = int(orig_height * scale)
            else:
                new_width = orig_width
                new_height = orig_height

            # Limit height too
            max_height = 100
            if new_height > max_height:
                scale = max_height / new_height
                new_height = max_height
                new_width = int(new_width * scale)

            scaled_pixbuf = pixbuf.scale_simple(
                new_width, new_height, GdkPixbuf.InterpType.BILINEAR
            )
            texture = Gdk.Texture.new_for_pixbuf(scaled_pixbuf)
            picture = Gtk.Picture.new_for_paintable(texture)
            picture.set_size_request(new_width, new_height)
            picture.add_css_class("preview-picture")
            self.preview_image_box.append(picture)
        except Exception:
            pass

    def update_status(self, running):
        """Update status label

        Args:
            running: True if wallpaper is running
        """
        if running:
            self.status_label.set_label("● Running")
            self.status_label.remove_css_class("status-stopped")
            self.status_label.add_css_class("status-running")
        else:
            self.status_label.set_label("● Stopped")
            self.status_label.remove_css_class("status-running")
            self.status_label.add_css_class("status-stopped")
