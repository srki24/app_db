from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from Backend import *


# main widget
class StatusMain(RecycleDataViewBehavior, GridLayout):

    def update_sz(self, col, data):
        status_screen_message = self.parent.parent.parent.parent.parent.ids.error_message.text
        try:
            db.update_status(col, data, self.zahtevid_text, self.aktuelni_status_text)
            status_screen_message = f"Updated {col} = {data}"
            self.parent.parent.refresh()  # StatusRV
        except Exception as err:
            status_screen_message = str(err)
            db.conn.rollback()

    def delete_sz(self):
        db.delete_status(self.zahtevid_text, self.aktuelni_status_text)
        self.parent.parent.refresh()  # StatusRV


# RV
class StatusRV(RecycleView):

    def __init__(self, **kwargs):
        super(StatusRV, self).__init__(**kwargs)
        db_data = db.status_getall()
        self.status_load_data(db_data)


    def status_load_data(self, db_data):
        self.data = []
        for naziv_korisnika, zahtevid, aktuelni_status, datum in db_data:
            d = {'naziv_korisnika_tekst': naziv_korisnika,
                 'zahtevid_text': str(zahtevid),
                 'aktuelni_status_text': aktuelni_status,
                 'datum_text': str(datum)
                 }
            self.data.append(d)

    def text_search(self, text):
        if self.parent.parent.parent.ids.cb_state_id.state == 'normal':  # Max status search checkbox
            db_data = db.status_text_search(text.lower())
        else:
            db_data = db.status_max_text_search(text.lower())
        self.status_load_data(db_data)

    def id_search(self, id):
        if self.parent.parent.parent.ids.cb_state_id.state == 'normal':
            db_data = db.id_search(id)
        else:
            db_data = db.id_max_search(id)
        self.status_load_data(db_data)

    def refresh(self):
        self.data = []
        if self.parent.parent.parent.ids.cb_state_id.state == 'normal':
            db_data = db.status_getall()
        else:
            db_data = db.status_getall_max()
        self.status_load_data(db_data)


# Screen
class Status(Screen):

    def main_menu(self):
        self.manager.current = "main_screen"

    def zahtevi(self):
        self.manager.current = "requests_screen"
