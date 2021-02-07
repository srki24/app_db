import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv


class Mydb:

    def __init__(self):
        load_dotenv()
        database_online_uri = os.environ["DATABASE_ONLINE_URI"]
        database_local_uri = os.environ['DATABASE_LOCAL_URI']  # Used for testing
        self.conn = psycopg2.connect(database_online_uri)
        self.cur = self.conn.cursor()

    # Log in

    def add_user(self, username, password, email):
        self.cur.execute("INSERT INTO users (username, password, email)"
                         "VALUES (%s, crypt(%s, gen_salt('bf')), %s);", (username, password, email))
        self.conn.commit()

    def log_in(self, username, password):
        # Using crypt() to check if pw is good use:
        # select username from users username = username
        # and  password = crypto('checkedpw', password)

        self.cur.execute("(SELECT username FROM users where username = %s"
                         " and password = crypt(%s, password))", (username, password))

        # Returns username of the user, in order to double check if everything is allright
        return self.cur.fetchall()[0][0]

    # Correspondence

    def corr_getall(self):
        self.cur.execute("""
        select a.naziv_autora, ip.naziv_institucije_pos,
        p.datum, p.brstr, tj.naziv_teme,
        d.kutijaid, min(d.folijacija) sig_od ,max(d.folijacija) sig_do
        from pismo p inner join autor a on p.autorid = a.autorid
        inner join institucija_pos ip on ip.institucija_posid = p.institucija_posid
        inner join depo d on d.pismoid = p.pismoid
        inner join kutija k on k.kutijaid = d.kutijaid
        inner join tematska_jedinica tj on tj.tematska_jedinicaid = k.tematska_jedinicaid
        group by a.naziv_autora, ip.naziv_institucije_pos, p.datum, p.brstr, d.kutijaid, tj.naziv_teme
        """)
        return self.cur.fetchall()

    def corr_author_search(self, text):
        text = "%" + text + "%"  # not the greatest solution but...
        self.cur.execute("""
        select a.naziv_autora, ip.naziv_institucije_pos,
        p.datum, p.brstr, tj.naziv_teme,
        d.kutijaid, min(d.folijacija) sig_od ,max(d.folijacija) sig_do
        from pismo p inner join autor a on p.autorid = a.autorid
        inner join institucija_pos ip on ip.institucija_posid = p.institucija_posid
        inner join depo d on d.pismoid = p.pismoid
        inner join kutija k on k.kutijaid = d.kutijaid
        inner join tematska_jedinica tj on tj.tematska_jedinicaid = k.tematska_jedinicaid
        WHERE LOWER(naziv_autora) like %s or LOWER(naziv_institucije_pos) like %s 
        group by a.naziv_autora, ip.naziv_institucije_pos, p.datum, p.brstr, d.kutijaid, tj.naziv_teme
        """, (text, text))
        return self.cur.fetchall()

    def corr_date_search(self, mini='1800', maxi='1900'):
        self.cur.execute("""
        select a.naziv_autora, ip.naziv_institucije_pos,
        p.datum, p.brstr, tj.naziv_teme,
        d.kutijaid, min(d.folijacija) sig_od ,max(d.folijacija) sig_do
        from pismo p inner join autor a on p.autorid = a.autorid
        inner join institucija_pos ip on ip.institucija_posid = p.institucija_posid
        inner join depo d on d.pismoid = p.pismoid
        inner join kutija k on k.kutijaid = d.kutijaid
        inner join tematska_jedinica tj on tj.tematska_jedinicaid = k.tematska_jedinicaid
        WHERE EXTRACT(YEAR from DATUM) BETWEEN %s and %s
        group by a.naziv_autora, ip.naziv_institucije_pos, p.datum, p.brstr, d.kutijaid, tj.naziv_teme
        """, (mini, maxi))
        return self.cur.fetchall()

    def corr_min_date(self):

        # Returns date of the first letter
        self.cur.execute("select extract(year from min(datum)) from pismo")
        return self.cur.fetchall()

    def corr_max_date(self):

        # Returns date of the last letter
        self.cur.execute("select extract(year from max(datum)) from pismo")
        return self.cur.fetchall()

    def corr_checkbox_search(self, lst):
        self.cur.execute("""
        select a.naziv_autora, ip.naziv_institucije_pos,
        p.datum, p.brstr, tj.naziv_teme,
        d.kutijaid, min(d.folijacija) sig_od ,max(d.folijacija) sig_do
        from pismo p inner join autor a on p.autorid = a.autorid
        inner join institucija_pos ip on ip.institucija_posid = p.institucija_posid
        inner join depo d on d.pismoid = p.pismoid
        inner join kutija k on k.kutijaid = d.kutijaid
        inner join tematska_jedinica tj on tj.tematska_jedinicaid = k.tematska_jedinicaid
        WHERE tj.tematska_jedinicaid in %s
        group by a.naziv_autora, ip.naziv_institucije_pos, p.datum, p.brstr, d.kutijaid, tj.naziv_teme
        """, (lst,))
        return self.cur.fetchall()

    # Users

    def users_getall(self):
        self.cur.execute('SELECT * FROM korisnik_view')
        return self.cur.fetchall()

    def users_max_id(self):
        self.cur.execute('SELECT max(korisnikid) FROM korisnik')
        return self.cur.fetchall()[0]

    def users_search(self, name):
        name = "%" + name + "%"
        self.cur.execute("SELECT * FROM korisnik_view "
                         "WHERE LOWER(naziv_korisnika) like %s", (name,))
        return self.cur.fetchall()

    def user_insert(self, user_id, mlb, naziv_korisnika, ulica, br, grad, drzava, telefon, mail):
        self.cur.execute("""insert into korisnik_view 
                         (korisnikid, mlb, naziv_korisnika, 
                         adresa_korisnika.ulica, adresa_korisnika.broj, adresa_korisnika.grad, adresa_korisnika.drzava,
                         telefon, mail)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s , %s)""",
                         (user_id, mlb, naziv_korisnika, ulica, br, grad, drzava, telefon, mail))
        self.conn.commit()

    def user_delete(self, tup):
        self.cur.execute("""DELETE FROM korisnik WHERE korisnikid in %s""", (tup,))
        self.conn.commit()

    def user_get_name(self, tup):
        self.cur.execute("""SELECT naziv_korisnika FROM korisnik WHERE korisnikid in %s""", (tup,))
        return self.cur.fetchall()

    def user_update(self, user_id, column, value):

        # If column is not separated by dot
        if "." not in column:
            query = sql.SQL("""UPDATE korisnik_view set {column} = %s WHERE korisnikid = %s""")
            query = query.format(column=sql.Identifier(column))

        else:
            table, field = column.split('.')
            query = sql.SQL("""UPDATE korisnik_view set {column} = %s WHERE korisnikid = %s""")
            query = query.format(column=sql.Identifier(table, field))

        self.cur.execute(query, (value, user_id))
        self.conn.commit()

    def requests_getall(self):
        self.cur.execute("""select k.korisnikid, z.zahtevid, k.mlb, k.naziv_korisnika, z.datum_zahteva, 
        (select sum(brstr) from trazenadok where zahtevid = z.zahtevid group by z.zahtevid) from
        korisnik k inner join zahtev z on k.korisnikid = z.korisnikid
        """)
        return self.cur.fetchall()

    def requests_search(self, name):
        name = '%' + name + '%'
        self.cur.execute("""select k.korisnikid, z.zahtevid, k.mlb, k.naziv_korisnika, z.datum_zahteva, 
        (select sum(brstr) from trazenadok where zahtevid = z.zahtevid group by z.zahtevid ) from
        korisnik k inner join zahtev z on k.korisnikid = z.korisnikid
        WHERE LOWER(k.naziv_korisnika) like %s""", (name,))
        return self.cur.fetchall()

    # Sa ovim upitom punim Recycle view u trazenadok popupu
    # pisma koja se već nalaze među traženim dokumentima su isključena iz liste!

    def unselected_letters(self, zahtevid):
        self.cur.execute("""select p.pismoid, a.naziv_autora, i.naziv_institucije_pos, p.datum, p.brstr
        from pismo p inner join autor a on p.autorid = a.autorid
        inner join institucija_pos i on i.institucija_posid = p.institucija_posid
        where pismoid not in (select pismoid from trazenadok where zahtevid = %s)""", (zahtevid,))
        return self.cur.fetchall()

    def populate_trazenadok(self, zahtevid):
        self.cur.execute("""select td.pismoid, a.naziv_autora, i.naziv_institucije_pos, p.datum, td.brstr
        from trazenadok td inner join pismo p on td.pismoid = p.pismoid
        inner join autor a on a.autorid = p.autorid
        inner join institucija_pos i on i.institucija_posid = p.institucija_posid
        WHERE zahtevid = %s""", (zahtevid,))
        return self.cur.fetchall()

    def clear_trazenadok(self, zahtevid):
        self.cur.execute('DELETE from trazenadok where zahtevid = %s', (zahtevid,))
        self.conn.commit()

    def insert_trazenadok(self, zahtevid, pismoid):
        self.cur.execute('INSERT INTO trazenadok (zahtevid, pismoid) VALUES (%s, %s)',
                         (zahtevid, pismoid))
        self.conn.commit()

    def details_get_userid(self, zahtevid):
        self.cur.execute("SELECT korisnikid FROM zahtev WHERE zahtevid = %s", (zahtevid,))
        return self.cur.fetchone()

    def details_get_state(self, korisnikid):
        self.cur.execute("SELECT (adresa_korisnika).drzava FROM korisnik where korisnikid = %s",
                         (korisnikid,))
        return self.cur.fetchone()

    def details_check_status(self, zahtevid, status):
        self.cur.execute("SELECT aktuelni_status FROM status_zahteva WHERE zahtevid = %s"
                         " AND aktuelni_status = %s", (zahtevid, status))
        return self.cur.fetchone()


    def details_get_request(self, zahtevid):
        self.cur.execute("SELECT upitid FROM upit_mk WHERE "
                         "zahtevid = %s", (zahtevid,))
        return self.cur.fetchone()

    def insert_request_mk(self, zahtevid, date):
        self.cur.execute(" INSERT INTO upit_mk (zahtevid, datum_upit) values (%s, %s)", (zahtevid, date))
        self.conn.commit()

    def insert_request(self, korisnikid, date):
        self.cur.execute("INSERT INTO zahtev(korisnikid, datum_zahteva) "
                         "VALUES (%s, %s)", (korisnikid, date))
        self.conn.commit()

    def delete_request(self, zahtevid):
        self.cur.execute("DELETE FROM zahtev WHERE zahtevid = %s", (zahtevid, ))
        self.conn.commit()

    def update_request_date(self, zahtevid, date):
        self.cur.execute("UPDATE zahtev SET datum_zahteva = %s "
                         "WHERE zahtevid = %s", (date, zahtevid))
        self.conn.commit()

    def delete_status(self, zahtevid, aktuelni_status):
        self.cur.execute("DELETE FROM status_zahteva WHERE zahtevid = %s "
                         "AND aktuelni_status = %s", (zahtevid, aktuelni_status))
        self.conn.commit()

    def delete_greater_status(self, zahtevid, aktuelni_status):
        self.cur.execute("DELETE FROM status_zahteva WHERE zahtevid = %s "
                         "AND aktuelni_status >= %s", (zahtevid, aktuelni_status))
        self.conn.commit()

    def insert_status(self, zahtevid, aktuelni_status, date=0):
        self.cur.execute("INSERT INTO status_zahteva (zahtevid, aktuelni_status, datum)"
                         " VALUES (%s, %s, %s)", (zahtevid, aktuelni_status, date))
        self.conn.commit()

    def update_status(self, column, data, zahtevid, aktuelni_status):
        query = sql.SQL("UPDATE status_zahteva SET {column} = %s "
                        "WHERE zahtevid = %s AND aktuelni_status = %s")

        query = query.format(column=sql.Identifier(column))
        self.cur.execute(query, (data, zahtevid, aktuelni_status))
        self.conn.commit()


    def details_update_state(self, korisnikid, drzava):
        self.cur.execute("UPDATE korisnik SET adresa_korisnika.drzava = %s "
                         "WHERE korisnikid = %s", (drzava, korisnikid))
        self.conn.commit()

    def get_contract(self, zahtevid):
        self.cur.execute("SELECT cena_po_strani, ukupno_strana, ukupna_cena "
                         "FROM ugovor where zahtevid = %s", (zahtevid,))
        return self.cur.fetchone()

    def insert_contract(self, zahtevid, date):
        # Default price per page is 5
        self.cur.execute("INSERT INTO ugovor (zahtevid, datum_ugovora, cena_po_strani) "
                         "VALUES (%s, %s, 5)", (zahtevid, date))
        self.conn.commit()

    def delete_contract(self, zahtevid):
        self.cur.execute("DELETE FROM ugovor WHERE zahtevid = %s", (zahtevid,))
        self.conn.commit()

    def update_contract(self, col, value, zahtevid):
        query = sql.SQL("""UPDATE ugovor set {column} = %s WHERE zahtevid = %s""")
        query = query.format(column=sql.Identifier(col))
        self.cur.execute(query, (value, zahtevid))
        self.conn.commit()

    def last_status(self, zahtevid):
        self.cur.execute("""select max(aktuelni_status) from status_zahteva
                        where zahtevid = %s group by zahtevid""", (zahtevid,))
        return str(self.cur.fetchall()[0]).strip("',)(")

    def status_getall(self):
        self.cur.execute("""
                    select k.naziv_korisnika, sz.zahtevid, sz.aktuelni_status, sz.datum 
                    FROM  status_zahteva sz INNER JOIN zahtev z
                    ON sz.zahtevid = z.zahtevid
                    INNER JOIN korisnik k on k.korisnikid = z.korisnikid
                            """)
        return self.cur.fetchall()

    def status_getall_max(self):
        self.cur.execute("""
                    select k.naziv_korisnika, sz.zahtevid, max(sz.aktuelni_status), sz.datum 
                    FROM  status_zahteva sz INNER JOIN zahtev z
                    ON sz.zahtevid = z.zahtevid
                    INNER JOIN korisnik k on k.korisnikid = z.korisnikid
                    GROUP BY k.naziv_korisnika, sz.zahtevid, sz.datum
""")
        return self.cur.fetchall()

    def status_text_search(self, text):
        text = "%" + text + "%"
        self.cur.execute("""SELECT k.naziv_korisnika, sz.zahtevid, sz.aktuelni_status, sz.datum 
                    FROM status_zahteva sz INNER JOIN zahtev z
                    ON sz.zahtevid = z.zahtevid
                    INNER JOIN korisnik k on k.korisnikid = z.korisnikid
                    WHERE LOWER(naziv_korisnika) like %s""", (text,))
        return self.cur.fetchall()

    def status_max_text_search(self, text):
        text = "%" + text + "%"
        self.cur.execute("""
                        SELECT k.naziv_korisnika, sz.zahtevid, max(sz.aktuelni_status), max(sz.datum)
                        FROM  status_zahteva sz INNER JOIN zahtev z
                        ON sz.zahtevid = z.zahtevid
                        INNER JOIN korisnik k on k.korisnikid = z.korisnikid
                        WHERE LOWER(naziv_korisnika) like %s 
                        GROUP BY k.naziv_korisnika, sz.zahtevid""", (text,))

        return self.cur.fetchall()

    def id_search(self, zahtev_id):
        if not zahtev_id:  # Used for crash prevention since querry is executed on press, should be optimised
            self.cur.execute("""select k.naziv_korisnika, sz.zahtevid, sz.aktuelni_status, sz.datum 
                    FROM  status_zahteva sz INNER JOIN zahtev z
                    ON sz.zahtevid = z.zahtevid
                    INNER JOIN korisnik k on k.korisnikid = z.korisnikid""")

        else:
            self.cur.execute("""select k.naziv_korisnika, sz.zahtevid, sz.aktuelni_status, sz.datum 
                    FROM  status_zahteva sz INNER JOIN zahtev z
                    ON sz.zahtevid = z.zahtevid
                    INNER JOIN korisnik k on k.korisnikid = z.korisnikid
                    WHERE sz.zahtevid = %s""", (zahtev_id,))
        return self.cur.fetchall()

    def id_max_search(self, zahtev_id):
        if not zahtev_id:  # Used for crash prevention since querry is executed on press, should be optimised
            self.cur.execute("""select k.naziv_korisnika, sz.zahtevid, max(sz.aktuelni_status), max(sz.datum) 
                    FROM  status_zahteva sz INNER JOIN zahtev z
                    ON sz.zahtevid = z.zahtevid
                    INNER JOIN korisnik k on k.korisnikid = z.korisnikid
                    GROUP BY k.naziv_korisnika, sz.zahtevid""")

        else:
            self.cur.execute("""select k.naziv_korisnika, sz.zahtevid, max(sz.aktuelni_status), sz.datum
                    FROM  status_zahteva sz INNER JOIN zahtev z
                    ON sz.zahtevid = z.zahtevid
                    INNER JOIN korisnik k on k.korisnikid = z.korisnikid
                    WHERE sz.zahtevid = %s and
                    sz.aktuelni_status = (select max(aktuelni_status) from status_zahteva WHERE zahtevid = %s)
                    GROUP BY k.naziv_korisnika, sz.zahtevid, sz.datum""", (zahtev_id, zahtev_id))
        return self.cur.fetchall()

    # Two functions used for testing
    def sql_fetch(self, n):
        self.cur.execute(n)
        return self.cur.fetchall()

    def sql_commit(self, n):
        self.cur.execute(n)
        self.conn.commit()

    def close(self):
        self.conn.close()

db = Mydb()