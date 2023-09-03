import os
import re
import ast
import sshx
import json
import sqlite3
import socket
import qrcode
import cryptocompare
from uuid import uuid4
from pathlib import Path
from time import time, sleep
from random import randint, choice
from pyrogram import Client, filters, enums
from pyrogram.errors import NotAcceptable, BadRequest
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

session = "run"

if Path(session + ".session").is_file() is True:
    try:
        os.remove(session + ".session")
    except:
        pass

with open("data.json", "r") as json_file:
    data_file = json.load(json_file)
    admin_id = data_file['admin']
    api_id = data_file['api_id']
    api_hash = data_file['api_hash']
    TOKEN = data_file['Token']


seller_id = [12345678]
folder = 'backup'
cache = [False]
backup = [False]
run_backup = [False]
Filtering_system = [False]
run_filtering = [False]
checked_filtering = []
checked_connections = []


app = Client(session, api_id, api_hash, bot_token=TOKEN)


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 0))
owners_port = int(s.getsockname()[1])
print("Running SSH bot on port ", owners_port)

#database
conn = sqlite3.connect('ssh.db', check_same_thread=False)
cur = conn.cursor()


old_hosts = []
cache_list = []
host_cache = []
text_cache = []


def sellers_id_add_list():
    seller_id.clear()
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Sellers")
            sellers = cur.fetchall()
            for i in range(len(sellers)):
                seller_id.append(sellers[i][0])
            break
        except:
            pass
sellers_id_add_list()


def Admin_Tools_keys():
    keyboard = [
        [InlineKeyboardButton("✔️چکر", callback_data='checker'), InlineKeyboardButton("📊آمار", callback_data='stats')],
        [InlineKeyboardButton("🖥اطلاعات سرور", callback_data='servers'), InlineKeyboardButton("⚫️ظرفیت سرورها", callback_data='full')],
        [InlineKeyboardButton("⛔️تست فیلترینگ", callback_data='Filtering')],
        [InlineKeyboardButton("🔴 غیر فعال کاربر", callback_data='disable'), InlineKeyboardButton("🟢 فعال کاربر", callback_data='enable')],
        [InlineKeyboardButton("🔄تمدید کاربر ", callback_data='update'), InlineKeyboardButton("🗑حذف اکانت", callback_data='remove')],
        [InlineKeyboardButton("👤اطلاعات اکانت", callback_data='userinfo'), InlineKeyboardButton("📄اکانت های کاربر", callback_data='userconfigs')],
        [InlineKeyboardButton("🚻ریست ترافیک", callback_data='TrfRes'), InlineKeyboardButton("➕افزایش ترافیک", callback_data='TrfPlus')],
        [InlineKeyboardButton("🔑تغییر پسورد اکانت", callback_data='ADPASS')],
        [InlineKeyboardButton("🛠ساخت اکانت یوزر تلگرام", callback_data='create'), InlineKeyboardButton("🛠ساخت اکانت", callback_data='Create_none')],
        [InlineKeyboardButton("📦ارسال پیام همگانی", callback_data='message'), InlineKeyboardButton("💲فروشنده ها", callback_data='sellers')],
        [InlineKeyboardButton("⚙️تنظیمات", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def Seller_Tools_keys():
    keyboard = [
        [InlineKeyboardButton("📊آمار", callback_data='stats'), InlineKeyboardButton("👤اطلاعات کاربر", callback_data='userinfo')],
        [InlineKeyboardButton("🔴 غیر فعال کاربر", callback_data='disable'), InlineKeyboardButton("🟢 فعال کاربر", callback_data='enable')],
        [InlineKeyboardButton("🔄تمدید کاربر", callback_data='update')],
        [InlineKeyboardButton("🛠ساخت اکانت", callback_data='Create_none'), InlineKeyboardButton("🗑حذف کاربر", callback_data='remove')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def User_Tools_keys():
    keyboard = [
        [InlineKeyboardButton("🛒خرید🛒", callback_data='buy')],
        [InlineKeyboardButton("💰تعرفه قیمت ها", callback_data='price'), InlineKeyboardButton("🔄تمدید", callback_data='upgrade')],
        [InlineKeyboardButton("ℹ️اطلاعات سرویس", callback_data='config'), InlineKeyboardButton("📦سرویس های من", callback_data='service')],
        [InlineKeyboardButton("👥پشتیبانی", callback_data='support'), InlineKeyboardButton("🆘راهنمای نصب و اجرا", callback_data='help')],
        [InlineKeyboardButton("🆓پروکسی تلگرام", callback_data='FREEPX')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def server_cb_creator(job):
    hosts = Get_hosts()
    keyboard = []
    if len(hosts) >= 2:
        if len(hosts) % 2 == 0:
            for i in range(0, len(hosts) - 1, 2):
                keyboard.append([InlineKeyboardButton(hosts[i], callback_data=(job + hosts[i])), InlineKeyboardButton(hosts[i + 1], callback_data=(job + hosts[i + 1]))])
        else:
            for i in range(0, len(hosts) - 1, 2):
                keyboard.append([InlineKeyboardButton(hosts[i], callback_data=(job + hosts[i])), InlineKeyboardButton(hosts[i + 1], callback_data=(job + hosts[i + 1]))])
            keyboard.append([InlineKeyboardButton(hosts[-1], callback_data=(job + hosts[-1]))])
    else:
        if hosts == []:
            pass
        else:
            keyboard.append([InlineKeyboardButton(hosts[0], callback_data=(job + hosts[0]))])
    keyboard.append([InlineKeyboardButton("<< back", callback_data="back_admin")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def QR_Maker(link):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=15,
        border=2
    )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(back_color=(20, 20, 20), fill_color=(255, 255, 255))
    photo = "cache/" + uuid4().hex[0:8] + ".png"
    img.save(photo)
    return photo


def countuser_m():
    fname = "All.txt"
    count = 0
    with open(fname, 'r') as f:
        for line in f:
            count += 1
    f.close()
    return count


def checker(ids):
    txt = open("All.txt", "r")
    if ids not in txt.read():
        txt = open("All.txt", "a")
        txt.writelines("\n")
        txt.writelines(ids)
        txt.close()


def checker_notify(ids):
    txt = open("All.txt", "r")
    if ids in txt.read():
        return True
    else:
        return False


def trx_price(irr_price):
    irr_price = int(irr_price)
    irr = (get_settings())['usd']
    try:
        trx = cryptocompare.get_price('TRX', currency='USD')['TRX']["USD"]
        price = (irr_price / irr) / trx
        price = str("{:.2f}".format(float(price))) + " TRX"
    except:
        price = str("{:.2f}".format(float(irr_price / irr))) + "$"
        #price = "مبلغ مشخص نیست لطفا از کارت به کارت استفاده کنین"
    return price


def get_random_server():
    hosts = Get_hosts()
    for host in hosts:
        if check_domain_reached_maximum(host) is False:
            return host
    return None


def Check_in_hosts(host):
    hosts = Get_hosts()
    if host in hosts:
        return host, True
    else:
        return host, False


def get_host_username(text):
    username = ""
    text = text.replace("http://", "")
    if "ssh://" in text:
        host = (text.split("@")[1]).split(":")[0]
        username = (text.split("ssh://")[1]).split(":")[0]
    if True:
        if "SSH Host :" in text:
            host = ((text.split("SSH Host :")[1].split("\n")[0]))
        elif "ssh host:" in text:
            host = ((text.split("ssh host:")[1].split("\n")[0]))
        elif "SSH Host:" in text:
            host = ((text.split("SSH Host:")[1].split("\n")[0]))
        elif "ssh host :" in text:
            host = ((text.split("ssh host :")[1].split("\n")[0]))
        elif "host:" in text:
            host = ((text.split("host:")[1].split("\n")[0]))
        elif "host :" in text:
            host = ((text.split("host :")[1].split("\n")[0]))
        elif "Host:" in text:
            host = ((text.split("Host:")[1].split("\n")[0]))
        elif "Host :" in text:
            host = ((text.split("Host :")[1].split("\n")[0]))
        host = host.replace("*", "")
        host = host.replace(" ", "")
        host = host.replace(" ", "")
        if "user :" in text:
            username = text.split("user :")[1].split("\n")[0]
        elif "User :" in text:
            username = text.split("User :")[1].split("\n")[0]
        elif "user :" in text:
            username = text.split("user:")[1].split("\n")[0]
        elif "User:" in text:
            username = text.split("User:")[1].split("\n")[0]
        elif "Username :" in text:
            username = text.split("Username :")[1].split("\n")[0]
        elif "username :" in text:
            username = text.split("username :")[1].split("\n")[0]
        elif "Username:" in text:
            username = text.split("Username:")[1].split("\n")[0]
        elif "username:" in text:
            username = text.split("username:")[1].split("\n")[0]
        username = username.replace(" ", "")
        username = username.replace(" ", "")

        hosts = Get_hosts()
        if host in hosts:
            return host, username
        else:
            return None, None


def Login_test(username, password, host):
    try:
        Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
        port, udgpw = Session.Ports()
        int(port)
        return True
    except:
        return False


def update_host(link):
    text = "🗒Logs:\n"
    from_host = (link.split("/transfer from ")[1]).split(" to")[0]
    data = link.split("to ")[1]
    with open("Pannels.txt", 'a+') as txt:
        if from_host in txt.read():
            text += "The host does not exist."
            return text
        if data not in txt.read():
            to_host = data.split("@")[0]
            username = (data.split(":")[0]).split("@")[1]
            password = data.split(":")[1]
            if sshx.Login(username, password, to_host) is False:
                text += "Please send the correct Login data."
                return text
            if Login_test(username, password, to_host) is False:
                text += "Please send the correct Login data."
                return text
        else:
            text += "This host is exist."
            return text
    try:
        session = "ssh/" + from_host + ".session"
        os.remove(session)
        text += "Session has been removed\n"
    except Exception as e:
        text += f"Error Session removing: {str(e)}\n"

    with open("Pannels.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        if from_host in line:
            from_password = line.split(":")[1].replace("\n", "")
            from_user = line.split(":")[0].split("@")[1]
            break

    try:
        with open("Pannels.txt", "w") as f:
            for line in lines:
                if line.strip("\n") != (from_host + "@" + from_user + ":" + from_password):
                    f.write(line)
        text += "host has been removed from the list"
        with open("Pannels.txt", 'a+') as txt:
            txt.writelines(data + "\n")
        text += "The New host added"
        to_host = data.split("@")[0]
        update_users_host(from_host, to_host)
        text += "Changed all users that had the host"
    except Exception as e:
        os.remove("Pannels.txt")
        with open("Pannels.txt", "a+") as f:
            for line in lines:
                f.writelines(line)
        text += f"Error host list removing: {str(e)}"
    return text


def Get_hosts():
    hosts = []
    with open("Pannels.txt", 'r') as t:
        for data in t.readlines():
            data = data.replace('\n', "")
            hosts.append(data.split("@")[0])
    return hosts


def get_host_username_password(host):
    with open("Pannels.txt", 'r') as txt:
        for data in txt.readlines():
            data = data.replace('\n', "")
            if data.split("@")[0] == host:
                username = (data.split(":")[0]).split("@")[1]
                password = data.split(":")[1]
                return username, password


def check_domain_reached_maximum(host):
    settings = get_settings()
    maximum = settings['maximum']
    username, password = get_host_username_password(host)
    Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
    Clients = int(Session.Count_Clients())
    if Clients >= maximum:
        return True
    else:
        return False


#DB

def add_user_db(chat_id, name, username, account, host):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Users (ID, Name, Username, Account, Host) VALUES (?, ?, ?, ?, ?)", (chat_id, name, username, account, host))
            conn.commit()
            break
        except:
            pass


def add_cache(chat_id, status):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Cache (Chat, Status) VALUES (?, ?)", (chat_id, status))
            conn.commit()
            break
        except:
            pass


def add_seller(chat_id, name, username, limit):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Sellers (ID, Name, Username, 'limit') VALUES (?, ?, ?, ?)", (chat_id, name, username, limit))
            conn.commit()
            break
        except:
            pass


def add_check_admin(chat_id, name, username, code, status, timing):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Checked (ID, Name, Username, Code, Confirm, Checked) VALUES (?, ?, ?, ?, ?, ?)", (chat_id, name, username, code, status, timing))
            conn.commit()
            break
        except:
            pass


def add_collector(chat_id, status, cache_list, hosts_list):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Collector (ID, Status, Cache, Hosts) VALUES (?, ?, ?, ?)", (chat_id, status, str(cache_list), str(hosts_list)))
            conn.commit()
            break
        except:
            pass


def add_code_buy(chat_id, code, status, cache_list):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Buy (ID, Code, Status, Data) VALUES (?, ?, ?, ?)", (chat_id, code, status, str(cache_list)))
            conn.commit()
            break
        except:
            pass


def check_cache(chat_id):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Cache WHERE Chat=:Chat", {'Chat': chat_id})
            records = cur.fetchall()
            if records == []:
                return False
            else:
                return True
        except:
            pass


def check_exist_user(host, user):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Users WHERE Host=:Host AND Account=:Account", {'Host': host, 'Account': user})
            records = cur.fetchall()
            if records == []:
                return False
            else:
                return True
        except:
            pass


def check_code_exists(code):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Buy WHERE Code=:Code", {'Code': code})
            records = cur.fetchall()
            if records == []:
                return False
            else:
                return True
        except:
            pass


def check_admin_confirm(code):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Checked WHERE Code=:Code", {'Code': code})
            records = cur.fetchall()
            if records == []:
                return False
            else:
                return True
        except:
            pass


def check_seller_exist(chat_id):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Sellers WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            if records == []:
                return False
            else:
                return True
        except:
            pass


def get_card_info():
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Pay WHERE ID=:ID", {'ID': 1})
            records = cur.fetchall()
            return records[0][1], records[0][2], records[0][3]
        except:
            pass


def get_wallet_info():
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Wallet WHERE ID=:ID", {'ID': 1})
            records = cur.fetchall()
            return records[0][1], records[0][2], records[0][3], records[0][4]
        except:
            pass


def get_collector_cache(chat_id):
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Collector WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            for row in records:
                return ast.literal_eval(row[2]), ast.literal_eval(row[3])
        except:
            pass


def get_cache_status(chat_id):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Cache WHERE Chat=:Chat", {'Chat': chat_id})
            records = cur.fetchall()
            for row in records:
                return row[1]
        except:
            pass


def get_name_db_hidden_user(name):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Users WHERE Name=:Name", {'Name': name})
            records = cur.fetchall()
            if records == []:
                return " ", False
            else:
                for row in records:
                    return row[0], True
        except:
            pass


def get_all_accounts_by_chat_id(chat_id):
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Users WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            Accounts = []
            Hosts = []
            if records == []:
                return Accounts, Hosts, False
            else:
                for i in range(len(records)):
                    Accounts.append(records[i][3])
                    Hosts.append(records[i][4])
                return Accounts, Hosts, True
        except:
            pass


def get_all_user_data(host, user):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Users WHERE Host=:Host AND Account=:Account", {'Host': host, 'Account': user})
            records = cur.fetchall()
            return records[0][0], records[0][1], records[0][2]
        except:
            pass


def get_db(host):
    DB_usernames = []
    cur.execute("SELECT * FROM Users WHERE Host=:Host", {'Host': host})
    records = cur.fetchall()
    for row in records:
        DB_usernames.append(row[3])
    return DB_usernames


def get_all_users_in_host(host):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Users WHERE Host=:Host", {'Host': host})
            records = cur.fetchall()
            return records
        except:
            pass


def get_all_sellers():
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Sellers")
            records = cur.fetchall()
            return records
        except:
            pass


def get_seller_info(chat_id):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Sellers WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            for row in records:
                return row[0], row[1], row[2], int(row[3])
        except:
            pass


def get_settings():
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Settings WHERE ID=:ID", {'ID': 1})
            records = cur.fetchall()
            s = records[0][1]
            s = s.replace("\'", "\"")
            p = re.compile('(?<!\\\\)\'')
            s = p.sub('\"', s)
            settings = json.loads(s)
            return settings
        except:
            pass


def get_check_admin_data(code):
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Checked WHERE Code=:Code", {'Code': code})
            records = cur.fetchall()
            for row in records:
                return row[1], row[2], row[4], row[5]
        except:
            pass


def get_code_buy_data(code):
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Buy WHERE Code=:Code", {'Code': code})
            records = cur.fetchall()
            for row in records:
                return row[0], ast.literal_eval(row[3])
        except:
            pass


def get_code_buy_info(chat_id, status):
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Buy WHERE ID=:ID", {'ID': chat_id})
            records = [cur.fetchall()[-1]]
            for row in records:
                if (row[2] == "add") or (row[2] == status):
                    return row[1], ast.literal_eval(row[3])
        except:
            pass


def delete_cache(chat_id):
    for i in range(5):
        try:
            cur.execute("DELETE FROM Cache WHERE Chat=?", (chat_id,))
            conn.commit()
            break
        except:
            pass


def delete_collector(chat_id):
    for i in range(5):
        try:
            cur.execute("DELETE FROM Collector WHERE ID=?", (chat_id,))
            conn.commit()
            break
        except:
            pass


def delete_code_buy(code):
    for i in range(5):
        try:
            cur.execute("DELETE FROM Buy WHERE Code=?", (code,))
            conn.commit()
            break
        except:
            pass


def delete_all_buy(chat_id, status):
    for i in range(5):
        try:
            cur.execute("DELETE FROM Buy WHERE ID=? AND Status=?", (chat_id, status,))
            conn.commit()
            break
        except:
            pass


def delete_user(host, user):
    for i in range(5):
        try:
            cur.execute("DELETE FROM Users WHERE Host=? AND Account=?", (host, user,))
            conn.commit()
            break
        except:
            pass


def delete_seller(chat_id):
    for i in range(5):
        try:
            cur.execute("DELETE FROM Sellers WHERE ID=?", (chat_id,))
            conn.commit()
            break
        except:
            pass


def update_settings(settings):
    for i in range(5):
        try:
            cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
            conn.commit()
        except:
            pass


def update_collector(chat_id, cache_list, hosts_list):
    for i in range(5):
        try:
            cur.execute("UPDATE Collector SET Cache = ?, Hosts = ? WHERE ID =?", (str(cache_list), str(hosts_list), chat_id))
            conn.commit()
        except:
            pass


def update_users_host(from_host, to_host):
    for i in range(5):
        try:
            cur.execute("UPDATE Users SET Host = ? WHERE Host =?", (to_host, from_host))
            conn.commit()
        except:
            pass


def update_card(name, username, card):
    for i in range(5):
        try:
            cur.execute("UPDATE Pay SET Name = ?, Username = ?, Card = ? WHERE ID =?", (name, username, card, 1))
            conn.commit()
        except:
            pass


def update_wallet(name, username, wallet):
    for i in range(5):
        try:
            cur.execute("UPDATE Wallet SET Name = ?, Username = ?, wallet = ? WHERE ID =?", (name, username, wallet, 1))
            conn.commit()
        except:
            pass


def update_code_status(code, status):
    for i in range(5):
        try:
            cur.execute("UPDATE Buy SET Status = ? WHERE Code =?", (status, code))
            conn.commit()
        except:
            pass


def update_seller_limit(chat_id, limit):
    for i in range(5):
        try:
            cur.execute("UPDATE Sellers SET 'limit' = ? WHERE ID =?", (limit, chat_id))
            conn.commit()
        except:
            pass


@app.on_message(filters.private & filters.command('cancel'))
def cancel(bot, message):
    host_cache.clear()
    cache_list.clear()
    text_cache.clear()
    chat_id = message.chat.id
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
        delete_collector(chat_id)
    if chat_id in admin_id:
        message.reply_text("Canceled❌\n/add\n/remove\n/transfer\n/specific\n/edit", reply_markup=Admin_Tools_keys())
    elif chat_id in seller_id:
        message.reply_text("Canceled❌", reply_markup=Seller_Tools_keys())
    else:
        message.reply_text("Canceled❌", reply_markup=User_Tools_keys())


@app.on_message(filters.chat(admin_id) & filters.forwarded)
def forward(bot, message):
    chat_id = message.chat.id
    if check_cache(chat_id) is True:
        status = get_cache_status(chat_id)
        if status == "message":
            delete_cache(chat_id)
            message.reply_text("Forwarding...")
            msg_id = message.id
            fname = "All.txt"
            sent = 0
            with open(fname, 'r') as f:
                for usertxt in f:
                    try:
                        bot.forward_messages(int(usertxt.replace('\n', '')), chat_id, msg_id)
                        sent += 1
                    except:
                        continue
            bot.send_message(chat_id, f"sent to {str(sent)} users")
        elif status == "forward":
            old_list, host_cahce = get_collector_cache(chat_id)
            cache_list = []
            for i in old_list:
                cache_list.append(i)
            try:
                cache_list.append(message.forward_from.id)
                cache_list.append(message.forward_from.first_name)
            except:
                user_chat_id, status = get_name_db_hidden_user(message.forward_sender_name)
                if status is True:
                    cache_list.append(user_chat_id)
                else:
                    cache_list.append(randint(123456, 999999))
                cache_list.append(message.forward_sender_name)
            try:
                cache_list.append(message.forward_from.username)
            except:
                cache_list.append("None")
            delete_cache(chat_id)
            add_cache(chat_id, "connection")
            update_collector(chat_id, cache_list, host_cahce)
            message.reply_text("send connection limit only number or /cancel")
        elif status == "userconfigs":
            try:
                user_id = message.forward_from.id
                text = "chat id"
                status = True
            except:
                user_id, status = get_name_db_hidden_user(message.forward_sender_name)
                text = "name (⚠️maybe from different users)"
            keyboard = []
            if status is True:
                accounts, hosts, status = get_all_accounts_by_chat_id(user_id)
                if status is True:
                    if len(accounts) >= 2:
                        if len(accounts) % 2 == 0:
                            for i in range(0, len(accounts) - 1, 2):
                                keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("IDADMIN_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("IDADMIN_" + hosts[i + 1] + "$" + accounts[i + 1]))])
                        else:
                            for i in range(0, len(accounts) - 1, 2):
                                keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("IDADMIN_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("IDADMIN_" + hosts[i + 1] + "$" + accounts[i + 1]))])
                            keyboard.append([InlineKeyboardButton(accounts[-1], callback_data=("IDADMIN_" + hosts[-1] + "$" + accounts[-1]))])
                    else:
                        keyboard.append([InlineKeyboardButton(accounts[0], callback_data=("IDADMIN_" + hosts[0] + "$" + accounts[0]))])
                    keyboard.append([InlineKeyboardButton("<< Back", callback_data='back_admin')])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text(f"Founded by {text} \n\nChoose: ", reply_markup=reply_markup)
                else:
                    keyboard.append([InlineKeyboardButton("<< Back", callback_data='back_admin')])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text("Not found❌", reply_markup=reply_markup)
            else:
                keyboard.append([InlineKeyboardButton("<< Back", callback_data='back_admin')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Not found❌", reply_markup=reply_markup)
            delete_cache(chat_id)
        elif status == "add_seller":
            keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                user_id = message.forward_from.id
                if check_seller_exist(user_id) is False:
                    try:
                        username = message.forward_from.username
                    except:
                        username = "None"
                    cache_list = [user_id, message.forward_from.first_name, username]
                    delete_cache(chat_id)
                    delete_collector(chat_id)
                    add_collector(chat_id, "limit_seller", cache_list, [])
                    add_cache(chat_id, "limit_seller")
                    message.reply_text("Ok now send a limit. only numbers\n\n0 = unlimited\n10 = 10 clients seller can create")
                else:
                    message.reply_text("🔵 This Seller is Exist", reply_markup=reply_markup)
            except:
                message.reply_text("❌This user is Hidden /cancel it", reply_markup=reply_markup)


@app.on_message(filters.chat(admin_id) & filters.command('edit'))
def start_edit(bot, message):
    link = message.text
    if link == "/edit":
        message.reply_text("<pre>/edit domain@user:pass</pre>", parse_mode=enums.ParseMode.HTML)
    elif "@" not in link:
        message.reply_text("not correct: /edit domain@user:pass")
    else:
        do = False
        try:
            data = link.split("/edit ")[1]
            with open("Pannels.txt", 'a+') as txt:
                data = link.split("/edit ")[1]
                if data in txt.read():
                    host = data.split("@")[0]
                    username = (data.split(":")[0]).split("@")[1]
                    password = data.split(":")[1]
                    for line in txt.readlines():
                        if host in line:
                            old_password = line.split(":")[1].replace("\n", "")
                            old_username = line.split(":")[0].split("@")[1]
                            break
                    session = "ssh/" + host + ".session"
                    os.remove(session)
                    if sshx.Login(username, password, host) is False:
                        message.reply_text("Please send the correct Login data")
                        ssc = sshx.Login(old_username, old_password, host)
                    if Login_test(username, password, host) is True:
                        do = True
                    else:
                        message.reply_text("Wrong Login data")
                        ssc = sshx.Login(old_username, old_password, host)
                else:
                    message.reply_text("This server does not exist")
        except Exception as e:
            message.reply_text("Error: " + str(e))
        if do is True:
            with open("Pannels.txt", "w") as f:
                for line in lines:
                    if line.strip("\n") != (host + "@" + old_username + ":" + old_password):
                        f.write(line)
                f.writelines(data + "\n")
            message.reply_text("Done✔️")


@app.on_message(filters.chat(admin_id) & filters.command('add'))
def start_add(bot, message):
    link = message.text
    if link == "/add":
        message.reply_text("<pre>/add domain@user:pass</pre>", parse_mode=enums.ParseMode.HTML)
    elif "@" not in link:
        message.reply_text("not correct: /add domain@user:pass")
    else:
        try:
            data = link.split("/add ")[1]
            with open("Pannels.txt", 'a+') as txt:
                data = link.split("/add ")[1]
                if data not in txt.read():
                    host = data.split("@")[0]
                    username = (data.split(":")[0]).split("@")[1]
                    password = data.split(":")[1]
                    if sshx.Login(username, password, host) is False:
                        message.reply_text("Please send the correct Login data")
                    if Login_test(username, password, host) is True:
                        txt.writelines(data + "\n")
                        message.reply_text("Added")
                    else:
                        message.reply_text("Wrong Login data")
                else:
                    message.reply_text("This server is exist")
        except Exception as e:
            message.reply_text("Error: " + str(e))


@app.on_message(filters.chat(admin_id) & filters.command('remove'))
def start_remove(bot, message):
    link = message.text
    if link == "/remove":
        message.reply_text("<pre>/remove domain</pre>", parse_mode=enums.ParseMode.HTML)
    else:
        if os.stat("Pannels.txt").st_size == 0:
            message.reply_text("There's not any server /add a server")
            raise
        text = "Done:\n"
        host = link.split("/remove ")[1]
        try:
            session = "ssh/" + host + ".session"
            os.remove(session)
            text += "Session has been removed\n"
        except Exception as e:
            text += f"Error Session removing: {str(e)}\n"
        with open("Pannels.txt", "r") as f:
            lines = f.readlines()
        for line in lines:
            if host in line:
                password = line.split(":")[1].replace("\n", "")
                user = line.split(":")[0].split("@")[1]
                break
        try:
            with open("Pannels.txt", "w") as f:
                for line in lines:
                    if line.strip("\n") != (host + "@" + user + ":" + password):
                        f.write(line)
            text += "host has been removed from the list"
        except Exception as e:
            os.remove("Pannels.txt")
            with open("Pannels.txt", "a+") as f:
                for line in lines:
                    f.writelines(line)
            text += f"Error host list removing: {str(e)}"
        message.reply_text(text)


@app.on_message(filters.chat(admin_id) & filters.command('specific'))
def start_specific(bot, message):
    link = message.text
    chat_id = message.chat.id
    if link == "/specific":
        message.reply_text("to send user new domain or else msg: <pre>/specific domain&text</pre>", parse_mode=enums.ParseMode.HTML)
    else:
        if os.stat("Pannels.txt").st_size == 0:
            message.reply_text("There's not any server /add a server")
            raise
        try:
            t0 = link.split("&")[1]
            if "http://" in link:
                link = link.split("http://")[1]
                link = link.replace("/", "")
            elif "https://" in link:
                link = link.split("https://")[1]
                link = link.replace("/", "")
            host = link.split("/specific ")[1]
            hosts = Get_hosts()
            count = 0
            if host in hosts:
                rec = get_all_users_in_host(host)
                bot.send_message(chat_id, "Sending...")
                for i in range(len(rec)):
                    ID = rec[i][0]
                    Account = rec[i][3]
                    try:
                        text = "\n\n" + t0 + "اکانت: " + Account
                        bot.send_message(ID, text, parse_mode=enums.ParseMode.HTML)
                        count += 1
                    except:
                        pass
                bot.send_message(chat_id, f"Send the specific msg from {host} to {str(count)}/{str(len(rec))} users.")
            else:
                message.reply_text("The host does not exist")
        except Exception as e:
            message.reply_text("Error: " + str(e))


@app.on_message(filters.chat(admin_id) & filters.command('change'))
def start_change(bot, message):
    link = message.text
    if link == "/transfer":
        message.reply_text("<pre>/transfer from domain to domain@user:pass</pre>", parse_mode=enums.ParseMode.HTML)
    else:
        if os.stat("Pannels.txt").st_size == 0:
            message.reply_text("There's not any server /add a server")
            raise
        try:
            text = update_host(link)
        except Exception as e:
            text = "Error: " + str(e)
        message.reply_text(text)


@app.on_message(filters.chat(admin_id) & filters.command('start'))
def start_admin(bot, message):
    text = '🔻<b>Tools</b>\n\n/add\n/remove\n/transfer\n/specific\n/edit'
    message.reply_text(text, reply_markup=Admin_Tools_keys(), parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.private & filters.command('start'))
def start_user(bot, message):
    chat_id = message.chat.id
    checker(str(chat_id))
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
        if chat_id in seller_id:
            delete_collector(chat_id)
    if chat_id in seller_id:
        text = '🔻<b>Tools</b>'
        message.reply_text(text, reply_markup=Seller_Tools_keys(), parse_mode=enums.ParseMode.HTML)
    else:
        if (get_settings())['sponser'] == "None":
            message.reply_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)
        else:
            try:
                chat_member = bot.get_chat_member((get_settings())['sponser'], chat_id)
                message.reply_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)

            except NotAcceptable:
                message.reply_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)

            except BadRequest as e:
                if "USER_NOT_PARTICIPANT" in str(e):
                    text = "برای استفاده از ربات اینجا باید جوین بشین:" + "\n\n" + (get_settings())['sponser']
                    keyboard = [[InlineKeyboardButton("جوین شدم✅", callback_data="JOIN")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text(text, reply_markup=reply_markup)
                else:
                    message.reply_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.private & filters.text)
def text_private(bot, message):
    chat_id = message.chat.id
    link = message.text
    if 'http://' in link:
        link = link.replace('http://', '')
    elif 'https://' in link:
        link = link.replace('https://', '')
    if check_cache(chat_id) is False:
        if chat_id in admin_id:
            try:
                host, user = get_host_username(link)
            except:
                host = None
                user = None
            if host is not None:
                msg = message.reply_text("Wait...").id
                username, password = get_host_username_password(host)
                try:
                    Session = sshx.PANNEL(host, username, password, 'User', user)
                    text = Session.User_info()
                    cb = host + "$" + user
                    keyboard = [
                        [InlineKeyboardButton("🔄تمدید کاربر", callback_data=('IDMNU&Update_' + cb)), InlineKeyboardButton("🗑حذف کاربر", callback_data=('IDMNU&Remove_' + cb))],
                        [InlineKeyboardButton("🟢 فعال کاربر", callback_data=('IDMNU&Active_' + cb)), InlineKeyboardButton("🔴 غیر فعال کاربر", callback_data=('IDMNU&Disable_' + cb))],
                        [InlineKeyboardButton("🆕ریست ترافیک", callback_data=('IDMNU&Reset_' + cb)), InlineKeyboardButton("🔑تغییر پسورد", callback_data=('IDMNU&PASSWORD_' + cb))]
                    ]
                    if "نامحدود" not in text:
                        keyboard.append([InlineKeyboardButton("➕افزایش ترافیک", callback_data=('IDMNU&Traffic_' + cb))])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.edit_message_text(chat_id, msg, text, reply_markup=reply_markup)
                except:
                    bot.edit_message_text(chat_id, msg, "چیزی پیدا نشد:(")
            else:
                message.reply_text("Menu /start")
        else:
            message.reply_text("Menu /start")
    else:
        status = get_cache_status(chat_id)

        if chat_id not in (admin_id + seller_id):
            if (status == "config"):
                try:
                    host, user = get_host_username(link)
                except:
                    host = None
                    user = None
                keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                rm = True
                if host is not None:
                    username, password = get_host_username_password(host)
                    if check_exist_user(host, user) is False:
                        try:
                            Session = sshx.PANNEL(host, username, password, 'User', user)
                            text = Session.User_info()
                            try:
                                username = message.forward_from.username
                            except:
                                username = "None"
                            add_user_db(chat_id, message.forward_sender_name, username, user, host)
                        except:
                            text = "چیزی پیدا نشد:("
                    else:
                        try:
                            Session = sshx.PANNEL(host, username, password, 'User', user)
                            text = Session.User_info()
                        except:
                            text = "چیزی پیدا نشد:("
                else:
                    host, st = Check_in_hosts(link)
                    if st is True:
                        delete_cache(chat_id)
                        add_cache(chat_id, "host_" + host)
                        text = "خب حالا نام کاربری ssh تون بفرستین "
                        rm = False
                    else:
                        text = "چیزی پیدا نشد:("
                message.reply_text(text, reply_markup=reply_markup)
                if rm is True:
                    delete_cache(chat_id)

            elif ("host_" in status):
                host = status.split("host_")[1]
                host, st = Check_in_hosts(host)
                user = link
                keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if st is True:
                    username, password = get_host_username_password(host)
                    if check_exist_user(host, user) is False:
                        try:
                            Session = sshx.PANNEL(host, username, password, 'User', user)
                            text = Session.User_info()
                            try:
                                username = message.forward_from.username
                            except:
                                username = "None"
                            add_user_db(chat_id, message.forward_sender_name, username, user, host)
                        except:
                            text = "چیزی پیدا نشد:("
                    else:
                        try:
                            Session = sshx.PANNEL(host, username, password, 'User', user)
                            text = Session.User_info()
                        except:
                            text = "چیزی پیدا نشد:("
                else:
                    text = "چیزی پیدا نشد:("
                message.reply_text(text, reply_markup=reply_markup)
                delete_cache(chat_id)

            elif ("support" in status):
                i = int(status.split("support ")[1])
                msg_id = message.id
                bot.forward_messages(admin_id[i], chat_id, msg_id)
                name = message.from_user.first_name
                try:
                    username = "@" + message.from_user.username
                except:
                    username = 'Null'
                text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username
                keyboard = [[InlineKeyboardButton("Answer to " + name, callback_data='ANS_' + str(chat_id))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                sleep(0.2)
                message.reply_text(text='🫡بزودی درخواستتون بررسی میشه')
                delete_cache(chat_id)
            return

        if status == "name_none":
            cache_list, host_cahce = get_collector_cache(chat_id)
            message.reply_text("Send GB only numbers (0 = unlimited) or /cancel")
            cache_list.append(link)
            delete_cache(chat_id)
            add_cache(chat_id, "GB_none")
            update_collector(chat_id, cache_list, host_cahce)

        elif status == "GB_none":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "connection_none")
                update_collector(chat_id, cache_list, host_cahce)
                message.reply_text("send connection limit only number or /cancel")
            except:
                message.reply_text("Send the correct number or /cancel")

        elif status == "connection_none":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("OK. send days only number or /cancel")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "days_none")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("Send the correct number or /cancel")

        elif status == "days_none":
            try:
                days = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                if check_seller_exist(chat_id) is True:
                    if days < 30:
                        raise
                    days = str(days)
                    connection_limit = str(cache_list[-1])
                    traffic = str(cache_list[2])
                    code = uuid4().hex[0:10]
                    name = message.from_user.first_name
                    try:
                        username = "@" + message.from_user.username
                    except:
                        username = 'Null'
                    t1 = f"💲Seller💲\nخرید \ndays: {days}\nGB: {traffic}\nConnection: {connection_limit}"
                    text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\ninfo buy:\n" + t1
                    cb = "Confirmed_" + code
                    no = "NO❌_" + code
                    keyboard = [[InlineKeyboardButton("Confirm✅", callback_data=cb), InlineKeyboardButton("NO❌", callback_data=no)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    for i in range(len(admin_id)):
                        bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                    cache_list = [days, traffic, connection_limit, '90', name, chat_id, username]
                    add_code_buy(chat_id, code, "check", cache_list)
                    message.reply_text("Admins checking ASAP.")

                else:
                    msg = message.reply_text("Wait...").id
                    host = cache_list[0]
                    passw = str(randint(123456, 999999))
                    username, password = get_host_username_password(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                        text = Session.Create(cache_list[1], passw, int(cache_list[-1]), int(link), int(cache_list[2]))
                        port, udgpw = Session.Ports()
                        url = f"ssh://{cache_list[1]}:{passw}@{host}:{port}"
                        photo = QR_Maker(url)
                        text += "\n\nURL: " + "<pre>" + url + "</pre>"
                        bot.send_photo(chat_id, open(photo, 'rb'), text, parse_mode=enums.ParseMode.HTML)
                        os.remove(photo)
                        bot.delete_messages(chat_id, msg)
                    except Exception as e:
                        bot.edit_message_text(chat_id, msg, "Error: " + str(e))
                delete_cache(chat_id)
                delete_collector(chat_id)
            except:
                message.reply_text("Send the correct number or /cancel")

        elif status == "password":
            try:
                user = link
                cache_list, host_cahce = get_collector_cache(chat_id)
                host = cache_list[0]
                username, password = get_host_username_password(host)
                try:
                    Session = sshx.PANNEL(host, username, password, 'User', user)
                    text = Session.User_info()
                    if "Error" not in text:
                        message.reply_text("Send The new password or /cancel")
                        cache_list.append(link)
                        delete_cache(chat_id)
                        add_cache(chat_id, "CPassword")
                        update_collector(chat_id, cache_list, host_cahce)
                    else:
                        message.reply_text(f"The user not found or \n⭕️ Connection Error: {host}\nLogs: {text}")
                        delete_cache(chat_id)
                        delete_collector(chat_id)
                except Exception as e:
                    message.reply_text(f"The user not found or \n⭕️ Connection Error: {host}\nLogs: {text}\n\n{str(e)}")
                    delete_cache(chat_id)
                    delete_collector(chat_id)
            except Exception as e:
                message.reply_text(f"Error: {str(e)}")
                delete_cache(chat_id)
                delete_collector(chat_id)

        elif status == "CPassword":
            try:
                passw = link
                cache_list, host_cahce = get_collector_cache(chat_id)
                host = cache_list[0]
                user = cache_list[1]
                username, password = get_host_username_password(host)
                Session = sshx.PANNEL(host, username, password, 'User', user)
                text = Session.Password(passw)
                message.reply_text(text)
            except Exception as e:
                message.reply_text(f"Error: {str(e)}")
            delete_cache(chat_id)
            delete_collector(chat_id)

        elif status == "name":
            cache_list, host_cahce = get_collector_cache(chat_id)
            message.reply_text("Send GB only numbers (0 = unlimited) or /cancel")
            cache_list.append(link)
            delete_cache(chat_id)
            add_cache(chat_id, "GB")
            update_collector(chat_id, cache_list, host_cahce)

        elif status == "GB":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("OK. Forward a message from the user or /cancel")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "forward")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("Send the correct number or /cancel")

        elif status == 'forward':
            message.reply_text("Forward a message from the user or /cancel")

        elif status == "connection":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("OK. send days only number or /cancel")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "days")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("Send the correct number or /cancel")

        elif status == "days":
            try:
                int(link)
                msg = message.reply_text("Wait...").id
                cache_list, host_cahce = get_collector_cache(chat_id)
                host = cache_list[0]
                user_id = cache_list[3]
                name = cache_list[4]
                Username = cache_list[5]
                passw = str(randint(123456, 999999))
                username, password = get_host_username_password(host)
                try:
                    Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                    text = Session.Create(cache_list[1], passw, int(cache_list[-1]), int(link), int(cache_list[2]))
                    port, udgpw = Session.Ports()
                    url = f"ssh://{cache_list[1]}:{passw}@{host}:{port}"
                    photo = QR_Maker(url)
                    text += "\n\nURL: " + "<pre>" + url + "</pre>"
                    bot.send_photo(chat_id, open(photo, 'rb'), text, parse_mode=enums.ParseMode.HTML)
                    os.remove(photo)
                    add_user_db(user_id, name, Username, cache_list[1], host)
                    bot.delete_messages(chat_id, msg)
                except Exception as e:
                    bot.edit_message_text(chat_id, msg, "Error: " + str(e))
                delete_cache(chat_id)
                delete_collector(chat_id)
            except Exception as e:
                print(e, "Line days")
                message.reply_text("Send the correct number or /cancel")

        elif status == "removehost":
            hosts = Get_hosts()
            if link in hosts:
                delete_cache(chat_id)
                add_cache(chat_id, "remove_" + link)
                message.reply_text('Send the user or /cancel')
            else:
                message.reply_text("The host does not exist send the correct address or /cancel")

        elif "remove_" in status:
            msg = message.reply_text("Wait...").id
            user = link
            host = status.split("remove_")[1]
            try:
                username, password = get_host_username_password(host)
                Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                text = Session.Delete(user)
                if check_exist_user(host, user) is True:
                    delete_user(host, user)
                    text += "\n\nand Deleted from DB"
            except Exception as e:
                text = "Error: " + str(e)
            delete_cache(chat_id)
            bot.edit_message_text(chat_id, msg, text)

        elif status == "updatehost":
            hosts = Get_hosts()
            if link in hosts:
                delete_cache(chat_id)
                add_cache(chat_id, "update_" + link)
                message.reply_text('Send the user or /cancel')
            else:
                message.reply_text("The host does not exist send the correct address or /cancel")

        elif "update_" in status:
            user = link
            host = status.split("update_")[1]
            add_collector(chat_id, "update", [], [])
            cache_list = [host, user]
            delete_cache(chat_id)
            add_cache(chat_id, "GB-update")
            message.reply_text("Send GB only numbers (0 = unlimited) or /cancel")
            update_collector(chat_id, cache_list, [])

        elif status == "GB-update":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("send connection limit only number or /cancel")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "connection-update")
                update_collector(chat_id, cache_list, [])
            except:
                message.reply_text("Send the correct number or /cancel")

        elif status == "connection-update":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("Send Days only numbers or /cancel")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "days-update")
                update_collector(chat_id, cache_list, [])
            except:
                message.reply_text("Send the correct number or /cancel")

        elif status == "days-update":
            try:
                days = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                host = cache_list[0]
                if check_seller_exist(chat_id) is True:
                    days = str(days)
                    user = cache_list[1]
                    connection_limit = str(cache_list[-1])
                    traffic = str(cache_list[2])
                    code = uuid4().hex[0:10]
                    name = message.from_user.first_name
                    try:
                        username = "@" + message.from_user.username
                    except:
                        username = 'Null'
                    t1 = f"💲Seller💲\nتمدید\ndays: {days}\nGB: {traffic}\nConnection: {connection_limit}"
                    text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\ninfo buy:\n" + t1
                    cb = "ConfirmUPGRADE_" + code
                    no = "NO❌_" + code
                    keyboard = [[InlineKeyboardButton("Confirm✅", callback_data=cb), InlineKeyboardButton("NO❌", callback_data=no)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    for i in range(len(admin_id)):
                        bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                    cache_list = [days, traffic, connection_limit, '90', user, host]
                    add_code_buy(chat_id, code, "checkup", cache_list)
                    message.reply_text("Admins checking ASAP.")
                else:
                    msg = message.reply_text("Wait...").id
                    username, password = get_host_username_password(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, 'User', cache_list[1])
                        text = Session.Update(int(cache_list[2]), days, int(cache_list[-1]))
                    except Exception as e:
                        text = "Error: " + str(e)
                    bot.edit_message_text(chat_id, msg, text)
                    cache_list.clear()
                    delete_cache(chat_id)
                    delete_collector(chat_id)
            except:
                message.reply_text("Send the correct number or /cancel")

        elif status == "plus":
            user = link
            cache_list, host_cahce = get_collector_cache(chat_id)
            cache_list.append(user)
            delete_cache(chat_id)
            add_cache(chat_id, "plus-Traffic")
            message.reply_text("Send GB only numbers (0 = unlimited) or /cancel")
            update_collector(chat_id, cache_list, [])

        elif status == "plus-Traffic":
            try:
                traffic = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                host = cache_list[0]
                user = cache_list[1]
                msg = message.reply_text("Wait...").id
                username, password = get_host_username_password(host)
                try:
                    Session = sshx.PANNEL(host, username, password, 'User', user)
                    text = Session.Update_Traffic(traffic)
                except Exception as e:
                    text = "Error: " + str(e)
                bot.edit_message_text(chat_id, msg, text)
                delete_cache(chat_id)
                delete_collector(chat_id)
            except:
                message.reply_text("Send the correct number or /cancel")

        elif status == "infohost":
            hosts = Get_hosts()
            if link in hosts:
                delete_cache(chat_id)
                add_cache(chat_id, "userinfo_" + link)
                message.reply_text('Send the user or /cancel')
            else:
                message.reply_text("The host does not exist send the correct address or /cancel")

        elif "userinfo_" in status:
            msg = message.reply_text("Wait...").id
            user = link
            host = status.split("userinfo_")[1]
            try:
                username, password = get_host_username_password(host)
                Session = sshx.PANNEL(host, username, password, 'User', user)
                text = Session.User_info()
                if check_seller_exist(chat_id) is False:
                    if check_exist_user(host, user) is True:
                        ID, Name, Username = get_all_user_data(host, user)
                        if (Username is None) or (Username == ""):
                            Username = "None"
                        else:
                            Username = "@" + Username
                        text += f"\n\nID: {ID}\nName: {Name}\nUsername: {Username}"
            except Exception as e:
                text = "Error: " + str(e)
            delete_cache(chat_id)
            bot.edit_message_text(chat_id, msg, text)

        elif status == "message":
            delete_cache(chat_id)
            message.reply_text("Sending...")
            fname = "All.txt"
            sent = 0
            with open(fname, 'r') as f:
                for usertxt in f:
                    try:
                        bot.send_message(int(usertxt.replace('\n', '')), link, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)
                        sent += 1
                    except:
                        continue
            bot.send_message(chat_id, f"sent to {str(sent)} users")

        elif status == "answer":
            cache_list, host_cahce = get_collector_cache(chat_id)
            try:
                keyboard = [[InlineKeyboardButton("✍️ پاسخ", callback_data=('SUPRT_' + str(chat_id)))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(int(cache_list[0]), link, reply_markup=reply_markup)
                message.reply_text("Sent")
            except:
                message.reply_text("The user blocked the bot")
            delete_cache(chat_id)
            delete_collector(chat_id)

        elif status == "change_wallet":
            name = message.from_user.first_name
            try:
                username = message.from_user.username
            except:
                username = 'Null'
            update_wallet(name, username, link)
            delete_cache(chat_id)
            message.reply_text("Changed .")

        elif status == "change":
            try:
                card = int(link)
                name = message.from_user.first_name
                try:
                    username = message.from_user.username
                except:
                    username = 'Null'
                update_card(name, username, card)
                delete_cache(chat_id)
                message.reply_text("Changed.")
            except:
                message.reply_text("Send only number or /cancel")

        elif (status == "enahost") or (status == "dishost"):
            hosts = Get_hosts()
            if link in hosts:
                delete_cache(chat_id)
                if status == "dishost":
                    add_cache(chat_id, "disable_" + link)
                else:
                    add_cache(chat_id, "enable_" + link)
                message.reply_text('Send the user or /cancel')
            else:
                message.reply_text("The host does not exist send the correct address or /cancel")

        elif ("disable_" in status) or ("enable_" in status):
            msg = message.reply_text("Wait...").id
            try:
                if "disable" in status:
                    host = status.split("disable_")[1]
                else:
                    host = status.split("enable_")[1]
                with open("Pannels.txt", 'r') as txt:
                    for data in txt.readlines():
                        data = data.replace('\n', "")
                        if host == data.split("@")[0]:
                            username = (data.split(":")[0]).split("@")[1]
                            password = data.split(":")[1]
                uname = link
                if "</pre>" in uname:
                    uname = uname.split("</pre>")[0].split("<pre>")[1]
                Session = sshx.PANNEL(host, username, password, 'User', uname)
                if "disable" in status:
                    bot.edit_message_text(chat_id, msg, Session.Disable())
                else:
                    bot.edit_message_text(chat_id, msg, Session.Enable())
            except Exception as e:
                bot.edit_message_text(chat_id, msg, "Error: " + str(e))
            delete_cache(chat_id)

        elif status == "limit_seller":
            try:
                limit = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                add_seller(int(cache_list[0]), cache_list[1], cache_list[2], limit)
                delete_cache(chat_id)
                delete_collector(chat_id)
                keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                sellers_id_add_list()
            except:
                message.reply_text("Send the correct number or /cancel")

        elif "Edit_limit#" in status:
            try:
                limit = int(link)
                seller = int(status.split("#")[1])
                update_seller_limit(seller, limit)
                keyboard = [[InlineKeyboardButton("<<", callback_data=('SLM_' + str(seller)))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("Only numbers or /cancel")

        elif "backup_timer" == status:
            try:
                hours = int(link)
                if 1 <= hours <= 72:
                    settings = get_settings()
                    settings['backup'] = hours
                    update_settings(settings)
                    keyboard = [[InlineKeyboardButton("<<", callback_data='Backup')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text("Done✔️", reply_markup=reply_markup)
                    delete_cache(chat_id)
                else:
                    message.reply_text("The number is too high send between 1-72 or /cancel")
            except:
                message.reply_text("Only numbers or /cancel")

        elif "Start_message" == status:
            settings = get_settings()
            settings['start'] = link
            update_settings(settings)
            keyboard = [[InlineKeyboardButton("<<", callback_data='WSMSG')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message.reply_text("Done✔️", reply_markup=reply_markup)
            delete_cache(chat_id)

        elif "Price_message" == status:
            settings = get_settings()
            settings['list'] = link
            update_settings(settings)
            keyboard = [[InlineKeyboardButton("<<", callback_data='WLMSG')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message.reply_text("Done✔️", reply_markup=reply_markup)
            delete_cache(chat_id)

        elif "Sponser" == status:
            if ("@" in link) and (" " not in link):
                try:
                    chat_member = bot.get_chat_member(link, chat_id)
                    settings = get_settings()
                    settings['sponser'] = link
                    update_settings(settings)
                    keyboard = [[InlineKeyboardButton("<<", callback_data='sponser')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text("Done✔️", reply_markup=reply_markup)
                    delete_cache(chat_id)

                except NotAcceptable:
                    message.reply_text("🔴Error: The bot not added to the channel or group")
                    delete_cache(chat_id)

                except BadRequest as e:
                    if "USER_NOT_PARTICIPANT" in str(e):
                        message.reply_text("🔴Error: Your not in the channel or group")
                    else:
                        message.reply_text("🔴Error: The channel or group deos not exist.")
                    delete_cache(chat_id)

            else:
                message.reply_text("Send the correct form: @channel")

        elif "AutoDelete" == status:
            try:
                days = int(link)
                settings = get_settings()
                settings['auto_delete'] = days
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='AutoDelete')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("Only numbers or /cancel")

        elif "USD" == status:
            try:
                usd = int(link)
                settings = get_settings()
                settings['usd'] = usd
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='USD')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("Only numbers or /cancel")

        elif "maximum" == status:
            try:
                maximum = int(link)
                settings = get_settings()
                settings['maximum'] = maximum
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='maximum')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("Only numbers or /cancel")

        elif "A_price" == status:
            try:
                price = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("Send Connection limit only numbers or /cancel")
                cache_list.append(price)
                delete_cache(chat_id)
                add_cache(chat_id, "A_connections")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("Only numbers or /cancel")

        elif "A_connections" == status:
            try:
                connections = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("Send days only numbers or /cancel")
                cache_list.append(connections)
                delete_cache(chat_id)
                add_cache(chat_id, "A_days")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("Only numbers or /cancel")

        elif "A_days" == status:
            try:
                days = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("Send traffic only numbers (0 = unlimited) or /cancel")
                cache_list.append(days)
                delete_cache(chat_id)
                add_cache(chat_id, "A_traffic")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("Only numbers or /cancel")

        elif "A_traffic" == status:
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                settings = get_settings()
                prices = settings['prices']
                prices.append(int(cache_list[0]))
                settings['prices'] = prices
                connections = settings['connections']
                connections.append(int(cache_list[1]))
                settings['connections'] = connections
                days = settings['days']
                days.append(int(cache_list[2]))
                settings['days'] = connections
                traffic = settings['traffic']
                traffic.append(int(link))
                settings['traffic'] = traffic
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='ADMINPRICES')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
                delete_collector(chat_id)
            except:
                message.reply_text("Only numbers or /cancel")

        elif "proxy" == status:
            if "t.me/proxy?" in link:
                settings = get_settings()
                settings['proxy'] = 'https://' + link
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='Sprx')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("Send link: https://t.me/proxy?server=... or /cancel")

        elif "Connectionmsg_" in status:
            if len(link) <= 64:
                host = status.split("Connectionmsg_")[1]
                if host in Get_hosts():
                    username, password = get_host_username_password(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                        text = Session.Message(link)
                    except Exception as e:
                        text = "Error: " + str(e)
                else:
                    text = "The server does not exist, You might deleted before"
                keyboard = [[InlineKeyboardButton("<< Menu", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text(text, reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("The message is too long, send a message less than 64 characters")

        elif "AutoRemove_" in status:
            try:
                days = int(link)
                host = status.split("AutoRemove_")[1]
                if host in Get_hosts():
                    username, password = get_host_username_password(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                        text = Session.Auto_remove(days)
                    except Exception as e:
                        text = "Error: " + str(e)
                else:
                    text = "The server does not exist, You might deleted before"
                keyboard = [[InlineKeyboardButton("<< Menu", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text(text, reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("Send only number or /cancel")

        elif "Gift_" in status:
            try:
                days = int(link)
                host = status.split("Gift_")[1]
                if host in Get_hosts():
                    username, password = get_host_username_password(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                        text = Session.Gift(days)
                    except Exception as e:
                        text = "Error: " + str(e)
                else:
                    text = "The server does not exist, You might deleted before"
                keyboard = [[InlineKeyboardButton("<< Menu", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text(text, reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("Send only number or /cancel")

        elif "Reset_" in status:
            try:
                user = link
                host = status.split("Reset_")[1]
                if host in Get_hosts():
                    username, password = get_host_username_password(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, 'User', user)
                        text = Session.Reset_traffic()
                    except Exception as e:
                        text = "Error: " + str(e)
                else:
                    text = "The server does not exist, You might deleted before"
            except Exception as e:
                text = "Error: " + str(e)
            keyboard = [[InlineKeyboardButton("<< Menu", callback_data='back_admin')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message.reply_text(text, reply_markup=reply_markup)
            delete_cache(chat_id)


@app.on_callback_query(filters.regex('back_admin'))
def call_back(bot, query):
    text = '🔻<b>We\'re back</b>\n\n/add\n/remove\n/transfer\n/specific\n/edit'
    query.edit_message_text(text=text, reply_markup=Admin_Tools_keys(), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('back_seller'))
def call_back_seller(bot, query):
    delete_cache(query.message.chat.id)
    query.edit_message_text(text="We're back to the menu", reply_markup=Seller_Tools_keys())


@app.on_callback_query(filters.regex('back'))
def call_back(bot, query):
    text = '🔻<b>خب برگشتیم</b>'
    query.edit_message_text(text=text, reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('servers'))
def call_servers(bot, query):
    query.edit_message_text(text="Select? ", reply_markup=server_cb_creator("HOST_"))


@app.on_callback_query(filters.regex('HSMSC_'))
def call_HSMSC(bot, query):
    rt = query.data
    host = rt.split("HSMSC_")[1]
    chat_id = query.message.chat.id
    if host in Get_hosts():
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, "Connectionmsg_" + host)
        bot.send_message(chat_id, "OK, send your message")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="The Server does not exist, You might delete it from the list", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSAR_'))
def call_HSAR(bot, query):
    rt = query.data
    host = rt.split("HSAR_")[1]
    chat_id = query.message.chat.id
    if host in Get_hosts():
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, "AutoRemove_" + host)
        bot.send_message(chat_id, "OK, send only number (day)")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="The Server does not exist, You might delete it from the list", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSUGift_'))
def call_HSUGift(bot, query):
    rt = query.data
    host = rt.split("HSUGift_")[1]
    chat_id = query.message.chat.id
    if host in Get_hosts():
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, "Gift_" + host)
        bot.send_message(chat_id, "OK, send only number (day)")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="The Server does not exist, You might delete it from the list", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSUL_'))
def call_HSUL(bot, query):
    rt = query.data
    host = rt.split("HSUL_")[1]
    if host in Get_hosts():
        keyboard = [
            [InlineKeyboardButton("✔️ Active", callback_data=f"ULA_{host}")],
            [InlineKeyboardButton("✖️ Disable", callback_data=f"ULD_{host}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id, f"Limit, server: {host}\nselect:", )
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="The Server does not exist, You might delete it from the list", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ULA_'))
def call_ULA(bot, query):
    rt = query.data
    host = rt.split("ULA_")[1]
    if host in Get_hosts():
        username, password = get_host_username_password(host)
        try:
            Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
            text = Session.Limit_on()
            keyboard = [[InlineKeyboardButton("🔙Back", callback_data=f"HSUL_{host}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=text, reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="The Server does not exist, You might delete it from the list", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ULD_'))
def call_ULD(bot, query):
    rt = query.data
    host = rt.split("ULD_")[1]
    if host in Get_hosts():
        username, password = get_host_username_password(host)
        try:
            Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
            text = Session.Limit_off()
            keyboard = [[InlineKeyboardButton("🔙Back", callback_data=f"HSUL_{host}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=text, reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="The Server does not exist, You might delete it from the list", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HOST_'))
def call_hosts(bot, query):
    rt = query.data
    host = rt.split("HOST_")[1]
    with open("Pannels.txt", 'r') as txt:
        for data in txt.readlines():
            data = data.replace('\n', "")
            if data.split("@")[0] == host:
                username = (data.split(":")[0]).split("@")[1]
                password = data.split(":")[1]
                try:
                    Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                    text = Session.Short_info()
                    if "Premium: ✔️" in text:
                        keyboard = [
                            [InlineKeyboardButton("✉️پیام اتصال", callback_data=f"HSMSC_{host}")],
                            [InlineKeyboardButton("❌حذف کاربران منقضی", callback_data=f"HSAR_{host}")],
                            [InlineKeyboardButton("🔒محدودیت کاربر", callback_data=f"HSUL_{host}")],
                            [InlineKeyboardButton("🎁هدیه روزانه", callback_data=f"HSUGift_{host}")],
                            [InlineKeyboardButton("🔙Back", callback_data="servers")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        query.edit_message_text(text=text, reply_markup=reply_markup)
                    else:
                        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        query.edit_message_text(text=text, reply_markup=reply_markup)
                except Exception as e:
                    keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    query.edit_message_text(text=("Error: " + str(e)), reply_markup=reply_markup)
                break


@app.on_callback_query(filters.regex('checker'))
def call_checker(bot, query):
    keyboard = [[InlineKeyboardButton("🔙Back", callback_data="back_admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if cache[0] is True:
        query.edit_message_text(text="Please wait another process is running...", reply_markup=reply_markup)
        raise
    settings = get_settings()
    maximum = settings['maximum']
    cache.clear()
    cache.append(True)
    query.edit_message_text(text="Processing Please wait this operation takes too much time...")
    chat_id = query.message.chat.id
    start = int(time())
    count_servers, checked_servers, online_servers, offline_servers, full_servers, count_clients, count_active_clients, count_inactive_clients, close_to_disabled, count_online_clients, count_deleted_clients, servers_traffic, notify, allowed_connections, remain_clients = (0,)*15
    total_usage = 0.0
    logs = ""
    with open("Pannels.txt", 'r') as txt:
        for data in txt.readlines():
            do = True
            count_servers += 1
            data = data.replace('\n', "")
            host = data.split("@")[0]
            username = (data.split(":")[0]).split("@")[1]
            password = data.split(":")[1]
            try:
                Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, server_traffic, online_c, done = Session.info()
                DB_usernames = get_db(host)
                for DB_username in DB_usernames:
                    if DB_username not in usernames:
                        delete_user(host, DB_username)
                try:
                    for i in connection_limits:
                        allowed_connections += int(i)
                except:
                    pass
                count_online_clients += online_c
                servers_traffic += float(server_traffic)
                text = f"ℹ️ {str(count_servers)}. server info \n🔗url: {host}/p/index.php\nUsername: {username}\nPass: {password}\nPort: {ports[0]}\n🔵 Clients: {str(len(usernames))}\n\n"
                online_servers += 1
                if len(usernames) >= maximum:
                    full_servers += 1
                else:
                    remain_clients += (maximum - len(usernames))
                if done is True:
                    count_clients += len(usernames)
                    for i in range(len(usernames)):
                        total_usage += float(usages[i])
                        if status[i] != "فعال":
                            if (int(days_left[i]) <= -(settings['auto_delete'])):
                                if "❌Deleted" in Session.Delete(usernames[i]):
                                    text += f"❌Deleted user {usernames[i]} & Days: {str(days_left[i])} ❌\n\n"
                                    count_deleted_clients += 1
                                    if check_exist_user(host, usernames[i]) is True:
                                        delete_user(host, usernames[i])
                            else:
                                count_inactive_clients += 1
                        else:
                            count_active_clients += 1
                            try:
                                if (0 < int(days_left[i]) <= 3) or ((("نامحدود" != traffics[i]) and (usages[i] != "0.0")) and (float(usages[i]) >= (float(traffics[i].split("گیگابایت")[0])) - 2.0)):
                                    if check_exist_user(host, usernames[i]) is True:
                                        ID, Name, Username = get_all_user_data(host, usernames[i])
                                        if checker_notify(str(ID)) is True:
                                            try:
                                                CB = "MIOU_" + host + "$" + usernames[i]
                                                Keyboard = [[InlineKeyboardButton("ℹ️اطلاعات بیشتر", callback_data=CB)]]
                                                Reply_markup = InlineKeyboardMarkup(Keyboard)
                                                if (traffics[i] == "نامحدود") and (usages[i] != "0.0"):
                                                    otherN = ""
                                                else:
                                                    otherN = " و " + traffics[i]
                                                NTX = f"⚠️اخطار\nاکانت:\n{usernames[i]}\n\n فقط {str(int(days_left[i]))} روز {otherN} مونده."
                                                bot.send_message(ID, NTX, reply_markup=Reply_markup)
                                                notify += 1
                                            except:
                                                pass
                                    close_to_disabled += 1
                            except:
                                pass
                    if "❌" in text:
                        bot.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
                    checked_servers += 1
            except Exception as e:
                offline_servers += 1
                logs += f"⭕️ Connection Error: {host}"
    count_clients -= count_deleted_clients
    remain_clients += count_deleted_clients
    if len(str(int(servers_traffic))) >= 3:
        total_usage_vps = f"{str('{:.2f}'.format(float(servers_traffic) / 1024))} TB"
    else:
        total_usage_vps = f"{str('{:.2f}'.format(float(servers_traffic)))} GB"
    if len(str(int(total_usage))) >= 3:
        totat_usage_clients = f"{str('{:.2f}'.format(float(total_usage) / 1024))} TB"
    else:
        totat_usage_clients = f"{str('{:.2f}'.format(float(total_usage)))} GB"
    text = f"🖥Servers: {str(count_servers)}\n☑️Checked: {str(checked_servers)}\n⚫️Full servers: {str(full_servers)}\n{logs}\n👤Clients: {str(count_clients)}\n✔️Active: {str(count_active_clients)}\n🔴Inactive: {str(count_inactive_clients)}\n🟢Online: {str(count_online_clients)}\n⚪️Remain: {str(remain_clients)}\n🔵Connections: {str(allowed_connections)}\n⚠️Alerts: {str(close_to_disabled)}\n❌Deleted: {str(count_deleted_clients)}\n🗳Notify: {str(notify)}\n\n🔁Server Usage: {total_usage_vps}\n🔄Clients Usage: {totat_usage_clients}\n\n⏳Time: {str(int(time() - start))}s"
    bot.send_message(chat_id, text, reply_markup=reply_markup)
    cache.clear()
    cache.append(False)


@app.on_callback_query(filters.regex('stats'))
def call_stats(bot, query):
    chat_id = query.message.chat.id
    if check_seller_exist(chat_id) is False:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="back_admin"), InlineKeyboardButton("⚫️Full Servers", callback_data='full')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Processing Please wait this operation takes too much time but not very long time as checker...")
        start = int(time())
        logs = ""
        sellers = get_all_sellers()
        sales = 0
        if sellers != []:
            for i in range(len(sellers)):
                accounts, hosts, status = get_all_accounts_by_chat_id(sellers[i][0])
                sales += len(accounts)
        count_servers, checked_servers, online_servers, offline_servers, full_servers, count_clients, count_active_clients, count_online_clients, count_inactive_clients, servers_traffic, remain_clients = (0,)*11
        with open("Pannels.txt", 'r') as txt:
            settings = get_settings()
            maximum = settings['maximum']
            for data in txt.readlines():
                count_servers += 1
                data = data.replace('\n', "")
                host = data.split("@")[0]
                username = (data.split(":")[0]).split("@")[1]
                password = data.split(":")[1]
                try:
                    Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                    info = Session.Short_info()
                    servers_traffic += float(info.split("🔃Traffic: ")[1].split(" GB")[0])
                    Clients = int(info.split("👤Clients: ")[1].split("\n")[0])
                    count_clients += Clients
                    count_active_clients += int(info.split("✔️Active: ")[1].split("\n")[0])
                    count_inactive_clients += int(info.split("🔴Disabled: ")[1].split("\n")[0])
                    count_online_clients += int((info.split("🟢Online: ")[1].split("\n")[0]).split("کاربر")[0].replace(" ", ""))
                    online_servers += 1
                    if Clients >= maximum:
                        full_servers += 1
                    else:
                        remain_clients += (maximum - Clients)
                    checked_servers += 1
                except Exception as e:
                    offline_servers += 1
                    logs += f"⭕️ Connection Error: {host}"
                if (checked_servers % 5 == 0):
                    query.edit_message_text(text=f"Collected data from {str(checked_servers)} servers...")
        if len(str(int(servers_traffic))) >= 3:
            total_usage_vps = f"{str('{:.2f}'.format(float(servers_traffic) / 1024))} TB"
        else:
            total_usage_vps = f"{str('{:.2f}'.format(float(servers_traffic)))} GB"
        text = f"📊Stats\n\n🖥Servers: {str(count_servers)}\n☑️Checked: {str(checked_servers)}\n⚫️Full: {str(full_servers)}\n{logs}\n👤 Clients: {str(count_clients)}\n✔️Active: {str(count_active_clients)}\n🔴Inactive: {str(count_inactive_clients)}\n🟢Online: {str(count_online_clients)}\n⚪️Remain: {str(remain_clients)}\n🔁Usage: {total_usage_vps}\n\n👥Bot users: {str(countuser_m())}\n💲Sellers: {str(len(sellers))}\n🏷Sales: {str(sales)}\n\n⏳Time: {str(int(time() - start))}s"
        query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("<<", callback_data='back_seller')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
        ID, Name, Username, Limit = get_seller_info(chat_id)
        text = "🏷Your sales: " + str(len(accounts)) + "\n🔻Limit: " + str(Limit)
        query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex('Filtering'))
def call_filtering(bot, query):
    keyboard = [[InlineKeyboardButton("<< back", callback_data="back_admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Processing Please wait...")
    start = int(time())
    FS = ""
    logs = ""
    count_servers, checked_servers, blocked_servers, online_servers = (0,)*4
    with open("Pannels.txt", 'r') as txt:
        for data in txt.readlines():
            count_servers += 1
            data = data.replace('\n', "")
            host = data.split("@")[0]
            username = (data.split(":")[0]).split("@")[1]
            password = data.split(":")[1]
            try:
                Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                status, server_msg = Session.IP_Check()
                if status is True:
                    blocked_servers += 1
                    FS += (f"🔴Offline: {host}\n")
                else:
                    if "Error" in server_msg:
                        checked_servers -= 1
                        FS += (f"❌unknown Error: {host}\n")
                        logs += (f"⭕️ {server_msg}: {host}\n")
                    else:
                        online_servers += 1
                checked_servers += 1
            except Exception as e:
                logs += f"⭕️ Connection Error: {host}"
            if (checked_servers % 5 == 0):
                query.edit_message_text(text=f"Collected data from {str(checked_servers)} servers...")
    text = f"{FS}\n🖥 Servers: {str(count_servers)}\n☑️Check servers: {str(checked_servers)}\n⚠️Blocked servers: {str(blocked_servers)}\n🟢Online servers: {online_servers}\n{logs}\n⏳Time: {str(int(time() - start))}s"
    query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex('full'))
def call_full(bot, query):
    keyboard = [[InlineKeyboardButton("<< back", callback_data="back_admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Processing Please wait...")
    start = int(time())
    FS = ""
    logs = ""
    count_servers, checked_servers, full_servers, remain_clients, count_clients = (0,)*5
    with open("Pannels.txt", 'r') as txt:
        settings = get_settings()
        maximum = settings['maximum']
        for data in txt.readlines():
            count_servers += 1
            data = data.replace('\n', "")
            host = data.split("@")[0]
            username = (data.split(":")[0]).split("@")[1]
            password = data.split(":")[1]
            try:
                Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                Clients = int(Session.Count_Clients())
                count_clients += Clients
                if Clients >= maximum:
                    full_servers += 1
                    FS += (f"🔴{str(Clients)}👤 {host}\n")
                else:
                    FS += (f"🔵{str(Clients)}👤 {host}\n")
                    remain_clients += (maximum - Clients)
                checked_servers += 1
            except Exception as e:
                logs += f"⭕️ Connection Error: {host}"
            if (checked_servers % 5 == 0):
                query.edit_message_text(text=f"Collected data from {str(checked_servers)} servers...")
    text = f"{FS}\n🖥 Servers: {str(count_servers)}\n☑️Check servers: {str(checked_servers)}\n⚠️Full servers: {str(full_servers)}\n👤Clients: {count_clients}\n⚪️Remain Clients: {str(remain_clients)}\n{logs}\n⏳Time: {str(int(time() - start))}s"
    query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex('JOIN'))
def call_Join(bot, query):
    try:
        chat_member = bot.get_chat_member(channel, query.message.chat.id)
        text = '🔻<b>🥰خوش اومدین</b>'
        query.edit_message_text(text, reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)
    except:
        query.answer("جوین نشدی😑", show_alert=True)


@app.on_callback_query(filters.regex('disable'))
def call_disable(bot, query):
    if check_seller_exist(query.message.chat.id) is False:
        query.edit_message_text(text="Select a server to get the user? ", reply_markup=server_cb_creator("DIS_"))
    else:
        add_cache(query.message.chat.id, "dishost")
        query.edit_message_text(text="Send the host or /cancel")


@app.on_callback_query(filters.regex('DIS_'))
def call_hosts(bot, query):
    rt = query.data
    host = rt.split("DIS_")[1]
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        add_cache(chat_id, "disable_" + host)
        query.edit_message_text(text='Send the user or /cancel')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('ENA_'))
def call_hosts(bot, query):
    rt = query.data
    host = rt.split("ENA_")[1]
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        add_cache(chat_id, "enable_" + host)
        query.edit_message_text(text='Send the user or /cancel')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('enable'))
def call_enable(bot, query):
    if check_seller_exist(query.message.chat.id) is False:
        query.edit_message_text(text="Select a server to get the user? ", reply_markup=server_cb_creator("ENA_"))
    else:
        add_cache(query.message.chat.id, "enahost")
        query.edit_message_text(text="Send the host or /cancel")


@app.on_callback_query(filters.regex('CAPASS_'))
def call_CAPASS(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        domain = data.split("CAPASS_")[1]
        cache_list = []
        cache_list.append(domain)
        add_collector(chat_id, "password", cache_list, [])
        add_cache(chat_id, "password")
        query.edit_message_text(text="Send The User or /cancel")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('ADPASS'))
def call_ADPASS(bot, query):
    if check_cache(query.message.chat.id) is False:
        query.edit_message_text(text="Select a Server to Change password of an account:", reply_markup=server_cb_creator("CAPASS_"))
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('RTRF_'))
def call_RTRF(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        domain = data.split("RTRF_")[1]
        add_cache(chat_id, "Reset_" + domain)
        query.edit_message_text(text="Send The User or /cancel")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('TrfRes'))
def call_TrfRes(bot, query):
    if check_cache(query.message.chat.id) is False:
        query.edit_message_text(text="Select a Server to Reset traffic of an account:", reply_markup=server_cb_creator("RTRF_"))
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('CTRPLUS_'))
def call_CTRPLUS(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        domain = data.split("CAPASS_")[1]
        cache_list = []
        cache_list.append(domain)
        add_collector(chat_id, "plus", cache_list, [])
        add_cache(chat_id, "plus")
        query.edit_message_text(text="Send The User or /cancel")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('TrfPlus'))
def call_TrfPlus(bot, query):
    if check_cache(query.message.chat.id) is False:
        query.edit_message_text(text="Select a Server to update traffic of an account:", reply_markup=server_cb_creator("CTRPLUS_"))
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('DM_'))
def call_DM(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        domain = data.split("DM_")[1]
        settings = get_settings()
        maximum = settings['maximum']
        if check_domain_reached_maximum(domain) is False:
            cache_list = []
            cache_list.append(domain)
            add_collector(chat_id, "domain", cache_list, [])
            delete_cache(chat_id)
            add_cache(chat_id, "name")
            query.edit_message_text(text="Send Name or /cancel")
        else:
            query.answer(f"⚠️This server reached the Maximum of {str(maximum)} Clients. select another server", show_alert=True)
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('create'))
def call_create(bot, query):
    if check_cache(query.message.chat.id) is False:
        query.edit_message_text(text="Select a Server to create an account:", reply_markup=server_cb_creator("DM_"))
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('DMNONE_'))
def call_DMNONE(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        domain = data.split("DMNONE_")[1]
        settings = get_settings()
        maximum = settings['maximum']
        if check_domain_reached_maximum(domain) is False:
            cache_list = []
            cache_list.append(domain)
            add_collector(chat_id, "domain_none", cache_list, [])
            delete_cache(chat_id)
            add_cache(chat_id, "name_none")
            query.edit_message_text(text="Send Name or /cancel")
        else:
            query.answer(f"⚠️This server reached the Maximum of {str(maximum)} Clients. select another server", show_alert=True)
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('Create_none'))
def call_create(bot, query):
    chat_id = query.message.chat.id
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="Select a Server to create an account:", reply_markup=server_cb_creator("DMNONE_"))
        else:
            ID, Name, Username, Limit = get_seller_info(chat_id)
            accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
            if (Limit == 0) or (Limit >= len(accounts)):
                keyboard = [[InlineKeyboardButton("🌎Direct", callback_data="SCC_D")]]
                keyboard.append([InlineKeyboardButton("<< Back", callback_data='back_seller')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text="Select: ", reply_markup=reply_markup)
            else:
                query.answer(f"⚠️You reached the Maximum of {str(Limit)} Clients limit. Contact to the support", show_alert=True)
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('SCC_'))
def call_SCC(bot, query):
    data = query.data
    chat_id = query.message.chat.id
    status = data.split("SCC_")[1]
    host = get_random_server()
    if host is not None:
        cache_list = []
        cache_list.append(host)
        add_collector(chat_id, "domain_none", cache_list, [])
        delete_cache(chat_id)
        add_cache(chat_id, "name_none")
        query.edit_message_text(text=f"Selected Server: {host}\nSend Name or /cancel")
    else:
        query.answer("All servers are Full❕", show_alert=True)


@app.on_callback_query(filters.regex('UP_'))
def call_up(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        host = data.split("UP_")[1]
        add_cache(chat_id, "update_" + host)
        query.edit_message_text(text='Send the user or /cancel')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('update'))
def call_update(bot, query):
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="Select a Server to update an account:", reply_markup=server_cb_creator("UP_"))
        else:
            add_cache(query.message.chat.id, "updatehost")
            query.edit_message_text(text="Send the host or /cancel")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('RM_'))
def call_RM(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        host = data.split("RM_")[1]
        add_cache(chat_id, "remove_" + host)
        query.edit_message_text(text='Send the user or /cancel')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('remove'))
def call_remove(bot, query):
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="Select a Server to remove an account:", reply_markup=server_cb_creator("RM_"))
        else:
            add_cache(query.message.chat.id, "removehost")
            query.edit_message_text(text="Send the host or /cancel")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('UI_'))
def call_UI(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        host = data.split("UI_")[1]
        add_cache(chat_id, "userinfo_" + host)
        query.edit_message_text(text='Send the user or /cancel')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('userinfo'))
def call_userinfo(bot, query):
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="Select a Server to get info of an account:", reply_markup=server_cb_creator("UI_"))
        else:
            add_cache(query.message.chat.id, "infohost")
            query.edit_message_text(text="Send the host or /cancel")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('userconfigs'))
def call_userconfigs(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        add_cache(chat_id, "userconfigs")
        keyboard = [[InlineKeyboardButton("<< Back", callback_data='back_admin')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='OK forward a message from the user or back. (if user is hidden not works)', reply_markup=reply_markup)
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('MIOU_'))
def call_MIOU(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    delete_collector(chat_id)
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    keyboard = [[InlineKeyboardButton("<< Back", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if check_exist_user(host, user) is True:
        try:
            username, password = get_host_username_password(host)
            Session = sshx.PANNEL(host, username, password, 'User', user)
            text = Session.User_info()
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except:
            query.answer("⚠️Error: بعدا تلا کنین یا به پشتیبانی پیام بدین", show_alert=True)
    else:
        query.edit_message_text(text="چیزی پیدا نشد!", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('IDADMIN_'))
def call_IDADMIN(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    delete_collector(chat_id)
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    if check_exist_user(host, user) is True:
        try:
            cb = data.split("_")[1]
            username, password = get_host_username_password(host)
            Session = sshx.PANNEL(host, username, password, 'User', user)
            text = Session.User_info()
            keyboard = [
                [InlineKeyboardButton("🔄تمدید کاربر", callback_data=('IDMNU&Update_' + cb)), InlineKeyboardButton("🗑حذف کاربر", callback_data=('IDMNU&Remove_' + cb))],
                [InlineKeyboardButton("🟢 فعال کاربر", callback_data=('IDMNU&Active_' + cb)), InlineKeyboardButton("🔴 غیر فعال کاربر", callback_data=('IDMNU&Disable_' + cb))],
                [InlineKeyboardButton("🆕ریست ترافیک", callback_data=('IDMNU&Reset_' + cb)), InlineKeyboardButton("🔑تغییر پسورد", callback_data=('IDMNU&PASSWORD_' + cb))],
                [InlineKeyboardButton("➕افزایش ترافیک", callback_data=('IDMNU&Traffic_' + cb))],
                [InlineKeyboardButton("<<", callback_data='back_admin')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            query.answer(f"⚠️Error: {str(e)}", show_alert=True)
    else:
        keyboard = [[InlineKeyboardButton("<< Back", callback_data='back_admin')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="چیزی پیدا نشد!", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('IDMNU&'))
def call_IDMNU(bot, query):
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    cb = data.split("_")[1]
    try:
        chat_id = query.message.chat.id
        status = (data.split("&")[1]).split("_")[0]
        username, password = get_host_username_password(host)
        if (status != "Update") and (status != "Remove") and (status != "PASSWORD") and (status != "Traffic"):
            Session = sshx.PANNEL(host, username, password, 'User', user)
        if status == "Active":
            text = Session.Enable()
        elif status == "Disable":
            text = Session.Disable()
        elif status == "Reset":
            text = Session.Reset_traffic()

        elif status == "Traffic":
            add_collector(chat_id, "plus", [], [])
            cache_list = [host, user]
            delete_cache(chat_id)
            add_cache(chat_id, "plus-Traffic")
            text = "Send GB only numbers (0 = unlimited) or /cancel"
            update_collector(chat_id, cache_list, [])

        elif status == "Remove":
            Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
            text = Session.Delete(user)
            if check_exist_user(host, user) is True:
                delete_user(host, user)

        elif status == "PASSWORD":
            add_collector(chat_id, "password", [], [])
            cache_list = [host, user]
            delete_cache(chat_id)
            add_cache(chat_id, "CPassword")
            text = "OK send a password or /cancel"
            update_collector(chat_id, cache_list, [])

        elif status == "Update":
            add_collector(chat_id, "update", [], [])
            cache_list = [host, user]
            delete_cache(chat_id)
            add_cache(chat_id, "GB-update")
            text = "Send GB only numbers (0 = unlimited) or /cancel"
            update_collector(chat_id, cache_list, [])
        keyboard = [[InlineKeyboardButton("<<", callback_data=('IDADMIN_' + cb))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        keyboard = [[InlineKeyboardButton("<< Back", callback_data='back_admin')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Error: {str(e)}", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ChangeWallet'))
def call_change(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        add_cache(chat_id, "change_wallet")
        query.edit_message_text(text="OK send the new card only number")
    else:
        query.answer("Please /cancel it first", show_alert=True)


@app.on_callback_query(filters.regex('wallet'))
def call_wallet(bot, query):
    keyboard = [[InlineKeyboardButton("🔧Change", callback_data='ChangeWallet')], [InlineKeyboardButton("<< Back", callback_data='settings')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    name, username, wallet, crypto = get_wallet_info()
    text = f"💳Wallet: <pre>{str(wallet)}</pre>\n\n👤Last admin changed the info \nName: {name}\nusername: @{username}"
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Card'))
def call_card(bot, query):
    keyboard = [[InlineKeyboardButton("🔧Change", callback_data='Change')], [InlineKeyboardButton("<< Back", callback_data='settings')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    name, username, card = get_card_info()
    text = f"💳Card: <pre>{str(card)}</pre>\n\n👤Last admin changed the info \nName: {name}\nusername: @{username}"
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Change'))
def call_change(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        add_cache(chat_id, "change")
        query.edit_message_text(text="OK send the new card only number")
    else:
        query.answer("Please /cancel it first", show_alert=True)


@app.on_callback_query(filters.regex('ANS_'))
def call_ANS(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        cache_list = [data.split("ANS_")[1]]
        add_collector(chat_id, "answer", cache_list, [])
        add_cache(chat_id, "answer")
        bot.send_message(chat_id, "Send your message or /cancel")
    else:
        bot.send_message(chat_id, "Please /cancel it first")


@app.on_callback_query(filters.regex("RLS_"))
def call_RLS(bot, query):
    data = query.data
    chat_id = int(data.split("RLS_")[1])
    keyboard = [[InlineKeyboardButton("<<", callback_data='sellers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    delete_seller(chat_id)
    sellers_id_add_list()
    query.edit_message_text(text="Removed✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex("ELS_"))
def call_ELS(bot, query):
    data = query.data
    chat_id = int(data.split("ELS_")[1])
    text = "Ok send only a number\n\n0 = unlimited\n10 = 10 clients"
    keyboard = [[InlineKeyboardButton("<<", callback_data=('SLM_' + str(chat_id)))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup)
    delete_cache(query.message.chat.id)
    add_cache(query.message.chat.id, ("Edit_limit#" + str(chat_id)))


@app.on_callback_query(filters.regex("SLM_"))
def call_SLM(bot, query):
    delete_cache(query.message.chat.id)
    data = query.data
    chat_id = int(data.split("SLM_")[1])
    accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
    ID, Name, Username, Limit = get_seller_info(chat_id)
    text = f"ID: {str(chat_id)}\nName: {Name}\nUsername: @{Username}\n\n🏷sales: {str(len(accounts))}\n🔻Limit: {Limit}"
    keyboard = [
        [InlineKeyboardButton("🗑Remove", callback_data=('RLS_' + str(chat_id))), InlineKeyboardButton("✏️Edit limit", callback_data=("ELS_" + str(chat_id)))],
        [InlineKeyboardButton("<<", callback_data='sellers')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex("ADDSELLER"))
def call_ADDSELLER(bot, query):
    delete_cache(query.message.chat.id)
    add_cache(query.message.chat.id, "add_seller")
    keyboard = [[InlineKeyboardButton("<<", callback_data='sellers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="OK, Forward a message from the seller. The seller must not be Hidden.", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('sellers'))
def call_sellers(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    sellers = get_all_sellers()
    keyboard = []
    if sellers != []:
        if len(sellers) >= 2:
            if len(sellers) % 2 == 0:
                for i in range(0, len(sellers) - 1, 2):
                    keyboard.append([InlineKeyboardButton(sellers[i][1], callback_data=("SLM_" + str(sellers[i][0]))), InlineKeyboardButton(sellers[i + 1][1], callback_data=("SLM_" + str(sellers[i + 1][0])))])
            else:
                for i in range(0, len(sellers) - 1, 2):
                    keyboard.append([InlineKeyboardButton(sellers[i][1], callback_data=("SLM_" + str(sellers[i][0]))), InlineKeyboardButton(sellers[i + 1][1], callback_data=("SLM_" + str(sellers[i + 1][0])))])
                keyboard.append([InlineKeyboardButton(sellers[-1][1], callback_data=("SLM_" + str(sellers[-1][0])))])
        elif len(sellers) == 1:
            keyboard.append([InlineKeyboardButton(sellers[0][1], callback_data=("SLM_" + str(sellers[0][0])))])
    keyboard.append([InlineKeyboardButton("➕ Add Seller", callback_data='ADDSELLER')])
    keyboard.append([InlineKeyboardButton("<< Back", callback_data='back_admin')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="🔻Select: ", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('price'))
def call_price(bot, query):
    keyboard = []
    keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (get_settings())['list']
    query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex('buy'))
def call_buy(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    data = query.data
    if "_" in data:
        code = data.split('buy_')[1]
        delete_code_buy(code)
    keyboard = []
    settings = get_settings()
    if settings['buy'] == 'on':
        text = "یکی از گزینه هارو انتخاب کنین:\n\n"
        for i in range(len(settings['prices'])):
            if settings['traffic'][i] == 0:
                traffic = "نامحدود"
            else:
                traffic = str(settings['traffic'][i]) + " گیگ"
            text += f"{str(i + 1)}. {traffic} - {str(settings['connections'][i])} کاربر - {str(settings['days'][i])} روزه - {str(settings['prices'][i])} تومن\n"
            tcb = f"{traffic} - {str(settings['connections'][i])} کاربر - {str(settings['days'][i])} روزه - {str(settings['prices'][i])} تومن"
            cb = f"BU_{str(settings['days'][i])}-{str(settings['traffic'][i])}#{str(settings['connections'][i])}&{str(settings['prices'][i])}"
            keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="فروش غیرفعاله", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('CC_'))
def call_CC(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("CC_")[1]
        days = data.split("-")[0]
        GB = data.split("-")[1].split("#")[0]
        client = data.split("#")[1].split("&")[0]
        price = data.split("&")[1]
        name, username, card = get_card_info()
        add_cache(chat_id, "buy")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='buy_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [days, GB, client, price, query.message.chat.first_name]
        add_code_buy(chat_id, Code, "add", cache_list)
        text = f"""
مبلغ:
{price} تومن
به شماره کارت :
<pre>{str(card)}</pre>
واریز کنین و سپس رسید عکس خودرا بفرستید
یکبار روی شماره کارت بزنین کپی میشه


برای کنسل کردن دکمه  بک بزنید
            """
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)


@app.on_callback_query(filters.regex('TR_'))
def call_TR(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("TR_")[1]
        days = data.split("-")[0]
        GB = data.split("-")[1].split("#")[0]
        client = data.split("#")[1].split("&")[0]
        price = data.split("&")[1]
        name, username, wallet, crypto = get_wallet_info()
        add_cache(chat_id, "buy")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='buy_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [days, GB, client, price, query.message.chat.first_name]
        add_code_buy(chat_id, Code, "add", cache_list)
        price = trx_price(price)
        text = f"""
مبلغ: 
{price}

به آدرس ترون :
<pre>{wallet}</pre>
واریز کنین و سپس رسید عکس خودرا بفرستید
یکبار روی آدرس بزنین کپی میشه


برای کنسل کردن دکمه  بک بزنید
            """
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)


@app.on_callback_query(filters.regex('BU_'))
def call_BU(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("BU_")[1]
        cb_cc = "CC_" + data
        cb_tr = "TR_" + data
        keyboard = [
            [InlineKeyboardButton("💳کارت به کارت", callback_data=cb_cc), InlineKeyboardButton("💲ترون", callback_data=cb_tr)]
        ]
        keyboard.append([InlineKeyboardButton("<<", callback_data='buy')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(text="روش پرداختو انتخاب کن:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except:
            query.edit_message_text(text="📃روش پرداختو انتخاب کن:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)


@app.on_callback_query(filters.regex("Confirmed_"))
def call_Confirmed(bot, query):
    data = query.data
    code = data.split("Confirmed_")[1]
    if check_code_exists(code) is True:
        chat_id, cache_list = get_code_buy_data(code)
        try:
            username_admin = "@" + query.message.chat.username
        except:
            username_admin = "Null"
        days = int(cache_list[0])
        GB = int(cache_list[1])
        connection_limit = int(cache_list[2])
        name = cache_list[4]
        if check_seller_exist(chat_id) is True:
            USERNAME = cache_list[-1]
        else:
            USERNAME = "None"
        try:
            host = get_random_server()
            if host is None:
                query.answer(f"Error: Add a host", show_alert=True)
            user = host.split('.')[0] + "a" + str(randint(1243, 6523))
            passw = str(randint(214254, 999999))
            username, password = get_host_username_password(host)
            Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
            text = f"🥰مرسی از خریدتون\n\n"
            text += Session.Create(user, passw, connection_limit, days, GB)
            if "Error" not in text:
                port, udgpw = Session.Ports()
                add_check_admin(query.message.chat.id, query.message.chat.first_name, username_admin, code, "Yes", int(time()))
                url = f"ssh://{user}:{passw}@{host}:{port}"
                photo = QR_Maker(url)
                text += "\n\nURL: " + "<pre>" + url + "</pre>"
                bot.send_photo(chat_id, open(photo, 'rb'), text, parse_mode=enums.ParseMode.HTML)
                os.remove(photo)
                add_user_db(chat_id, name, USERNAME, user, host)
                if check_seller_exist(chat_id) is False:
                    keyboard = [[InlineKeyboardButton("آموزش اتصال📡", callback_data='help')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.send_message(chat_id, "برای آموزش وصل شدن به سرویس دکمه پایینو بزنین", reply_markup=reply_markup)
                delete_code_buy(code)
                query.answer("Details sent to the user", show_alert=True)
            else:
                query.answer(f"Error: {text}", show_alert=True)
        except Exception as e:
            query.answer(f"Error: {str(e)}", show_alert=True)
    else:
        if check_admin_confirm(code) is True:
            Name, Username, Confirm, Checked = get_check_admin_data(code)
            query.answer(f"Checked by {Name}, Username: {Username}, Confirm: {Confirm}", show_alert=True)
        else:
            query.answer(f"Checked by another admin.", show_alert=True)


@app.on_callback_query(filters.regex("NO❌_"))
def call_NO(bot, query):
    data = query.data
    code = data.split("NO❌_")[1]
    if check_code_exists(code) is True:
        try:
            username = "@" + query.message.chat.username
        except:
            username = "Null"
        add_check_admin(query.message.chat.id, query.message.chat.first_name, username, code, "No", int(time()))
        chat_id, cache_list = get_code_buy_data(code)
        bot.send_message(chat_id, "خریدتون تایید نشد☹️ اگه ما اشتباه میکنیم پیام بدین به پشتیبانی 🙂")
        delete_code_buy(code)
        query.answer("Details sent to the user", show_alert=True)
    else:
        if check_admin_confirm(code) is True:
            Name, Username, Confirm, Checked = get_check_admin_data(code)
            query.answer(f"Checked by {Name}, Username: {Username}, Confirm: {Confirm}", show_alert=True)
        else:
            query.answer(f"Checked by another admin.", show_alert=True)


@app.on_callback_query(filters.regex('upgrade'))
def call_upgrade(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    data = query.data
    if "_" in data:
        code = data.split('upgrade_')[1]
        delete_code_buy(code)
    accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
    keyboard = []
    settings = get_settings()
    if status is False:
        query.answer("سرویسی پیدا نشد. اگه سرویسی دارین دکمه اطلاعات سرویس بزنین و بفرستین 🙂", show_alert=True)
    else:
        if settings['buy'] == 'on':
            if len(accounts) >= 2:
                if len(accounts) % 2 == 0:
                    for i in range(0, len(accounts) - 1, 2):
                        keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("UPG_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("UPG_" + hosts[i + 1] + "$" + accounts[i + 1]))])
                else:
                    for i in range(0, len(accounts) - 1, 2):
                        keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("UPG_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("UPG_" + hosts[i + 1] + "$" + accounts[i + 1]))])
                    keyboard.append([InlineKeyboardButton(accounts[-1], callback_data=("UPG_" + hosts[-1] + "$" + accounts[-1]))])
            else:
                keyboard.append([InlineKeyboardButton(accounts[0], callback_data=("UPG_" + hosts[0] + "$" + accounts[0]))])
            keyboard.append([InlineKeyboardButton("<<", callback_data='back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text="یکی برای تمدید انتخاب کن", reply_markup=reply_markup)
        else:
            keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text="فروش غیرفعاله", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('UPG_'))
def call_UPG(bot, query):
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    if check_exist_user(host, user) is True:
        keyboard = []
        query.edit_message_text(text="wait...")
        username, password = get_host_username_password(host)
        Session = sshx.PANNEL(host, username, password, 'User', user)
        text = "اطلاعات سرویس :\n\n" + Session.User_info()
        if "Error" in text:
            text = "مشکلی پیش اومده بعدا تلاش کنین یا به پشتیبانی اطلاع بدین"
        else:
            text += "\n\nبرای تمدید یکی از گزینه هارو انتخاب کنین🙂"
            keyboard = []
            settings = get_settings()
            for i in range(len(settings['prices'])):
                if settings['traffic'][i] == 0:
                    traffic = "نامحدود"
                else:
                    traffic = str(settings['traffic'][i]) + " گیگ"
                tcb = f"{traffic} - {str(settings['connections'][i])} کاربر - {str(settings['days'][i])} روزه - {str(settings['prices'][i])} تومن"
                cb = f"UPB_{str(settings['days'][i])}-{str(settings['traffic'][i])}#{str(settings['connections'][i])}&{str(settings['prices'][i])}:{user}@{host}"
                keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        query.answer("سرویسی پیدا نشد☹️", show_alert=True)


@app.on_callback_query(filters.regex('UPB_'))
def call_BU(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("UPB_")[1]
        cb_cc = "UPC_" + data
        cb_tr = "UPTXR_" + data
        keyboard = [
            [InlineKeyboardButton("💳کارت به کارت", callback_data=cb_cc), InlineKeyboardButton("💲ترون", callback_data=cb_tr)]
        ]
        keyboard.append([InlineKeyboardButton("<<", callback_data='upgrade')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(text="روش پرداختو انتخاب کن:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except:
            query.edit_message_text(text="📃روش پرداختو انتخاب کن:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)

@app.on_callback_query(filters.regex('UPTXR_'))
def call_UPTXR(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("UPTXR_")[1]
        days = data.split("-")[0]
        GB = data.split("-")[1].split("#")[0]
        connection_limit = data.split("#")[1].split("&")[0]
        price = data.split("&")[1].split(":")[0]
        user = (data.split("@")[0]).split(":")[1]
        host = data.split("@")[1]
        name, username, wallet, crypto = get_wallet_info()
        add_cache(chat_id, "upgrade")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='upgrade_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [days, GB, connection_limit, price, user, host]
        add_code_buy(chat_id, Code, "upgrade", cache_list)
        price = trx_price(price)
        text = f"""
مبلغ: 
{price}

به آدرس ترون :
<pre>{wallet}</pre>
واریز کنین و سپس رسید عکس خودرا بفرستید
یکبار روی آدرس بزنین کپی میشه


برای کنسل کردن دکمه  بک بزنید
            """
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)


@app.on_callback_query(filters.regex('UPC_'))
def call_UPC(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("UPC_")[1]
        days = data.split("-")[0]
        GB = data.split("-")[1].split("#")[0]
        connection_limit = data.split("#")[1].split("&")[0]
        price = data.split("&")[1].split(":")[0]
        user = (data.split("@")[0]).split(":")[1]
        host = data.split("@")[1]
        name, username, card = get_card_info()
        add_cache(chat_id, "upgrade")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='upgrade_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [days, GB, connection_limit, price, user, host]
        add_code_buy(chat_id, Code, "upgrade", cache_list)
        text = f"""
مبلغ:
{price} تومن
به شماره کارت :
<pre>{str(card)}</pre>
واریز کنید و سپس رسید عکس خودرا بفرستید
یکبار روی شماره کارت بزنید کپی میشه

اگر روش پرداخت دیگه ای مد نظر دارین به پشتیبانی پیام بدین

برای کنسل کردن دکمه  بک بزنید
            """
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)


@app.on_callback_query(filters.regex("ConfirmUPGRADE_"))
def call_Confirmed_UPGRADE(bot, query):
    data = query.data
    code = data.split("ConfirmUPGRADE_")[1]
    if check_code_exists(code) is True:
        chat_id, cache_list = get_code_buy_data(code)
        try:
            username_admin = "@" + query.message.chat.username
        except:
            username_admin = "Null"
        days = int(cache_list[0])
        GB = int(cache_list[1])
        connection_limit = int(cache_list[2])
        user = cache_list[4]
        host = cache_list[5]
        username, password = get_host_username_password(host)
        try:
            text = f"🥰مرسی از خریدتون\n\n"
            Session = sshx.PANNEL(host, username, password, 'User', user)
            '''data = Session.User_info()
            try:
                old_days = int((data.split('Days : ')[1]).split("\n")[0])
                if old_days >= 1:
                    days += old_days
            except:
                pass'''
            server_msg = Session.Update(GB, days, connection_limit)
            text += server_msg
            if "Error" not in server_msg:
                add_check_admin(query.message.chat.id, query.message.chat.first_name, username_admin, code, "Yes", int(time()))
                if check_seller_exist(chat_id) is False:
                    keyboard = [[InlineKeyboardButton("آموزش اتصال📡", callback_data='help')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.send_message(chat_id, f"🥰اکانتتون تمدید شد:\n{user}\n\nبرای آموزش وصل شدن به سرویس دکمه پایینو بزنین", reply_markup=reply_markup)
                else:
                    bot.send_message(chat_id, f"✅ تمدید شد\n\nUsername : {user}\nSSH Host : {host}")
                delete_code_buy(code)
                query.answer("Details sent to the user", show_alert=True)
            else:
                query.answer(f"Error: {server_msg}", show_alert=True)
        except Exception as e:
            query.answer(f"Error: {str(e)}", show_alert=True)
    else:
        if check_admin_confirm(code) is True:
            Name, Username, Confirm, Checked = get_check_admin_data(code)
            query.answer(f"Checked by {Name}, Username: {Username}, Confirm: {Confirm}", show_alert=True)
        else:
            query.answer(f"Checked by another admin.", show_alert=True)


@app.on_callback_query(filters.regex('config'))
def call_config(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        add_cache(chat_id, "config")
        keyboard = [[InlineKeyboardButton("<< Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = """
خب همون پیامی که ادمین براتون فرستاده بود کپی کنین و اینجا بفرستین مثل:
SSH Host: sub.domain.com
Port : 22
Udgpw : 7301-7309
Username : user124
...


یا آدرس سرور سرویستون بفرستین 
مثلا:
sub.domain.com
        """
        query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        query.edit_message_text(text="لطفا /cancel را بفرستید ")


@app.on_callback_query(filters.regex('message'))
def call_message(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        add_cache(chat_id, "message")
        query.edit_message_text(text='Send your message (text, voice) or forward /cancel')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('service'))
def call_service(bot, query):
    chat_id = query.message.chat.id
    accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
    keyboard = []
    if status is True:
        if len(accounts) >= 2:
            if len(accounts) % 2 == 0:
                for i in range(0, len(accounts) - 1, 2):
                    keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("ID_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("ID_" + hosts[i + 1] + "$" + accounts[i + 1]))])
            else:
                for i in range(0, len(accounts) - 1, 2):
                    keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("ID_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("ID_" + hosts[i + 1] + "$" + accounts[i + 1]))])
                keyboard.append([InlineKeyboardButton(accounts[-1], callback_data=("ID_" + hosts[-1] + "$" + accounts[-1]))])
        else:
            keyboard.append([InlineKeyboardButton(accounts[0], callback_data=("ID_" + hosts[0] + "$" + accounts[0]))])
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"انتخاب کنین:", reply_markup=reply_markup)
    else:
        query.answer("چیزی پیدا نشد. اگه سرویسی دارین دکمه اطلاعات سرویس بزنین و سرویستون بفرستین 🙂", show_alert=True)


@app.on_callback_query(filters.regex('ID_'))
def call_ID(bot, query):
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    cb = host + "$" + user
    if check_exist_user(host, user) is True:
        try:
            username, password = get_host_username_password(host)
            Session = sshx.PANNEL(host, username, password, 'User', user)
            text = Session.User_info()
            keyboard = [[InlineKeyboardButton("🔑تغییر پسورد", callback_data=('SELFCPA_' + cb))]]
            settings = get_settings()
            if settings['buy'] == 'on':
                keyboard.append([InlineKeyboardButton("🔄تمدید", callback_data=("UPG_" + cb))])
                #Traffic
            keyboard.append([InlineKeyboardButton("<<", callback_data='service')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except:
            query.answer("⚠️خطا لطفا بعدا تلا کنین", show_alert=True)
    else:
        keyboard = [[InlineKeyboardButton("<< Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="چیزی پیدا نشد!", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('support'))
def call_support(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    if check_cache(chat_id) is False:
        keyboard = []
        randomize = []
        for i in range(len(admin_id)*100):
            if len(admin_id) != len(randomize):
                r = choice(admin_id)
                if r not in randomize:
                    randomize.append(r)
            else:
                break
        for i in range(len(randomize)):
            keyboard.append([InlineKeyboardButton(f"پشتیبانی {str(i + 1)}", callback_data=("SUPRT_" + str(randomize[i])))])
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="🫡یکی از گزینه هارو انتخاب کنین", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="لطفا /cancel را بفرستید ")


@app.on_callback_query(filters.regex('SUPRT_'))
def call_support_choose(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    data = query.data
    ad = data.split("SUPRT_")[1]
    add_cache(chat_id, f"support {str(admin_id.index(int(ad)))}")
    keyboard = [[InlineKeyboardButton("<< Back", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="خب اسکرین شات یا پیامتون بفرستین 🫡", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('FREEPX'))
def call_FREEPX(bot, query):
    keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    proxy = get_settings()['proxy']
    if proxy == "None":
        query.answer("این بخش غیرفعاله☹️", show_alert=True)
    else:
        text = "Telegram Proxy:\n\n" + proxy
    query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex('help'))
def call_help(bot, query):
    keyboard = [
        [InlineKeyboardButton("IOS🍏", callback_data='IOS'), InlineKeyboardButton("Android🤖", callback_data='Android')],
        [InlineKeyboardButton("Mac🍎", callback_data='Mac'), InlineKeyboardButton("Windows💻", callback_data='Windows')]
    ]
    keyboard.append([InlineKeyboardButton("<<", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "سیستم عامل مورد نظرتو انتخاب کن🫡"
    query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex('IOS'))
def call_ios(bot, query):
    keyboard = [[InlineKeyboardButton("<<", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '<b>لینک دانلود برای گوشی های آیفون 🍏</b>\n\n⭐️<a href="https://apps.apple.com/us/app/napsternetv/id1629465476"><b>NapsternetV ios 15.0+</b></a>\n\n▫️بقیه برنامه ها برای پروتکل SSH\n⚪️<a href="https://apps.apple.com/us/app/http-injector/id1659992827"><b>HTTP Injector ios 15.0+</b></a>\n⚪️<a href="https://apps.apple.com/us/app/streisand/id6450534064"><b>Streisand ios 14.0 +</b></a>\n⚪️<a href="https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690"><b>V2box ios 15.0 +</b></a>\n\n➖➖➖➖➖➖➖➖\n\n🔻آموزش برنامه نپستر پروتکل SSH:\nhttps://t.me/vipinowedu/17\n\n\n🔹برنامه Streisand و V2box هم مثل همین برنامه هست\n'
    query.edit_message_text(text=text, reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Android'))
def call_Android(bot, query):
    keyboard = [[InlineKeyboardButton("<<", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '<b>لینک دانلود برای گوشی های اندروید 🤖</b>\n\n⚪️<a href="https://play.google.com/store/apps/details?id=com.napsternetlabs.napsternetv"><b>NapsternetV Google play</b></a>\n⚫️<a href="https://t.me/vipinowedu/25"><b> در تلگرام NapsternetV فایل نصبی</b></a>\n⚪️<a href="https://play.google.com/store/apps/details?id=com.evozi.injector&hl=en&gl=US"><b>HTTP Injector Google play</b></a>\n⚪️<a href="https://play.google.com/store/apps/details?id=com.evozi.injector.lite"><b>HTTP Injector Lite Google play مناسب اندروید پایین 4.3</b></a>\n⚪️<a href="https://play.google.com/store/apps/details?id=com.netmod.syna&hl=en_US"><b>NetMod Google play</b></a>\n\n➖➖➖➖➖➖➖➖\n\n🔻آموزش برنامه نپستر پروتکل SSH:\nhttps://t.me/vipinowedu/18\n'
    query.edit_message_text(text=text, reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Mac'))
def call_Mac(bot, query):
    keyboard = [[InlineKeyboardButton("<<", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '<b>لینک دانلود برای مک 🍎</b>\n\nℹ️ برای سیستم عامل های مک برنامه های آیفون استفاده میشه\n\n⭐️<a href="https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690"><b>v2box macOS 11.0 +</b></a>\n⭐️<a href="https://apps.apple.com/us/app/streisand/id6450534064"><b>Streisand macOS 11.0 +</b></a>\n⭐️<a href="https://apps.apple.com/us/app/foxray/id6448898396"><b>Foxray macOS 13.0+</b></a>\n\n▫️<a href="https://apps.apple.com/us/app/ssh-proxy/id597790822?mt=12"><b>SSH proxy macOS 10.9+</b></a>\n\n➖➖➖➖➖➖➖➖\n\n🔻آموزش برنامه V2box پروتکل Vless:\nhttps://t.me/vipinowedu/36\n\nبرنامه Streisand هم مثل همین برنامه هست'
    query.edit_message_text(text=text, reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Windows'))
def call_Windows(bot, query):
    keyboard = [[InlineKeyboardButton("<<", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '<b>لینک دانلود برای ویندوز 🖥</b>\n\nℹ️ وارد لینک زیر بشین کلمه آبی چینی بالا رو بزنین\nصفحه که با ز شد آخر صفحه برین اینو دانلود کنین:\nv2rayN-With-Core.zip\n \n▫️<a href="https://github.com/2dust/v2rayN/releases"><b>V2rayN</b></a>\nبرای ویندوز 10 به پایین اینم دانلود شه:\n🔹<a href="https://download.visualstudio.microsoft.com/download/pr/513d13b7-b456-45af-828b-b7b7981ff462/edf44a743b78f8b54a2cec97ce888346/windowsdesktop-runtime-6.0.15-win-x64.exe"><b>Microsoft .NET 6.0 Desktop Runtime</b></a>\n\n▫️<a href="https://sourceforge.net/projects/netmodhttp/"><b>Netmod ( SSH )</b></a>\n▪️<a href="https://t.me/vipinowedu/52"><b>فایل نصبی Netmod</b></a>\n▫️<a href="https://sourceforge.net/projects/respite-vpn/"><b>Respite VPN ( SSH )</b></a>\n\n\n➖➖➖➖➖➖➖➖\n\n🔻آموزش برنامه Netmod پروتکل SSH:\nhttps://t.me/vipinowedu/53'
    query.edit_message_text(text=text, reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('CTBKup'))
def call_bktimer(bot, query):
    chat_id = query.message.chat.id
    add_cache(chat_id, "backup_timer")
    text = "OK send a number 1-72"
    keyboard = [[InlineKeyboardButton("<<", callback_data='Backup')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('BKupON'))
def call_bkon(bot, query):
    if os.stat("Pannels.txt").st_size == 0:
        query.edit_message_text(text="There's not any server /add a server")
    else:
        if True:
            if backup[0] is False:
                chat_id = query.message.chat.id
                query.edit_message_text(text=f"Starting... delay every {str(get_settings()['backup'])}h")
                backup.clear()
                backup.append(True)
                run_backup.clear()
                run_backup.append(True)
                first = True
                start_time = 1
                while True:
                    if run_backup[0] is True:
                        text = ""
                        if ((int(time()) - start_time) < ((get_settings()['backup'] * 60) * 60)) and (first is False):
                            sleep(3)
                        else:
                            count_all, count_errors, count_goods = (0,)*3
                            with open("Pannels.txt", 'r') as txt:
                                for data in txt.readlines():
                                    do = True
                                    count_all += 1
                                    data = data.replace('\n', "")
                                    host = data.split("@")[0]
                                    username = (data.split(":")[0]).split("@")[1]
                                    password = data.split(":")[1]
                                    session = 'ssh/' + host + ".session"
                                    if Path(session).is_file() is False:
                                        if sshx.Login(username, password, host) is False:
                                            do = False
                                    if do is True:
                                        try:
                                            Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                                            status, content = Session.Backup_content()
                                            if status is True:
                                                f = folder + "/" + host + ".sql"
                                                if Path(f).is_file() is True:
                                                    os.remove(f)
                                                with open(f, 'wb') as file:
                                                    file.write(content)
                                                sleep(1)
                                                bot.send_document(chat_id, document=open(f, 'rb'), caption=f"Saved at {f}", file_name=f)
                                                count_goods += 1
                                            else:
                                                count_errors += 1
                                                text += f"{content} | {host}"
                                        except Exception as e:
                                            count_errors += 1
                                            text += f"{str(e)} | {host}"
                                    else:
                                        count_errors += 1
                                        text += f"Error To Login: {host}"
                            bot.send_message(chat_id, f"🖥Servers: {str(count_all)}\n🟢Goods: {str(count_goods)}\n🔴Errors: {str(count_errors)}\n\nErrors info: {text}")
                            start_time = int(time())
                            first = False
                    else:
                        break
            else:
                query.answer("Already ON", show_alert=True)


@app.on_callback_query(filters.regex('BKupOFF'))
def call_bkoff(bot, query):
    if backup[0] is True:
        backup.clear()
        backup.append(False)
        run_backup.clear()
        run_backup.append(False)
        keyboard = [[InlineKeyboardButton("<<", callback_data='Backup')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Stopped.", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("Already OFF", show_alert=True)


@app.on_callback_query(filters.regex('BKupBot'))
def call_bkbot(bot, query):
    chat_id = query.message.chat.id
    query.edit_message_text(text="Sending...")
    files = ["All.txt", "ssh.db", "data.json", "Pannels.txt", "logs.txt"]
    logs = "Done✔️\n\nLogs:\n\n"
    for file in files:
        try:
            bot.send_document(chat_id, document=open(file, 'rb'), file_name=file)
        except Exception as e:
            logs += ("File: " + file + " " + str(e) + "\n")
        sleep(0.5)
    bot.send_message(chat_id, logs)


@app.on_callback_query(filters.regex('Backup'))
def call_backup(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("تغییر تایم بکاپ 🕔", callback_data='CTBKup')],
        [InlineKeyboardButton("روشن🟢", callback_data='BKupON')],
        [InlineKeyboardButton("خاموش🔴", callback_data='BKupOFF')],
        [InlineKeyboardButton("بکاپ ربات🤖", callback_data='BKupBot')]
    ]
    settings = get_settings()
    if backup[0] is False:
        backup_status = "OFF ❌"
    else:
        backup_status = "ON ✅"
    text = '<b>Backup Settings</b>\n\n' + "🔄Status\n\n" + "Backup: " + backup_status + "\n" + "🕔Timer: " + str(settings['backup']) + " hours"
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('WSMSG'))
def call_WSMSG(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ESMSG')],
    ]
    settings = get_settings()
    text = '<b>Start MSG Settings</b>\n\n' + "Text:\n\n" + settings['start']
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('ESMSG'))
def call_ESMSG(bot, query):
    chat_id = query.message.chat.id
    add_cache(chat_id, "Start_message")
    text = "OK send the text"
    keyboard = [[InlineKeyboardButton("<<", callback_data='WSMSG')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('WLMSG'))
def call_WLMSG(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ELMSG')],
    ]
    settings = get_settings()
    text = '<b>Price MSG Settings</b>\n\n' + "Text:\n\n" + settings['list']
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('ELMSG'))
def call_ELMSG(bot, query):
    chat_id = query.message.chat.id
    add_cache(chat_id, "Price_message")
    text = "OK send the text"
    keyboard = [[InlineKeyboardButton("<<", callback_data='WLMSG')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('sponser'))
def call_sponser(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ESship')],
        [InlineKeyboardButton("Delete✖️", callback_data='Delship')],
    ]
    settings = get_settings()
    text = '<b>Sponser Settings</b>\n\n' + "Current: " + settings['sponser']
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Delship'))
def call_Delship(bot, query):
    settings = get_settings()
    settings['sponser'] = "None"
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='sponser')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('ESship'))
def call_ESship(bot, query):
    chat_id = query.message.chat.id
    add_cache(chat_id, "Sponser")
    text = "OK add the bot in the channel or group then send the username like @channel"
    keyboard = [[InlineKeyboardButton("<<", callback_data='sponser')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('AutoDelete'))
def call_AutoDelete(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='EADel')],
    ]
    settings = get_settings()
    text = '<b>Auto Delete Settings</b>\n\n' + "Current: " + str(settings['auto_delete']) + " Days"
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EADel'))
def call_EADel(bot, query):
    chat_id = query.message.chat.id
    add_cache(chat_id, "AutoDelete")
    text = "OK send only number"
    keyboard = [[InlineKeyboardButton("<<", callback_data='AutoDelete')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('USD'))
def call_USD(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='Edollar')],
    ]
    settings = get_settings()
    text = '<b>USD Settings</b>\n\n' + "Current: " + str(settings['usd']) + " Toman"
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Edollar'))
def call_Edollar(bot, query):
    chat_id = query.message.chat.id
    add_cache(chat_id, "USD")
    text = "OK send only number\n\nبه تومن بفرستین مثل 50000"
    keyboard = [[InlineKeyboardButton("<<", callback_data='USD')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('maximum'))
def call_maximum(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='EMXM')],
    ]
    settings = get_settings()
    text = '<b>Maximum Settings</b>\n\n' + "Current: " + str(settings['maximum']) + " Clients"
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EMXM'))
def call_EMXM(bot, query):
    chat_id = query.message.chat.id
    add_cache(chat_id, "maximum")
    text = "OK send only number"
    keyboard = [[InlineKeyboardButton("<<", callback_data='maximum')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('BSOPtion'))
def call_BSOPtion(bot, query):
    settings = get_settings()
    if settings['buy'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    keyboard = [
        [InlineKeyboardButton(f"{cb} {emoji_cb}", callback_data=f'EBS_{cb}')],
    ]
    text = '<b>Shop Settings</b>\n\n' + "Current: " + settings['buy'] + " " + emoji
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EBS_'))
def call_EBS(bot, query):
    data = query.data
    buy = data.split("EBS_")[1]
    settings = get_settings()
    settings['buy'] = buy
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='BSOPtion')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ADMINPRICES'))
def call_ADMINPRICES(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Delete✖️", callback_data='DAPR')],
        [InlineKeyboardButton("Add➕", callback_data='AAPR')]
    ]
    settings = get_settings()
    currnet = ""
    for i in range(len(settings['prices'])):
        if settings['traffic'][i] == 0:
            traffic = "نامحدود"
        else:
            traffic = str(settings['traffic'][i]) + " گیگ"
        currnet += f"{str(i + 1)}. {traffic} - {str(settings['connections'][i])} کاربر - {str(settings['days'][i])} روزه - {str(settings['prices'][i])} تومن\n"
    text = '<b>Prices Settings</b>\n\n' + "Current: \n" + currnet
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('AAPR'))
def call_AAPR(bot, query):
    chat_id = query.message.chat.id
    add_collector(chat_id, "domain_none", [], [])
    delete_cache(chat_id)
    add_cache(chat_id, "A_price")
    text = "OK send the price only number, Like: 50000 (it means 50000 Toman) or /cancel"
    query.edit_message_text(text=text, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('DAPR'))
def call_DAPR(bot, query):
    settings = get_settings()
    if len(settings['traffic']) == 0:
        query.answer("There's not anything, add new one", show_alert=True)
    else:
        keyboard = []
        for i in range(len(settings['prices'])):
            if settings['traffic'][i] == 0:
                traffic = "نامحدود"
            else:
                traffic = str(settings['traffic'][i]) + " گیگ"
            tcb = f"{traffic} - {str(settings['connections'][i])} کاربر - {str(settings['days'][i])} روزه - {str(settings['prices'][i])} تومن"
            cb = "DSELP_" + str(i)
            keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
        keyboard.append([InlineKeyboardButton("<<", callback_data='ADMINPRICES')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Ok choose to delete:", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('DSELP_'))
def call_DSELP(bot, query):
    data = query.data
    i = int(data.split("DSELP_")[1])
    settings = get_settings()
    prices = settings['prices']
    del prices[i]
    connections = settings['connections']
    del connections[i]
    days = settings['days']
    del days[i]
    traffic = settings['traffic']
    del traffic[i]
    settings['prices'] = prices
    settings['connections'] = connections
    settings['days'] = days
    settings['traffic'] = traffic
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='ADMINPRICES')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('FLCHON'))
def call_FLCHON(bot, query):
    if os.stat("Pannels.txt").st_size == 0:
        query.edit_message_text(text="There's not any server /add a server")
    else:
        if True:
            if Filtering_system[0] is False:
                chat_id = query.message.chat.id
                query.edit_message_text(text=f"Started")
                Filtering_system.clear()
                Filtering_system.append(True)
                run_filtering.clear()
                run_filtering.append(True)
                while True:
                    if run_filtering[0] is True:
                        with open("Pannels.txt", 'r') as txt:
                            for data in txt.readlines():
                                do = True
                                data = data.replace('\n', "")
                                host = data.split("@")[0]
                                username = (data.split(":")[0]).split("@")[1]
                                password = data.split(":")[1]
                                session = 'ssh/' + host + ".session"
                                if Path(session).is_file() is False:
                                    if sshx.Login(username, password, host) is False:
                                        do = False
                                if do is True:
                                    if True:
                                        Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                                        if host in checked_connections:
                                            checked_connections.remove(host)
                                        status, content = Session.IP_Check()
                                        if (status is True) and (host not in checked_filtering):
                                            text = "🔴Blocked in some countries: " + host
                                            checked_filtering.append(host)
                                            bot.send_message(chat_id, text)
                                        else:
                                            if "Error" not in content:
                                                if host in checked_connections:
                                                    checked_filtering.remove(host)
                                    except:
                                        if host not in checked_connections:
                                            text = "🔴Connection Error: " + host
                                            checked_connections.append(host)
                                            bot.send_message(chat_id, text)
                        sleep(300)
                    else:
                        break
            else:
                query.answer("Already ON", show_alert=True)


@app.on_callback_query(filters.regex('FLCHOFF'))
def call_FLCHOFF(bot, query):
    if Filtering_system[0] is True:
        Filtering_system.clear()
        Filtering_system.append(False)
        run_filtering.clear()
        run_filtering.append(False)
        keyboard = [[InlineKeyboardButton("<<", callback_data='FILCH')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Stopped.", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("Already OFF", show_alert=True)


@app.on_callback_query(filters.regex('FILCH'))
def call_FILCH(bot, query):
    keyboard = [
        [InlineKeyboardButton("ON 🟢", callback_data='FLCHON')],
        [InlineKeyboardButton("OFF 🔴", callback_data='FLCHOFF')]
    ]
    if Filtering_system[0] is False:
        status = "OFF ❌"
    else:
        status = "ON ✅"
    text = '<b>Filtering System Checker Settings</b>\n\n' + "🔄Status: " + status
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('APRX'))
def call_APRX(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    add_cache(chat_id, "proxy")
    text = "OK send the proxy"
    keyboard = [[InlineKeyboardButton("<<", callback_data='Sprx')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('DPRX'))
def call_DPRX(bot, query):
    settings = get_settings()
    settings['proxy'] = "None"
    update_settings(settings)
    text = "Done✔️"
    keyboard.append([InlineKeyboardButton("<<", callback_data='Sprx')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Sprx'))
def call_Sprx(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    settings = get_settings()
    if settings['proxy'] == "None":
        keyboard = [[InlineKeyboardButton("Add➕", callback_data='APRX')]]
    else:
        keyboard = [
            [InlineKeyboardButton("Edit✏️", callback_data='APRX')],
            [InlineKeyboardButton("Delete✖️", callback_data='DPRX')],
        ]
    text = '<b>Proxy Settings</b>\n\n' + "Current: \n" + settings['proxy']
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('settings'))
def call_settings(bot, query):
    keyboard = [
        [InlineKeyboardButton("ولت ترون💵", callback_data='wallet'), InlineKeyboardButton("شماره کارت💳", callback_data='Card')],
        [InlineKeyboardButton("پیام استارت📃", callback_data='WSMSG'), InlineKeyboardButton("پیام تعرفه قیمت💰", callback_data='WLMSG')],
        [InlineKeyboardButton("اسپانسر📢", callback_data='sponser'), InlineKeyboardButton("بکاپ📥", callback_data='Backup')],
        [InlineKeyboardButton("حذف خودکار کاربر🗑", callback_data='AutoDelete'), InlineKeyboardButton("قیمت دلار💲", callback_data='USD')],
        [InlineKeyboardButton("قیمت ها🛒", callback_data='ADMINPRICES'), InlineKeyboardButton("چکر فیلترینگ🔎", callback_data='FILCH')],
        [InlineKeyboardButton("وضعیت خرید", callback_data='BSOPtion'), InlineKeyboardButton("پروکسی", callback_data='Sprx')],
        [InlineKeyboardButton("محدودیت تعداد کاربر هر سرور👤", callback_data='maximum')]
    ]
    keyboard.append([InlineKeyboardButton("<<", callback_data='back_admin')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '<b>تنظیمات🖥</b>'
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.chat(admin_id) & filters.voice)
def admin_voice(bot, message):
    chat_id = message.chat.id
    if check_cache(chat_id) is True:
        status = get_cache_status(chat_id)
        if status == "message":
            delete_cache(chat_id)
            message.reply_text("Sending...")
            fname = "All.txt"
            sent = 0
            file_id = message.voice.file_id
            with open(fname, 'r') as f:
                for usertxt in f:
                    try:
                        bot.send_voice(int(usertxt.replace('\n', '')), file_id)
                        sent += 1
                    except:
                        continue
            bot.send_message(chat_id, f"sent to {str(sent)} users")


@app.on_message(filters.private & filters.photo)
def image_users(bot, message):
    chat_id = message.chat.id
    if check_cache(chat_id) is True:
        status = get_cache_status(chat_id)
        msg_id = message.id
        if "support" in status:
            n = int(status.split("support ")[1])
            bot.forward_messages(admin_id[n], chat_id, msg_id)
            name = message.from_user.first_name
            try:
                username = "@" + message.from_user.username
            except:
                username = 'Null'
            text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username
            keyboard = [[InlineKeyboardButton("Answer to " + name, callback_data='ANS_' + str(chat_id))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(admin_id[n], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            sleep(0.2)
            message.reply_text(text='بزودی درخواستتون بررسی میکنیم🫡')
        elif status == "buy":
            name = message.from_user.first_name
            try:
                username = "@" + message.from_user.username
            except:
                username = 'Null'
            code, cache_list = get_code_buy_info(chat_id, "add")
            delete_all_buy(chat_id, "add")
            add_code_buy(chat_id, code, "add", cache_list)
            t1 = f"days: {cache_list[0]}\nGB: {cache_list[1]}\nConnection: {cache_list[2]}\nprice: {cache_list[3]} Toman"
            text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\ninfo buy:\n" + t1
            cb = "Confirmed_" + code
            no = "NO❌_" + code
            keyboard = [[InlineKeyboardButton("Confirm✅", callback_data=cb), InlineKeyboardButton("NO❌", callback_data=no)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            for i in range(len(admin_id)):
                try:
                    bot.forward_messages(admin_id[i], chat_id, msg_id)
                    bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                except:
                    pass
            update_code_status(code, "check")
            message.reply_text(text='بزودی درخواستتون بررسی میکنیم🫡')
        elif status == "upgrade":
            name = message.from_user.first_name
            try:
                username = "@" + message.from_user.username
            except:
                username = 'Null'
            code, cache_list = get_code_buy_info(chat_id, "upgrade")
            delete_all_buy(chat_id, "upgrade")
            add_code_buy(chat_id, code, "upgrade", cache_list)
            t1 = f"🔄تمدید\ndays: {cache_list[0]}\nGB: {cache_list[1]}\nConnection: {cache_list[2]}\nprice: {cache_list[3]} Toman\nHost: {cache_list[5]}\nUser: {cache_list[4]}"
            text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\ninfo buy:\n" + t1
            cb = "ConfirmUPGRADE_" + code
            no = "NO❌_" + code
            keyboard = [[InlineKeyboardButton("Confirm✅", callback_data=cb), InlineKeyboardButton("NO❌", callback_data=no)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            for i in range(len(admin_id)):
                try:
                    bot.forward_messages(admin_id[i], chat_id, msg_id)
                    bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                except:
                    pass
            update_code_status(code, "checkup")
            message.reply_text(text='بزودی درخواستتون بررسی میکنیم🫡')
        delete_cache(chat_id)


app.run()
