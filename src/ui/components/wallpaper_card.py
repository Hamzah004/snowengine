import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, GdkPixbuf
import os

from src.ui.components.thumbnail_manager import ThumbnailManager


class WallpaperCard:
    """Creates a wallpaper card widget"""

    @staticmethod
    def create(wallpaper, on_delete_callback):
        """Create a wallpaper card widget

        Args:
            wallpaper: Dict with 'name', 'path', 'type' keys
            on_delete_callback: Callback function for delete button

        Returns:
            Gtk.Box widget representing the card
        """
        # Main card container
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.add_css_class("wallpaper-card")

        # Add thumbnail
        WallpaperCard._add_thumbnail(card, wallpaper)

        # Bottom row with name and delete button
        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        bottom_row.set_margin_top(4)
        bottom_row.set_margin_bottom(4)
        bottom_row.set_margin_start(4)
        bottom_row.set_margin_end(4)

        name = (
            wallpaper["name"][:12] + "..."
            if len(wallpaper["name"]) > 12
            else wallpaper["name"]
        )
        name_label = Gtk.Label(label=name)
        name_label.add_css_class("card-name")
        name_label.set_ellipsize(3)
        name_label.set_hexpand(True)
        name_label.set_halign(Gtk.Align.START)
        bottom_row.append(name_label)

        # Delete button
        delete_btn = Gtk.Button()
        delete_btn.set_child(Gtk.Image.new_from_icon_name("user-trash-symbolic"))
        delete_btn.add_css_class("delete-btn")
        delete_btn.set_tooltip_text("Delete video")
        delete_btn.connect("clicked", lambda b: on_delete_callback(wallpaper))
        bottom_row.append(delete_btn)

        card.append(bottom_row)

        # Store wallpaper data on the widget
        card.wallpaper_data = wallpaper

        return card

    @staticmethod
    def _add_thumbnail(card, wallpaper):
        """Add thumbnail image to card

        Args:
            card: Gtk.Box card widget
            wallpaper: Wallpaper dict with 'path' key
        """
        thumb_path = ThumbnailManager.get_thumbnail(wallpaper["path"])
        if thumb_path and os.path.exists(thumb_path):
            try:
                # Load image naturally and scale proportionally
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(thumb_path)
                orig_w = pixbuf.get_width()
                orig_h = pixbuf.get_height()

                # Scale to max width 150, keep aspect ratio
                max_w = 150
                if orig_w > max_w:
                    scale = max_w / orig_w
                    new_w = max_w
                    new_h = int(orig_h * scale)
                else:
                    new_w = orig_w
                    new_h = orig_h

                scaled = pixbuf.scale_simple(
                    new_w, new_h, GdkPixbuf.InterpType.BILINEAR
                )
                texture = Gdk.Texture.new_for_pixbuf(scaled)
                picture = Gtk.Picture.new_for_paintable(texture)
                picture.set_size_request(new_w, new_h)
                picture.add_css_class("card-thumbnail")
                card.append(picture)
                return
            except Exception:
                pass

        # Fallback icon if thumbnail fails
        icon = Gtk.Image.new_from_icon_name("video-x-generic-symbolic")
        icon.set_pixel_size(48)
        icon.add_css_class("card-icon")
        card.append(icon)
