from datetime import datetime as dt
from datetime import timedelta as td
from pygal.style import DarkStyle
import matplotlib.dates as mdates
import numpy as np
import pygal
import sqlite3
import calendar

now = dt.now()
last_month = "%02d" % (now.month - 1 if now.month > 1 else 12,)
last_month_int = int(last_month)


def get_monthly_count():
    conn = sqlite3.connect("gym_session_data.db")
    c = conn.cursor()
    raw_data = list(c.execute('''SELECT *, count(session_start) From gym_session
                                 WHERE date BETWEEN '2013-01' AND (?)
                                 GROUP BY strftime('%Y-%m', date)''', ('2017-{}'.format(last_month),)))
    conn.close()

    date = [i[1][:-3] for i in raw_data]
    count = [i[4] for i in raw_data]
    date_count = list(zip(date, count))

    return date_count


def get_day_count():
    conn = sqlite3.connect("gym_session_data.db")
    c = conn.cursor()
    raw_data = list(c.execute('''SELECT count(session_start) From gym_session
                                 WHERE date BETWEEN '2013-01' AND (?)
                                 GROUP BY strftime('%w', date)''', ('2017-{}'.format(last_month),)))
    conn.close()
    week_data = [i[0]for i in raw_data]

    return week_data


def get_total():
    conn = sqlite3.connect("gym_session_data.db")
    c = conn.cursor()
    raw_data = list(c.execute('''SELECT *, count(session_start) From gym_session
                                 WHERE date BETWEEN '2013-01' AND (?)''', ('2017-{}'.format(last_month),)))
    conn.close()
    total_sessions = [i[4] for i in raw_data]
    total_days = [i[0] for i in raw_data]
    missed_sessions = [x - y for x, y in zip(total_days, total_sessions)]
    total = list(zip(total_sessions, missed_sessions, total_days))

    return total

def get_long_short():
    conn = sqlite3.connect("gym_session_data.db")
    c = conn.cursor()
    raw_data = list(c.execute('''SELECT date,
                                 sum(strftime('%s', session_end) - strftime(
                                 '%s', session_start))From gym_session
                                 WHERE date BETWEEN '2013-01' AND (?)
                                 AND session_start IS NOT NULL 
                                 GROUP BY date''', ('2017-{}'.format(last_month),)))

    raw_data.sort(key=lambda tup: tup[1])
    clean_data = [s for s in raw_data if len(str(s[1])) == 4]

    return clean_data



# LINE CHART for Total Monthly Gym Session

x_data = [i[0] for i in get_monthly_count()]
x_data_str = [dt.strftime(dt.strptime(x_data[x_data.index(i)], '%Y-%m').date(),'%b-%Y') for i in x_data]
y_data = [i[1] for i in get_monthly_count()]

np_x = mdates.datestr2num(x_data)
np_y = np.array(y_data)
np_pol = np.poly1d(np.polyfit(np_x, np_y, 5))
trend_data = np_pol(np_x)


line_chart = pygal.Line(style=DarkStyle,
                        x_label_rotation=-45,
                        width=1500,
                        show_y_guides=False,
                        )

line_chart.title = "Monthly Gym Visits"
line_chart.x_labels = x_data_str
line_chart.y_labels = list(range(0, 31))
line_chart.add("Visits", y_data, dots_size=1.5, stroke=False)
line_chart.add("Trend", trend_data, dots_size=1.5, show_dots=False)
line_chart.render_to_file("line_chart.svg")

# BAR CHART for Least and Most Popular Days at the Gym

x_days = ['Sunday', 'Monday', 'Tuesday',
          'Wednesday', 'Thursday', 'Friday', 'Saturday']
y_day_data = get_day_count()

bar_chart = pygal.Bar(style=DarkStyle,
                      spacing=10,
                      height=300,
                      width=600,
                      show_y_guides=False,
                      print_values=True)
bar_chart.title = "Least and Most Popular Days at the Gym from Jan-2013 to {}-2017"\
    .format(calendar.month_abbr[last_month_int])

bar_chart.x_labels = x_days
bar_chart.add("Total Days", y_day_data)
bar_chart.render_to_file("bar_chart.svg")

# PIE CHART for Total Session and Missed Sessions

pie_sess = get_total()[0][0]
pie_miss = get_total()[0][1]
pie_total = get_total()[0][2]

pie_chart = pygal.Pie(style=DarkStyle,
                      font_size=32)
pie_chart.title = "Total Gym Sessions from Jan-2013 to {}-2017 | {} Days"\
    .format(calendar.month_abbr[last_month_int], pie_total)

pie_chart.add("Missed Days", pie_miss)
pie_chart.add("Days Attended", pie_sess)
pie_chart.render_to_file("pie_chart.svg")

time_dates = [i[0] for i in get_long_short()]
time_data = [i[1] for i in get_long_short()]
average_sess = np.mean(np.array)

# BAR CHART for Session Durations

bar_chart_time = pygal.HorizontalBar(style=DarkStyle,
                                     print_values=True,
                                     height=400,
                                     spacing=20,
                                     margin=50,
                                     legend_at_bottom=True,
                                     legend_at_bottom_columns=3)

bar_chart_time.title = "Gym Session Durations"

bar_chart_time.add("Longest ({})".format(time_dates[-1]), time_data[-1])
bar_chart_time.add("Average", int(average_sess))
bar_chart_time.add("Shortest ({})".format(time_dates[0]), time_data[0])
bar_chart_time.value_formatter = lambda x: str(td(seconds=x))


bar_chart_time.render_to_file("bar_chart2.svg")
