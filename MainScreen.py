from kivy.uix.screenmanager import Screen
from Backend import *


class LoginScreen(Screen):

    def auth(self, uname, pw):
        try:
            if db.log_in(uname, pw) == uname:
                self.manager.current = "main_screen"
            else:
                self.ids.under_login.text = "Invalid username/password"
        except IndexError:
            self.ids.under_login.text = "Invalid username/password"
        except Exception as err:
            self.ids.under_login.text = str(err)
            db.conn.rollback()

    def sign_up(self):
        self.manager.current = "sign_up_screen"

    def forgot_password(self): # to be added
        print('Nije još razrađeno')


class SignUpScreen(Screen):

    def back(self):
        self.manager.current = "login_screen"

    def sign_up(self, uname, pw, mail):
        try:
            db.add_user(uname, pw, mail)
        except Exception as err:
            self.ids.sign_up_result.text = str(err)
            db.conn.rollback()
        else:
            self.ids.sign_up_result.color = (0, 1, 0)
            self.ids.sign_up_result.text = "You have successfully created an account." \
                                           " Please go back to the main page to LogIn."


class MainScreen(Screen):
    def logout(self):
        self.manager.current = "login_screen"

    def menu_correspondence(self):
        self.manager.current = 'correspondence_screen'

    def menu_users(self):
        self.manager.current = 'users_screen'

    def menu_requests(self):
        self.manager.current = 'requests_screen'

    def menu_status(self):
        self.manager.current = 'status_screen'
