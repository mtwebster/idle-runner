#!/usr/bin/python3

import signal
import setproctitle

from gi.repository import GLib, Gio

signal.signal(signal.SIGINT, signal.SIG_DFL)

# https://github.com/linuxmint/cinnamon-session/blob/master/cinnamon-session/org.gnome.SessionManager.Presence.xml#L13
IDLE = 3 

class Main:
    def __init__(self):
        # what

        try:
            self.proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                        Gio.DBusProxyFlags.DO_NOT_AUTO_START,
                                                        None,
                                                        "org.gnome.SessionManager",
                                                        "/org/gnome/SessionManager/Presence",
                                                        "org.gnome.SessionManager.Presence",
                                                        None)

            self.proxy.connect("g-signal",
                               self.on_proxy_signal)
        except GLib.Error as e:
            print("idle-runner: Could not connect to session manager - %s" % e.message)
            exit(1)

    def on_proxy_signal(self, proxy, sender, signal, params, data=None):
        if signal == "StatusChanged":
            if params[0] == 3:
                self.run_script()

    def run_script(self):
        print("Yay")



if __name__ == "__main__":
    setproctitle.setproctitle('idle-runner')

    main = Main()

    ml = GLib.MainLoop.new(None, True)
    ml.run()
