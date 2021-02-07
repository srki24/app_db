from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from Backend import *
from MainScreen import *
from Correspondence import *
from Users import *
from Requests import *
from Status import *

# Kvy builder uses above imported classes
Builder.load_file('design.kv')
Window.size = (1200, 800)


class RootWidget(ScreenManager):
    pass


class MainApp(App):
    def build(self):
        return RootWidget()  # object not class


if __name__ == '__main__':
    MainApp().run()

db.close()
