import gtk, gtk.glade
import pynotify

from weewar import WeeServerError, WeeAuthError

pynotify.init(u"WeeWar notifications")

class Alerter(object):
	games = None
	monitor = None
	in_error_state = False

	_notification = None
	_error = None
	_errormessage = None

	_popup_menu = None

	def __init__(self, monitor, config):
		self.monitor = monitor
		self.config = config
		self.monitor.set_auth_info(config.username, config.api_key)
		self.games = {}
		popup_menu_xml = gtk.glade.XML('popup-menu.glade')
		popup_menu_xml.signal_autoconnect(self)
		self._popup_menu = popup_menu_xml.get_widget('popup-menu')
		settings_dialog_xml = gtk.glade.XML('settings-dialog.glade')
		settings_dialog_xml.signal_autoconnect(self)
		self._settings_dialog = settings_dialog_xml.get_widget('settings-dialog')
		self._username_entry = settings_dialog_xml.get_widget('username_entry')
		self._key_entry = settings_dialog_xml.get_widget('key_entry')
		self._interval_entry = settings_dialog_xml.get_widget('interval_entry')
		self._reset_settings()
		self.show_icon()

	def _reset_settings(self):
		self._username_entry.set_text(self.config.username)
		self._key_entry.set_text(self.config.api_key)
		self._interval_entry.set_value(self.config.interval)

	def _filter_active(self, new):
		active = {}
		changed = False
		for id, ngame in new.items():
			try:
				changed = changed or ngame['needs_attention'] != self.games[id]['needs_attention']
			except KeyError:
				changed = True
			if ngame['needs_attention']:
				active[id] = ngame
		self.games = new
		return active, changed

	def watch(self):
		try:
			games = self.monitor.user_games()
		except WeeServerError, ex:
			self.show_error(ex.message)
			return
		except WeeAuthError, ex:
			self.show_error(u"Cannot authenticate. Please check your username and API key.")
			return
		active, changed = self._filter_active(games)
		if len(active) == 0:
			summary = u"No game requires your attention"
		elif len(active) == 1:
			summary = u"A game requires your attention"
		else:
			summary = u"%d games require your attention" % len(active)
		message = '\n'.join(
				[(u"<a href=\"%(link)s\">%(name)s</a> since %(since)s" % game)
					for game in active.values()]
				)
		message += "\n\n<a href=\"http://weewar.com/headquarters/games\">Go to HQ</a>"
		self._summary = summary
		self._message = message
		if changed:
			self.show_notification()

	def show_notification(self):
		self.in_error_state = False
		self.icon.set_tooltip(u"WeeWar Monitor - %s" % self._summary)
		if self._notification:
			a = self._notification
			a.update(self._summary, self._message)
		else:
			a = pynotify.Notification(self._summary, self._message)
			a.set_urgency(pynotify.URGENCY_NORMAL)
		a.set_timeout(pynotify.EXPIRES_DEFAULT)
		a.show()
		self._notification = a

	def show_error(self, message=None):
		self.in_error_state = True
		title = u"WeeWar: Error"
		if self._errormessage == message:
			return	# do not display again
		else:
			if message:
				self._errormessage = message
		self.icon.set_tooltip(u"WeeWar Monitor - %s" % self._errormessage)
		if self._error:
			e = self._error
			e.update(title, self._errormessage, 'dialog-warning')
		else:
			e = pynotify.Notification(title, self._errormessage, 'dialog-warning')
			e.set_urgency(pynotify.URGENCY_NORMAL)
		e.set_timeout(pynotify.EXPIRES_DEFAULT)
		e.show()
		self._error = e

	def show_icon(self):
		self.icon = gtk.status_icon_new_from_file('tank.gif')
		self.icon.set_tooltip(u"WeeWar Monitor")
		self.icon.connect('activate', self.on_systray_icon_activate)
		self.icon.connect('popup-menu', self.on_systray_icon_popup_menu, self._popup_menu)

	def on_systray_icon_activate(self, *args):
		if self.in_error_state:
			self.show_error()
		else:
			self.show_notification()
		return False

	def on_systray_icon_popup_menu(self, widget, button, time, menu):
		menu.show_all()
		menu.popup(None, None, None, button, time)
		return False

	def on_preferences_activate(self, *args):
		self._settings_dialog.show_all()
		return False

	def on_settings_cancel_button_clicked(self, *args):
		self._reset_settings()
		self._settings_dialog.hide()
		return False

	def on_settings_apply_button_clicked(self, *args):
		self.config.username = self._username_entry.get_text()
		self.config.api_key = self._key_entry.get_text()
		self.config.interval = self._interval_entry.get_value()
		self.config.save()
		self._settings_dialog.hide()
		return False

	def on_quit_activate(self, *args):
		gtk.main_quit()
