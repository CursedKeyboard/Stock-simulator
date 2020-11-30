import sqlite3
import datetime


def create_database(file_name: str, initial_funds: float):
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE shares_bought
        (purchaseid integer primary key, name text,date text,time text,price real,qty real)
        """
    )   
    
    c.execute(
        """CREATE TABLE data
        (start_funds real,balance real, date_created text)
        """
    )

    c.execute(
        """CREATE TABLE watchlist
        (ticker text UNIQUE, price_when_added real, date_added text)
        """)

    c.execute(
        """CREATE TABLE shares_sold
        (sellid integer primary key, ticker text, 
        qtysold real, price real, revenue real, date text, time text, sharebought integer, 
        FOREIGN KEY(sharebought) REFERENCES shares_bought(purchaseid))"""
    )
    c.execute("INSERT INTO data VALUES (?, ?, ?)", (initial_funds, initial_funds, str(datetime.date.today())))
    conn.commit()
    conn.close()


def get_user_data(file_name: str) -> tuple:
    """ Return user data from sql file """
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    initial_current_dateCreated = conn.execute("SELECT * FROM data").fetchone()
    c.close()
    return initial_current_dateCreated


def get_user_watchlist_data(file_name: str) -> tuple:
    """ Return user watchlist data """
    conn = sqlite3.connect(file_name)
    data = conn.execute("SELECT * FROM watchlist").fetchall()
    conn.close()
    return data

if __name__ == "__main__":
    create_database("test.db", 100)
    conn = sqlite3.connect("test.db")
    conn.execute("INSERT INTO shares VALUES ('MSFT','2020:11:19','11:43:23',35.4,100)")
    conn.execute("INSERT INTO shares VALUES ('MSFT','2020:11:19','10:43:23',35.4,100)")
    for share in conn.execute("SELECT * FROM shares ORDER BY date,time"):
        print(share)
    for data in conn.execute("SELECT * FROM data"):
        print(data)
    conn.close()

    get_user_data("test.db")