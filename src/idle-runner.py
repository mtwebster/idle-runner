#!/usr/bin/python3

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

    def on_presence_proxy_signal(self, proxy, sender, signal, params, data=None):
        if signal == "StatusChanged":
            if params[0] == IDLE:
                self.run_script("command-line")
            else:
                self.run_script("unidle-command-line")

    def run_script(self, key):
        cmd = self.settings.get_string(key)

        try:
            success = GLib.spawn_command_line_async(cmd)
        except GLib.Error as e:
            print(e.message)

if __name__ == "__main__":
    setproctitle.setproctitle('idle-runner')

    main = Main()

    ml = GLib.MainLoop.new(None, True)
    ml.run()