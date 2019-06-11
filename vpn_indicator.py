#!/usr/bin/python
import time

import gi
import os,subprocess
import signal

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GObject
from threading import Thread


APPINDICATOR_ID = 'testindicator'

CURRPATH = os.path.dirname(os.path.realpath(__file__))

class Indicator():
    def __init__(self):
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, "network-error-symbolic", appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())
        notify.init(APPINDICATOR_ID)
        vpns = self.check_vpn_connections()
        self.indicator.set_label("VPN Interfaces: "+vpns+"", APPINDICATOR_ID)
        # the thread:
        self.update = Thread(target=self.update_vpns)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()

    def build_menu(self):
        menu = gtk.Menu()

        checkvpn = gtk.MenuItem('Check vpn connections')
        checkvpn.connect('activate', self.check_vpn_connections)

        """item_color2 = gtk.MenuItem('Change red')
        item_color2.connect('activate', self.change_red)"""

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)

        menu.append(checkvpn)
        """menu.append(item_color2)"""
        menu.append(item_quit)
        menu.show_all()
        return menu

    def check_vpn_connections(self):
        connected = ""
        num_connected = 0
	
        try:
            vpns = subprocess.check_output("ifconfig | grep tun", shell=True).decode("utf-8")
            connected = vpns.split("\n")
            num_connected = len(connected)-1 #empty blank line

        except subprocess.CalledProcessError as e:
            pass

        if (num_connected==1):
            self.indicator.set_icon("network-transmit-symbolic")
        elif (num_connected>1):
            self.indicator.set_icon("network-transmit-receive-symbolic")
        else:
            self.indicator.set_icon("network-error-symbolic")

        return str(num_connected)

    """def change_red(self, source):
        self.indicator.set_icon("starred-symbolic")"""

    def update_vpns(self):
        while True:
            time.sleep(10)
            mention = "VPN Interfaces: "+self.check_vpn_connections()
            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(
                self.indicator.set_label,
                mention, APPINDICATOR_ID,
                priority=GObject.PRIORITY_DEFAULT
                )

    def quit(self, source):
        gtk.main_quit()


Indicator()
signal.signal(signal.SIGINT, signal.SIG_DFL)
gtk.main()
