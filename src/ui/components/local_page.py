import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
import os

from src.ui.components.wallpaper_card import WallpaperCard


class LocalPageComponent:
    """Local videos page component"""

    def __init__(self):
        self.wallpaper_grid = None
        self.video_count_label = None
        self.wallpapers = []
        self.selected_wallpaper = None

    def create_local_page(
        self,
        config_manager,
        on_wallpaper_selected,
        on_refresh_clicked,
        on_open_folder_clicked,
        on_delete_video,
    ):
        """Create and return the local page widget

        Args:
            config_manager: ConfigManager instance
            on_wallpaper_selected: Callback for wallpaper selection
            on_refresh_clicked: Callback for refresh button
            on_open_folder_clicked: Callback for add folder button
            on_delete_video: Callback for delete video

        Returns:
            Gtk.Box containing the local page
        """
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.add_css_class("content-area")

        # Header with title, count, and buttons
        header = self._create_header(on_refresh_clicked, on_open_folder_clicked)
        content.append(header)

        # Scrollable grid of wallpapers
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)

        self.wallpaper_grid = Gtk.FlowBox()
        self.wallpaper_grid.set_valign(Gtk.Align.START)
        self.wallpaper_grid.set_halign(Gtk.Align.FILL)
        self.wallpaper_grid.set_max_children_per_line(10)
        self.wallpaper_grid.set_min_children_per_line(1)
        self.wallpaper_grid.set_column_spacing(12)
        self.wallpaper_grid.set_row_spacing(12)
        self.wallpaper_grid.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.wallpaper_grid.add_css_class("wallpaper-grid")
        self.wallpaper_grid.set_homogeneous(False)
        self.wallpaper_grid.connect("child-activated", on_wallpaper_selected)

        scrolled.set_child(self.wallpaper_grid)
        content.append(scrolled)

        return content

    def _create_header(self, on_refresh_clicked, on_open_folder_clicked):
        """Create the page header with title and controls"""
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.add_css_class("feeds-header")
        header.set_margin_bottom(12)

        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title = Gtk.Label(label="Local Videos")
        title.add_css_class("feeds-title")
        title.set_halign(Gtk.Align.START)
        title_box.append(title)

        self.video_count_label = Gtk.Label(label="")
        self.video_count_label.add_css_class("video-count")
        title_box.append(self.video_count_label)
        header.append(title_box)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header.append(spacer)

        refresh_btn = Gtk.Button(label="↻ Refresh")
        refresh_btn.add_css_class("refresh-button")
        refresh_btn.connect("clicked", on_refresh_clicked)
        header.append(refresh_btn)

        folder_btn = Gtk.Button(label="📁 Add Folder")
        folder_btn.add_css_class("folder-button")
        folder_btn.set_margin_start(6)
        folder_btn.connect("clicked", on_open_folder_clicked)
        header.append(folder_btn)

        return header

    def load_wallpapers(self, config_manager, on_delete_video):
        """Load wallpapers from configured folders

        Args:
            config_manager: ConfigManager instance
            on_delete_video: Callback for delete button
        """
        # Clear existing children
        while True:
            child = self.wallpaper_grid.get_first_child()
            if child is None:
                break
            self.wallpaper_grid.remove(child)

        folders = config_manager.get("video_folders", [])
        hidden_videos = config_manager.get("hidden_videos", [])
        self.wallpapers = []

        video_extensions = (".mp4", ".webm", ".mkv", ".avi", ".mov", ".gif")

        for directory in folders:
            if os.path.exists(directory):
                try:
                    for f in os.listdir(directory):
                        if f.lower().endswith(video_extensions):
                            full_path = os.path.join(directory, f)
                            # Skip hidden videos
                            if full_path in hidden_videos:
                                continue
                            self.wallpapers.append(
                                {
                                    "name": os.path.splitext(f)[0],
                                    "path": full_path,
                                    "type": "local",
                                }
                            )
                except Exception:
                    pass

        # Update video count label
        count = len(self.wallpapers)
        self.video_count_label.set_label(f"({count})")

        # Add cards (limit to 24 for performance)
        for wp in self.wallpapers[:24]:
            card = WallpaperCard.create(wp, on_delete_video)
            self.wallpaper_grid.append(card)
