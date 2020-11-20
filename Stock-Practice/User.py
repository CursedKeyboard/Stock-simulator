import sqlite3
from typing import List
import dearpygui.core as dp

class User():
    """ A user in the program """

    def __init__(self, file_name: str):
        self.load_data(file_name)
        self.file = file_name
        dp.log(f"Finished loading user data")
    
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

        user_data = conn.execute("SELECT * FROM user_data")
        self.start_funds = user_data[0]
        self.current_balance = user_data[1]
    
    def buy_share(self, share: Share, amount) -> None:
        """ Buy <amount> shares for the User """
        self.current_balance -= share.get_price() * amount
        conn = sqlite3.connect(self.file)
        conn.execute


    


