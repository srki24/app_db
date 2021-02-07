from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from datetime import datetime
from Backend import *


# Users widget
class UsersMain(RecycleDataViewBehavior, GridLayout):


    def get_user_screen(self):

        # Navigating the UserScreen widget
        # Defining as a function, because I cannot access UsersMain.parents during
        # initialisation, since has none at that moment.
        # Should be optimized

        user_screen = self.parent.parent.parent.parent.parent
        return user_screen


    def cb_active(self, active):

        user_screen = self.get_user_screen()
        user_screen.ids.error_message.text = ''

        if active:
            # Adding id of the user to the selected users list located in the UsersScreen widget
            user_screen.selected_korisnikid.add(int(self.korisnikid_text))

            # Used for error checking - Recycle View lazy loads checkboxes thus errors can occur

            user_screen.ids.error_message.color = (0, 1, 0)
            user_screen.ids.error_message.text = \
                f'Users with IDs: {user_screen.selected_korisnikid} are currently selected '

        else:

            # If checkbox is being deactivated, we are trying to remove selected user from the list
            try:
                user_screen.selected_korisnikid.remove(int(self.korisnikid_text))
                user_screen.ids.error_message.color = (0, 1, 0)
                user_screen.ids.error_message.text = \
                    f'Users with IDs: {user_screen.selected_korisnikid} are currently selected '

            except Exception as err:
                user_screen.ids.error_message.color = (1, 0, 0)
                user_screen.ids.error_message.text = \
                    f'{err}! Please double check before deleting,' \
                    f' currently selected IDs are: {user_screen.selected_korisnikid}'

    def u_update(self, column, value):

        user_screen = self.get_user_screen()
        try:
            db.user_update(int(self.korisnikid_text), column, value)

            user_screen.ids.error_message.color = (0, 1, 0)
            user_screen.ids.error_message.text = \
                f'Updated {self.naziv_korisnika_text} {column} to {value}! '
        except Exception as err:
            db.conn.rollback()
            user_screen.ids.error_message.color = (1, 0, 0)
            user_screen.ids.error_message.text = str(err)


# Users screen Label
class UsersMainLabel(GridLayout):
    pass


# RV
class UsersRV(RecycleView):

    def __init__(self, **kwargs):
        super(UsersRV, self).__init__(**kwargs)
        db_data = db.users_getall()
        self.users_load_data(db_data)

    def users_load_data(self, db_data):
        self.data = []
        for idx, row in enumerate(db_data):

            korisnikid, korisnik_mlb, naziv_korisnika, adresa_korisnika, telefon_korisnika, mail_korisnika = row

            ulica, broj, grad, drzava = adresa_korisnika.strip("""";()""").split(',')

            d = {'index_text': str(idx),
                 'korisnikid_text': str(korisnikid),
                 'mlb_text': korisnik_mlb,
                 'naziv_korisnika_text': naziv_korisnika,
                 'ulica_text': ulica,
                 'broj_text': broj,
                 'grad_text': grad,
                 'drzava_text': drzava,
                 'telefon_text': telefon_korisnika,
                 'mail_text': mail_korisnika,
                 'cb.status': False
                 }
            self.data.append(d)


    def text_input_search(self, name):
        db_data = db.users_search(name.lower())
        self.users_load_data(db_data)


# Main screen
class Users(Screen):

    selected_korisnikid = {0}

    def main_menu(self):
        self.manager.current = "main_screen"

    def requests_scr(self):
        self.manager.current = "requests_screen"

    def error_users(self, text, color='red'):
        if color == 'red':
            self.ids.error_message.color = (1, 0, 0)
        elif color == 'green':
            self.ids.error_message.color = (0, 1, 0)
        self.ids.error_message.text = text

    def u_insert(self, mlb, naziv, ulica, broj, grad, drzava, telefon, mail):
        c = 'red' #default
        korisnikid = db.users_max_id()[0] + 1 # Max existing id +1

        # If number is not added, default it to 0, preventing sql err
        if broj == '':
            broj = 0

        try:
            db.user_insert(korisnikid, mlb, naziv, ulica, int(broj), grad, drzava, telefon, mail)
        except Exception as err:
            msg = str(err)
            db.conn.rollback()
        else:
            msg = f'Successfully added user {naziv}'
            c = 'green'
            # Clearing data
            self.ids.mlb_insert.text = ''
            self.ids.naziv_korisnika_insert.text = ''
            self.ids.ulica_insert.text = ''
            self.ids.broj_insert.text = ''
            self.ids.grad_insert.text = ''
            self.ids.drzava_insert.text = ''
            self.ids.telefon_insert.text = ''
            self.ids.mail_insert.text = ''
        self.error_users(msg, c)

    def delete_user(self):
        c = 'red'  # red by default, much more warning cases
        if self.selected_korisnikid == {0}:
            msg = "You need to select user that you wish to delete"
        elif len(self.selected_korisnikid) > 2:
            msg = "Please select just one user you wish to delete"

        else:
            try:
                name = db.user_get_name(tuple(self.selected_korisnikid))
                db.user_delete(tuple(self.selected_korisnikid))
                msg = f'Successfully deleted user(s) {name}'
                c = 'green'
            except Exception as err:
                msg = err
                db.conn.rollback()
            else:
                # clearing selection and refreshing recycle view
                self.selected_korisnikid.clear()
                self.selected_korisnikid.add(0)
                self.ids.users_rv.refresh_from_data()

        self.error_users(msg, c)

    def add_request(self):
        added_requests_ids = []
        if self.selected_korisnikid == {0}:
            msg = "Please select a user"
            c = 'red'
        else:
            for korisnik_id in self.selected_korisnikid:
                if korisnik_id == 0:
                    pass
                else:
                    try:
                        today = str(datetime.today().strftime('%Y-%m-%d'))
                        db.insert_request(korisnik_id, today)
                        added_requests_ids.append(korisnik_id)
                        msg = f'Resuest for user(s) {list(self.selected_korisnikid)[1:]} sucessfully added'
                        c = 'green'
                    except Exception as err:
                        msg = str(err)
                        c = 'red'
        self.error_users(msg, c)
