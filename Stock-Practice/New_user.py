import sqlite3

def create_database(file_name: str,initial_funds: float):
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE shares
        (name text,date text,time text,price real,qty real)
        """
    )   
    
    c.execute(
        """CREATE TABLE data
        (start_funds real,balance real)
        """
    )
    
    c.execute("INSERT INTO data VALUES (?, ?)", (initial_funds, initial_funds))
    conn.commit()
    conn.close()

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