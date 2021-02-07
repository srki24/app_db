from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from datetime import datetime
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from Backend import *


class TrazenaDokRV(RecycleView):

    def __init__(self, **kwargs):
        super(TrazenaDokRV, self).__init__(**kwargs)

    # Loads only those letters which are not selected
    def trazenadokrv_load_data(self, zahtevid):
        self.data = []
        db_data = db.unselected_letters(zahtevid)
        for i in db_data:
            d = {'pismoid_text': str(i[0]),
                 'autor_text': str(i[1]),
                 'institucija_text': str(i[2]),
                 'datum_text': str(i[3]),
                 'brstr_text': str(i[4])
                 }
            self.data.append(d)


# Scroll view
class TrazenaDokScroll(ScrollView):

    # Create widgets only for selected letters
    # Not the greatest solution, but had to be done this way.
    # Coordination among Recycle view and Scroll view widgets might not be optimal solution

    def trazenadok_create_layout(self, pismoid, autor, institucija, datum, broj_strana):

        layout = GridLayout(cols=6)
        layout.add_widget(Label(text=str(pismoid), size_hint_x=0.2))
        layout.add_widget(Label(text=str(autor), size_hint_x=0.6))
        layout.add_widget(Label(text=str(institucija), size_hint_x=0.8))
        layout.add_widget(Label(text=str(datum), size_hint_x=0.4))
        layout.add_widget(Label(text=str(broj_strana), size_hint_x=0.25))
        layout.add_widget(Label(text='', size_hint_x=0.25))  # empty label used for spacing
        self.ids.content.add_widget(layout)

    def trazenadokscroll_load_data(self, zahtevid):  # populate from scratch
        self.ids.content.clear_widgets()
        db_data = db.populate_trazenadok(zahtevid)
        for pismoid, autor, institucija, datum, broj_strana in db_data:
            self.trazenadok_create_layout(pismoid, autor, institucija, datum, broj_strana)

    def remove_all(self):
        self.ids.content.clear_widgets()

    def update_trazenadok(self, zahtevid):
        # should be revisited

        db.clear_trazenadok(zahtevid)  # Delete all of records for the request

        trazena_dok = []  # list of IDs of requested letters

        # widgets in the scroll view

        scrollview_gridlayout = self.children[0].children[0].children
        for widget in scrollview_gridlayout:
            pismoid = widget.children[-1].text
            trazena_dok.append(pismoid)

        # insert into requested documents all of the requested letters
        for pismoid in set(trazena_dok):
            try:
                db.insert_trazenadok(zahtevid, pismoid)

            except Exception as err:
                print(err)
                db.conn.rollback()


# Rv
class TrazenaDok(RecycleDataViewBehavior, GridLayout):

    def dodaj_pismo(self):
        # add widget to the scroll view and remove it from the recycle view
        scrollview = self.parent.parent.parent.parent.parent.parent.parent.ids.scrollview_id
        scrollview.trazenadok_create_layout(self.pismoid_text, self.autor_text,
                                            self.institucija_text, self.datum_text, self.brstr_text)

        self.parent.remove_widget(self)


# Empty class used just for layout
class TrazenaDokLayout(GridLayout):
    pass


# Popup window
class TrazenaDokPopup(Popup):
    zahtevid = StringProperty()

    def __init__(self, zahtevid, **kwargs):
        super(TrazenaDokPopup, self).__init__(**kwargs)

        self.zahtevid = zahtevid


# Popup window
class DetaljiPopup(Popup):
    zahtevid = StringProperty()

    today = str(datetime.today().strftime('%Y-%m-%d'))

    def __init__(self, zahtevid, **kwargs):

        # This part needs reworking ...
        # Maybe get all states of a request and iterate over them and adjust accordingly?
        super(DetaljiPopup, self).__init__(**kwargs)

        self.zahtevid = zahtevid
        self.korisnikid = str(db.details_get_userid(zahtevid)[0])

        msg = self.update_status()
        self.update_message(msg)

        # checking if employee has accepted or rejected request, or neither

        zaposleni_prihvatio = db.details_check_status(self.zahtevid, 'Zaposleni prihvatio')
        zaposleni_odbio = db.details_check_status(self.zahtevid, 'Zaposleni odbio')

        # and adjusting toggle button accordingly

        if zaposleni_prihvatio:
            self.ids.prihvati_zahtev_id.state = 'down'
        elif zaposleni_odbio:
            self.ids.odbij_zahtev_id.state = 'down'
        else:
            pass

        # State of the user and ministry answer

        self.drzava_text = str(db.details_get_state(self.korisnikid)[0])
        self.potvrda_neophodna()

        ministarstvo_prihvatilo = db.details_check_status(self.zahtevid, 'Ministarstvo prihvatilo')
        ministarstvo_odbilo = db.details_check_status(self.zahtevid, 'Ministarstvo odbilo')

        if ministarstvo_prihvatilo:
            self.ids.mk_potvrdaid.state = 'down'
        elif ministarstvo_odbilo:
            self.ids.mk_odbijenoid.state = 'down'
        else:
            pass

        # Contract toggle button
        if db.details_check_status(self.zahtevid, 'Poslat ugovor'):
            self.generisi_ugovor()
            self.ids.ugovorid.state = 'down'
        else:
            self.ids.ugovorid.state = 'normal'
            self.ids.cena_po_straniid.text = '0'
            self.ids.ukupno_stranaid.text = '0'
            self.ids.ukupna_cenaid.text = '0'

        # Payment
        if db.details_check_status(self.zahtevid, 'Uplata proknjizena'):
            self.ids.uplataid.state = 'down'
        else:
            pass

        # Bill processed
        if db.details_check_status(self.zahtevid, 'Izdat racun'):
            self.ids.racunid.state = 'down'
        else:
            pass

    def update_status(self):
        msg = f"Zahtev ID: {self.zahtevid} aktuelni status je {db.last_status(self.zahtevid)}."
        return msg

    def update_message(self, msg):
        self.ids.error_message.text = msg

    def potvrda_neophodna(self):
        if self.ids.drzavaid.text == 'Srbija':
            self.neophodna_potvrda_text = 'Potvrda Ministarstva nije potrebna'
        else:
            self.neophodna_potvrda_text = 'Neophodno je najpre tražiti potvrdu Ministarstva kulture'

    def prihvati(self, state):
        if state == 'down':
            try:
                db.delete_status(self.zahtevid, 'Zaposleni odbio')
                db.insert_status(self.zahtevid, 'Zaposleni prihvatio', self.today)
                msg = self.update_status()
            except Exception as err:
                msg = str(err)
                db.conn.rollback()
        else:
            try:
                db.delete_status(self.zahtevid, 'Zaposleni prihvatio')
                msg = self.update_status()
            except Exception as err:
                msg = str(err)
                db.conn.rollback()
        self.update_message(msg)

    def odbij(self, state):

        if state == 'down':
            # Aktuelni_status > Zaposleni prihvatio; BRIŠU SE I SVI KASNIJI STATUSI!!!
            try:
                db.delete_greater_status(self.zahtevid, 'Zaposleni prihvatio')
                db.insert_status(self.zahtevid, 'Zaposleni odbio', self.today)

                # resetting status of all of the buttons
                self.ids.mk_odbijenoid.state = 'normal'
                self.ids.mk_potvrdaid.state = 'normal'
                self.ids.ugovorid.state = 'normal'
                self.ids.uplataid.state = 'normal'
                self.ids.racunid.state = 'normal'
                msg = self.update_status()
            except Exception as err:
                msg = str(err)
                db.conn.rollback()
        else:
            try:
                db.delete_status(self.zahtevid, 'Zaposleni odbio')
                msg = self.update_status()

            except Exception as err:
                msg = str(err)
                db.conn.rollback()
        self.update_message(msg)

    # Update države na ovom mestu ostavljem u slučaju da je napravljena greška pri unosu
    def update_drzava(self, drzava):
        try:
            db.details_update_state(self.korisnikid, drzava)
            msg = f'Uspešno ste ažurirali zemlju korisnika u {self.ids.drzavaid.text}'

        except Exception as err:
            msg = str(err)
            db.conn.rollback()
        self.drzava_text = self.ids.drzavaid.text
        self.update_message(msg)
        self.potvrda_neophodna()

    # Upit MK

    def upit_mk(self):
        # employee must accept the request first
        if not db.details_check_status(self.zahtevid, 'Zaposleni prihvatio'):
            msg = 'Zahtev nije prihvaćen. Najpre ga morate prihvatiti.'
        # Country must not be Serbia
        elif self.drzava_text == 'Srbija':
            msg = 'Zemlja korisnika je Srbija, nije potrebno tražiti zahtev od Ministarstva'
        # Request must have not been submitted

        # maybe should remove this one and allow multiple requests

        elif db.details_get_request(self.zahtevid):
            msg = f'Za zahtev pod brojem: {self.zahtevid} već je poslat zahtev ministarstvu.'

        else:
            try:
                db.insert_request_mk(self.zahtevid, self.today)
                msg = f'Upit za zahtev {self.zahtevid} uspešno poslat'
                text = f"""
                Poštovani,
                    Molimo da u skladu sa odredbama Zakona o kulturnim dobrima izdate saglasnost za pristup
                arhivskoj građi Muzeja. """
                print(text)

            except Exception as err:
                msg = str(err)
                db.conn.rollback()
        self.update_message(msg)

    # Potvrdjen ili odbijen zahtev od strane ministarstva

    def zahtev_mk_povtrdjen(self, state):

        if not db.details_get_request(self.zahtevid):
            msg = f"Ne možete odabrati ovu opciju, morate najpre poslati upit. " \
                  f"Aktuelni status zahteva {self.zahtevid} " \
                  f"je {db.last_status(self.zahtevid)}."
        else:
            if state == 'down':
                try:
                    db.delete_status(self.zahtevid, 'Ministarstvo odbilo')
                    db.insert_status(self.zahtevid, 'Ministarstvo prihvatilo', self.today)
                    msg = self.update_status()

                except Exception as err:
                    msg = str(err)
                    db.conn.rollback()

            elif state == 'normal':
                try:
                    db.delete_status(self.zahtevid, 'Ministarstvo prihvatilo')
                    msg = self.update_status()

                except Exception as err:
                    msg = str(err)
                    db.conn.rollback()
        self.update_message(msg)

    def zahtev_mk_odbijen(self, state):

        if not db.details_get_request(self.zahtevid):
            msg = f"Ne možete odabrati ovu opciju, morate najpre poslati upit.  " \
                  f"Aktuelni status zahteva {self.zahtevid} " \
                  f"je {db.last_status(self.zahtevid)}."
        else:
            if state == 'down':
                try:
                    db.delete_status(self.zahtevid, 'Ministarstvo prihvatilo')
                    db.insert_status(self.zahtevid, 'Ministarstvo odbilo', self.today)
                    msg = self.update_status()

                except Exception as err:
                    msg = str(err)
                    db.conn.rollback()

            elif state == 'normal':
                try:
                    db.delete_status(self.zahtevid, 'Ministarstvo odbilo')
                    msg = self.update_status()

                except Exception as err:
                    msg = str(err)
                    db.conn.rollback()
        self.update_message(msg)

    # UGOVOR

    def generisi_ugovor(self):
        ugovor_data = db.get_contract(self.zahtevid)
        if not ugovor_data:
            try:
                # Triggers in the database will calculate number of pages and total price
                db.insert_contract(self.zahtevid, self.today)
                ugovor_data = db.get_contract(self.zahtevid)
                if not ugovor_data[1]:  # ukupno str

                    # maybe make ukupno_strana required field in the database itself?
                    db.delete_contract(self.zahtevid)
                    msg = 'Broj traženih stranica je 0. Najpre izaberite stranice'

            except Exception as err:
                msg = str(err)
                db.conn.rollback()
            else:
                self.update_message(msg)
        else:
            cena_po_str, brstr, ukupna_cena = ugovor_data
            self.ids.cena_po_straniid.text = str(cena_po_str)
            self.ids.ukupno_stranaid.text = str(brstr)
            self.ids.ukupna_cenaid.text = str(ukupna_cena)

    def update_ugovor(self, col, value):
        try:
            db.update_contract(col, value, self.zahtevid)
            msg = 'Ugovor uspešno ažuriran'
        except Exception as err:
            msg = str(err)
            db.conn.rollback()
        self.generisi_ugovor()
        self.update_message(msg)

    def posalji_ugovor(self, state):

        if state == 'down':
            if not db.details_check_status(self.zahtevid, 'Zaposleni prihvatio'):
                msg = f"Najpre morate odobriti zahtev."

            elif self.drzava_text != 'Srbija' and not db.details_check_status(self.zahtevid, 'Ministarstvo prihvatilo'):
                msg = f"Korisnik nije državljanin Srbije. Najpre morate dobiti dozvolu ministarstva."

            else:
                if db.get_contract(self.zahtevid):
                    try:
                        db.insert_status(self.zahtevid, 'Poslat ugovor', self.today)
                        msg = self.update_status()
                        print('Ugovor poslat')
                    except Exception as err:
                        msg = str(err)
                        db.conn.rollback()
                else:
                    msg = 'Najpre morate generisati ugovor'
        else:
            try:
                db.delete_greater_status(self.zahtevid, 'Poslat ugovor')
                msg = self.update_status()
                self.ids.uplataid.state = 'normal'
                self.ids.racunid.state = 'normal'
            except Exception as err:
                msg = str(err)
                db.conn.rollback()
        self.update_message(msg)

    def posalji_instrukcije(self):
        if db.details_check_status(self.zahtevid, 'Poslat ugovor'):

            text = f"""
            Poštovani,

            molimo vas da uplatite svotu od {(db.get_contract(self.zahtevid))[2]} eura 
            izraženu u dinarskoj protivvrednosti na dan uplate, na račun Muzeja: 123-4512-2221155.

            Srdačan pozdrav
            """

            print(text)
            msg = self.update_status()

        else:
            msg = 'Ne možete posalti instrukcije plaćanja pre nego što sastavite ugovor!'
        self.update_message(msg)

    def uplata_proknjizena(self, state):
        if state == 'down':
            if db.details_check_status(self.zahtevid, 'Poslat ugovor'):
                try:
                    db.insert_status(self.zahtevid, 'Uplata proknjizena', self.today)
                    msg = self.update_status()
                except Exception as err:
                    msg = str(err)
                    db.conn.rollback()
            else:
                msg = 'Plaćanje ne može postojati, ukoliko ne postoji ugovor'
        if state == 'normal':
            try:
                db.delete_greater_status(self.zahtevid, 'Uplata proknjizena')
                msg = self.update_status()
                self.ids.racunid.state = 'normal'
            except Exception as err:
                msg = str(err)
                db.conn.rollback()
        self.update_message(msg)

    def posalji_racun(self, state):
        if state == 'down':
            if db.details_check_status(self.zahtevid, 'Uplata proknjizena'):
                try:
                    db.insert_status(self.zahtevid, 'Izdat racun', self.today)
                    msg = self.update_status()
                except Exception as err:
                    msg = str(err)
                    db.conn.rollback()
            else:
                msg = 'Ne možete izdati račun pre nego što se potvrdi uplata.'

        if state == 'normal':
            try:
                db.delete_status(self.zahtevid, 'Izdat racun')
                msg = self.update_status()
            except Exception as err:
                msg = str(err)
                db.conn.rollback()
        self.update_message(msg)


# Recycled widget
class RequestsMain(RecycleDataViewBehavior, GridLayout):

    def request_update_message(self, msg, color='r'):
        message_widget = App.get_running_app().root.ids.requests_id.ids.error_message
        message_widget.text = msg
        if color == 'r':
            message_widget.color = (1, 0, 0)
        elif color == 'g':
            message_widget.color = (0, 1, 0)

    def open_detalji(self, zahtevid):
        detalji = DetaljiPopup(zahtevid)
        detalji.open()

    def open_trazenadok(self, zahtevid):
        trazena_dok = TrazenaDokPopup(zahtevid)
        trazena_dok.open()

    def delete_request(self):
        try:
            db.delete_request(self.zahtevid_text)
            self.parent.remove_widget(self)
            msg = F'Successfully deleted zahtev {self.zahtevid_text} from {self.z_naziv_korisnika_text}'
            color = 'g'
        except Exception as err:
            msg = str(err)
            color = 'r'
            db.conn.rollback()

        self.request_update_message(msg, color)

    def update_date(self, date):
        try:
            db.update_request_date(self.zahtevid_text, date)
            color = 'g'
            msg = F'Successfully update date to {date} on {self.zahtevid_text} from {self.z_naziv_korisnika_text}'

        except Exception as err:
            msg = str(err)
            color = 'r'
            db.conn.rollback()
        self.request_update_message(msg, color)


# Layout
class RequestsMainLabel(GridLayout):
    pass


# Recycleview
class RequestsRV(RecycleView):

    def __init__(self, **kwargs):
        super(RequestsRV, self).__init__(**kwargs)
        self.requests_populate()

    def requests_load_data(self, db_data):
        self.data = []
        for idx, row in enumerate(db_data):
            korisnikid, zahtevid, mlb, naziv_korisnika, datum_zahteva, brstr = row
            max_status = db.last_status(zahtevid)
            d = {'z_idx_text': str(idx),
                 'z_korisnikid_text:': str(korisnikid),
                 'z_status_text': max_status,
                 'z_mlb_text': mlb,
                 'z_naziv_korisnika_text': naziv_korisnika,
                 'z_datum_text': str(datum_zahteva),
                 'z_detalji_text': 'Broj zahteva: ' + str(zahtevid),
                 'z_trazenadok_text': 'Ukupno str. ' + str(brstr),
                 'zahtevid_text': str(zahtevid)
                 }
            self.data.append(d)

    def requests_populate(self):
        db_data = db.requests_getall()
        self.requests_load_data(db_data)

    def requests_search(self, name):
        db_data = db.requests_search(name.lower())
        self.requests_load_data(db_data)


# Screen
class Requests(Screen):

    def main_menu(self):
        self.manager.current = "main_screen"

    def users(self):
        self.manager.current = 'users_screen'

    def status(self):
        self.manager.current = 'status_screen'
