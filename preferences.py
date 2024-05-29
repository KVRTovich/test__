import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GObject
import subprocess,os

class Preferences(Adw.ApplicationWindow):

    def __init__(self, app):
        __gtype_name__ = 'Preferences'
        super().__init__(application=app)
        self.builder = Gtk.Builder()
        self.builder.add_from_file("UI/preferences.ui")
        self.win = self.builder.get_object("main_window")
        self.textview = self.builder.get_object("tfx")
        self.apply = self.builder.get_object('apply')
        self.apply.connect("clicked", self.apply_handler)
        self.buffer = self.textview.get_buffer()
        self.buffer.set_text(subprocess.run(["cat /etc/systemd/timesyncd.conf | grep -oP '^NTP=\K.*'"], shell=True, capture_output=True, text=True).stdout.strip())
        if os.geteuid() == 0:
            self.apply.set_sensitive(True)
            self.textview.set_sensitive(True)
        else:
            self.apply.set_sensitive(False)
            self.textview.set_sensitive(False)

    def on_activate(self):
        self.win.show()

    def apply_handler(self, handler):
        start_iter = self.buffer.get_start_iter()
        end_iter = self.buffer.get_end_iter()
        text = self.buffer.get_text(start_iter, end_iter, True)
        subprocess.run(["sed -i 's/^NTP=$/NTP={}/' /etc/systemd/timesyncd.conf".format(text)], shell = True,executable='/bin/bash')


