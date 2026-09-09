#!/usr/bin/python3

import os
import signal
import setproctitle

from gi.repository import GLib, Gio

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

# https://github.com/linuxmint/cinnamon-session/blob/master/cinnamon-session/org.gnome.SessionManager.Presence.xml#L13
IDLE = 3 

class Main:
    def __init__(self):
        self.settings = Gio.Settings(schema_id="org.webster.idlerunner")

        self.logind_proxy = None
        self.inhibitor_fd = -1
        self.running_sleep_script = False

        try:
            self.presence_proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                                 Gio.DBusProxyFlags.DO_NOT_AUTO_START,
                                                                 None,
                                                                 "org.gnome.SessionManager",
                                                                 "/org/gnome/SessionManager/Presence",
                                                                 "org.gnome.SessionManager.Presence",
                                                                 None)

            self.presence_proxy.connect("g-signal",
                                        self.on_presence_proxy_signal)
        except GLib.Error as e:
            print("idle-runner: Could not connect to session manager presence- %s" % e.message)
            exit(1)

        try:
            self.logind_proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SYSTEM,
                                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START,
                                                               None,
                                                               "org.freedesktop.login1",
                                                               "/org/freedesktop/login1",
                                                               "org.freedesktop.login1.Manager",
                                                               None)

            self.logind_proxy.connect("g-signal",
                                      self.on_logind_proxy_signal)
        except GLib.Error as e:
            print("idle-runner: Could not connect to logind, sleep and wake commands will not run- %s" % e.message)
            return

        self.settings.connect("changed::sleep-command-line", self.update_inhibitor)
        self.update_inhibitor()

    def on_presence_proxy_signal(self, proxy, sender, signal, params, data=None):
        if signal == "StatusChanged":
            if params[0] == IDLE:
                self.run_script("command-line")
            else:
                self.run_script("unidle-command-line")

    def on_logind_proxy_signal(self, proxy, sender, signal, params, data=None):
        if signal == "PrepareForSleep":
            if params[0]:
                self.run_sleep_script()
            else:
                self.running_sleep_script = False
                self.run_script("wake-command-line")

                # If the sleep command overran logind's delay we may still be
                # holding the old lock - drop it and take a fresh one.
                self.release_inhibitor()
                self.update_inhibitor()

    def run_script(self, key):
        cmd = self.settings.get_string(key)

        try:
            success = GLib.spawn_command_line_async(cmd)
        except GLib.Error as e:
            print(e.message)

    # Unlike the other hooks we need to wait for this one to finish before
    # letting the machine suspend.  We hold a delay inhibitor while it runs -
    # logind gives us InhibitDelayMaxSec (5 seconds by default) before it stops
    # waiting for us.
    def run_sleep_script(self):
        cmd = self.settings.get_string("sleep-command-line")

        if cmd.strip() == "":
            return

        try:
            success, argv = GLib.shell_parse_argv(cmd)
            pid = GLib.spawn_async(argv,
                                   flags=GLib.SpawnFlags.SEARCH_PATH | GLib.SpawnFlags.DO_NOT_REAP_CHILD)[0]
        except GLib.Error as e:
            print(e.message)
            self.release_inhibitor()
            return

        self.running_sleep_script = True
        GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, self.on_sleep_script_finished)

    def on_sleep_script_finished(self, pid, status, data=None):
        GLib.spawn_close_pid(pid)

        # We've already woken back up if this is unset - the inhibitor it was
        # holding is gone, and any current one belongs to the next sleep.
        if self.running_sleep_script:
            self.running_sleep_script = False
            self.release_inhibitor()

    # Only hold the inhibitor when there's actually something to run, otherwise
    # we'd be adding a delay to every suspend for nothing.
    def update_inhibitor(self, settings=None, key=None):
        if self.settings.get_string("sleep-command-line").strip() == "":
            self.release_inhibitor()
            return

        if self.inhibitor_fd > -1:
            return

        try:
            res, fd_list = self.logind_proxy.call_with_unix_fd_list_sync("Inhibit",
                                                                        GLib.Variant("(ssss)",
                                                                                     ("sleep",
                                                                                      "idle-runner",
                                                                                      "Running the sleep command",
                                                                                      "delay")),
                                                                        Gio.DBusCallFlags.NONE,
                                                                        -1,
                                                                        None,
                                                                        None)

            self.inhibitor_fd = fd_list.get(res[0])
        except GLib.Error as e:
            print("idle-runner: Could not inhibit sleep- %s" % e.message)

    def release_inhibitor(self):
        if self.inhibitor_fd > -1:
            os.close(self.inhibitor_fd)
            self.inhibitor_fd = -1

if __name__ == "__main__":
    setproctitle.setproctitle('idle-runner')

    main = Main()

    ml = GLib.MainLoop.new(None, True)
    ml.run()
