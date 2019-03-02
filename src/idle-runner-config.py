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

        self.run_button = self.builder.get_object("run_button")
        self.run_button.connect("clicked", self.on_run_clicked)

        self.entry = self.builder.get_object("entry")

        cmd = self.settings.get_string("command-line")
        self.entry.set_text(cmd)

        self.entry.connect("changed", self.on_entry_changed)

        self.window.present()

    def on_window_destroy(self, window, event, data=None):
        Gtk.main_quit()

    def on_cancel_clicked(self, button, data=None):
        Gtk.main_quit()

    def on_save_clicked(self, button, data=None):
        cmd = self.entry.get_text()

        self.settings.set_string("command-line", cmd)

        Gtk.main_quit()

    def on_run_clicked(self, button, data=None):
        cmd = self.entry.get_text()

        message = None
        mtype = Gtk.MessageType.INFO

        try:
            success, out, error, estatus = GLib.spawn_command_line_sync(cmd)

            if out.decode() == "" and error.decode() == "":
                message = "No output"
            else:
                message = "<tt>stdout:\n%s\n\nstderr:\n%s</tt>" % (out.decode(), error.decode())
        except GLib.Error as e:
            message = e.message
            mtype = Gtk.MessageType.ERROR

        report =  Gtk.MessageDialog(self.window,
                                    Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    mtype,
                                    Gtk.ButtonsType.OK,
                                    None)

        label = Gtk.Label()
        label.set_markup(message)
        label.show()

        report.get_message_area().pack_start(label, True, True, 0)

        report.run()  
        report.destroy()

    def on_entry_changed(self, entry, data=None):
        cmd = self.entry.get_text()

        self.run_button.set_sensitive(cmd.strip() != "")

if __name__ == "__main__":
    setproctitle.setproctitle("idle-runner-config")
    ConfigWindow()

    Gtk.main()
