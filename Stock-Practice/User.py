import sqlite3
import dearpygui.core as dp
import datetime


class User:
    """ A user in the program """

    def __init__(self, file_name: str):
        self.load_data(file_name)
        self.file = file_name
        dp.log(f"Finished loading user data")
    
    def __str__(self) -> str:
        """ Return a string representation of this User """
        s = ""
        s += "Shares: \n"
        for share_name in self.share_by_name:
            s += self.share_by_name[share_name] + "\n"
      
        s += "Starting funds: " + str(self.start_funds) + "\n"
        s += "Current funds: " + str(self.current_balance)
        return s

    def load_data(self, file_name: str):
        """
        Method to load user data in <self> using database provided by <file_name>. 
        
        Keyword Arguments:
        self -- The User instance data will be loaded into
        file_name -- The file name data will be read off of
        """
        conn = sqlite3.connect(file_name)
        dp.log(f"Established connection to {file_name}")
        self.share_by_name, self.share_quantity = {}, {}
        for share in conn.execute("SELECT * FROM shares_bought ORDER BY date"):
            share_name = share[1]
            share_data = list((share[0],) + share[2:])
            share_quantity = share_data[-1]
            self.update_share_map(share_name, share_data)
            self.update_share_count(share_name, share_quantity)
        dp.log("Loaded share data")

        user_data = conn.execute("SELECT * FROM data").fetchone()
        self.start_funds = user_data[0]
        self.current_balance = user_data[1]
        self.start_date = user_data[2]
        dp.log("Loaded user data")

        watchlist_data = conn.execute("SELECT * FROM watchlist")
        self.watchlist = {}
        for row in watchlist_data:
            ticker, price_when_added, date_added = row[0], row[1], row[2]
            self.add_to_watchlist(ticker, price_when_added, False, date_added)

        self.share_sold_map = {}
        sold_data = conn.execute("SELECT * FROM shares_sold")
        for row in sold_data:
            self.update_sold_share_map(row[0], row[1:])
        dp.log("Loaded sold shares data")

        conn.close()

    def buy_share(self, amount: float, price: float, ticker: str, date: str, time: str) -> None:
        """ Buy <amount> shares for the User """
        self.current_balance -= round(price * amount, 2)
        self.current_balance = round(self.current_balance, 2)
        share_data = (ticker, date, time, price, amount)

        conn = sqlite3.connect(self.file)
        conn.execute(""" INSERT INTO shares_bought(name, date, time, price, qty) VALUES (?, ?, ?, ?, ?)""", share_data)
        conn.execute(""" UPDATE data SET balance = ?""", (self.current_balance,))
        conn.commit()
        pid = \
            conn.execute(""" SELECT purchaseid FROM shares_bought WHERE date =? AND time=?""", (date, time)).fetchall()
        self.update_share_count(ticker, amount)
        share_map_data = list(pid[-1] + share_data[1:])
        self.update_share_map(ticker, share_map_data)

        conn.close()

    def add_to_watchlist(self, share_name: str, share_price: str, database: bool,
                         date_added: str = str(datetime.date.today())):
        """ Add <share_name> to the watchlist and update it accordingly """
        if share_name in self.watchlist:
            raise ValueError(f"{share_name} already in watchlist")
        else:
            self.watchlist[share_name] = (share_price, date_added)
            if database:
                conn = sqlite3.connect(self.file)
                conn.execute(" INSERT INTO watchlist VALUES (?, ?, ?)", (share_name, share_price, date_added))
                conn.commit()
                conn.close()

    def remove_from_watchlist(self, share_name):
        if share_name not in self.watchlist:
            raise KeyError(f"{share_name} not in watchlist!")
        else:
            self.watchlist.pop(share_name)
            conn = sqlite3.connect(self.file)
            conn.execute(" DELETE FROM watchlist WHERE ticker = (?)", (share_name,))

        conn = sqlite3.connect(self.file)
        conn.execute("DELETE FROM watchlist WHERE ticker = ?", (share_name,))
        conn.commit()
        conn.close()

    def update_share_count(self, share_name: str, share_count: float):
        """ Update the share count of a ticker accordingly"""
        if share_name in self.share_quantity:
            self.share_quantity[share_name] += share_count
            self.share_quantity[share_name] = round(self.share_quantity[share_name], 2)
        else:
            self.share_quantity[share_name] = share_count
            self.share_quantity[share_name] = round(self.share_quantity[share_name], 2)

    def update_share_map(self, share_name, share_data):
        """ Update the share map of a user's owned shares accordingly"""
        if share_name in self.share_by_name:
            self.share_by_name[share_name].append(share_data)
        else:
            self.share_by_name[share_name] = [share_data]

    def update_sold_share_map(self, sellid: int, data):
        """ Update the shares sold map of a user's sold shares """
        self.share_sold_map[sellid] = data

    def sell_share(self, ticker: str, purchaseid: int, qty: float, sell_price: float,
                   date: str = str(datetime.date.today()), time: str = str(datetime.datetime.now().time())):
        """
        Sell a User's <purchaseid> shares based on a certain quantity and sell price and record this
        into the database
        """
        revenue = round(qty * sell_price, 2)
        data = (ticker, qty, sell_price, revenue, date, time, purchaseid)
        conn = sqlite3.connect(self.file)
        conn.execute("""INSERT INTO shares_sold (ticker, qtysold, price, revenue, date, time, sharebought) 
        VALUES (?,?,?,?,?,?,?)""", data)
        sellid = conn.execute("""SELECT sellid FROM shares_sold WHERE date=? and time=?""", (date, time)).fetchone()
        self.update_sold_share_map(sellid, data)
        self.current_balance += revenue
        self.current_balance = round(self.current_balance, 2)
        conn.execute(""" UPDATE data SET balance = ?""", (self.current_balance,))
        self.update_share_count(ticker, -qty)li
        old_quantity = \
            conn.execute(""" SELECT qty FROM shares_bought WHERE purchaseid = ?""", (purchaseid,)).fetchone()[0]
        new_quantity = round(old_quantity - qty, 2)

        if new_quantity > 0:
            conn.execute("""UPDATE shares_bought SET qty = ?  WHERE purchaseid = ?""", (new_quantity, purchaseid))
            for share_buy in self.share_by_name[ticker]:
                if share_buy[0] == purchaseid:
                    share_buy[-1] = new_quantity
        else:
            conn.execute((""" DELETE FROM shares_bought WHERE purchaseid = ?"""), (purchaseid,))
            for i in range(len(self.share_by_name[ticker])):
                share_buy = self.share_by_name[ticker][i]
                if share_buy[0] == purchaseid:
                    self.share_by_name[ticker].pop(i)
                    if len(self.share_by_name[ticker]) == 0:
                        self.share_by_name.pop(ticker)
                    break

        conn.commit()
        conn.close()
