from kivy.support import install_twisted_reactor

install_twisted_reactor()

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, Clock, Logger, ListProperty
from kivymd.navigationdrawer import NavigationDrawer
from kivymd.theming import ThemeManager
from twisted.internet import reactor

from app.service.irc_client import IRCClientFactory


class NavDrawer(NavigationDrawer):
    def __init__(self, **kw):
        super(NavDrawer, self).__init__(**kw)
        Clock.schedule_once(self.__post_init__)

    def __post_init__(self, *args):
        pass


class KivyIRCClient(App):
    main_widget = ObjectProperty(None)
    channel = ListProperty()
    scr_mngr = ObjectProperty(None)
    config = ObjectProperty(None)
    irc_client = ObjectProperty(None)
    theme_cls = ThemeManager()
    nav_drawer = ObjectProperty(None)
    previous_date = ObjectProperty(None)
    connection = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(KivyIRCClient, self).__init__(**kwargs)

    def build(self):
        self.main_widget = Builder.load_file('kivy_irc.kv')
        self.scr_mngr = self.main_widget.ids.scr_mngr
        self.nav_drawer = NavDrawer()
        self.config = self.config
        self.channel = eval(self.config.get('irc', 'channel'))
        self.connect_irc()
        return self.main_widget

    def build_config(self, config):
        config.setdefaults('irc', {
            'nickname': 'guest',
            'channel': ['#kivy', '#kivy-1997']
        })

    def connect_irc(self):
        reactor.connectTCP("irc.freenode.net", 6667,
                           IRCClientFactory(self, self.config.get('irc', 'channel'),
                                            self.config.get('irc', 'nickname')))

    def on_irc_connection(self, connection):
        Logger.info("IRC: connected successfully!")
        self.connection = connection
        for screen in self.scr_mngr.screens:
            screen.__post_connection__(self.connection)

    def on_joined(self, connection):
        for screen in self.scr_mngr.screens:
            screen.__post_joined__(self.connection)

    def on_stop(self):
        self._shutdown()
        pass

    def _shutdown(self):
        self.protocol.quit('Goodbye IRC...')


if __name__ == '__main__':
    KivyIRCClient().run()
