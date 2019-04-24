import datetime as date
import sys
import threading as thread

import matplotlib.animation
import matplotlib.pyplot as plt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
# alpha vantage will allow simple get requests for multiple pieces of data
# I implemented my own class, but the server would decline service due to constant updates (even with interval of 20)
from alpha_vantage import timeseries
from matplotlib import style

# will hold list information for graphing and refreshing data
data_dict = {}
tickers = []

KEY = "C40DJ2J52FXID878"
refresh_rate = 0
if len(sys.argv) <= 1:
    refresh_rate = 15
else:
    refresh_rate = int(sys.argv[1])


# simple ticker entry for stock symbols
class simple(QWidget):
    def __init__(self):
        super().__init__()
        self.top = 0
        self.left = 0
        self.width = 400
        self.height = 300
        self.label = QLabel(self)
        self.textbox = QLineEdit(self)
        self.button = QPushButton(self)
        self.button.setObjectName("enter_ticker")
        self.button.setText("enter ticker")
        self.button.move(self.width - self.button.width(), 0)
        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.label.height())
        self.setWindowTitle("Insert new ticker")
        self.textbox.move(self.label.width() + 5, 0)
        self.label.setText("Ticker")
        self.button.clicked.connect(self.handle_button)
        self.show()

    @pyqtSlot()
    def handle_button(self):
        ticker = self.textbox.text().upper()
        if ticker in tickers:
            self.textbox.setText("Already in list")
            return
        else:
            tickers.append(ticker)



def handle_data(raw_data_json):
    global data_update_thread
    global tickers
    time = date.datetime.now()
    clean_list = []
    for x in raw_data_json[0]:
        clean_list.append(x['1. symbol'])
        data_dict[x['1. symbol']] = dict(price=float(x['2. price']), time=time)
    print(data_dict)
    tickers = clean_list
    data_update_thread = thread.Timer(refresh_rate, data_thread_handler)
    data_update_thread.setDaemon(True)
    data_update_thread.start()


def data_thread_handler():
    global data_update_thread
    if len(tickers) > 0:
        try:
            handle_data(holder.get_batch_stock_quotes(tickers))
        except ValueError as e:
            print(e)
            data_update_thread = thread.Timer(refresh_rate, data_thread_handler)
            data_update_thread.setDaemon(True)
            data_update_thread.start()

    else:
        print("empty")
        data_update_thread = thread.Timer(refresh_rate, data_thread_handler)
        data_update_thread.setDaemon(True)
        data_update_thread.start()


from itertools import cycle
colors = cycle(['red','blue','yellow', 'purple', 'magenta', 'cyan', 'green'])

def handle_graph():
    plot_count = [1]
    def animate(*i):
        print(data_dict)
        plt.cla()
        for count, x in enumerate(data_dict):
            if x not in ax_data:
                ax_data[x] = (next(colors), [[], []])
            ax_data[x][1][0].append(data_dict[x]['price'])
            ax_data[x][1][1].append(data_dict[x]['time'].timestamp()/10000)
        for x in ax_data:
            plt.plot(ax_data[x][1][1], ax_data[x][1][0], color=ax_data[x][0], label=x, linewidth=1)
        leg = plt.legend()
        for x in leg.get_lines():
            x.set_linewidth(4)
    to_plot = [[[],[]]]
    style.use('fivethirtyeight')
    fig = plt.figure()
    ax_data = {}
    ani = matplotlib.animation.FuncAnimation(fig, animate,interval=5000)
    plt.show()


app = QApplication(sys.argv)
window = simple()

holder = timeseries.TimeSeries(key=KEY)

# handling data updating... DaemonThread used so that the GUI will trigger closing
data_update_thread = thread.Timer(refresh_rate, data_thread_handler)
data_update_thread.setDaemon(True)
data_update_thread.start()


thread.Thread(target=handle_graph, daemon=True).start()

print('made it')
# launching application

sys.exit(app.exec_())
