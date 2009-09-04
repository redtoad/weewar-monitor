from config import Config
from weewar import WeeMonitor
from alert import Alerter
import gtk, gobject

config = Config()
monitor = WeeMonitor()
alerter = Alerter(monitor, config)

def check():
	alerter.watch()
	return True

check()
gobject.timeout_add(config.interval * 1000, check)
gtk.main()
