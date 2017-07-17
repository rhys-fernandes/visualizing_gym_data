import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from bs4 import BeautifulSoup

db_file = "gym_session_data.db"
conn = sqlite3.connect(db_file)
db = conn.cursor()


def get_data():
    raw_data = []
    soup = BeautifulSoup(open("data.html"), "html.parser")
    for i in soup.find_all("div", {"class": "eventscroll"}):
        raw_data = i.get_text().split()
        raw_data = [x for x in raw_data if x != "No"]
        raw_data = [x for x in raw_data if x != "access"]
        raw_data = [x for x in raw_data if x != "made"]

    clean_data = list(raw_data)
    paired_data = list(zip(clean_data[0::2], clean_data[1::2]))
    raw_dict = defaultdict(list)
    for i, x in paired_data:
        raw_dict[i].append(x)

    for key, val in raw_dict.items():
        for i in val:
            # remove any value that isn't the min or max
            if i != max(val) and i != min(val):
                raw_dict[key] = [x for x in raw_dict[key] if x != i]
            # remove duplicates
            elif val.count(i) > 1:
                raw_dict[key].remove(i)
                # values less that 2 become null[]

    # remove single values
    clean_dict = dict([(k, v) for k, v in raw_dict.items() if len(v) > 1])

    return clean_dict


def create_db():
    # Create Table
    db.execute("""CREATE TABLE gym_session
                 (id INTEGER PRIMARY KEY,
                  date TEXT, 
                  session_start TEXT, 
                  session_end TEXT
                  )""")

    conn.commit()
    conn.close()


def fill_db(data):
    date_field = []
    d1 = date(2013, 1, 1)  # start date
    d2 = date(2017, 12, 31)  # end date
    delta = d2 - d1  # timedelta

    for i in range(delta.days + 1):
        date_field.append(d1 + timedelta(days=i))

    s_times = data

    for x in date_field:
        db.execute("""INSERT INTO gym_session(date)
                     VALUES(?)""", (x,))


    db.execute("""SELECT * FROM gym_session""")
    result = db.fetchall()

    for d in result:
        print(d[0])
        for k, v in sorted(s_times.items()):
            if d[1] == k:
                with conn:
                    db.execute("""UPDATE gym_session
                                  SET session_start = ?, session_end = ?
                                  WHERE date = ?""", (v[1], v[0], d[1]))

    conn.close()

