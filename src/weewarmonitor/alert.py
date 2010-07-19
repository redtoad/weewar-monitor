
import ConfigParser
import gtk, gtk.glade
import gobject
import os.path
import pynotify

from weewar import AuthenticationError, ServerError, headquarter

import resources

pynotify.init(u"WeeWar notifications")

CONFIG_SECTION = 'weewar'

class Alerter(object):
    
    """
    """

    games = None
    monitor = None
    in_error_state = False

    _notification = None
    _error = None
    _errormessage = None

    _popup_menu = None

    def __init__(self, config_file):
        """
        """
        self.games = {}
        self.config_file = config_file
        print 'laoading config %s...' % self.config_file
        
        resource_xml = resources.alerter
        resource_xml.signal_autoconnect(self)
        self._popup_menu = resource_xml.get_widget('popup-menu')
        self._settings_dialog = resource_xml.get_widget('settings-dialog')
        self._username_entry = resource_xml.get_widget('username_entry')
        self._key_entry = resource_xml.get_widget('key_entry')
        self._interval_entry = resource_xml.get_widget('interval_entry')
        
        # load config
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)
        try:
            self.username = self.config.get(CONFIG_SECTION, 'username')
            self.api_key = self.config.get(CONFIG_SECTION, 'api_key')
            self.interval = self.config.getint(CONFIG_SECTION, 'interval')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.config.add_section(CONFIG_SECTION)
            self.username = ''
            self.api_key = ''
            self.interval = 5
            self.save_config()
        
        self._reset_settings()
        self.show_icon()

    def save_config(self):
        """
        Save config file.
        """
        self.config.set(CONFIG_SECTION, 'username', self.username)
        self.config.set(CONFIG_SECTION, 'api_key', self.api_key)
        self.config.set(CONFIG_SECTION, 'interval', self.interval)
        with open(self.config_file, 'wb') as configfile:
            self.config.write(configfile)


    def _reset_settings(self):
        self._username_entry.set_text(self.username)
        self._key_entry.set_text(self.api_key)
        self._interval_entry.set_value(self.interval)

    def watch(self):
        print "watching..."
        try:
            attention, games = self.user_games()
            print games
            active = [id for id, data in games.items()
                      if data.get('inNeedOfAttention', False)]

            if len(active) == 0:
                summary = u"No game requires your attention"
            elif len(active) == 1:
                summary = u"A game requires your attention"
            else:
                summary = u"%d games require your attention" % len(active)
            message = '\n'.join(
                    [(u"<a href=\"%(link)s\">%(name)s</a> since %(since)s" % games[id])
                        for id in active]
                    )
            message += "\n\n<a href=\"http://weewar.com/headquarters/games\">Go to HQ</a>"
            self._summary = summary
            self._message = message
            #if changed:
            #    self.show_notification()
        except ServerError, ex:
            self.show_error(ex.message)
        except AuthenticationError, ex:
            self.show_error(u"Cannot authenticate. Please check your username "
                             "and API key.")
        return True

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
            return    # do not display again
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

    def user_games(self):
        games = {}
        needs_attention, gamedata = headquarter(self.username, self.api_key)
        for game in gamedata:
            id = game.get('id')
            games[id] = game
        return needs_attention, games

    def show_icon(self):
        self.icon = gtk.status_icon_new_from_pixbuf(resources.tank)
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
        self.username = self._username_entry.get_text()
        self.api_key = self._key_entry.get_text()
        self.interval = self._interval_entry.get_value()
        self.save_config()
        self._settings_dialog.hide()
        return False

    def on_quit_activate(self, *args):
        gtk.main_quit()


if __name__ == '__main__':
    alerter = Alerter(os.path.expanduser('~/.weewar-alerter'))
    alerter.watch()
    gobject.timeout_add(alerter.interval * 1000, alerter.watch)
    gtk.main()
