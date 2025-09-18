#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GObject
import sys
import os
import fcntl
import signal

class SingleInstance:
    def __init__(self, lockfile):
        self.lockfile = lockfile
        self.fd = None

        lockdir = os.path.dirname(lockfile)
        if not os.path.exists(lockdir):
            os.makedirs(lockdir)
        
    def is_running(self):
        # Try to create and lock a lock file
        self.fd = open(self.lockfile, 'w')
        try:
            fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return False
        except IOError:
            return True
            
    def cleanup(self):
        if self.fd:
            try:
                fcntl.lockf(self.fd, fcntl.LOCK_UN)
                self.fd.close()
            except:
                pass
            try:
                os.unlink(self.lockfile)
            except:
                pass

class ShortcutsOverlay(Gtk.Window):
    def __init__(self):
        super().__init__(title="Keyboard Shortcuts")
        
        # Window properties for overlay effect
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.stick()
        
        # Set transparent background
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)
        self.set_opacity(0.7)
        
        # Connect events
        self.connect("draw", self.on_draw)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", self.on_destroy)
        self.connect("notify::is-active", self.on_focus_change)
        
        # Create UI
        self.setup_ui()
        
        # Set position (centered)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Set default size
        self.set_default_size(800, 950)

        # Watch for key press events
        self.set_events(Gdk.EventMask.KEY_PRESS_MASK)
        
    def on_draw(self, widget, cr):
        # Draw transparent background
        cr.set_source_rgba(0, 0, 0, 0)  # Dark semi-transparent
        cr.set_operator(Gdk.OPERATOR_SOURCE)
        cr.paint()
        return False

    def setup_ui(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        main_box.set_border_width(20)
        
        # Title
        title = Gtk.Label()
        title.set_markup("<span size='x-large' weight='bold'>Keyboard Shortcuts</span>")
        title.set_justify(Gtk.Justification.CENTER)
        main_box.pack_start(title, False, False, 0)
        
        # Shortcuts container
        shortcuts_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Create notebook for tabs
        notebook = Gtk.Notebook()
        notebook.set_show_tabs(True)
        notebook.set_show_border(False)
        notebook.popup_enable()
        
        # Common Linux Mint shortcuts
        shortcuts = [
            ("Super", "Open menu/search"),
            ("Super + A", "Show applications"),
            ("Ctrl + Alt + L", "Lock screen"),
            ("Super + D", "Show desktop"),
            ("Alt + Tab", "Switch applications"),
            ("Alt + `", "Switch windows of same application"),
            ("Ctrl + Alt + T", "Open terminal"),
            ("Ctrl + Alt + Arrow Keys", "Switch workspaces"),
            ("Ctrl + Alt + Shift + Arrow Keys", "Move window to another workspace"),
            ("Print Screen", "Take screenshot"),
            ("Alt + Print Screen", "Take screenshot of current window"),
            ("Ctrl + Print Screen", "Take screenshot to clipboard"),
            ("Super + Arrow Keys", "Snap windows"),
            ("Super + H", "Hide/unhide window"),
            ("Alt + F2", "Run command dialog"),
            ("Ctrl + Q", "Close application (if supported)"),
            ("Ctrl + W", "Close tab/window"),
            ("Ctrl + T", "New tab"),
            ("ESC", "Close this overlay")
        ]

        categories = {
            "System": [
                ("Super", "Open menu/search"),
                ("Super + Enter", "Launch this application"),
                ("Ctrl + Alt + L", "Lock screen"),
                ("Ctrl + Alt + Del", "Log out"),
                ("Ctrl + Alt + T", "Open terminal"),
                ("Super + D", "Show desktop"),
                ("Alt + F2", "Run command dialog"),
                ("Print Screen", "Take screenshot")
            ],
            "Navigation": [
                ("Alt + Tab", "Switch applications"),
                ("Alt + `", "Switch windows of same application"),
                ("Alt + F4", "Close window"),
                ("Alt + F7", "Move window (with arrow keys)"),
                ("Alt + F8", "Resize window (with arrow keys)"),
                ("Alt + F10", "Toggle maximize"),
                ("Super + Arrow Keys", "Snap windows"),
                ("Super + H", "Hide/unhide window")
            ],
            "Workspaces": [
                ("Ctrl + Alt + ←/→", "Switch workspaces horizontally"),
                ("Ctrl + Alt + Shift + ↑/↓", "Move window between workspaces vertically"),
                ("Ctrl + Alt + Shift + ←/→", "Move window between workspaces horizontally"),
                ("Ctrl + Alt + ↑", "Show workspaces overview"),
                ("Ctrl + Alt + ↓", "Exploded view of current workspace"),
                ("Ctrl + Alt + D", "Show desktop (minimize all)")
            ],
            "Applications": [
                ("Ctrl + Q", "Quit application"),
                ("Ctrl + W", "Close tab/window"),
                ("Ctrl + T", "New tab"),
                ("Ctrl + N", "New window"),
                ("Ctrl + S", "Save"),
                ("Ctrl + O", "Open"),
                ("Ctrl + Z", "Undo"),
                ("Ctrl + Shift + Z", "Redo")
            ],
            "Browser": [
                ("Alt + ", "Back"),
                ("Ctrl + [", ""),
                ("Alt + ", "Forward"),
                ("Ctrl + ]", ""),
                ("Alt + Home", "Home"),
                ("Ctrl + R", "Reload page"),
                ("Ctrl + N", "New window"),
                ("Ctrl + Shift + N", "Open last closed window"),
                ("Ctrl + T", "New tab"),
                ("Ctrl + Shift + T", "Open last closed tab"),
                ("Ctrl + Z", "Undo"),
                ("Ctrl + Shift + Z", "Redo"),
                ("Ctrl + Shift + I", "Web developer tools"),
                ("Ctrl + Shift + C", "Inspect HTML element"),
                ("Ctrl + Shift + J", "Browser console"),
            ],
            "Terminal": [
                ("Ctrl + Shift + T", "New tab"),
                ("Ctrl + Shift + N", "New window"),
                ("Ctrl + Shift + W", "Close tab"),
                ("Ctrl + Shift + Q", "Close window"),
                ("Ctrl + Shift + C", "Copy text"),
                ("Ctrl + Shift + V", "Paste text"),
                ("Ctrl + Shift + F", "Find"),
                ("Ctrl + Shift + G", "Find Next"),
                ("Ctrl + Shift + H", "Find Previous"),
                ("Ctrl + Shift + J", "Clear highlight"),
                ("Ctrl + PageUp", "Switch to previous tab"),
                ("Ctrl + PageDown", "Switch to next tab"),
            ],
        }
        
        # Create a page for each category
        for category_name, shortcuts in categories.items():
            # Create scrolled window for each category
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_min_content_height(450)

            # Create container for shortcuts
            shortcuts_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            shortcuts_box.set_border_width(10)

            # Add shortcuts to the container
            for keys, description in shortcuts:
                shortcut_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                shortcut_row.set_homogeneous(True)

                keys_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

                key_parts = keys.split(" + ")
                for i, key_part in enumerate(key_parts):
                    key_label = Gtk.Label(label=key_part)
                    key_label.get_style_context().add_class("key-box")

                    keys_box.pack_start(key_label, False, False, 0)

                    # Add plus sign between keys
                    if i < len(key_parts) - 1:
                        plus_label = Gtk.Label(label="+")
                        plus_label.get_style_context().add_class("plus-sign")
                        keys_box.pack_start(plus_label, False, False, 0)
                
                #keys_label = Gtk.Label()
                #keys_label.set_markup(f"<span weight='bold'>{keys}</span>")
                #keys_label.set_xalign(0)
                keys_box.set_size_request(200, -1)
                #keys_box.set_justify(Gtk.Justification.CENTER)
                
                desc_label = Gtk.Label(label=description)
                desc_label.set_xalign(0)
                desc_label.set_line:wrap(True)
                
                shortcut_row.pack_start(keys_box, True, True, 0)
                shortcut_row.pack_start(desc_label, True, True, 0)
                
                shortcuts_box.pack_start(shortcut_row, False, False, 0)
        
            # Add scrollable container
            #scrolled = Gtk.ScrolledWindow()
            #scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scrolled.add(shortcuts_box)
            #scrolled.set_min_content_height(400)

            tab_label = Gtk.Label(label=category_name)

            notebook.append_page(scrolled, tab_label)
        
        main_box.pack_start(notebook, True, True, 0)
        
        # Footer note
        footer_box = Gtk.Box()
        footer_box.get_style_context().add_class("footer")
        footer = Gtk.Label()
        footer.set_markup("<span style='italic' size='large'>Press 'ESC' or 'q' to close</span>")
        footer.set_justify(Gtk.Justification.CENTER)
        footer_box.pack_start(footer, True, False, 0)
        main_box.pack_start(footer_box, False, False, 0)
        
        self.add(main_box)
        
        # Style the widgets
        self.apply_styles()
        
    def apply_styles(self):
        style_provider = Gtk.CssProvider()
        css = """
        window {
            border-radius: 12px;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.2);
        }
        
        label {
            color: #ffffff;
            padding: 3px;
        }
        
        scrolledwindow {
            border: 1px solid rgba(0, 0, 0, 0.2);
            border-radius: 6px;
            background-color: rgba(0, 0, 0, 0.8);
        }

        .footer {
            background-color: rgba(0, 0, 0, 0.8);
            border: none;
            border-radius: 0 0 12px 12px;
            padding: 6px 12px;
            margin: 0;
            color: #ffffff;
        }

        .key-box {
            background-color: rgba(125, 125, 125, 0.15);
            border: 1px solid rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            padding: 4px 8px;
            font-weight: bold;
            color: #ffffff;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
        }

        .plus-sign {
            color: rgba(255, 255, 255, 0.7);
            font-weight: bold;
            padding: 0px 4px;
        }

        notebook {
            background-color: transparent;
            border: none;
        }

        notebook header {
            background-color: transparent;
            border: none;
        }

        notebook tab {
            background-color: rgba(0, 0, 0, 0.8);
            border: 2px solid rgba(0, 0, 0, 0.8);
            border-radius: 12px 12px 0 0;
            padding: 6px 12px;
            margin: 0 2px;
            color: #ffffff;
        }

        notebook tab:checked {
            background-color: rgba(50, 150, 100, 0.5);
            border: 2px solid rgba(0, 0, 0, 0.8);
        }

        notebook tab:hover {
            border: 2px solid rgba(255, 255, 255, 0.8)
        }

        scrolledwindow {
            background-color: rgba(0, 0, 0, 0.8);
            border-radius: 6px 6px 0 0;
        }
        """
        style_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def on_key_press(self, widget, event):
        # Close on 'ESC' or 'q' key
        keyname = Gdk.keyval_name(event.keyval)
        if keyname and (keyname.lower() in ['q', 'escape']):
            Gtk.main_quit()
            return True
        return False

    def on_focus_change(self, window, pspec):
        if not window.get_is_active():
            Gtk.main_quit()

    def on_destroy(self, widget):
        # Clean up lock file
        if hasattr(self, 'lock'):
            self.lock.cleanup()

def main():
    # Create lock file in tmp dir
    lockfile = os.path.join(os.path.expanduser('~/.cache/mint-hud'), 'mint-hud.lock')
    print(lockfile)

    # Check if another instance is running
    lock = SingleInstance(lockfile)
    if lock.is_running():
        print('Another instance is currently running')
        sys.exit(1)

    # Create and show the overlay
    win = ShortcutsOverlay()
    win.show_all()

    # Store the lock in the window object
    win.lock = lock
    
    # Handle focus and input
    win.set_modal(True)
    win.set_type_hint(Gdk.WindowTypeHint.DIALOG)
    
    # Ensure window is focused
    win.present()

    # Set up signal handler for clean exit
    def signal_handler(sig, frame):
        lock.cleanup()
        Gtk.main_quit()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Start the application
    Gtk.main()

if __name__ == "__main__":
    main()
