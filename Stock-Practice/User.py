import sqlite3
from typing import List
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
        self.share_by_name = {}
        for share in conn.execute("SELECT * FROM shares ORDER BY date"):
            share_name = share[0]
            if share_name in self.share_by_name:
                self.share_by_name[share_name].append(share[1:])
            else:
                self.share_by_name[share_name] = list(share[1:])

        user_data = conn.execute("SELECT * FROM data").fetchone()
        self.start_funds = user_data[0]
        self.current_balance = user_data[1]
        self.start_date = user_data[2]
    
    def buy_share(self, share, amount) -> None:
        """ Buy <amount> shares for the User """
        self.current_balance -= share.get_price() * amount
        conn = sqlite3.connect(self.file)
        conn.execute


    


