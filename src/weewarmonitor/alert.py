
import ConfigParser
import gtk, gtk.glade
import gobject
import os.path
import pynotify
import webbrowser
from weewar import AuthenticationError, ServerError, headquarter

import resources

pynotify.init(u"WeeWar notifications")

CONFIG_SECTION = 'weewar'

def needs_attention(game):
    return game.get('inNeedOfAttention', False)

class Alerter(object):
    
    # The Alerter has different states. At the beginning it is in state INIT
    # until everything has been initialised. After that it will be IDLE until
    # something note-worthy happens when it will be put in state ALERT (and 
    # trying to catch the user's eye). Should an error occur (e.g. no 
    # connection to the server, the Alerter will be put in state ERROR. 
    INIT, IDLE, ALERT, DISCONNECTED, ERROR = range(5)
    
    INFO, ERROR = range(2)
    
    DEFAULT_USERNAME = ''
    DEFAULT_APIKEY = ''
    DEFAULT_INTERVAL = 30.0 #sec
    
    def __init__(self, config_file):
        
        self.state = None
        self.games = {}
        
        print 'loading config %s...' % config_file
        self.config_file = config_file
        self.load_config(self.config_file)
        
        self._init_gui()
        self._reset_settings()
        self.update(self.INIT, 'Connecting...')
        
    def _init_gui(self):
        """
        Loads GTK resources and connects callbacks.
        """
        resource_xml = resources.alerter
        resource_xml.signal_autoconnect(self)
        
        self.settings = resource_xml.get_widget('settings-dialog')
        self._username_entry = resource_xml.get_widget('username_entry')
        self._key_entry = resource_xml.get_widget('key_entry')
        self._interval_entry = resource_xml.get_widget('interval_entry')

        self.popup_menu = resource_xml.get_widget('popup-menu')

        self.icon = gtk.status_icon_new_from_pixbuf(resources.tank)
        self.icon.connect('activate', self.on_systray_icon_activate)
        self.icon.connect('popup-menu', self.on_systray_icon_popup_menu, self.popup_menu)
        self.icon.set_visible(True)

    def update(self, state, tooltip=None):
        """
        Updates the application's state information. This mostly decides how 
        the status icon/tooltip/popup menu look like.
        """
        if tooltip:
            self.icon.set_tooltip(tooltip)
            
        ## build dynamic pop-up
        
        if not hasattr(self, 'popup_menu_items'):
            self.popup_menu_items = {}
        
        # a set of game ids that needs dealing with
        ids = set(self.popup_menu_items.keys() + [game['id'] for game in self.games])
        
        # these are all currently played games
        for game in self.games:
            id = game['id']
            # a new game needs a new menu item
            if not id in self.popup_menu_items:
                item = gtk.ImageMenuItem('%(name)s (#%(id)s)' % game)
                item.connect('activate', lambda w,d=None: webbrowser.open(game['link']))
                self.popup_menu.prepend(item)
                self.popup_menu_items[id] = item
            else:
                item = self.popup_menu_items[id]
            # set icon depending on game's state
            if needs_attention(game):
                img = gtk.image_new_from_pixbuf(resources.message)
                item.set_image(img)
            else:
                item.set_image(None)
            # we have dealt with this game
            ids.remove(id)
            
        # remove old menu items from pop-up menu
        for id in ids:
            self.popup_menu_items[id].destroy()
            del self.popup_menu_items[id]
        
        # one and the same state cannot follow each other
        if state==self.state:
            return
        
        # IDLE (default)
        # The application is doing nothing.
        if state==self.INIT:
            self.icon.set_from_pixbuf(resources.tank)
            self.icon.set_blinking(False)
            
        # IDLE (default)
        # The application is doing nothing.
        elif state==self.IDLE:
            self.icon.set_from_pixbuf(resources.tank)
            self.icon.set_blinking(False)
            
        # ALERT
        # A change to the state of one or more games has been found of which 
        # the user will be notified.
        elif state==self.ALERT:
            self.icon.set_from_pixbuf(resources.tank)
            self.icon.set_blinking(True)
        
        # DISCONNECTED
        # No connection to the server can be established. In regular intervals, 
        # which are not as frequent as in IDLE, the state will be changed back 
        # to IDLE to check for recovered connectivity.    
        elif state==self.DISCONNECTED:
            self.icon.set_from_pixbuf(resources.tank)
            self.icon.set_blinking(False)
            self.icon.set_tooltip('Connecting...')
            
        # ERROR
        # A non-recoverable error has occurred. User intervention is necessary.
        elif state==self.ERROR:
            self.icon.set_from_pixbuf(resources.tank)
            self.icon.set_blinking(False)
            
        self.state = state
        
    def notify(self, title, msg, type=INFO):
        """
        Takes care of the actual notification via pynotify. Neither the status 
        icon not the overall state of the application is changed!
        """
        icon = 'dialog-warning' if type==self.ERROR else resources.tank

        # icon can be 
        # (1) URI specifying icon file name (e.g. file://path/my-icon.png)
        # (2) stock icon name - one that would succeed in a call to 
        #     gtk_icontheme_lookup() (e.g. 'stock-delete') 
        #     Note: these are not necessarily normal GTK stock icons - any 
        #     theme icon will work.
        # (3) a pixbuf 
        if isinstance(icon, gtk.gdk.Pixbuf):
            note = pynotify.Notification(title, msg)
            note.set_icon_from_pixbuf(icon)
        else:
            note = pynotify.Notification(title, msg, icon)

        note.attach_to_status_icon(self.icon)
        note.set_urgency(pynotify.URGENCY_NORMAL)
        note.set_timeout(pynotify.EXPIRES_DEFAULT)
        note.show()

    def fetch_game_data(self):
        """
        Fetches game data from weewar headquarters and triggers notification 
        for new active games.
        """
        try:
            # call ELIZA API to get your current games
            attention, games = headquarter(self.username, self.api_key)

            # these games are already marked as active
            # and need no further alert
            flagged_active = [game['id'] for game in 
                              filter(needs_attention, self.games)]

            # notify user for every NEW active game
            for game in games:
                if needs_attention(game) and game['id'] not in flagged_active:
                    self.notify('%(name)s (#%(id)s)' % game, 
                        '%(since)s' % game)

            self.games = games
            self.update(self.ALERT if len(flagged_active)>0 else self.IDLE, 
                    '%i games are awaiting your orders.' % len(flagged_active))
            return True

        except ServerError, e:
            self.update(self.ERROR, 'Error while connecting!')
            self.notify('Error while connecting!', e.message, self.ERROR)
        except AuthenticationError, e:
            self.update(self.ERROR, 'Error while connecting!')
            self.notify('Error while connecting!', 
                'Cannot authenticate. Please check your username and API key.', 
                self.ERROR)

        # something went wrong!
        return False
    
    def _reset_settings(self):
        """
        Writes config values into dialogue.
        """
        self._username_entry.set_text(self.username)
        self._key_entry.set_text(self.api_key)
        self._interval_entry.set_value(self.interval)

    def load_config(self, path):
        """
        Loads config from file. If the file does not exist, it will be created
        with default values.
        """
        config = ConfigParser.ConfigParser()
        try:
            config.read(path)
            self.username = config.get(CONFIG_SECTION, 'username')
            self.api_key = config.get(CONFIG_SECTION, 'api_key')
            self.interval = config.getfloat(CONFIG_SECTION, 'interval')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            config.add_section(CONFIG_SECTION)
            self.username = self.DEFAULT_USERNAME
            self.api_key = self.DEFAULT_APIKEY
            self.interval = self.DEFAULT_INTERVAL
            self.save_config(path)

    def save_config(self, path):
        """
        Saves config to file.
        """
        print 'saving config %s...' % path
        config = ConfigParser.ConfigParser()
        config.add_section(CONFIG_SECTION)
        config.set(CONFIG_SECTION, 'username', self.username)
        config.set(CONFIG_SECTION, 'api_key', self.api_key)
        config.set(CONFIG_SECTION, 'interval', self.interval)
        with open(path, 'wb') as configfile:
            config.write(configfile)
            return True
        
    def run(self):
        """
        Application's main loop.
        """
        self.fetch_game_data()
        gobject.timeout_add(int(self.interval * 1000), self.fetch_game_data)
        gtk.main()

    def on_systray_icon_activate(self, *args):
        # TODO: Show popup
        return False

    def on_systray_icon_popup_menu(self, widget, button, time, menu):
        menu.show_all()
        menu.popup(None, None, None, button, time)
        return False

    def on_preferences_activate(self, *args):
        self.settings.show_all()
        return False

    def on_settings_cancel_button_clicked(self, *args):
        self._reset_settings()
        self.settings.hide()
        return False

    def on_settings_apply_button_clicked(self, *args):
        self.username = self._username_entry.get_text()
        self.api_key = self._key_entry.get_text()
        self.interval = self._interval_entry.get_value()
        self.save_config(self.config_file)
        self.settings.hide()
        return False

    def on_quit_activate(self, *args):
        gtk.main_quit()

def main():
    config = os.path.expanduser('~/.weewar-alerter')
    alerter = Alerter(config)
    alerter.run()

if __name__ == '__main__':
    main()
    
