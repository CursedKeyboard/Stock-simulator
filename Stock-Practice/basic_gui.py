import dearpygui.core as gg
from dearpygui.simple import *
from new_user import create_database, get_user_data
import os
import User
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
                gg.add_label_text("Error", color=(255, 0, 0),
                                  before="##balance_input",label="Username must be alphabetical")
                gg.log_error("User-name must be only alphabets")
                return
            elif initial_data["User Name"] + ".db" in os.listdir():
                gg.add_label_text("Error", color=(255, 0, 0),
                                  before="##balance_input",label="Username already exists!")
                gg.log_error("User-name must be unique")
                return

            if initial_data["Start Balance"] <= 0:
                gg.add_label_text("Error_start_balance",
                                  color=(255, 0, 0, 1), before="Proceed",label="Balance must be greater than 0$")
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

        # headers = ("USERNAME", "STARTING BALANCE", "CURRENT BALANCE", "DATE CREATED", "")
        # gg.add_table("files", headers=headers)
        gg.add_separator()
        with managed_columns("row", 5):
            gg.add_text("USERNAME")
            gg.add_text("STARTING BALANCE")
            gg.add_text("CURRENT BALANCE")
            gg.add_text("DATE CREATED")
            gg.add_text("")
        gg.add_separator()

        def load_user(sender, data):
            user = User.User(data["file_name"] + ".db")
            gg.delete_item("Choose User")
            MainGui(user)

        for file in os.listdir():
            count = 1
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


class MainGui():
    
    main_tickers = ["AAPL", "MSFT", "AMD", "TSLA"]

    def __init__(self, user: User.User):
        self.user = user
        self.dashboard_stocks()

    def menu(self, *args):
        with menu_bar("Menu"):
            gg.add_menu_item("User", enabled=not args[0])
            gg.add_menu_item("Stocks", enabled=not args[1])
            gg.add_menu_item("My Stocks", enabled =not args[2])
            gg.add_menu_item("Watchlist", enabled=not args[3])
            if len(args) == 5:
                gg.add_menu_item(args[4], enabled=False)

    def dashboard_stocks(self):
        with window("Dashboard", width=500, height=500):
            self.menu(False, True, False, False)
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
                        gg.add_text(str(self.user.share_by_name[ticker][-1]))
                    except KeyError:
                        gg.add_text("0")
            gg.add_separator()  

    def info_single_stock(self, sender, data: Dict[str, str]):
        gg.delete_item(data["Previous Window"])
        ticker = data["Ticker"]
        with window(ticker + "##window", width=500, height=500):
            self.menu(False, False, False, False, data["Ticker"])
            ticker_data = yfs.get_quote_table(ticker, dict_result=True)
            date_time = datetime.datetime.now()
            time = date_time.time()
            date = date_time.date()
            with group("day_info"):
                gg.add_text("Date: " + str(date), color=[255,0,0])
                gg.add_text("Time: " + str(time), color=[255,0,0])

            gg.add_separator()
            gg.add_text("Today")
            gg.add_separator()
            with managed_columns("day_info_ticker", columns=3):
                gg.add_text("Last close: " + str(ticker_data["Previous Close"]))
                gg.add_text("Open price: " + str(ticker_data["Open"]))
                gg.add_text("Current price: " + str(round(ticker_data["Quote Price"], 3)))
            gg.add_separator()

            with group("Extra info", horizontal=True):
                with group("Extra Info##1"):
                    gg.add_text("Volume: " + str(ticker_data["Volume"]), bullet=True)
                    gg.add_text("Market Cap: " + str(ticker_data["Market Cap"]), bullet=True)
            
                with group("Extra info##2"):
                    gg.add_text("52 Week Range: " + str(ticker_data["52 Week Range"]), bullet=True)
                    gg.add_text("1y Target Estimate: " + str(ticker_data["1y Target Est"]), bullet=True)

            gg.add_spacing(count=10)

            date_data_since = date - datetime.timedelta(365)
            table_monthly_interval_data = yfs.get_data(ticker, start_date=date_data_since, interval="1mo")
            gg.add_table("monthly_data", headers=["date"] + [header for header in table_monthly_interval_data])
            for date in table_monthly_interval_data.index:
                list_values = [str(date)[:10]]
                list_values.extend(list(table_monthly_interval_data.loc[date]))
                for i in range(len(list_values)):
                    if type(list_values[i]) == str:
                        continue
                    else:
                        list_values[i] = str(round(list_values[i], 3))
                gg.add_row("monthly_data", list_values)

            gg.add_spacing(count=2)
            price = ticker_data["Quote Price"]

            def purchase_stocks(sender, data):
                total_price = gg.get_value("Quantity") * price
                print(str(self.user.current_balance), str(total_price))
                if self.user.current_balance < total_price:
                    gg.add_text("Cannot purchase, insufficient funds", before="Buy Shares", color=[255,0,0])
                else:
                    self.user.buy_share(gg.get_value("Quantity"), price, ticker, str(date), str(time))

            def get_dynamic_cost(sender, data):
                cost = gg.get_value("Quantity") * price
                gg.delete_item("Cost: ")
                gg.add_label_text("Cost: ", label=f"Total cost:{cost}", parent="Stock amount buy")

            with group("Buy Stock Group"):
                with group("Stock amount buy", horizontal=True):
                    gg.add_input_float("##Stock volume", tip="Number of stocks you want to buy", default_value=0,
                                       width=100, source="Quantity")
                    gg.add_label_text("Cost: ", label="Cost: 0")
                    gg.set_render_callback(get_dynamic_cost)
                gg.add_button("Buy Shares", callback=purchase_stocks)


if __name__ == "__main__":
    initial_screen()

    gg.start_dearpygui()
