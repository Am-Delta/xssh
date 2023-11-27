import os
import re
import json
import sqlite3
from termcolor import colored
from random import randint
from pathlib import Path


if not os.path.exists('ssh'):
    os.makedirs('ssh')

if not os.path.exists('backup'):
    os.makedirs('backup')

if not os.path.exists('cache'):
    os.makedirs('cache')


new_dict = {}
file = "data.json"


def db_update():
    conn = sqlite3.connect('ssh.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Settings WHERE ID=:ID", {'ID': 1})
    records = cur.fetchall()
    s = records[0][1]
    s = s.replace("\'", "\"")
    p = re.compile('(?<!\\\\)\'')
    s = p.sub('\"', s)
    s = s.replace(u'\\xa0', u' ').replace(u"\u00A0", " ").replace(u"\\u", " ").replace(u'\\U', u' ')
    settings = json.loads(s, strict=False)
    if settings.get("phone", None) is None:
        add_dict = {
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
            "invite": "off"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()
    if settings.get("list_status", None) is None:
        add_dict = {
            "list_status": "on",
            "support_status": "on",
            "upgrade_days": "off",
            "dropbear": "off",
            "select_server_users": "off",
            "select_server_sellers": "off",
            "first_connect": "off",
            "after_buy": "برای آموزش وصل شدن به سرویس دکمه پایینو بزنین",
            "delete_user": "off"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()
    if settings.get("info_service", None) is None:
        add_dict = {
            "info_service": "on"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()
    if settings.get("notification", None) is None:
        add_dict = {
            "notification": "on",
            "before_start_msg": "None",
            "password_method": "number",
            "password_length": 6
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("plisio", None) is None:
        add_dict = {
            "plisio": "off",
            "plisio_API": "None",
            "buy_notification": "on",
            "server_archives": []
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("tuic", None) is None:
        add_dict = {
            "tuic": "off"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("phone_notification", None) is None:
        add_dict = {
            "phone_notification": "on"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("online_access", None) is None:
        add_dict = {
            "online_access": "off"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("default_password_status", None) is None:
        add_dict = {
            "default_password_status": "off",
            "default_password": "123456",
            "change_password": "on"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("support_chat", None) is None:
        add_dict = {
            "support_chat": "on",
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("addresses", None) is None:
        add_dict = {
            "addresses": {},
            "random_price": "off",
            "random_price_min": 100,
            "random_price_max": 1000,
            "zarinpal": "off",
            "zarinpal_address": "None",
            "idpay": "off",
            "idpay_address": "None",
            "nextpay": "off",
            "nextpay_address": "None"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("filtering_checker_minutes", None) is None:
        add_dict = {
            "filtering_checker_minutes": 30,
            "SSH_custom": {},
            "Maxium_servers": {},
            "tutorial_windows": "on",
            "tutorial_android": "on",
            "tutorial_ios": "on",
            "tutorial_mac": "on",
            "tutorial_custom": "off",
            "tutorial_custom_button_name": [],
            "tutorial_custom_button_data": []
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("perfect_money", None) is None:
        add_dict = {
            "perfect_money": "off",
            "perfect_money_account_id": "None",
            "perfect_money_account_password": "None"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("custom_tutorial_only_button", None) is None:
        add_dict = {
            "custom_tutorial_only_button": "off",
            "custom_tutorial_only_button_name": "آموزش خرید",
            "custom_tutorial_only_button_type": "text",
            "custom_tutorial_only_button_file_id": 0,
            "custom_tutorial_only_button_caption": "text"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("invitation_limit", None) is None:
        add_dict = {
            "invitation_limit": 10,
            "buy_only_customers": "off"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("invitation_type", None) is None:
        add_dict = {
            "invitation_type": "money",
            "invitation_percentage": 10,
            "currency_usdt": "off"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    if settings.get("notify_test_account", None) is None:
        add_dict = {
            "notify_test_account": "on",
            "trx_caption": "",
            "card_caption": "",
            "server_custom_caption": {}
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()

    try:
        cur.execute("SELECT * FROM Redeem")
        records = cur.fetchall()
    except sqlite3.OperationalError:
        cur.execute("""CREATE TABLE Redeem (
            Code text,
            Value int,
            kind text,
            Count int,
            UserIDs text,
            Timer int
            )""")

    try:
        cur.execute("SELECT * FROM Payments")
        records = cur.fetchall()
    except sqlite3.OperationalError:
        cur.execute("""CREATE TABLE Payments (
            ID int,
            Name text,
            Username text,
            Payment text,
            Value int,
            Data text,
            Status text,
            Timer int
            )""")
    try:
        cur.execute("SELECT * FROM Tests WHERE Account=:Account", {'Account': "user"})
    except sqlite3.OperationalError:
        name1 = "Account"
        cur.execute('''ALTER TABLE Tests ADD COLUMN ''' + name1 + ''' text''')
    conn.commit()
    cur.close()
    conn.close()


def fix_panel_txt():
    if os.stat("Pannels.txt").st_size != 0:
        with open("Pannels.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if "?" in lines[0]:
                return
        os.remove("Pannels.txt")
        with open("Pannels.txt", "a+", encoding="utf-8") as f:
            for line in lines:
                line = line.replace("\n", "")
                host = line.split("@")[0]
                username = line.split("@")[1].split(":")[0]
                password = line.split(":")[1]
                new_line = f"{host}:80@{username}:{password}?shahan:path&sshport:udgpw\n"
                f.writelines(new_line)


def fix_panel_txt_2():
    if os.stat("Pannels.txt").st_size != 0:
        with open("Pannels.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines[0].count("&") == 2:
                return
        os.remove("Pannels.txt")
        with open("Pannels.txt", "a+", encoding="utf-8") as f:
            for data in lines:
                data = data.replace("\n", "")
                host = data.split(":")[0]
                port = data.split("@")[0].split(":")[1]
                username = data.split("@")[1].split(":")[0]
                password = data.split("?")[0].split("@")[1].split(":")[1]
                panel = data.split("?")[1].split(":")[0]
                route_path = data.split("&")[0].split("?")[1].split(":")[1]
                sshport = data.split("&")[1].split(":")[0]
                udgpw = data.split("&")[1].split(":")[1]
                remark = host.split(".")[0]
                new_line = f"{host}:{port}@{username}:{password}?{panel}:{route_path}&{sshport}:{udgpw}&{remark}\n"
                f.writelines(new_line)


def run():
    if Path("Pannels.txt").is_file() is False:
        open("Pannels.txt", "w", encoding="utf-8")
    if Path("All.txt").is_file() is False:
        with open("All.txt", "a+") as f:
            f.writelines("1" + "\n")
    if Path("ssh.db").is_file() is False:
        os.system('python3 sshdb.py')
        print("Database Created, change the settings in the bot")
    if Path("backup.db").is_file() is True:
        os.remove("ssh.db")
        os.rename('backup.db', 'ssh.db')
        print(colored("\nBackup recoverd", 'blue'))
    fix_panel_txt()
    fix_panel_txt_2()
    db_update()
    print(colored("\nRunning the bot... if you see any issues run the command again.\n\nif you wanna stop the bot use this command:\n\npkill -9 python3 or pkill -9 python\n\nYou can now close the window.", 'white'))
    os.system('nohup python3 -u session-updater.py &')
    #os.system('nohup python3 -u backup-ssh.py &')
    os.system('nohup python3 -u bot.py &')
    if Path("sshdb.py").is_file() is True:
        os.remove('sshdb.py')


def options_set():
    print(colored("\nType admin id, if you want add multiple admins type like this: 123456 654321 789456", 'white'))
    while True:
        data = input("ids: ")
        if " " not in data:
            try:
                admin_id = [int(data)]
                break
            except:
                print(colored("[-] Error: Type the correct value only numbers", 'red'))
        else:
            admin_id = []
            for admin in data.split(" "):
                try:
                    admin_id.append(int(admin))
                    status = True
                except:
                    status = False
                    print(colored("[-] Error: Type the correct value only numbers", 'red'))
                    break
            if status is True:
                break

    print(colored("\nBot Token: ", 'white'))
    Token = input("")

    print(colored("\nif you want send your api_id or (default: n)", 'white'))
    while True:
        data = input(": ")
        if data == "n" or data == "":
            API_ID = ['27720937', "24467048"]
            API_HASH = ["5998e6087a8e2c2eadab9fc3c51d5444", "7e81e7df9b9b66deab287cb47bbc6d8a"]
            n = randint(0, 1)
            api_id = API_ID[n]
            api_hash = API_HASH[n]
            api = True
            break
        else:
            try:
                int(data)
                api_id = data
                api = False
                break
            except:
                print(colored("[-] Error: Type the correct value only numbers", 'red'))

    if api is False:
        print(colored("\napi_hash: ", 'white'))
        api_hash = input("")

    add_dict = {
        "admin": admin_id,
        "api_id": api_id,
        "api_hash": api_hash,
        "Token": Token
    }
    new_dict.update(add_dict)

    if Path(file).is_file() is True:
        os.remove(file)
        print(colored("\nData renewed", 'cyan'))

    with open(file, 'w') as outfile:
        json.dump(new_dict, outfile)
        print(colored("\nSaved data in " + file, 'cyan'))


if Path(file).is_file() is True:
    print(colored("\nThe old settings exist, Do you want to change the settings? send y to change (Default: n)", 'cyan'))
    job = input("")
    if job == 'y':
        options_set()
        run()
    else:
        run()
else:
    options_set()
    run()
