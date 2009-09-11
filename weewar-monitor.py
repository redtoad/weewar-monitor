
import gtk
import gobject
import os.path

from alert import Alerter

config = os.path.expanduser('~/.weewar-alerter')
alerter = Alerter(config)

def check():
	alerter.watch()
	return True

check()
gobject.timeout_add(alerter.interval * 1000, check)
gtk.main()
