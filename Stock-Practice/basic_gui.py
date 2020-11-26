import dearpygui.core as gg
from dearpygui.simple import *
from database_functions import create_database, get_user_data
import os
from User import User
import yahoo_fin.stock_info as yfs
from typing import Dict
import datetime

gg.show_logger()
gg.set_log_level(gg.mvTRACE)
gg.log("trace message")
gg.log_debug("debug message")
gg.log_info("info message")
gg.log_warning("warning message")
gg.log_error("error message")


def create_new_user_gui():
    with window("Main"):
        gg.add_input_text(
            name="##user_name",
            hint="User name",
            tip="Your username",
            parent="Main"
            )
        gg.add_input_int(
            name="##balance_input",
            default_value=500,
            tip="Your starting balance",
            parent="Main"
            )

        def create_new_user_data(sender, data) -> None:
            initial_data = {
            "User Name": gg.get_value("##user_name"),
            "Start Balance": gg.get_value("##balance_input")
            }

            if not initial_data["User Name"].isalpha():
                gg.add_label_text("Error", color=[255, 0, 0],
                                  before="##balance_input", label="Username must be alphabetical")
                gg.log_error("User-name must be only alphabets")
                return
            elif initial_data["User Name"] + ".db" in os.listdir():
                gg.add_label_text("Error", color=[255, 0, 0],
                                  before="##balance_input",label="Username already exists!")
                gg.log_error("User-name must be unique")
                return

            if initial_data["Start Balance"] <= 0:
                gg.add_label_text("Error_start_balance",
                                  color=[255, 0, 0], before="Proceed",label="Balance must be greater than 0$")
                gg.log_error("Balance must be greater than 0$!")
                return
            
            create_database(initial_data["User Name"] + ".db", initial_data["Start Balance"])
            gg.delete_item("Main")
            initial_screen()
        
        gg.add_button("Proceed", callback=create_new_user_data)


def initial_screen():
    with window("Main"):

        def change_to_choosing_user(sender, data):
            gg.delete_item("Main")
            choose_user_screen()

        gg.add_button("Load", callback=change_to_choosing_user)

        def change_to_new_user(sender, data):
            gg.delete_item("Main")
            create_new_user_gui()

        gg.add_button("New", callback=change_to_new_user)


def choose_user_screen():

    with window("Choose User",width=600):

        gg.add_separator()
        with managed_columns("row", 5):
            gg.add_text("USERNAME")
            gg.add_text("STARTING BALANCE")
            gg.add_text("CURRENT BALANCE")
            gg.add_text("DATE CREATED")
            gg.add_text("")
        gg.add_separator()

        def load_user(sender, data):
            user = User(data["file_name"] + ".db")
            gg.delete_item("Choose User")
            MainGui(user)

        count = 1
        for file in os.listdir():
            if(file[-3:]) == ".db":
                user_name = file[:-3]
                initial_balance, current_balance, date_created = get_user_data(file)
                with managed_columns(f"row{count}", 5):
                    gg.add_text(f"{user_name}")
                    gg.add_text(f"{initial_balance}")
                    gg.add_text(f"{current_balance}")
                    gg.add_text(f"{date_created}")
                    gg.add_button(f"load {user_name}", callback=load_user, callback_data={"file_name": user_name})
                gg.add_separator()
                count += 1


class MainGui:
    
    main_tickers = ["AAPL", "MSFT", "AMD", "TSLA"]

    def __init__(self, user: User):
        self.user = user
        self.dashboard_stocks()

    def menu(self, curr_window_name, *args):
        def change_to_window(sender, data):
            scene = data["Scene Function"]
            gg.delete_item(curr_window_name)
            scene()

        with menu_bar("Menu"):
            gg.add_menu_item("User", enabled=not args[0])
            gg.add_menu_item("Stocks", enabled=not args[1], callback=change_to_window,
                             callback_data={"Scene Function": self.dashboard_stocks})
            gg.add_menu_item("My Stocks", enabled=not args[2])
            gg.add_menu_item("Watchlist", enabled=not args[3])

    def dashboard_stocks(self):
        with window("Dashboard", width=500, height=500):
            self.menu("Dashboard", False, True, False, False)
            gg.add_separator()
            with managed_columns("headers", 3):
                gg.add_text("TICKER")
                gg.add_text("LIVE PRICE")
                gg.add_text("MY SHARES")
            for ticker in self.main_tickers:
                gg.add_separator()
                with managed_columns(ticker + "col", 3):
                    live_price = round(yfs.get_live_price(ticker), 3)
                    gg.add_button(ticker, callback=self.info_single_stock, callback_data={"Ticker": ticker, 
                    "Previous Window": "Dashboard"})
                    gg.add_text(str(live_price))
                    try:
                        gg.add_text(str(self.user.share_quantity[ticker]))
                    except KeyError:
                        gg.add_text("0")
            gg.add_separator()

            def go_to_single_stock_info(sender, data):
                input_ticker = gg.get_value(sender)
                data["Ticker"] = input_ticker
                if str(yfs.get_live_price(input_ticker)) == 'nan':
                    set_item_label("Search ticker input", label=f"No ticker called {input_ticker} found")
                    return
                else:
                    set_item_label("Search ticker input", label="Loading...")
                    self.info_single_stock(sender, data)

            gg.add_input_text(name="Search ticker input", width=100,
                              default_value='AAPL', tip="Search for a stock ticker", label="Get Ticker Info",
                              callback=go_to_single_stock_info,
                              callback_data={"Previous Window": "Dashboard"}, on_enter=True, uppercase=True)

    def info_single_stock(self, sender, data: Dict[str, str]):
        gg.delete_item(data["Previous Window"])
        ticker = data["Ticker"]
        with window(ticker + "##window", width=500, height=500, no_scrollbar=False):
            self.menu(ticker + "##window", False, False, False, False)
            ticker_data = yfs.get_quote_table(ticker, dict_result=True)
            date_time = datetime.datetime.now()
            time = date_time.time()
            date = date_time.date()
            price = round(ticker_data["Quote Price"], 2)
            with group("heading", horizontal=True):
                with group("day_info"):
                    gg.add_text("Date: " + str(date), color=[255, 0, 0])
                    gg.add_text("Time: " + str(time), color=[255, 0, 0])
                try:
                    gg.add_label_text("Current Shares",
                                      label=f"Number of shares: {self.user.share_quantity[ticker]}",
                                      color=[0, 255, 0])
                except KeyError:
                    gg.add_label_text("Current Shares",
                                      label=f"Number of shares: 0",
                                      color=[0, 255, 0])
            with menu_bar("local_info"):
                gg.add_menu_item("ticker", label=ticker, enabled=False)
                gg.add_label_text("Current Balance", label=f"Current Balance: {self.user.current_balance}",
                                  color=[255, 0, 0])

            gg.add_separator()
            gg.add_text("Today")
            gg.add_separator()
            with managed_columns("day_info_ticker", columns=3):
                gg.add_text("Last close: " + str(ticker_data["Previous Close"]))
                gg.add_text("Open price: " + str(ticker_data["Open"]))
                gg.add_text("Current price: " + str(price))
            gg.add_separator()

            with group("Extra info", horizontal=True):
                with group("Extra Info##1"):
                    gg.add_text("Volume: " + str(ticker_data["Volume"]), bullet=True)
                    gg.add_text("Market Cap: " + str(ticker_data["Market Cap"]), bullet=True)
            
                with group("Extra info##2"):
                    gg.add_text("52 Week Range: " + str(ticker_data["52 Week Range"]), bullet=True)
                    one_year_estimate = ticker_data["1y Target Est"]
                    if one_year_estimate > price:
                        percent_change = round((one_year_estimate / price) * 10, 2)
                        colour = [0, 255, 0]
                    else:
                        percent_change = round((price / one_year_estimate) * 10, 2)
                        colour = [255, 0, 0]
                    with group("1Y estimate", horizontal=True):
                        gg.add_text(f"1y Target Estimate: {ticker_data['1y Target Est']} |", bullet=True)
                        gg.add_text(f"{percent_change}%", color=colour)

            gg.add_spacing(count=5)

            # Table of share data on first day of each month since 365 days ago
            date_data_since = date - datetime.timedelta(365)
            table_monthly_interval_data = yfs.get_data(ticker, start_date=date_data_since, interval="1mo")
            gg.add_table("monthly_data", headers=["date"] + [header for header in table_monthly_interval_data])
            for date_index in table_monthly_interval_data.index:
                list_values = [str(date_index)[:10]]
                list_values.extend(list(table_monthly_interval_data.loc[date_index]))
                for i in range(len(list_values)):
                    if type(list_values[i]) == str:
                        continue
                    else:
                        list_values[i] = str(round(list_values[i], 3))
                gg.add_row("monthly_data", list_values)

            gg.add_spacing(count=2)

            def make_plot():
                date_data_since = date - datetime.timedelta(30)
                scatter_plot_weekly_data = yfs.get_data(ticker, start_date=date_data_since, interval="1d")
                indecis = [x for x in scatter_plot_weekly_data.index]
                start_date = indecis[0]
                x_axis = [(x - start_date).days for x in indecis]
                y_axis_max = [scatter_plot_weekly_data.loc[x]['high'] for x in indecis]
                y_axis_min = [scatter_plot_weekly_data.loc[x]['low'] for x in indecis]
                gg.add_plot("30 Day Price Fluctuation", height=300, scale_max=.5,
                            x_axis_name=f"Days since {start_date}", y_axis_name="Single share price")
                gg.add_scatter_series("30 Day Price Fluctuation", "Day High", x=x_axis, y=y_axis_max, size=3)
                gg.add_scatter_series("30 Day Price Fluctuation", "Day Low", x=x_axis, y=y_axis_min, marker=1, size=3)

                # Set initial plot view
                gg.set_plot_xlimits("30 Day Price Fluctuation", 0, 30)
                gg.set_plot_ylimits("30 Day Price Fluctuation", min(y_axis_min)*.97, max(y_axis_max)*1.03)
                gg.set_plot_ylimits_auto("30 Day Price Fluctuation")
                gg.set_plot_xlimits_auto("30 Day Price Fluctuation")

            make_plot()
            # Create purchase button and what not

            def purchase_stocks(sender, data):
                quantity = round(gg.get_value("Quantity"), 2)
                total_price = quantity * price
                gg.set_item_color("Message", style=1, color=[255, 0, 0])
                if self.user.current_balance < total_price:
                    set_item_label("Message", "Cannot purchase, insufficient funds")
                elif 0 >= total_price:
                    set_item_label("Message", "Must spend more than 0$")
                else:
                    set_item_label("Message", f"Purchase of {quantity} {ticker} shares at {price} made")
                    gg.set_item_color("Message", style=1, color=[0, 255, 0])
                    self.user.buy_share(quantity, price, ticker, str(date), str(time))
                    set_item_label("Current Balance", f"Current Balance: {self.user.current_balance}")
                    set_item_label("Current Shares", f"Number of shares: {self.user.share_quantity[ticker]}")

            with group("Buy Stock Group"):
                def get_dynamic_cost(sender, data):
                    # TODO dynamic colouring
                    cost = round(gg.get_value("Quantity") * price, 2)
                    set_item_label("Stock volume", f"Total Cost: {cost}")

                gg.add_input_float("Stock volume", default_value=0,
                                   width=100, source="Quantity", label="Total cost: 0",
                                   callback=get_dynamic_cost, on_enter=True)
                gg.add_label_text("Message", label="", color=[255, 0, 0])
                gg.add_button("Buy Shares", callback=purchase_stocks)


if __name__ == "__main__":
    gg.add_additional_font(f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/arial.ttf")
    initial_screen()
    gg.start_dearpygui()
