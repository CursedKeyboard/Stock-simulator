import sqlite3
from typing import List, Tuple
import dearpygui.core as dp


class User():
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
        for share in conn.execute("SELECT * FROM shares ORDER BY date"):
            share_name = share[0]
            share_data = share[1:]
            share_quantity = share_data[-1]
            self.update_share_map(share_name, share_data)
            self.update_share_count(share_name, share_quantity)

        user_data = conn.execute("SELECT * FROM data").fetchone()
        self.start_funds = user_data[0]
        self.current_balance = user_data[1]
        self.start_date = user_data[2]

    def buy_share(self, amount: float, price: float, ticker: str, date: str, time: str) -> None:
        """ Buy <amount> shares for the User """
        self.current_balance -= round(price * amount, 2)
        self.current_balance = round(self.current_balance, 2)
        share_data = (ticker, date, time, price, amount)

        conn = sqlite3.connect(self.file)
        conn.execute(""" INSERT INTO shares VALUES (?, ?, ?, ?, ?)""", share_data)
        print(conn.execute(""" SELECT balance FROM data """).fetchone())
        conn.execute(""" UPDATE data SET balance = ?""", (self.current_balance,))
        conn.commit()

        self.update_share_count(ticker, amount)
        self.update_share_map(ticker, share_data[1:])

        conn.close()

    def update_share_count(self, share_name: int, share_count: float):
        """ Update the share count of a ticker accordingly"""
        if share_name in self.share_quantity:
            self.share_quantity[share_name] += share_count
            self.share_quantity[share_name] = round(self.share_quantity[share_name], 2)
        else:
            self.share_quantity[share_name] = share_count
            self.share_quantity[share_name] = round(self.share_quantity[share_name], 2)

    def update_share_map(self, share_name, share_data: Tuple[str, str, str, float, float]):
        """ Update the share map of a user's owned shares accordingly"""
        if share_name in self.share_by_name:
            self.share_by_name[share_name].append(share_data)
        else:
            self.share_by_name[share_name] = [share_data]
