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


c.execute("""CREATE TABLE Tests (
            ID int,
            'date' text,
            Account text
            )""")


c.execute("""CREATE TABLE Redeem (
            Code text,
            Value int,
            kind text,
            Count int,
            UserIDs text,
            Timer int
            )""")


c.execute("""CREATE TABLE Payments (
            ID int,
            Name text,
            Username text,
            Payment text,
            Value int,
            Data text,
            Status text,
            Timer int
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
    "buy-traffic": "off",
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
    "crypto_buy": "off",
    "windows": "\nلینک دانلود برای ویندوز 🖥\n\n▫️Netmod ( SSH )\nhttps://sourceforge.net/projects/netmodhttp/\n\n ▫️Respite VPN ( SSH )\nhttps://sourceforge.net/projects/respite-vpn/\n\n ▫️Respite HTTP Injector + \nhttps://sourceforge.net/projects/http-injector-plus/",
    "ios": "\nلینک دانلود برای گوشی های آیفون 🍏\n⭐️NapsternetV ios 15.0+\nhttps://apps.apple.com/us/app/napsternetv/id1629465476\n\n⚪️HTTP Injector ios 15.0+\nhttps://apps.apple.com/us/app/http-injector/id1659992827\n\n⚪️Streisand ios 14.0 +\nhttps://apps.apple.com/us/app/streisand/id6450534064\n\n⚪️V2box ios 15.0 +\nhttps://apps.apple.com/us/app/v2box-v2ray-client/id6446814690\n ",
    "android": "\nلینک دانلود برای گوشی های اندروید 🤖\n\n⚪️NapsternetV Google play\nhttps://play.google.com/store/apps/details?id=com.napsternetlabs.napsternetv\n\n⚪️HTTP Injector Google play\nhttps://play.google.com/store/apps/details?id=com.evozi.injector&hl=en&gl=US\n\n⚪️HTTP Injector Lite Google play مناسب اندروید پایین 4.3\nhttps://play.google.com/store/apps/details?id=com.evozi.injector.lite\n\n⚪️NetMod Google play\nhttps://play.google.com/store/apps/details?id=com.netmod.syna&hl=en_US\n\n⚪️ARMod Google play \nhttps://play.google.com/store/apps/details?id=com.artunnel57",
    "mac": "\nلینک دانلود برای مک 🍎\n\n⭐️v2box macOS 11.0 +\nhttps://apps.apple.com/us/app/v2box-v2ray-client/id6446814690\n\n⭐️Streisand macOS 11.0 +\nhttps://apps.apple.com/us/app/streisand/id6450534064\n\n▫️SSH proxy macOS 10.9+\nhttps://apps.apple.com/us/app/ssh-proxy/id597790822?mt=12",
    "support": "None",
    "test": "off",
    "test-traffic": 256,
    "phone": "off",
    "irphone": "off",
    "seller_custom": "on",
    "seller_prices": [50000, 150000],
    "seller_connections": [1, 2],
    "seller_days": [30, 30],
    "seller_traffic": [50, 100],
    "seller_plus_traffic": [10, 20],
    "seller_plus_prices": [20000, 35000],
    "lang": "en",
    "invite": "off",
    "list_status": "on",
    "support_status": "on",
    "upgrade_days": "off",
    "dropbear": "off",
    "select_server_users": "off",
    "select_server_sellers": "off",
    "first_connect": "off",
    "delete_user": "off",
    "after_buy": "برای آموزش وصل شدن به سرویس دکمه پایینو بزنین",
    "info_service": "on",
    "notification": "on",
    "before_start_msg": "None",
    "password_method": "number",
    "password_length": 6,
    "plisio": "off",
    "plisio_API": "None",
    "buy_notification": "on",
    "phone_notification": "on",
    "server_archives": [],
    "tuic": "off",
    "online_access": "off",
    "default_password_status": "off",
    "default_password": "123456",
    "change_password": "on",
    "support_chat": "on",
    "addresses": {},
    "random_price": "off",
    "random_price_min": 100,
    "random_price_max": 1000,
    "zarinpal": "off",
    "zarinpal_address": "None",
    "idpay": "off",
    "idpay_address": "None",
    "nextpay": "off",
    "nextpay_address": "None",
    "filtering_checker_minutes": 30,
    "SSH_custom": {},
    "Maxium_servers": {},
    "tutorial_windows": "on",
    "tutorial_android": "on",
    "tutorial_ios": "on",
    "tutorial_mac": "on",
    "tutorial_custom": "off",
    "tutorial_custom_button_name": [],
    "tutorial_custom_button_data": [],
    "perfect_money": "off",
    "perfect_money_account_id": "None",
    "perfect_money_account_password": "None",
    "custom_tutorial_only_button": "off",
    "custom_tutorial_only_button_name": "آموزش خرید",
    "custom_tutorial_only_button_type": "text",
    "custom_tutorial_only_button_file_id": 0,
    "custom_tutorial_only_button_caption": "text",
    "invitation_limit": 10,
    "buy_only_customers": "off",
    "invitation_type": "money",
    "invitation_percentage": 10,
    "currency_usdt": "off",
    "notify_test_account": "on",
    "trx_caption": "",
    "card_caption": "",
    "server_custom_caption": {}

}

c.execute("INSERT INTO Settings (ID, Settings) VALUES (?, ?)", (1, str(settings)))
conn.commit()
