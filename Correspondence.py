from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from Backend import *


# Correspondence Widget which is later recycled
class CorrespondenceMain(RecycleDataViewBehavior, GridLayout):
    pass


# Correspondence Recycle View which recycles the widget above
class CorrespondenceRV(RecycleView):


    def __init__(self, **kwargs):
        super(CorrespondenceRV, self).__init__(**kwargs)
        self.get_corr()

    # Used for data loading into the Recycle View
    def corr_load_data(self, db_data):
        self.data = []
        for i in db_data:
            d = {'author_text': str(i[0]),
                 'institution_text': str(i[1]),
                 'date_text': str(i[2]),
                 'pages_text': str(i[3]),
                 'topic_text': str(i[4])}
            if i[6] == i[7]:
                d['sig_text'] = f'MNT, K {i[5]} : {i[6]}'
            else:
                d['sig_text'] = f'MNT, K {i[5]} : {i[6]}-{i[7]}'
            self.data.append(d)

    def get_corr(self):
        # Initial loading

        db_data = db.corr_getall()
        self.corr_load_data(db_data)


    def text_input_search(self, txt):
        db_data = db.corr_author_search(txt.text.lower())
        self.corr_load_data(db_data)

    def date_search(self, min_date, max_date):

        # If first or last date is omitted, they will be generated dynamically
        if min_date.text == '':
            min_date = db.corr_min_date()[0][0]
        else:
            min_date = min_date.text
        if max_date.text == '':
            max_date = db.corr_max_date()[0][0]
        else:
            max_date = max_date.text
        db_data = db.corr_date_search(min_date, max_date)
        self.corr_load_data(db_data)

    # Used for Correspondence checkbox search,
    # By default everything is selected (dict value is pkey of tematska_jedinica

    tematska_jedinica_index = {'univerzitet': 1, 'ambasada': 2, 'cestitke': 3, 'razno': 8, 'patenti': 9}

    def checkbox_search(self, value, name):

        # If checkbox is activated, set appropriate value
        if value:
            if name == 'univerzitet':
                self.tematska_jedinica_index[name] = 1
            if name == 'ambasada':
                self.tematska_jedinica_index[name] = 2
            if name == 'cestitke':
                self.tematska_jedinica_index[name] = 3
            if name == 'razno':
                self.tematska_jedinica_index[name] = 8
            if name == 'patenti':
                self.tematska_jedinica_index[name] = 9

            # if checkbox is deactivated, set value to 0
        else:
            self.tematska_jedinica_index[name] = 0

        # get selected data from the database

        db_data = db.corr_checkbox_search(tuple(self.tematska_jedinica_index.values()))
        self.corr_load_data(db_data)


# Correspondence Main screen
class Correspondence(Screen):

    def main_menu(self):
        self.manager.current = "main_screen"
