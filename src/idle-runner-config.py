#!/usr/bin/python3

import signal
import setproctitle

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib

signal.signal(signal.SIGINT, signal.SIG_DFL)


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

        # Enter idle controls
        self.idle_entry = self.builder.get_object("idle_entry")
        self.idle_run_button = self.builder.get_object("idle_run_button")

        cmd = self.settings.get_string("command-line")
        self.idle_entry.set_text(cmd)
        self.idle_entry.connect("changed", self.on_entry_changed, self.idle_run_button)

        self.idle_run_button.connect("clicked", self.on_run_clicked, self.idle_entry)

        self.on_entry_changed(self.idle_entry, self.idle_run_button)

        # Leave idle controls
        self.unidle_entry = self.builder.get_object("unidle_entry")
        self.unidle_run_button = self.builder.get_object("unidle_run_button")

        cmd = self.settings.get_string("unidle-command-line")
        self.unidle_entry.set_text(cmd)
        self.unidle_entry.connect("changed", self.on_entry_changed, self.unidle_run_button)

        self.unidle_run_button.connect("clicked", self.on_run_clicked, self.unidle_entry)

        self.on_entry_changed(self.unidle_entry, self.unidle_run_button)

        self.window.present()

    def on_window_destroy(self, window, event, data=None):
        Gtk.main_quit()

    def on_cancel_clicked(self, button, data=None):
        Gtk.main_quit()

    def on_save_clicked(self, button, data=None):
        cmd = self.idle_entry.get_text()
        self.settings.set_string("command-line", cmd)

        cmd = self.unidle_entry.get_text()
        self.settings.set_string("unidle-command-line", cmd)

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
