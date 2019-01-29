import numpy as np
import pandas as pd
from sklearn import linear_model
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import quandl
import math
import os
import sys

from dateutil.parser import parse

p_port_alpha = '2018-05-24'
p_alpha = '2018-05-24'
count = count_pf = count_plt = count_ss = aplha_count =  beta_count = count_al = count_sr =  count_cs = count_pt = count_show_folio = 0
start_ss = '2018-01-01'
end_ss = '2018-05-23'

# Decent colors
# 1a3333 (dark more greenish navy blue)
def symbol_to_path(symbol, base_dir='Stocks/'):
    return os.path.join(base_dir, (symbol + '.csv'))


def get_data(symbols, start_date, end_date):
    # Create an empty dataframe
    dates = pd.date_range(start_date, end_date)
    df = pd.DataFrame(index=dates)

    if ('SPY' not in symbols):
        symbols.insert(0, 'SPY')
    # Read data into temporary dataframe
    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol),
                              index_col='Date', parse_dates=True,
                              usecols=['Date', 'Adj Close'], na_values=['nan'])
        df = df.join(df_temp, how='inner')
        df = df.rename(columns={'Adj Close': symbol})
        if symbol == 'SPY':
            df = df.dropna(subset=['SPY'])
    #     print(df)
    return df


def normalize_data(df):
    return df / df.ix[0, :]


def slice_data(df1, start_date='2018-03-18', end_date='2012-03-18', company='SPY'):
    stock_names = []
    no_of_stocks = 1
    for x in range(no_of_stocks):
        stock_names.append(company)

    df_sliced = df1.ix[start_date:end_date, stock_names]

    return df_sliced


def sharpe_ratio(daily_df):
    df_mean = daily_df.mean()
    df_std = daily_df.std()
    sharperatio = df_mean / df_std
    rt_252 = 15.8745
    sharperatio = sharperatio * rt_252
    return sharperatio


def compute_daily_returns(df):
    daily_returns = (df / df.shift(1)) - 1
    return daily_returns


def compute_cumulative_returns(df, begin_date, end_date):
    print(len(df_selected.shape))
    if len(df) > 1:
        cumulative_returns = (df.ix[begin_date:end_date, :] / df.ix[0]) - 1
    else:
        cumulative_returns = (df.ix[begin_date:end_date] / df.ix[0]) - 1
    return cumulative_returns


def get_rolling(df, w=20):
    rmean = df.rolling(window=w, center=False).mean()
    rstddev = df.rolling(window=w, center=False).std()
    return rmean, rstddev


def get_ballinger_bands(rm, rstd):
    upper_band = rm + (2 * rstd)
    lower_band = rm - (2 * rstd)
    return upper_band, lower_band


def simple_mov_avg(df):
    rmean, rstddev = get_rolling(df, 20)
    sma = (df / rmean) - 1
    return sma


def compute_ballinger_bands(df):
    rmean, rstddev = get_rolling(df, 20)
    #     sma = simple_mov_avg(df)
    print("std deviation: \n", rstddev)
    stddev = rmean + (2 * rstddev)
    bbands = ((df - rmean) / (stddev)) * 100
    return bbands


def pred_date(no, my_num):
    for i in range(1, (no + 1)):
        if (i % 7 == 0):
            my_num = my_num - 2
        if (i % 29 == 0):
            my_num -= 1
    return my_num

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Roboto', size=18, weight="bold")
        self.general_font = tkfont.Font(family='Roboto', size=12, weight="bold")
        self.roboto20 = tkfont.Font(family='Roboto', size=15, weight='bold')

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        self.frames["WelcomePage"] = WelcomePage(parent=container, controller=self)
        self.frames["ActiveTrading"] = ActiveTrading(parent=container, controller=self)
        self.frames["PassiveTrading"] = PassiveTrading(parent=container, controller=self)
        self.frames["ShowStocks"] = ShowStocks(parent=container, controller=self)
        self.frames["CompareStocks"] = CompareStocks(parent=container, controller=self)
        self.frames["DailyReturns"] = DailyReturns(parent=container, controller=self)
        self.frames["Beta"] = Beta(parent=container, controller=self)
        self.frames["Portfolio"] = Portfolio(parent=container, controller=self)
        self.frames["Alpha"] = Alpha(parent=container, controller=self)
        self.frames["PredictLongTerm"] = PredictLongTerm(parent=container, controller=self)
        # self.frames["CAPM"] = CAPM(parent=container, controller=self)

        self.frames["WelcomePage"].grid(row=0, column=0, sticky="nsew")
        self.frames["ActiveTrading"].grid(row=0, column=0, sticky="nsew")
        self.frames["PassiveTrading"].grid(row=0, column=0, sticky="nsew")
        self.frames["ShowStocks"].grid(row=0, column=0, sticky="nsew")
        self.frames["CompareStocks"].grid(row=0, column=0, sticky="nsew")
        self.frames["DailyReturns"].grid(row=0, column=0, sticky="nsew")
        self.frames["Beta"].grid(row=0, column=0, sticky="nsew")
        self.frames["Portfolio"].grid(row=0, column=0, sticky="nsew")
        self.frames["Alpha"].grid(row=0, column=0, sticky="nsew")
        self.frames["PredictLongTerm"].grid(row=0, column=0, sticky="nsew")
        # self.frames["CAPM"].grid(row=0, column=0, sticky="nsew")
        self.show_frame("WelcomePage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class WelcomePage(tk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        filename = PhotoImage(file="images/welcome.png")
        background_label = Label(self, image=filename)
        background_label.image = filename
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        label = tk.Label(background_label, text="Stock Market Trading Application", font=('roboto', 36, 'bold'),
                         bg='#008080', fg='#102933')

        button1 = tk.Button(background_label, text=" Active Trading ", width=18, height=2, bg="#102933", fg="white",
                            font=(25),
                            command=lambda: controller.show_frame("ActiveTrading"))
        button2 = tk.Button(background_label, text=" Passive Trading", width=18, height=2, bg="#102933", fg="white",
                            font=(25),
                            command=lambda: controller.show_frame("PassiveTrading"))

        label1 = tk.Label(background_label,
                          text="To first Analyze the situation in stock market,\n you can choose options from below.",
                          width=45,
                          font=controller.general_font, bg='#67e7de', fg='#102933')
        button3 = tk.Button(background_label, text="Graph for Stocks ", bg="#102933", fg="white", width=18, height=2,
                            font=(25),
                            command=lambda: controller.show_frame("ShowStocks"))

        button4 = tk.Button(background_label, text="Stock comparison\nw.r.t. Market ", bg="#102933", fg="white",
                            width=18, height=2, font=(25),
                            command=lambda: controller.show_frame("CompareStocks"))

        label.pack(side="top", fill="x", pady=10)
        
        button1.place(x=420, y=100)
        button2.place(x=800, y=100)
        label1.place(x=458, y=200)
        button3.place(x=420, y=300)
        button4.place(x=800, y=300)
        
class ActiveTrading(tk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        filename = PhotoImage(file="images/active.png")
        bg_label = Label(self, image=filename)
        bg_label.image = filename
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        label_activ = tk.Label(bg_label,text="Welcome to active trading",font=('roboto', 30, 'bold'),bg="#00182B",fg='white')
        label_desc = tk.Label(bg_label, text="Select here to invest in the companies of your choice",
                         background='#00182B', fg='#B16F24', font=('roboto', 14, 'bold'), justify="center")
        button_port = tk.Button(bg_label, text="Portfolio ",bg="#00182B",fg='white',font=("roboto",14,"bold"),width=18, height=2,
                                command=lambda: controller.show_frame("Portfolio"))
        label_right = tk.Label(bg_label,text="To know the statistics before selecting stocks for your Portfolio,\n"
                                             "The following options below can help:",
                          background='#00182B', fg='#B16F24', font=('roboto', 14, 'bold'), justify="center")
        button_daily = tk.Button(bg_label, text="Daily Returns " ,bg="#00182B",fg='white',font=("roboto",12,"bold"),width=18, height=1,
                            command=lambda: controller.show_frame("DailyReturns"))

        button_beta = tk.Button(bg_label, text="Beta", bg="#00182B",fg='white',font=("roboto",12,"bold"),width=18, height=1,
                                command=lambda: controller.show_frame("Beta"))
        button_alpha = tk.Button(bg_label, text="Alpha",bg="#00182B",fg='white',font=("roboto",12,"bold"),width=18, height=1,
                                 command=lambda: controller.show_frame("Alpha"))

        button_home = tk.Button(bg_label, text="Go back to home page",bg="#00182B",fg='white',font=("roboto",10,"bold"),width=18, height=1,
                                command=lambda: controller.show_frame("WelcomePage"))

        label_activ.pack(side="top", fill="x",pady=10)
        label_desc.place  (x=35,y=100)# side="top", fill="x",padx=300,pady=10)
        button_port.place (x=120,y=190)
        label_right.place (x=720,y=90)
        button_daily.place(x=870,y=160)
        button_beta.place (x=870,y=200)
        button_alpha.place(x=870,y=240)
        button_home.place (x=580,y=450)


class Beta(tk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        left_frame = ttk.Frame(self)
        left_frame.pack(padx=100, pady=10, side=LEFT)
        right_frame = ttk.Frame(self)
        right_frame.pack(padx=50, pady=10, side=LEFT)

        label1 = ttk.Label(left_frame, text="Beta or slope w.r.t. market", font=controller.title_font, justify="center")
        label1.pack(side="top", fill="x", padx=10, pady=10)

        label2 = ttk.Label(left_frame, text="Select the stocks below.", font=controller.general_font, justify="center")
        label2.pack(side="top", fill="x", padx=10, pady=10)

        res = Label(left_frame, text="", font=("arial", 1))
        res.pack()

        bottom = ttk.Label(right_frame)

        def plot_data(df_spy_company, company, lastend, p):
            global count, bottom
            if (count > 0):
                bottom.destroy()
                count = 0

            bottom = ttk.Label(right_frame)
            bottom.grid(column=0, row=1)

            f1 = Figure(figsize=(8, 3.5), dpi=100)
            axes = f1.add_subplot(111)

            axes.scatter(x=df_spy_company['SPY'], y=df_spy_company[company])
            axes.plot(lastend, p, color='green', linestyle='dashed', linewidth=3)

            axes.set_xlabel('SPY')
            axes.set_ylabel(company)
            axes.set_title("Scatterplot between SPY and " + company + " along with the slope")
            axes.legend(loc=9)
            canvas = FigureCanvasTkAgg(f1, master=bottom)
            canvas.draw()  # canvas.show()
            canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

            button3 = ttk.Button(bottom, text="Clear ",
                                 command=lambda: bottom.destroy())
            button3.pack()
            count += 1

        def fake_predict(x, m, c):
            l = []
            for i in x:
                l.append(i * m + c)
            return l

        def calculate_beta(df_x, df_y, company, df_spy_company):
            global beta_count, res
            if (beta_count > 0):
                res.pack_forget()
                beta_count = 0
            res = Label(left_frame, text="Beta= ", font=("arial", 10, "bold"), justify="center")
            res.pack()
            mini = df_spy_company['SPY'].min()
            maxi = df_spy_company['SPY'].max()

            m = 0
            c = 0
            df_x = df_x[1:]
            df_y = df_y[1:]
            x = df_x.SPY.values
            y = df_y[company].values
            print("DAILY RETURNS OF SLICED SPY=\n", x)
            print("DAILY RETURNS OF SLICED", company, "=\n", y)

            m = (((np.mean(x) * np.mean(y)) - np.mean(x * y)) / ((np.mean(x) ** 2) - (np.mean(x ** 2))))
            c = (np.mean(y) - (m * np.mean(x)))

            m_str = str(m)
            res.config(text="Beta = " + m_str)
            p = fake_predict((maxi, mini), m, c)

            beta_count += 1
            lastend = [maxi, mini]
            plot_data(df_spy_company, company, lastend, p)

            return m

        OPTIONS = ["Select Company ", "Google", "Apple", "IBM", "Amazon", "Netflix", "Facebook", "Tesla"]  # etc

        variable = tk.StringVar(left_frame)
        variable.set(OPTIONS[0])  # default value

        COMPANY_LIST = {"Google": "GOOG",
                        "Apple": "AAPL",
                        "IBM": "IBM",
                        "Amazon": "AMZN",
                        "Netflix": "NFLX",
                        "Facebook": "FB",
                        "Tesla": "TSLA"
                        }

        def option_selection_menu(event):
            company = str(COMPANY_LIST.get(variable.get(), "GOOG"))
            start_date = '2018-01-01'
            end_date = '2018-05-18'

            df_company_SPY = get_data([company], start_date, end_date)
            df_daily = compute_daily_returns(df_company_SPY)
            df_spy_beta = slice_data(df_company_SPY, start_date, end_date, 'SPY')
            spy_daily = compute_daily_returns(df_spy_beta)
            df_sliced_company_beta = slice_data(df_company_SPY, start_date, end_date, company)
            company_daily = compute_daily_returns(df_sliced_company_beta)
            calculate_beta(spy_daily, company_daily, company, df_daily)
            return

        w = ttk.OptionMenu(left_frame, variable, *OPTIONS, command=option_selection_menu)
        w.pack()

        button2 = ttk.Button(left_frame, text="Go back to Active trading page",
                             command=lambda: controller.show_frame("ActiveTrading"))
        button2.pack()

class Alpha(tk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        filename = PhotoImage(file="images/alpha.png")
        bg_label = Label(self, image=filename)
        bg_label.image = filename
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        label1 = tk.Label(bg_label, text=" Alpha or Prediction value ", font=('Roboto',24,"bold"), justify="center",bg="#3C3E4F",fg="#537194")
        label1.pack(side="top", fill="x", pady=19)

        label2 = tk.Label(bg_label, text="Select the stocks below.", font=('Roboto',14,"bold"), justify="center",bg="#353747",fg="#537194")
        label2.place(x=30,y=70)

        options1 = ['Select date to predict for', '1 day ahead', '5 days ahead', '10 days ahead', '20 days ahead']

        variable1 = tk.StringVar(bg_label)
        variable1.set(options1[1])

        date_dict = {'1 day ahead': '2018-05-24',
                     '5 days ahead': '2018-05-28',
                     '10 days ahead': '2018-06-02',
                     '20 days ahead': '2018-06-12',
                     '30 days ahead': '2018-06-22',
                     }

        def date_assign(event):
            global p_alpha
            p_alpha = str(date_dict.get(variable1.get(), "2018-05-24"))
            return

        w1 = ttk.OptionMenu(bg_label, variable1, *options1, command=date_assign)
        w1.place(x=40,y=110)
        res = Label(bg_label, text="", font=("arial", 1),bg="#DBDCE3",fg="#1c1c45")

        bottom = ttk.Label(bg_label)

        def plot_data(X, Y, company, X_df, y_df):
            global count_al, bottom
            if (count_al > 0):
                bottom.destroy()
                count = 0

            bottom = ttk.Label(bg_label)
            bottom.place(x=400,y=150)

            f1 = Figure(figsize=(8, 3.5), dpi=100)
            axes = f1.add_subplot(111)
            axes.plot(X_df, y_df)
            axes.plot(X, Y)
            axes.set_xlabel("Days starting from 2012-03-17 to prediction date")
            axes.set_ylabel("Prices")
            axes.set_title("Plot between " + company + "'s one month data with prediction")
            c = [company, "Prediction"]
            axes.legend(c, loc=9)
            canvas = FigureCanvasTkAgg(f1, master=bottom)
            canvas.draw()  # canvas.show()
            canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

            button3 = ttk.Button(bottom, text="Clear ",
                                 command=lambda: bottom.destroy())
            button3.pack()
            count_al += 1

        def preserve(X_preserve):
            return X_preserve

        def calculate_alpha(df_company, company, end_date):
            global count_al, res, p_alpha
            if (count_al > 0):
                res.pack_forget()
                count_al = 0
            res = Label(bg_label, text="Predicted value= ", font=("arial", 10, "bold"), justify="center",bg="#DBDCE3",fg="#1c1c45")
            res.place(x=30,y=180)

            date_vals = df_company.index

            date_arr = np.array([])

            for date in (date_vals):
                date_arr = np.append(date_arr, date.strftime("%d-%m-%y"))
            no_of_days = len(date_arr)

            d = np.array([])
            for i in range(1, (no_of_days + 1)):
                d = np.append(d, i)

            X = d[:]
            y = df_company[company].values
            X_preserve = preserve(X)
            X = X.reshape(-1, 1)
            l_model = linear_model.LinearRegression()
            l_model.fit(X, y)
            df_temp = df_company[company].values
            temp = df_temp[-1]
            pred_added = (parse(p_alpha) - parse(end_date)).days
            pred_trading_days = pred_date(pred_added, pred_added)
            pred = no_of_days + pred_trading_days

            pred_value_1 = l_model.predict([[1]])
            pred_value_2 = l_model.predict([[pred]])
            val_alpha = (pred_value_2 / temp)
            print("Val_alpha= ", val_alpha)
            pred_str = str(pred_value_2[0])
            alpha_str = str(val_alpha[0])
            res.config(text="Predicted value = " + pred_str + "\ni.e. " + alpha_str + "% of present value",bg="#d5d7d8",fg="#1c1c45")

            plot_data([1, pred], [pred_value_1, pred_value_2], company, X_preserve, y)
            count_al += 1
            return

        OPTIONS = ["Select Company ", "Google", "Apple", "IBM", "Amazon", "Netflix", "Facebook", "Tesla"]  # etc

        variable = tk.StringVar(bg_label)
        variable.set(OPTIONS[0])  # default value

        COMPANY_LIST = {"Google": "GOOG",
                        "Apple": "AAPL",
                        "IBM": "IBM",
                        "Amazon": "AMZN",
                        "Netflix": "NFLX",
                        "Facebook": "FB",
                        "Tesla": "TSLA"
                        }

        def option_selection_menu(event):
            global p_alpha
            company = str(COMPANY_LIST.get(variable.get(), "GOOG"))
            start_date = '2018-03-23'
            end_date = '2018-05-23'

            df_company_SPY = get_data([company], start_date, end_date)
            df_sliced_company = slice_data(df_company_SPY, start_date, end_date, company)

            calculate_alpha(df_sliced_company, company, end_date)
            return

        w = ttk.OptionMenu(bg_label, variable, *OPTIONS, command=option_selection_menu)
        w.place(x=40,y=140)

        button2 = ttk.Button(bg_label, text="Go back to Active trading page",
                             command=lambda: controller.show_frame("ActiveTrading"))
        button2.place(x=30,y=240)

folio_set = set()
folio_list = []
class Portfolio(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        filename = PhotoImage(file="images/portfolio.png")
        bg_label = Label(self, image=filename)
        bg_label.image = filename
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        left_frame = ttk.Frame(self)
        left_frame.place(x=10, y=100)

        right_frame = ttk.Frame(self)
        right_frame.place(x=500, y=100)

        global p_port_alpha
        label = ttk.Label(left_frame, text="This section is to make your own Portfolio ", font=controller.general_font)
        label.place(x=10,y=10)

        label_add = ttk.Label(left_frame, text="Add stocks to the portfolio below: ", font=controller.general_font,
                              justify="center")
        label_add.pack(side="top", fill="x", padx=150, pady=10)
        label_list = ttk.Label(left_frame)

        options1 = ['Select date to predict for', '1 day ahead', '5 days ahead', '10 days ahead', '20 days ahead']
        variable1 = tk.StringVar(left_frame)
        variable1.set(options1[1])

        date_dict = {'1 day ahead': '2018-05-24',
                     '5 days ahead': '2018-05-29',
                     '10 days ahead': '2018-06-02',
                     '20 days ahead': '2018-06-12',
                     '30 days ahead': '2018-06-22',
                     }

        def date_assign(event):
            global p_port_alpha
            p_port_alpha = str(date_dict.get(variable1.get(), "2018-05-24"))
            return

        w1 = ttk.OptionMenu(left_frame, variable1, *options1, command=date_assign)
        w1.pack()
        res = Label(left_frame, text="")

        def preserve(X_preserve):
            return X_preserve

        def calculate_alpha(df_company, end_date):
            global count_pf, res, p_port_alpha, val_alpha_port
            if (count_pf > 0):
                res.pack_forget()
                count_pf = 0
            res = Label(left_frame, text="Prediction for today= ", font=("arial", 10, "bold"), justify="center")
            res.pack()
            company = 'Portfolio'
            df_temp = df_company[company].values
            temp = df_temp[-1]

            date_vals = df_company.index
            date_arr = np.array([])

            for date in (date_vals):
                date_arr = np.append(date_arr, date.strftime("%d-%m-%y"))
            no_of_days = len(date_arr)

            d = np.array([])
            for i in range(1, (no_of_days + 1)):
                d = np.append(d, i)

            X = d[:]
            y = df_company[company].values
            X_preserve = preserve(X)
            X = X.reshape(-1, 1)
            l_model = linear_model.LinearRegression()
            l_model.fit(X, y)

            pred_added = (parse(p_port_alpha) - parse(end_date)).days
            pred_trading_days = pred_date(pred_added, pred_added)
            pred = no_of_days + pred_trading_days

            pred_value_1 = l_model.predict([[1]])
            pred_value_2 = l_model.predict([[pred]])
            val_alpha_port = (pred_value_2 / temp)
            print(val_alpha_port)
            pred_str = str(pred_value_2)
            alpha_str = str(val_alpha_port)

            res.config(text="Prediction = " + pred_str + "i.e." + alpha_str + "%")
            count_pf += 1
            return

        def add_stock_to_list(comp_str):
            """pressed button's value is inserted into the end of the text area"""
            global folio_set
            folio_set.add(comp_str)
            return

        def show_folio():
            global folio_set, folio_list, count_show_folio, label_list
            if (count_show_folio > 0):
                label_list.pack_forget()
                count_show_folio = 0
            folio_list = list(folio_set)
            print()
            folio_str = ', '.join(folio_list)
            label_list = ttk.Label(left_frame, text="My Stocks:  ", font=("arial", 10, "bold"), justify="center")
            label_list.config(text="My Stocks: " + folio_str)
            label_list.pack()
            count_show_folio += 1
            return

        def clear_folio():
            global folio_list, folio_set, count_show_folio
            folio_list[:] = []
            folio_set.clear()
            show_folio()
            return

        def plot_data(df_comp):
            global count_cs, bottom
            if (count_cs > 0):
                bottom.destroy()
                count_ss = 0

            bottom = ttk.Label(right_frame)
            bottom.grid(column=0, row=1)

            f1 = Figure(figsize=(8, 4), dpi=100)
            axes = f1.add_subplot(111)
            axes.plot(df_comp)
            axes.set_xlabel('Trading Days -->')
            axes.set_ylabel('Normalized Price -->')
            axes.set_title("Our portfolio in comparison to market ")
            label = ['SPY', 'Portfolio']
            axes.legend(label, loc=9)

            canvas = FigureCanvasTkAgg(f1, master=bottom)
            canvas.draw()  # canvas.show()
            canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
            canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

            button3 = ttk.Button(bottom, text="Clear ",
                                 command=lambda: bottom.destroy())
            button3.pack()
            count_cs += 1

        def get_data_portfolio():
            global folio_list

            start_date = '2018-01-01'
            end_date = '2018-05-23'
            length_folio = len(folio_list)
            if (length_folio == 0):
                return
            folio_list1 = []
            weight = 1 / length_folio
            for x in folio_list:
                folio_list1.append(x)
            print(folio_list1)
            df = get_data(folio_list1, start_date, end_date)
            df_SPY = df.ix[start_date:end_date, ['SPY']]
            print(folio_list)
            df_sliced_company = df.ix[start_date:end_date, folio_list]
            df_normalized_company = normalize_data(df_sliced_company)
            df_normalized_SPY = normalize_data(df_SPY)

            df_normalized_company[df_normalized_company.select_dtypes(include=['number']).columns] *= weight
            s_portfolio = df_normalized_company.sum(axis=1)
            df_portfolio = s_portfolio.to_frame()
            df_portfolio1 = df_portfolio
            df_portfolio = pd.DataFrame(df_portfolio, columns=['nn'])
            df_portfolio = df_portfolio1.join(df_portfolio, how='inner')
            df_portfolio = df_portfolio.rename(columns={0: 'Portfolio'})
            df_portfolio = df_portfolio.ix[start_date: end_date, ['Portfolio']]
            calculate_alpha(df_portfolio, end_date)
            df_portfolio = df_normalized_SPY.join(df_portfolio, how='inner')

            plot_data(df_portfolio)

            return

        ttk.Button(left_frame, text="Google", width=25, command=lambda: add_stock_to_list('GOOG')).pack()
        ttk.Button(left_frame, text="Apple", width=25, command=lambda: add_stock_to_list('AAPL')).pack()
        ttk.Button(left_frame, text="IBM", width=25, command=lambda: add_stock_to_list('IBM')).pack()
        ttk.Button(left_frame, text="Amazon", width=25, command=lambda: add_stock_to_list('AMZN')).pack()
        ttk.Button(left_frame, text="Netflix", width=25, command=lambda: add_stock_to_list('NFLX')).pack()
        ttk.Button(left_frame, text="Facebook", width=25, command=lambda: add_stock_to_list('FB')).pack()
        ttk.Button(left_frame, text="Tesla", width=25, command=lambda: add_stock_to_list('TSLA')).pack()
        ttk.Button(left_frame, text="Show my stocks", width=25, command=show_folio).pack(pady=2)
        ttk.Button(left_frame, text="Show portfolio vs Market \nfor equal Allocations ", width=25,
                   command=get_data_portfolio).pack(pady=2)
        ttk.Button(left_frame, text="Clear stocks from Portfolio", width=25, command=clear_folio).pack(pady=2)

        button2 = ttk.Button(left_frame, text="Go back to Active trading page", width=30,
                             command=lambda: controller.show_frame("ActiveTrading"))
        button2.pack(pady=1)

        button = ttk.Button(left_frame, text="Go back to home page", width=30,
                            command=lambda: controller.show_frame("WelcomePage"))
        button.pack(pady=1)


class PassiveTrading(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        filename = PhotoImage(file="images/passive.png")
        bg_label = Label(self, image=filename)
        bg_label.image = filename
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        left_frame = Frame(bg_label, bg="#354562")
        left_frame.grid(row=0, column=0, padx=50, pady=100)

        right_frame = Frame(bg_label, bg="#354562")
        right_frame.grid(row=0, column=1, padx=20, pady=100)

        label = tk.Label(left_frame, text="Long term Investment", font=controller.general_font, justify="center",
                         bg="#354562", fg="white", )
        label.pack(side="top", fill="x", padx=150, pady=10)

        OPTIONS = ["Select Company", "SPY", "Google", "Apple", "IBM", "Amazon", "Netflix", "Facebook", "Tesla"]  # etc

        COMPANY_LIST = {"SPY": "SPY",
                        "Google": "GOOG",
                        "Apple": "AAPL",
                        "IBM": "IBM",
                        "Amazon": "AMZN",
                        "Netflix": "NFLX",
                        "Facebook": "FB",
                        "Tesla": "TSLA"
                        }

        variable = tk.StringVar(left_frame)
        variable.set(OPTIONS[0])  # default value
        bottom = ttk.Label(right_frame)

        def plot_data(df):
            global count_pt, bottom
            if (count_pt > 0):
                bottom.destroy()

            bottom = ttk.Label(right_frame)
            bottom.grid(column=0, row=1)

            f1 = Figure(figsize=(8, 4), dpi=100)
            axes = f1.add_subplot(111)
            axes.plot(df)
            axes.set_xlabel('Trading Days since 2012-->')
            axes.set_ylabel('Price in dollars-->')
            axes.set_title("Stock Pricing upto the present day ")

            axes.legend(loc='center')
            canvas = FigureCanvasTkAgg(f1, master=bottom)
            canvas.draw()  # canvas.show()
            canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

            canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
            label_showing = ttk.Label(bottom, text="Showing data from the year 2012-2018 ",
                                      font=controller.general_font, justify='center')

            button3 = ttk.Button(bottom, text="Clear ",
                                 command=lambda: bottom.destroy())
            button3.pack()
            label_showing.pack()
            count_pt += 1

        def option_selection_menu(event):
            company = str(COMPANY_LIST.get(variable.get(), "SPY"))
            start_date = '2012-05-24'
            end_date = '2018-01-30'
            df = get_data([company], start_date, end_date)
            df_sliced = slice_data(df, start_date, end_date, company)
            rmean, rstddev = get_rolling(df_sliced, 20)
            plot_data(rmean)
            return

        w = ttk.OptionMenu(left_frame, variable, *OPTIONS, command=option_selection_menu)
        # w["menu"].config(bg="#354562")
        w.pack()

        button_pred = ttk.Button(left_frame, text="Predict prices for the next year",# bg="#354562", fg="white",
                                command=lambda: controller.show_frame("PredictLongTerm"))
        button_pred.pack()

        button = ttk.Button(left_frame, text="Go back to home page",# bg="#354562", fg="white",
                           command=lambda: controller.show_frame("WelcomePage"))
        button.pack()


class ShowStocks(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        left_frame = Frame(self, bg="gainsboro")
        left_frame.grid(row=0, column=0, padx=100, pady=100)
        right_frame = Frame(self)
        right_frame.grid(row=0, column=1, padx=20, pady=100)
        label = ttk.Label(left_frame, text="Select the stocks below.", font=controller.title_font)
        label.pack(side="top", fill="x", padx=10, pady=10)
        button = ttk.Button(left_frame, text="Go back to home page",
                            command=lambda: controller.show_frame("WelcomePage"))
        button.pack()

        OPTIONS = ["Select Company", "SPY", "Google", "Apple", "IBM", "Amazon", "Netflix", "Facebook", "Tesla"]  # etc

        COMPANY_LIST = {"SPY": "SPY",
                        "Google": "GOOG",
                        "Apple": "AAPL",
                        "IBM": "IBM",
                        "Amazon": "AMZN",
                        "Netflix": "NFLX",
                        "Facebook": "FB",
                        "Tesla": "TSLA"
                        }
        variable = tk.StringVar(left_frame)
        variable.set(OPTIONS[0])  # default value

        options1 = ['Select start date', '1 month data', '2 months data', '3 months data', '6 months data']
        variable1 = tk.StringVar(left_frame)
        variable1.set(options1[0])

        st_date_dict = {
            '1 month data': '2018-04-23',
            '2 months data': '2018-03-23',
            '3 months data': '2018-02-23',
            '6 months data': '2017-11-23',
        }

        def date_assign(event):
            global start_ss
            start_ss = str(st_date_dict.get(variable1.get(), "2018-04-23"))
            return

        bottom = ttk.Label(right_frame)

        def plot_data(df, rmean, upper, lower, company):
            global count_ss, bottom
            if (count_ss > 0):
                bottom.pack_forget()
                count_ss = 0

            bottom = ttk.Label(right_frame)
            bottom.pack()

            f1 = Figure(figsize=(8, 4), dpi=100)
            axes = f1.add_subplot(111)
            axes.plot(df)
            axes.plot(rmean)
            axes.plot(upper)
            axes.plot(lower)
            label = [company, 'Rolling mean', 'Upper band', 'Lower band']
            axes.set_xlabel('Trading Days since Jan 2018-->')
            axes.set_ylabel('Price -->')
            axes.set_title("Stock Pricing upto the present day ")
            axes.legend(label, loc='upper left')
            canvas = FigureCanvasTkAgg(f1, master=bottom)
            canvas.draw()  # canvas.show()
            canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

            canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

            label_showing = ttk.Label(bottom, text="Showing data from the year 2017-2018 ",
                                      font=controller.general_font, justify='center')

            button3 = ttk.Button(bottom, text="Clear ",
                                 command=lambda: bottom.destroy())
            button3.pack()
            label_showing.pack()
            count_ss += 1

        def option_selection_menu(event):
            global start_ss
            company = str(COMPANY_LIST.get(variable.get(), "SPY"))
            end_ss = '2018-05-23'
            df = get_data([company], start_ss, end_ss)
            df_sliced = slice_data(df, start_ss, end_ss, company)
            if (start_ss == '2018-04-23'):
                window = 7
            elif (start_ss == '2018-03-23'):
                window = 15
            else:
                window = 20
            rmean, rstd = get_rolling(df_sliced, window)
            upper_band, lower_band = get_ballinger_bands(rmean, rstd)
            plot_data(df_sliced, rmean, upper_band, lower_band, company)
            return

        w1 = ttk.OptionMenu(left_frame, variable1, *options1, command=date_assign)
        w1.pack()
        w = ttk.OptionMenu(left_frame, variable, *OPTIONS, command=option_selection_menu)
        w.pack()


class CompareStocks(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=100, pady=100)
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, padx=20, pady=100)
        label = ttk.Label(left_frame, text="Select the stocks below.", font=controller.title_font, justify='center')
        label.pack(side="top", fill="x", padx=10, pady=10)
        button = ttk.Button(left_frame, text="Go back to home page",
                            command=lambda: controller.show_frame("WelcomePage"))
        button.pack()

        OPTIONS = ["Select Company to compare ", "Google", "Apple", "IBM", "Amazon", "Netflix", "Facebook",
                   "Tesla"]  # etc

        COMPANY_LIST = {"Google": "GOOG",
                        "Apple": "AAPL",
                        "IBM": "IBM",
                        "Amazon": "AMZN",
                        "Netflix": "NFLX",
                        "Facebook": "FB",
                        "Tesla": "TSLA"
                        }
        variable = tk.StringVar(left_frame)
        variable.set(OPTIONS[0])  # default value
        bottom = ttk.Label(right_frame)

        def plot_data(df_comp, company):
            axes = f1.add_subplot(111)
            axes.plot(df_comp)
            axes.set_xlabel('Trading Days since 2012-->')
            axes.set_ylabel('Price -->')
            axes.set_title("Stock Pricing upto the present day ")
            label = ['SPY', company]
            axes.legend(label, loc=9)

        def option_selection_menu(event):
            company = str(COMPANY_LIST.get(variable.get(), "GOOG"))
            start_date = '2014-03-18'
            end_date = '2018-03-18'
            df_stock = get_data([company], start_date, end_date)

            df_norm = normalize_data(df_stock)
            plot_data(df_norm, company)
            return

class DailyReturns(ttk.Frame):

    def __init__(self, parent, controller):
        OPTIONS = ["Select Company ", "Google", "Apple", "IBM", "Amazon", "Netflix", "Facebook",
                   "Tesla"]  # etc

        COMPANY_LIST = {"Google": "GOOG",
                        "Apple": "AAPL",
                        "IBM": "IBM",
                        "Amazon": "AMZN",
                        "Netflix": "NFLX",
                        "Facebook": "FB",
                        "Tesla": "TSLA"
                        }
        variable = tk.StringVar(left_frame)
        variable.set(OPTIONS[0])  # default value

        bottom = ttk.Label(right_frame)

        def plot_data(df_comp, company):
            axes = f1.add_subplot(111)
            axes.plot(df_comp)
            axes.set_xlabel('Trading Days since 2018-04-23 -->')
            axes.set_ylabel('Price -->')
            axes.set_title("Stock Pricing upto the present day ")
            axes.legend(['SPY', company], loc=9)

        def create_label(s_ratio, company):
            global count_sr, res_daily
            if (count_sr > 0):
                res_daily.destroy()
                count_sr = 0
            res_daily = Label(left_frame, text="Sharpe ratio: ", font=("arial", 10, "bold"), justify="center")
            res_daily.pack()

            s_r_str_spy = str(s_ratio['SPY'])
            s_r_str_comp = str(s_ratio[company])
            res_daily.config(text="Sharpe ratio:\n" + "SPY: " + s_r_str_spy + "\n" + company + ": " + s_r_str_comp)
            count_sr += 1

        def option_selection_menu(event):
            company = str(COMPANY_LIST.get(variable.get(), "GOOG"))
            start_date = '2018-04-23'
            end_date = '2018-05-23'
            df_stock = get_data([company], start_date, end_date)
            df_daily = compute_daily_returns(df_stock)
            plot_data(df_daily, company)
            sharperatio = sharpe_ratio(df_daily)
            create_label(sharperatio, company)
            print(sharperatio)
            return

class PredictLongTerm(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        left_frame = ttk.Frame(self)
        # left_frame.place(x=400, y=100)
        left_frame.grid(row=0, column=0, padx=100, pady=100)
        right_frame = ttk.Frame(self)
        # right_frame.place(x=400,y=100)
        right_frame.grid(row=0, column=1, padx=20, pady=100)
        label = ttk.Label(left_frame, text="Select the stocks below.", font=controller.title_font, justify='center')
        label.pack(side="top", fill="x", padx=10, pady=10)
        button1 = ttk.Button(left_frame, text="Go back to Passive trading page",
                             command=lambda: controller.show_frame("PassiveTrading"))
        button1.pack()
        button = ttk.Button(left_frame, text="Go back to home page",
                            command=lambda: controller.show_frame("WelcomePage"))
        button.pack()

        OPTIONS = ["Select Company to compare ", "Google", "Apple", "IBM", "Amazon", "Netflix", "Facebook",
                   "Tesla"]  # etc

        COMPANY_LIST = {"Google": "GOOG",
                        "Apple": "AAPL",
                        "IBM": "IBM",
                        "Amazon": "AMZN",
                        "Netflix": "NFLX",
                        "Facebook": "FB",
                        "Tesla": "TSLA"
                        }
        variable = tk.StringVar(left_frame)
        variable.set(OPTIONS[0])  # default value
        bottom = ttk.Label(right_frame)

        def plot_data(X, Y, company, X_df, y_df):
            global count_plt, bottom
            if (count_plt > 0):
                bottom.destroy()
                count = 0

            bottom = ttk.Label(right_frame)
            bottom.grid(column=0, row=1)

            f1 = Figure(figsize=(8, 3.5), dpi=100)
            axes = f1.add_subplot(111)
            axes.plot(X_df, y_df)
            axes.plot(X, Y)
            axes.set_xlabel("Days starting from 2012-05-23 to 2018-05-19")
            axes.set_ylabel("Prices")
            axes.set_title("" + company + "'s 6 years data with next year prediction")
            axes.legend([company, 'prediction slope'], loc=9)
            canvas = FigureCanvasTkAgg(f1, master=bottom)
            canvas.draw()  # canvas.show()
            canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

            button3 = ttk.Button(bottom, text="Clear ",
                                 command=lambda: bottom.destroy())
            button3.pack()
            count_plt += 1

        def preserve(X_preserve):
            return X_preserve

        def calculate_alpha(df_company, company, end_date):
            global count_plt, res
            if (count_plt > 0):
                res.pack_forget()
                count_plt = 0
            res = Label(left_frame, text="Predicted value= ", font=("arial", 10, "bold"), justify="center")
            res.pack()

            date_vals = df_company.index

            date_arr = np.array([])

            for date in (date_vals):
                date_arr = np.append(date_arr, date.strftime("%d-%m-%y"))
            no_of_days = len(date_arr)
            d = np.array([])

            for i in range(1, (no_of_days + 1)):
                d = np.append(d, i)

            X = d[:]
            y = df_company[company].values
            X_preserve = preserve(X)
            X = X.reshape(-1, 1)
            l_model = linear_model.LinearRegression()
            l_model.fit(X, y)
            p = "2019-05-24"
            pred_added = (parse(p) - parse(end_date)).days
            print("Before : ", pred_added)

            # pred_trading_days = pred_date(pred_added, pred_added)
            pred = no_of_days + pred_added
            pred_value_1 = l_model.predict([[1]])
            pred_value_2 = l_model.predict([[pred]])
            pred_str = str(pred_value_2)
            df_temp = df_company[company].values
            temp = df_temp[-1]
            print(type(temp))
            alpha = (pred_value_2 / temp)
            alpha_str = str(alpha)
            res.config(text="Predicted value = " + pred_str + "\ni.e. " + alpha_str + "% of present value")
            # alpha_count += 1
            plot_data([1, pred], [pred_value_1, pred_value_2], company, X_preserve, y)
            count_plt += 1
            return

        def option_selection_menu(event):
            start_date = '2012-05-23'
            end_date = '2018-05-23'
            company = str(COMPANY_LIST.get(variable.get(), "GOOG"))
            # start_date = '2015-05-23'
            # end_date = '2018-05-23'
            df_stock = get_data([company], start_date, end_date)
            df_stock_sliced = slice_data(df_stock, start_date, end_date, company)
            calculate_alpha(df_stock_sliced, company, end_date)
            return

        w = ttk.OptionMenu(left_frame, variable, *OPTIONS, command=option_selection_menu)
        w.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.state('zoomed')
    app.mainloop()

