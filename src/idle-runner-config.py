#!/usr/bin/python3

import signal
import setproctitle

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib

signal.signal(signal.SIGINT, signal.SIG_DFL)

HOOKS = (
    ("command-line", "idle_entry", "idle_run_button"),
    ("unidle-command-line", "unidle_entry", "unidle_run_button"),
    ("sleep-command-line", "sleep_entry", "sleep_run_button"),
    ("wake-command-line", "wake_entry", "wake_run_button")
)


class ConfigWindow:
    def __init__(self):
        self.settings = Gio.Settings(schema_id="org.webster.idlerunner")

        self.builder = Gtk.Builder()

        self.builder.add_from_file("/usr/share/idle-runner/idle-runner.glade")

        self.window = self.builder.get_object("window")
        self.window.connect("delete-event", self.on_window_destroy)

        self.save_button = self.builder.get_object("save_button")
        self.save_button.connect("clicked", self.on_save_clicked)

        self.cancel_button = self.builder.get_object("cancel_button")
        self.cancel_button.connect("clicked", self.on_cancel_clicked)

        self.entries = {}

        for key, entry_id, button_id in HOOKS:
            entry = self.builder.get_object(entry_id)
            run_button = self.builder.get_object(button_id)

            entry.set_text(self.settings.get_string(key))
            entry.connect("changed", self.on_entry_changed, run_button)

            run_button.connect("clicked", self.on_run_clicked, entry)

            self.on_entry_changed(entry, run_button)

            self.entries[key] = entry

        self.window.present()

    def on_window_destroy(self, window, event, data=None):
        Gtk.main_quit()

    def on_cancel_clicked(self, button, data=None):
        Gtk.main_quit()

    def on_save_clicked(self, button, data=None):
        for key, entry in self.entries.items():
            self.settings.set_string(key, entry.get_text())

        Gtk.main_quit()

    def on_run_clicked(self, button, entry):
        cmd = entry.get_text()

        message = None
        mtype = Gtk.MessageType.INFO

        try:
            success = GLib.spawn_command_line_async(cmd)
        except GLib.Error as e:
            message = e.message
            mtype = Gtk.MessageType.ERROR

            report =  Gtk.MessageDialog(self.window,
                                        Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                        Gtk.MessageType.ERROR,
                                        Gtk.ButtonsType.OK,
                                        None)

            label = Gtk.Label()
            label.set_markup(message)
            label.show()

            report.get_message_area().pack_start(label, True, True, 0)

            report.run()  
            report.destroy()

    def on_entry_changed(self, entry, button):
        cmd = entry.get_text()

        button.set_sensitive(cmd.strip() != "")

if __name__ == "__main__":
    setproctitle.setproctitle("idle-runner-config")
    ConfigWindow()

    Gtk.main()
