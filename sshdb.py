import sqlite3

conn = sqlite3.connect('ssh.db')
c = conn.cursor()


c.execute("""CREATE TABLE Buy (
            ID int,
            Code text,
            Status text,
            Data text
            )""")


c.execute("""CREATE TABLE Users (
            ID int,
            Name text,
            Username text,
            Account text,
            Host text
            )""")


c.execute("""CREATE TABLE Cache (
            Chat int,
            Status text
            )""")


c.execute("""CREATE TABLE Collector (
            ID int,
            Status text,
            Cache int,
            Hosts text
            )""")

c.execute("""CREATE TABLE Pay (
            ID int,
            Name text,
            Username text,
            Card int
            )""")

c.execute("INSERT INTO Pay (ID, Name, Username, Card) VALUES (?, ?, ?, ?)", (1, "Default", "None", 565000020002))
conn.commit()

c.execute("""CREATE TABLE Wallet (
            ID int,
            Name text,
            Username text,
            Wallet text,
            Crypto text
            )""")

c.execute("INSERT INTO Wallet (ID, Name, Username, Wallet, Crypto) VALUES (?, ?, ?, ?, ?)", (1, "Default", "None", "TAuhCY9PbmKw7gKgjKqkqQHmazNKUXHR26", "TRX"))
conn.commit()

c.execute("""CREATE TABLE Checked (
            ID int,
            Name text,
            Username text,
            Code text,
            Confirm text,
            Checked int
            )""")


c.execute("""CREATE TABLE Sellers (
            ID int,
            Name text,
            Username text,
            'limit' int
            )""")


c.execute("""CREATE TABLE Referrals (
            ID int,
            Name text,
            Username text,
            Referrals text
            )""")


c.execute("""CREATE TABLE Clients (
            ID int,
            Name text,
            Username text,
            Phone text,
            Balance int
            )""")


c.execute("""CREATE TABLE Sales (
            'date' text,
            count int
            )""")


c.execute("""CREATE TABLE Settings (
            ID int,
            Settings text
            )""")


settings = {
    "start": "سلام خوش اومدین",
    "list": "قیمتا به این صورته : \n\nسی روزه یک کاربر 50 گیگ  50 هزار تومن \n\n ....",
    "sponser": "None",
    "usd": 50000,
    "maximum": 30,
    "backup": 6,
    "auto_delete": 100,
    "buy": "on",
    "prices": [50000, 150000],
    "connections": [1, 2],
    "days": [30, 30],
    "traffic": [50, 100],
    "plus-traffic": [10, 20],
    "plus-prices": [20000, 35000],
    "proxy": "None",
    "referral": 5000,
    "card_buy": "off",
    "trx_buy": "on",
    "crypto_buy": "off"
}

c.execute("INSERT INTO Settings (ID, Settings) VALUES (?, ?)", (1, str(settings)))
conn.commit()
