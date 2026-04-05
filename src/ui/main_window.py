import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, Gio
import os

from src.core.config import ConfigManager
from src.core.mpvpaper import MPVPaperManager
from src.assets.styles.pixel_theme import apply_theme
from src.ui.components.sidebar import SidebarComponent
from src.ui.components.local_page import LocalPageComponent
from src.ui.components.settings_page import SettingsPageComponent
from src.ui.components.right_panel import RightPanelComponent
from src.ui.components.youtube_manager import YouTubeManager
from src.ui.components.thumbnail_manager import ThumbnailManager


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.config_manager = ConfigManager()
        self.mpvpaper = MPVPaperManager(self.config_manager)
        self.current_page = "local"
        self.css_provider = None

        # Components
        self.sidebar_component = SidebarComponent()
        self.local_page_component = LocalPageComponent()
        self.settings_page_component = SettingsPageComponent()
        self.right_panel_component = RightPanelComponent()

        self.set_title("SnowEngine")
        self.set_default_size(900, 600)
        self.set_size_request(600, 400)  # Minimum size

        self.apply_current_theme()
        self.setup_ui()
        self.load_wallpapers()
        self.update_status()
        self.update_preview()

        GLib.timeout_add(2000, self.update_status)

    def apply_current_theme(self):
        """Apply current theme from config"""
        dark_mode = self.config_manager.get("dark_mode", True)
        self.css_provider = apply_theme(dark_mode)

    def setup_ui(self):
        """Setup main UI layout"""
        # Main scrollable container for responsiveness
        main_scroll = Gtk.ScrolledWindow()
        main_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.add_css_class("main-container")
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)

        # Sidebar
        sidebar = self.sidebar_component.create_sidebar(self.switch_page)
        main_box.append(sidebar)

        # Content stack
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.content_stack.set_hexpand(True)
        self.content_stack.set_vexpand(True)

        # Create pages
        local_page = self.local_page_component.create_local_page(
            self.config_manager,
            self.on_wallpaper_selected,
            self.on_refresh_clicked,
            self.on_open_folder_clicked,
            self.on_delete_video,
        )
        self.content_stack.add_named(local_page, "local")

        settings_page = self.settings_page_component.create_settings_page(
            self.config_manager,
            {
                "on_monitor_changed": self.on_monitor_changed,
                "on_zoom_changed": self.on_zoom_changed,
                "on_pan_changed": self.on_pan_changed,
                "on_autopause_changed": self.on_autopause_changed,
                "on_dark_mode_changed": self.on_dark_mode_changed,
                "on_username_changed": self.on_username_changed,
                "on_choose_avatar": self.on_choose_avatar,
            },
        )
        self.content_stack.add_named(settings_page, "settings")

        main_box.append(self.content_stack)

        # Right panel
        right_panel = self.right_panel_component.create_right_panel(
            self.config_manager,
            {
                "on_switch_page": self.switch_page,
                "on_apply_clicked": self.on_apply_clicked,
                "on_youtube_clicked": self.on_youtube_clicked,
                "on_stop_clicked": self.on_stop_clicked,
                "on_scale_changed": self.on_scale_changed,
                "on_volume_changed": self.on_volume_changed,
                "on_audio_changed": self.on_audio_changed,
                "on_loop_changed": self.on_loop_changed,
            },
        )
        main_box.append(right_panel)

        main_scroll.set_child(main_box)
        self.set_content(main_scroll)

    def switch_page(self, page):
        """Switch content page"""
        self.current_page = page
        self.content_stack.set_visible_child_name(page)
        self.sidebar_component.switch_page(page)

    def load_wallpapers(self):
        """Load wallpapers from configured folders"""
        self.local_page_component.load_wallpapers(
            self.config_manager, self.on_delete_video
        )

    def on_wallpaper_selected(self, flowbox, child):
        """Handle wallpaper selection"""
        card = child.get_child()
        if hasattr(card, "wallpaper_data"):
            wp = card.wallpaper_data
            self.local_page_component.selected_wallpaper = wp
            name = wp["name"][:18] + "..." if len(wp["name"]) > 18 else wp["name"]
            self.right_panel_component.title_label.set_label(name)

            thumb_path = ThumbnailManager.get_thumbnail(wp["path"])
            if thumb_path:
                self.right_panel_component.set_preview_image(thumb_path)

    def on_apply_clicked(self, button):
        """Apply selected wallpaper"""
        wp = self.local_page_component.selected_wallpaper
        if not wp:
            return

        volume = int(self.right_panel_component.volume_slider.get_value())
        loop = self.right_panel_component.loop_switch.get_active()
        scale_mode = self.right_panel_component.scale_combo.get_active_id() or "fill"
        enable_audio = self.right_panel_component.audio_switch.get_active()

        self.config_manager.set("volume", volume)
        self.config_manager.set("loop", loop)
        self.config_manager.set("scale_mode", scale_mode)
        self.config_manager.set("enable_audio", enable_audio)

        success, msg = self.mpvpaper.play(
            wp["path"],
            volume=volume,
            loop=loop,
            scale_mode=scale_mode,
            enable_audio=enable_audio,
        )

        if success:
            self.config_manager.save_state(wp["path"], "local")
            self.update_preview()
            self.update_status()

    def on_youtube_clicked(self, button):
        """Play YouTube video"""
        url = self.right_panel_component.url_entry.get_text().strip()
        if not url:
            return

        volume = int(self.right_panel_component.volume_slider.get_value())
        loop = self.right_panel_component.loop_switch.get_active()
        scale_mode = self.right_panel_component.scale_combo.get_active_id() or "fill"
        enable_audio = self.right_panel_component.audio_switch.get_active()

        success, msg = self.mpvpaper.play_youtube(
            url,
            volume=volume,
            loop=loop,
            scale_mode=scale_mode,
            enable_audio=enable_audio,
        )

        if success:
            self.config_manager.save_state(url, "youtube")
            self.right_panel_component.title_label.set_label("YouTube Video")
            self.update_status()
            # Fetch YouTube thumbnail
            YouTubeManager.fetch_thumbnail(
                url, self.right_panel_component.set_preview_image
            )

    def on_stop_clicked(self, button):
        """Stop current wallpaper"""
        self.mpvpaper.stop()
        self.update_status()

    def on_refresh_clicked(self, button):
        """Refresh wallpaper list"""
        self.load_wallpapers()

    def on_open_folder_clicked(self, button):
        """Open folder selection dialog"""
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Video Folder")
        dialog.select_folder(self, None, self.on_folder_selected)

    def on_folder_selected(self, dialog, result):
        """Handle folder selection"""
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                path = folder.get_path()
                folders = self.config_manager.get("video_folders", [])
                if path not in folders:
                    folders.append(path)
                    self.config_manager.set("video_folders", folders)
                self.load_wallpapers()
        except Exception:
            pass

    def on_delete_video(self, wallpaper):
        """Delete video from local list"""
        dialog = Adw.MessageDialog.new(
            self,
            f"Remove '{wallpaper['name']}'?",
            "This will remove the video from the list. The file will NOT be deleted from your system.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("remove", "Remove")
        dialog.set_response_appearance("remove", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")

        dialog.connect("response", self.on_delete_response, wallpaper)
        dialog.present()

    def on_delete_response(self, dialog, response, wallpaper):
        """Handle delete confirmation"""
        if response == "remove":
            try:
                video_path = wallpaper["path"]

                # Add to hidden videos list instead of deleting
                hidden_videos = self.config_manager.get("hidden_videos", [])
                if video_path not in hidden_videos:
                    hidden_videos.append(video_path)
                    self.config_manager.set("hidden_videos", hidden_videos)

                # Reload wallpapers list
                self.load_wallpapers()
            except Exception as e:
                print(f"Error removing video: {e}")

    def update_preview(self):
        """Update preview image and title"""
        state = self.config_manager.load_state()
        if not state or not state.get("current_video"):
            return

        video = state["current_video"]
        if state["type"] == "local":
            thumb_path = ThumbnailManager.get_thumbnail(video)
            if thumb_path and os.path.exists(thumb_path):
                self.right_panel_component.set_preview_image(thumb_path)
            self.right_panel_component.title_label.set_label(
                os.path.basename(video)[:20]
            )
        elif state["type"] == "youtube":
            self.right_panel_component.title_label.set_label("YouTube Video")
            # Try to load cached YouTube thumbnail
            video_id = YouTubeManager.extract_video_id(video)
            if video_id:
                cached_path = ThumbnailManager.get_youtube_thumbnail_path(video_id)
                if cached_path:
                    self.right_panel_component.set_preview_image(cached_path)
                else:
                    YouTubeManager.fetch_thumbnail(
                        video, self.right_panel_component.set_preview_image
                    )

    def update_status(self):
        """Update status label"""
        status = self.mpvpaper.get_status()
        self.right_panel_component.update_status(status.get("running", False))
        return True

    # Settings callbacks
    def on_monitor_changed(self, combo):
        """Handle monitor change"""
        monitor = combo.get_active_id() or "*"
        self.config_manager.set("monitor", monitor)

    def on_zoom_changed(self, spin):
        """Handle zoom change"""
        self.config_manager.set("video_zoom", spin.get_value())

    def on_pan_changed(self, spin):
        """Handle pan change"""
        self.config_manager.set(
            "video_pan_x", self.settings_page_component.pan_x_spin.get_value()
        )
        self.config_manager.set(
            "video_pan_y", self.settings_page_component.pan_y_spin.get_value()
        )

    def on_autopause_changed(self, switch, state):
        """Handle autopause change"""
        self.config_manager.set("auto_pause", state)
        return False

    def on_dark_mode_changed(self, switch, state):
        """Handle dark mode change"""
        self.config_manager.set("dark_mode", state)
        self.apply_current_theme()
        return False

    def on_username_changed(self, entry):
        """Handle username change"""
        username = entry.get_text()
        self.config_manager.set("username", username)

    def on_choose_avatar(self, button):
        """Open avatar selection dialog"""
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Avatar Image")

        filter_images = Gtk.FileFilter()
        filter_images.set_name("Images")
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/jpeg")
        filter_images.add_mime_type("image/gif")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_images)
        dialog.set_filters(filters)

        dialog.open(self, None, self.on_avatar_selected)

    def on_avatar_selected(self, dialog, result):
        """Handle avatar selection"""
        try:
            file = dialog.open_finish(result)
            if file:
                path = file.get_path()
                self.config_manager.set("avatar_path", path)
        except Exception:
            pass

    # Right panel callbacks
    def on_scale_changed(self, combo):
        """Handle scale mode change"""
        pass  # No immediate action needed

    def on_volume_changed(self, slider):
        """Handle volume change"""
        pass  # No immediate action needed

    def on_audio_changed(self, switch, state):
        """Handle audio toggle"""
        return False

    def on_loop_changed(self, switch, state):
        """Handle loop toggle"""
        return False


class SnowApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.snow.engine")

    def do_activate(self):
        win = MainWindow(self)
        win.present()


def main():
    app = SnowApp()
    app.run()


if __name__ == "__main__":
    main()
