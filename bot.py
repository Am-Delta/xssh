import os
import re
import ast
import sshx
import json
import sqlite3
import socket
import qrcode
import requests
import jdatetime
import cryptocompare
from uuid import uuid4
from pathlib import Path
from time import time, sleep
from datetime import datetime
from unidecode import unidecode
from random import randint, choice
from pyrogram import Client, filters, enums
from pyrogram.errors import NotAcceptable, BadRequest, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


session = "run"

if Path(session + ".session").is_file() is True:
    os.remove(session + ".session")

with open("data.json", "r") as json_file:
    file_data = json.load(json_file)
    admin_id = file_data['admin']
    api_id = file_data['api_id']
    api_hash = file_data['api_hash']
    TOKEN = file_data['Token']

app = Client(session, api_id, api_hash, bot_token=TOKEN)


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 0))
owners_port = int(s.getsockname()[1])
print("Running SSH bot on port ", owners_port)

conn = sqlite3.connect('ssh.db', check_same_thread=False)
cur = conn.cursor()

folder = 'backup'
cache = [False]
backup = [False]
run_backup = [False]
Filtering_system = [False]
run_filtering = [False]
notify_system = [False]
run_notify = [False]
checked_filtering = []
checked_connections = []
checked_users = []
checked_id = []
old_hosts = []
cache_list = []
host_cache = []
text_cache = []
seller_id = []
botusername = []
process_codes = []
backup_command = [False]
filter_name = ['root', 'Root', 'ROOT', 'ubuntu', 'Ubuntu', 'UBUNTU', 'centos', 'Centos', 'CentOS', 'user', 'User', 'Username', 'username']

API_main_address = "http://hd.ladokpro.pw:5000/usd"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
headers = {"user-agent": user_agent}


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
        [InlineKeyboardButton("🖥 مدیریت سرور ها", callback_data='SMT')],
        [InlineKeyboardButton("👤مدیریت اکانت ها", callback_data='Manager')],
        [InlineKeyboardButton("⛔️تست فیلترینگ", callback_data='Filtering'), InlineKeyboardButton("🎁کد هدیه", callback_data='GUA')],
        [InlineKeyboardButton("📦ارسال پیام همگانی", callback_data='message'), InlineKeyboardButton("💲فروشنده ها", callback_data='sellers')],
        [InlineKeyboardButton("⚙️تنظیمات", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def Seller_Tools_keys():
    keyboard = [
        [InlineKeyboardButton("📊آمار", callback_data='stats'), InlineKeyboardButton("👤اطلاعات کاربر", callback_data='userinfo')],
        [InlineKeyboardButton("🔴 غیر فعال کاربر", callback_data='disable'), InlineKeyboardButton("🟢 فعال کاربر", callback_data='enable')],
        [InlineKeyboardButton("🔄تمدید کاربر", callback_data='update'), InlineKeyboardButton("⬆️افزایش ترافیک", callback_data='TrfPlus')],
        [InlineKeyboardButton("🛠ساخت اکانت", callback_data='Create_none'), InlineKeyboardButton("🗑حذف کاربر", callback_data='remove')],
        [InlineKeyboardButton("🔑تغییر پسورد اکانت", callback_data='ADPASS')],
        [InlineKeyboardButton("📦 اکانت های من", callback_data='service'), InlineKeyboardButton("ℹ️ اطلاعات سرویس", callback_data='config')],
        [InlineKeyboardButton("🆘 آموزش", callback_data='help'), InlineKeyboardButton("💰کیف پول", callback_data='UWM')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def User_Tools_keys():
    keyboard = [
        [InlineKeyboardButton("💰کیف پول", callback_data='UWM')],
        [InlineKeyboardButton(" اطلاعات سرویس ℹ️", callback_data='config'), InlineKeyboardButton("📦 سرویس های من", callback_data='service')],
        [InlineKeyboardButton("🆘 آموزش", callback_data='help')]
    ]
    settings = get_settings()
    if settings['buy'] == 'on':
        keyboard.insert(0, [InlineKeyboardButton("🔄 تمدید", callback_data='upgrade'), InlineKeyboardButton("🛒 خرید", callback_data='buy')])
    if settings['list_status'] == "on":
        for i in range(len(keyboard)):
            if InlineKeyboardButton("💰کیف پول", callback_data='UWM') in keyboard[i]:
                keyboard[i].insert(1, InlineKeyboardButton("🏷 تعرفه قیمت ها", callback_data='price'))
                break
    if settings['test'] == "on":
        keyboard.insert(1, [InlineKeyboardButton("🗒 تست", callback_data='test')])
    if settings['buy-traffic'] == 'on':
        keyboard.insert(1, [InlineKeyboardButton("🔁 خرید ترافیک", callback_data='traffic')])
    if settings['proxy'] != "None":
        keyboard.insert(-1, [InlineKeyboardButton("🆓 پروکسی تلگرام", callback_data='FREEPX')])
    if settings['invite'] == "on":
        for i in range(len(keyboard)):
            if InlineKeyboardButton("🆓 پروکسی تلگرام", callback_data='FREEPX') in keyboard[i]:
                keyboard[i].insert(0, InlineKeyboardButton("🎁 دریافت هدیه", callback_data='referral'))
                break
    if settings['support_status'] == "on":
        for i in range(len(keyboard)):
            if InlineKeyboardButton("🆘 آموزش", callback_data='help') in keyboard[i]:
                keyboard[i].insert(0, InlineKeyboardButton("👥 پشتیبانی", callback_data='support'))
                break
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


# 4 & 3 & 2 & 1 Buttons in a table
'''def server_cb_creator(job):
    hosts, remarks = sshx.HOSTS()
    keyboard = []
    if len(hosts) >= 2:
        if len(hosts) >= 24:
            if len(users) % 4 == 0:
                for i in range(0, len(users) - 1, 4):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=(job + users[i])), InlineKeyboardButton(users[i + 1], callback_data=(job + users[i + 1])), InlineKeyboardButton(users[i + 2], callback_data=(job + users[i + 2])), InlineKeyboardButton(users[i + 3], callback_data=(job + users[i + 3]))])
            else:
                for i in range(0, len(users) - 3, 4):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=(job + users[i])), InlineKeyboardButton(users[i + 1], callback_data=(job + users[i + 1])), InlineKeyboardButton(users[i + 2], callback_data=(job + users[i + 2])), InlineKeyboardButton(users[i + 3], callback_data=(job + users[i + 3]))])
                if ((len(hosts) % 4 == 3) and (len(hosts) % 2 == 1) and (len(hosts) % 3 == 2)) or ((len(hosts) % 4 == 3) and (len(hosts) % 2 == 1) and (len(hosts) % 3 == 0)) or ((len(hosts) % 4 == 3) and (len(hosts) % 2 == 1) and (len(hosts) % 3 == 1)):
                    keyboard.append([InlineKeyboardButton(users[-3], callback_data=(job + users[-3])), InlineKeyboardButton(users[-2], callback_data=(job + users[-2])), InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
                elif (len(hosts) % 4 == 2) and (len(hosts) % 2 == 0):
                    keyboard.append([InlineKeyboardButton(users[-2], callback_data=(job + users[-2])), InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
                elif (len(hosts) % 4 == 1 and len(hosts) % 3 == 2) or (len(hosts) % 4 == 1 and (len(hosts) % 3 == 0)):
                    keyboard.append([InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
                else:
                    keyboard.append([InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
        elif len(hosts) >= 10:
            if len(hosts) % 3 == 0:
                for i in range(0, len(hosts) - 1, 3):
                    keyboard.append([InlineKeyboardButton(hosts[i], callback_data=(job + hosts[i])), InlineKeyboardButton(hosts[i + 1], callback_data=(job + hosts[i + 1])), InlineKeyboardButton(hosts[i + 2], callback_data=(job + hosts[i + 2]))])
            else:
                for i in range(0, len(hosts) - 2, 3):
                    keyboard.append([InlineKeyboardButton(hosts[i], callback_data=(job + hosts[i])), InlineKeyboardButton(hosts[i + 1], callback_data=(job + hosts[i + 1])), InlineKeyboardButton(hosts[i + 2], callback_data=(job + hosts[i + 2]))])
                if (len(hosts) % 2 == 0) or ((len(hosts) % 2 == 1) and (len(hosts) % 3 == 2)):
                    keyboard.append([InlineKeyboardButton(hosts[-2], callback_data=(job + hosts[-2])), InlineKeyboardButton(hosts[-1], callback_data=(job + hosts[-1]))])
                else:
                    keyboard.append([InlineKeyboardButton(hosts[-1], callback_data=(job + hosts[-1]))])
        else:
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
    return reply_markup'''


def Reply_action_sellers(hosts, users, job):
    keyboard = []
    if len(users) >= 2:
        if len(users) >= 10:
            if len(users) % 3 == 0:
                for i in range(0, len(users) - 1, 3):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=f"{job}{hosts[i]}${users[i]}"), InlineKeyboardButton(users[i + 1], callback_data=f"{job}{hosts[i + 1]}${users[i + 1]}"), InlineKeyboardButton(users[i + 2], callback_data=f"{job}{hosts[i + 2]}${users[i + 2]}")])
            else:
                for i in range(0, len(users) - 2, 3):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=f"{job}{hosts[i]}${users[i]}"), InlineKeyboardButton(users[i + 1], callback_data=f"{job}{hosts[i + 1]}${users[i + 1]}"), InlineKeyboardButton(users[i + 2], callback_data=f"{job}{hosts[i + 2]}${users[i + 2]}")])
                if (len(users) % 2 == 0) or ((len(users) % 2 == 1) and (len(users) % 3 == 2)):
                    keyboard.append([InlineKeyboardButton(users[-2], callback_data=f"{job}{hosts[-2]}${users[-2]}"), InlineKeyboardButton(users[-1], callback_data=f"{job}{hosts[-1]}${users[-1]}")])
                else:
                    keyboard.append([InlineKeyboardButton(users[-1], callback_data=f"{job}{hosts[-1]}${users[-1]}")])
        else:
            if len(users) % 2 == 0:
                for i in range(0, len(users) - 1, 2):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=f"{job}{hosts[i]}${users[i]}"), InlineKeyboardButton(users[i + 1], callback_data=f"{job}{hosts[i + 1]}${users[i + 1]}")])
            else:
                for i in range(0, len(users) - 1, 2):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=f"{job}{hosts[i]}${users[i]}"), InlineKeyboardButton(users[i + 1], callback_data=f"{job}{hosts[i + 1]}${users[i + 1]}")])
                keyboard.append([InlineKeyboardButton(users[-1], callback_data=f"{job}{hosts[-1]}${users[-1]}")])
    else:
        if users == []:
            pass
        else:
            keyboard.append([InlineKeyboardButton(users[0], callback_data=f"{job}{hosts[0]}${users[0]}")])
    keyboard.append([InlineKeyboardButton("<<", callback_data="back_seller")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def Reply_Kill(host, users):
    keyboard = []
    job = "HKR_" + host + "$"
    if len(users) >= 2:
        if len(users) >= 19:
            if len(users) % 4 == 0:
                for i in range(0, len(users) - 1, 4):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=(job + users[i])), InlineKeyboardButton(users[i + 1], callback_data=(job + users[i + 1])), InlineKeyboardButton(users[i + 2], callback_data=(job + users[i + 2])), InlineKeyboardButton(users[i + 3], callback_data=(job + users[i + 3]))])
            else:
                for i in range(0, len(users) - 3, 4):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=(job + users[i])), InlineKeyboardButton(users[i + 1], callback_data=(job + users[i + 1])), InlineKeyboardButton(users[i + 2], callback_data=(job + users[i + 2])), InlineKeyboardButton(users[i + 3], callback_data=(job + users[i + 3]))])
                if ((len(users) % 4 == 3) and (len(users) % 2 == 1) and (len(users) % 3 == 2)) or ((len(users) % 4 == 3) and (len(users) % 2 == 1) and (len(users) % 3 == 0)) or ((len(users) % 4 == 3) and (len(users) % 2 == 1) and (len(users) % 3 == 1)):
                    keyboard.append([InlineKeyboardButton(users[-3], callback_data=(job + users[-3])), InlineKeyboardButton(users[-2], callback_data=(job + users[-2])), InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
                elif (len(users) % 4 == 2) and (len(users) % 2 == 0):
                    keyboard.append([InlineKeyboardButton(users[-2], callback_data=(job + users[-2])), InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
                elif (len(users) % 4 == 1 and len(users) % 3 == 2) or (len(users) % 4 == 1 and (len(users) % 3 == 0)):
                    keyboard.append([InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
                else:
                    keyboard.append([InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
        elif len(users) >= 10:
            if len(users) % 3 == 0:
                for i in range(0, len(users) - 1, 3):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=(job + users[i])), InlineKeyboardButton(users[i + 1], callback_data=(job + users[i + 1])), InlineKeyboardButton(users[i + 2], callback_data=(job + users[i + 2]))])
            else:
                for i in range(0, len(users) - 2, 3):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=(job + users[i])), InlineKeyboardButton(users[i + 1], callback_data=(job + users[i + 1])), InlineKeyboardButton(users[i + 2], callback_data=(job + users[i + 2]))])
                if (len(users) % 2 == 0) or ((len(users) % 2 == 1) and (len(users) % 3 == 2)):
                    keyboard.append([InlineKeyboardButton(users[-2], callback_data=(job + users[-2])), InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
                else:
                    keyboard.append([InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
        else:
            if len(users) % 2 == 0:
                for i in range(0, len(users) - 1, 2):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=(job + users[i])), InlineKeyboardButton(users[i + 1], callback_data=(job + users[i + 1]))])
            else:
                for i in range(0, len(users) - 1, 2):
                    keyboard.append([InlineKeyboardButton(users[i], callback_data=(job + users[i])), InlineKeyboardButton(users[i + 1], callback_data=(job + users[i + 1]))])
                keyboard.append([InlineKeyboardButton(users[-1], callback_data=(job + users[-1]))])
    else:
        if users == []:
            pass
        else:
            keyboard.append([InlineKeyboardButton(users[0], callback_data=(job + users[0]))])
    keyboard.append([InlineKeyboardButton("<< back to servers", callback_data="servers")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def server_cb_creator(job):
    hosts, remarks = sshx.HOSTS()
    keyboard = []
    if len(hosts) >= 2:
        if len(hosts) % 2 == 0:
            for i in range(0, len(hosts) - 1, 2):
                keyboard.append([InlineKeyboardButton(remarks[i], callback_data=(job + hosts[i])), InlineKeyboardButton(remarks[i + 1], callback_data=(job + hosts[i + 1]))])
        else:
            for i in range(0, len(hosts) - 1, 2):
                keyboard.append([InlineKeyboardButton(remarks[i], callback_data=(job + hosts[i])), InlineKeyboardButton(remarks[i + 1], callback_data=(job + hosts[i + 1]))])
            keyboard.append([InlineKeyboardButton(remarks[-1], callback_data=(job + hosts[-1]))])
    else:
        if hosts == []:
            pass
        else:
            keyboard.append([InlineKeyboardButton(remarks[0], callback_data=(job + hosts[0]))])
    keyboard.append([InlineKeyboardButton("<< back", callback_data="back_admin")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def server_cb_creator_user(job, data):
    hosts, remarks = sshx.HOSTS()
    keyboard = []
    if len(hosts) >= 2:
        if len(hosts) % 2 == 0:
            for i in range(0, len(hosts) - 1, 2):
                keyboard.append([InlineKeyboardButton(remarks[i], callback_data=(job + data + "!" + hosts[i])), InlineKeyboardButton(remarks[i + 1], callback_data=(job + data + "!" + hosts[i + 1]))])
        else:
            for i in range(0, len(hosts) - 1, 2):
                keyboard.append([InlineKeyboardButton(remarks[i], callback_data=(job + data + "!" + hosts[i])), InlineKeyboardButton(remarks[i + 1], callback_data=(job + data + "!" + hosts[i + 1]))])
            keyboard.append([InlineKeyboardButton(remarks[-1], callback_data=(job + data + "!" + hosts[-1]))])
    else:
        if hosts == []:
            pass
        else:
            keyboard.append([InlineKeyboardButton(remarks[0], callback_data=(job + data + "!" + hosts[0]))])
    keyboard.append([InlineKeyboardButton("<< back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def QR_Maker(link):
    link = link.replace("<pre>", "").replace("</pre>", "")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=15,
        border=2
    )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    photo = "cache/" + uuid4().hex[0:8] + ".jpg"
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
        txt.writelines(ids)
        txt.writelines("\n")
        txt.close()


def checker_notify(ids):
    txt = open("All.txt", "r")
    if ids in txt.read():
        return True
    else:
        return False


def check_host_api(host):
    try:
        node1 = "ir1.node.check-host.net"
        node2 = "ir3.node.check-host.net"
        node3 = "ir4.node.check-host.net"
        node4 = "de1.node.check-host.net"
        url = f"https://check-host.net/check-ping?host={host}&node={node1}&node={node2}&node={node3}&node={node4}"
        headers = {
            'accept': 'application/json',
            'user-agent': user_agent
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            request_id = json.loads(r.text)['request_id']
            sleep(20)
            data = requests.get("https://check-host.net/check-result/" + request_id, headers=headers)
            if data.status_code == 200:
                results = json.loads(data.text)
                for result in results[node1][0]:
                    if result[0] == "OK":
                        return False
                for result in results[node2][0]:
                    if result[0] == "OK":
                        return False
                for result in results[node3][0]:
                    if result[0] == "OK":
                        return False
                for result in results[node4][0]:
                    if result[0] == "OK":
                        return True
    except:
        return True
    return True


def API_0():
    try:
        r = requests.get(API_main_address, headers=headers)
        if r.status_code == 200:
            price = int(json.loads(r.text)['usd'])
            if len(str(price)) >= 5:
                if price == 49000:
                    return False, 0
                else:
                    return True, price
            else:
                return False, 0
        else:
            return False, 0
    except:
        return False, 0


def API_1():
    try:
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }
        r = requests.get("https://www.tasnimnews.com/fa/currency/table", headers=headers)
        if r.status_code == 200:
            datas = json.loads(json.loads(r.text))['currency']
            for data in datas:
                if data['title'] == "price_dollar_rl":
                    price = int(float(data['p'].replace(",", "")))
                    if len(str(price)) >= 6:
                        return True, price // 10
                    else:
                        return False, 0
        else:
            return False, 0
    except:
        return False, 0


def API_2():
    try:
        data = {'signal': 'getdata'}
        r = requests.post("https://irarz.com/Aj.php", headers=headers, data=data)
        if r.status_code == 200:
            datas = json.loads(r.text)
            for data in datas:
                if data.get("price_dollar_rl", None) is not None:
                    price = int(float(unidecode(data['price_dollar_rl'].encode().decode().replace(",", ""))))
                    if len(str(price)) >= 6:
                        return True, price // 10
                    else:
                        return False, 1
        else:
            return False, r.status_code
    except:
        return False, 0


def API_3():
    try:
        r = requests.get("https://api.sarmayex.com/api/v2/currency/87", headers=headers)
        if r.status_code == 200:
            price = int(float(json.loads(r.text)['currency']['buy']['price']))
            if len(str(price)) >= 5:
                return True, price
            else:
                return False, 0
        else:
            return False, 0
    except:
        return False, 0


def API_4():
    try:
        r = requests.get("https://api.bitpin.ir/v1/mkt/markets/", headers=headers)
        if r.status_code == 200:
            datas = json.loads(r.text)['results']
            for data in datas:
                if data['title'] == "Tether/Toman":
                    price = int(float(data['price']))
                    if len(str(price)) >= 5:
                        return True, price
                    else:
                        return False, 0
        else:
            return False, 0
    except:
        return False, 0


def API_5():
    try:
        r = requests.get("https://api.pooleno.ir/v1/token/chartData/currentPrice/tether", headers=headers)
        if r.status_code == 200:
            price = json.loads(r.text)['priceRial']
            if len(str(price)) >= 6:
                return True, price // 10
            else:
                return False, 0
        else:
            return False, 0
    except:
        return False, 0


def API_6():
    try:
        r = requests.get("https://abantether.com/management/all-coins/?format=json", headers=headers)
        if r.status_code == 200:
            datas = json.loads(r.text)
            for data in datas:
                if data['symbol'] == "USDT":
                    price = int(float(data['priceBuy']))
                    if len(str(price)) >= 5:
                        return True, price
                    else:
                        return False, 0
        else:
            return False, 0
    except:
        return False, 0


def GET_USD():
    status, value = API_0()
    if status is True:
        return True, value
    status, value = API_1()
    if status is True:
        return True, value
    status, value = API_2()
    if status is True:
        return True, value
    status, value = API_3()
    if status is True:
        return True, value
    status, value = API_4()
    if status is True:
        return True, value
    status, value = API_5()
    if status is True:
        return True, value
    status, value = API_6()
    if status is True:
        return True, value

    return False, 0


def Toman_USD():
    status, value = GET_USD()
    if status is True:
        toman = value
    else:
        toman = (get_settings())['usd']
    return toman


def trx_price(irr_price):
    irr_price = int(irr_price)
    irr = Toman_USD()
    try:
        trx = cryptocompare.get_price('TRX', currency='USD')['TRX']["USD"]
        price = (irr_price / irr) / trx
        price = str("{:.2f}".format(float(price))) + " TRX"
    except:
        price = str("{:.2f}".format(float(irr_price / irr))) + "$"
        #price = "مبلغ مشخص نیست لطفا از کارت به کارت استفاده کنین"
    return price


def fixed_link_json(link):
    link = link.replace("'", "")
    link = link.replace('"', '')
    link = link.replace(u'\\xa0', u' ')
    link = link.replace("\\", "")
    return link


def randomized_text():
    return (randint(1, 5)) * "‎"


def get_random_server():
    hosts, remarks = sshx.HOSTS()
    for host in hosts:
        if check_domain_reached_maximum(host) is False:
            return host
    return None


def Check_in_hosts(host):
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        return host, True
    else:
        return host, False


def get_host_username(text):
    username = ""
    if "<pre>" in text:
        text = text.replace("<pre>", "")
        text = text.replace("</pre>", "")
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
        elif "SSH HOST:" in text:
            host = ((text.split("SSH HOST:")[1].split("\n")[0]))
        elif "SSH HOST :" in text:
            host = ((text.split("SSH HOST :")[1].split("\n")[0]))
        elif "host:" in text:
            host = ((text.split("host:")[1].split("\n")[0]))
        elif "host :" in text:
            host = ((text.split("host :")[1].split("\n")[0]))
        elif "Host:" in text:
            host = ((text.split("Host:")[1].split("\n")[0]))
        elif "Host :" in text:
            host = ((text.split("Host :")[1].split("\n")[0]))
        elif "HOST:" in text:
            host = ((text.split("HOST:")[1].split("\n")[0]))
        elif "HOST :" in text:
            host = ((text.split("HOST :")[1].split("\n")[0]))
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
        elif "USER :" in text:
            username = text.split("USER:")[1].split("\n")[0]
        elif "USER:" in text:
            username = text.split("USER:")[1].split("\n")[0]
        elif "Username :" in text:
            username = text.split("Username :")[1].split("\n")[0]
        elif "username :" in text:
            username = text.split("username :")[1].split("\n")[0]
        elif "Username:" in text:
            username = text.split("Username:")[1].split("\n")[0]
        elif "username:" in text:
            username = text.split("username:")[1].split("\n")[0]
        elif "USERNAME:" in text:
            username = text.split("USERNAME:")[1].split("\n")[0]
        elif "USERNAME :" in text:
            username = text.split("USERNAME :")[1].split("\n")[0]
        username = username.replace(" ", "")
        username = username.replace(" ", "")

        hosts, remarks = sshx.HOSTS()
        if host in hosts:
            return host, username
        else:
            return None, None


def check_domain_reached_maximum(host):
    settings = get_settings()
    maximum = settings['maximum']
    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
    Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
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


def add_referral(chat_id, name, username, referrals):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Referrals (ID, Name, Username, Referrals) VALUES (?, ?, ?, ?)", (chat_id, name, username, str(referrals)))
            conn.commit()
            break
        except:
            pass


def add_client_db(chat_id, name, username, phone, balance):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Clients (ID, Name, Username, Phone, Balance) VALUES (?, ?, ?, ?, ?)", (chat_id, name, username, phone, balance))
            conn.commit()
            break
        except:
            pass


def add_test_user(chat_id, user):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Tests (ID, 'date', Account) VALUES (?, ?, ?)", (chat_id, str(datetime.now()), user))
            conn.commit()
            break
        except:
            pass


def add_gift_code(value, count, timer, code):
    for i in range(5):
        try:
            cur.execute("INSERT INTO Redeem (Code, Value, kind, Count, UserIDs, Timer) VALUES (?, ?, ?, ?, ?, ?)", (code, value, 'gift', count, str([]), timer))
            conn.commit()
            break
        except:
            pass


def check_gift_code_exist(code):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Redeem WHERE Code=:Code", {'Code': code})
            records = cur.fetchall()
            if records == []:
                return False
            else:
                return True
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


def check_referral_exists(chat_id):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Referrals WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            if records == []:
                return False
            else:
                return True
        except:
            pass


def check_user_exists_in_clients_table(chat_id):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Clients WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            if records == []:
                return False
            else:
                return True
        except:
            pass


def check_test_exists(chat_id):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Tests WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            if records == []:
                return False
            else:
                return True
        except:
            pass


def check_user_phone_exist(chat_id):
    for i in range(3):
        try:
            cur.execute("SELECT * FROM Clients WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            if records[0][3] == "None":
                return False
            else:
                return True
        except:
            pass


def get_gift_code_full(code):
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Redeem WHERE Code=:Code", {'Code': code})
            records = cur.fetchall()
            return records[0][1], records[0][2], records[0][3], ast.literal_eval(records[0][4]), records[0][5]
        except:
            pass


def get_all_gift_codes():
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Redeem")
            records = cur.fetchall()
            codes = []
            for i in range(len(records)):
                codes.append(records[i][0])
            return codes
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
            s = s.replace(u'\\xa0', u' ')
            settings = json.loads(s, strict=False)
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


def get_referral_info(chat_id):
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Referrals WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            return records[0][1], ast.literal_eval(records[0][3])
        except:
            pass


def get_full_user_data_id(chat_id):
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Clients WHERE ID=:ID", {'ID': chat_id})
            records = cur.fetchall()
            for row in records:
                return row[1], row[2], row[3], row[4]
        except:
            pass


def get_count_test_users():
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Tests")
            records = cur.fetchall()
            return len(records)
        except:
            pass


def get_test_usernames():
    for i in range(5):
        try:
            cur.execute("SELECT * FROM Tests")
            records = cur.fetchall()
            test_usernames = []
            for row in records:
                if row[2] is not None:
                    test_usernames.append(row[2])
            return test_usernames
        except:
            pass


def delete_test_users():
    for i in range(5):
        try:
            cur.execute("DELETE FROM Tests")
            conn.commit()
            break
        except:
            pass


def delete_gift_code(code):
    for i in range(5):
        try:
            cur.execute("DELETE FROM Redeem WHERE Code=?", (code,))
            conn.commit()
            break
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


def delete_host_users_accounts(host):
    for i in range(5):
        try:
            cur.execute("DELETE FROM Users WHERE Host=?", (host,))
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


def update_user_username(from_user, to_user, host):
    for i in range(5):
        try:
            cur.execute("UPDATE Users SET Account = ? WHERE Host=? AND Account=?", (to_user, host, from_user))
            conn.commit()
        except:
            pass


def update_gift_code_by_chat_id(code, users_id):
    for i in range(5):
        try:
            cur.execute("UPDATE Redeem SET UserIDs = ? WHERE Code =?", (str(users_id), code))
            conn.commit()
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


def update_referall(referall_id, referrals):
    for i in range(5):
        try:
            cur.execute("UPDATE Referrals SET Referrals = ? WHERE ID =?", (str(referrals), referall_id))
            conn.commit()
        except:
            pass


def update_user_wallet(chat_id, balance):
    for i in range(5):
        try:
            cur.execute("UPDATE Clients SET Balance = ? WHERE ID =?", (balance, chat_id))
            conn.commit()
        except:
            pass


def update_phone_number(chat_id, phone_number):
    for i in range(5):
        try:
            cur.execute("UPDATE Clients SET Phone = ? WHERE ID =?", (phone_number, chat_id))
            conn.commit()
        except:
            pass


def update_host_users(host, new_host):
    for i in range(5):
        try:
            cur.execute("UPDATE Users SET Host = ? WHERE Host =?", (new_host, host))
            conn.commit()
        except:
            pass


@app.on_message(filters.chat(admin_id) & filters.command('backup'))
def backup_cmd(bot, message):
    if backup_command[0] is False:
        backup_command[0] = True
        chat_id = message.chat.id
        msg = message.reply_text("Wait...").id
        files = ["All.txt", "ssh.db", "data.json", "Pannels.txt", "logs.txt", "nohup.out"]
        logs = "Done✔️\n\nLogs:\n\n"
        for file in files:
            try:
                bot.send_document(chat_id, document=open(file, 'rb'), file_name=file)
            except Exception as e:
                logs += ("File: " + file + " " + str(e) + "\n")
            sleep(0.2)
        bot.send_message(chat_id, logs)
        bot.delete_messages(chat_id, msg)
        backup_command[0] = False
    else:
        message.reply_text("Don't spam!")


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
        message.reply_text("Canceled❌\n\n/backup", reply_markup=Admin_Tools_keys())
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
            msg = message.reply_text("Forwarding...").id
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
            bot.delete_messages(chat_id, msg)

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
            message.reply_text("تعداد محدودیت کانکشن بفرستین یا /cancel")

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
                    message.reply_text("پیدا نشد❌", reply_markup=reply_markup)
            else:
                keyboard.append([InlineKeyboardButton("<< Back", callback_data='back_admin')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("پیدا نشد❌", reply_markup=reply_markup)
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
                    message.reply_text("تعداد محدودیت به عدد بفرستین\n\n0 = نامحدود\n10 = 10 کاربر میتونه فروشنده بسازه")
                else:
                    message.reply_text("🔵 این فروشنده وجود داره", reply_markup=reply_markup)
                    delete_cache(chat_id)
                    delete_collector(chat_id)
            except:
                message.reply_text("❌فوروارد این کاربر هیدن هست", reply_markup=reply_markup)
                delete_cache(chat_id)

        elif status == "Adminuserbalance":
            keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                user_id = message.forward_from.id
                if check_user_exists_in_clients_table(user_id) is True:
                    name, u, phone, value = get_full_user_data_id(user_id)
                    keyboard = [
                        [InlineKeyboardButton("➖کاهش", callback_data=f'MAUB_{str(user_id)}'), InlineKeyboardButton("➕افزایش", callback_data=f'PAUB_{str(user_id)}')],
                        [InlineKeyboardButton("0️⃣صفر کردن موجودی", callback_data=f'ZAUB_{str(user_id)}')],
                        [InlineKeyboardButton("<<", callback_data='back_admin')]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text(f"موجودی: {str(value)} تومن.\n\nName: {name}\nUsername: {u}\nPhone: {phone}", reply_markup=reply_markup)
                else:
                    message.reply_text("🔵 کاربر وجود نداره", reply_markup=reply_markup)
            except:
                message.reply_text("❌فوروارد این کاربر هیدن هست", reply_markup=reply_markup)
            delete_cache(chat_id)


@app.on_message(filters.chat(admin_id) & filters.command('start'))
def start_admin(bot, message):
    if botusername == []:
        botusername.append((bot.get_me()).username)
    text = '🔻<b>Tools</b>\n\n/backup'
    chat_id = message.chat.id
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
        delete_collector(chat_id)
    message.reply_text(text, reply_markup=Admin_Tools_keys(), parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.private & filters.command('start'))
def start_user(bot, message):
    chat_id = message.chat.id
    checker(str(chat_id))
    if botusername == []:
        botusername.append((bot.get_me()).username)
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
        if chat_id in seller_id:
            delete_collector(chat_id)
    if chat_id in seller_id:
        text = '🔻<b>Tools</b>'
        message.reply_text(text, reply_markup=Seller_Tools_keys(), parse_mode=enums.ParseMode.HTML)
    else:
        link = message.text
        name = message.from_user.first_name
        if len(link) >= 7:
            try:
                ref_chat_id = int(link.split('/start ')[1])
                if ((check_referral_exists(ref_chat_id) is True) and (chat_id != ref_chat_id)) and (get_settings()['invite'] == "on"):
                    name, referrals = get_referral_info(ref_chat_id)
                    if (chat_id not in referrals):
                        ref_value = get_settings()['referral']
                        bot.send_message(ref_chat_id, f"کاربر {name} با لینکت وارد ربات شد.\nمبلغ {str(ref_value)} به موجودی کیف پولت اضافه شد 💝")
                        referrals.append(chat_id)
                        update_referall(ref_chat_id, referrals)
                        name, u, phone, old_value = get_full_user_data_id(ref_chat_id)
                        value = ref_value + old_value
                        update_user_wallet(ref_chat_id, value)
            except:
                pass
        if check_referral_exists(chat_id) is False:
            try:
                username = "@" + message.from_user.username
            except:
                username = 'None'
            add_referral(chat_id, name, username, [])
        if check_user_exists_in_clients_table(chat_id) is False:
            try:
                username = "@" + message.from_user.username
            except:
                username = 'None'
            add_client_db(chat_id, name, username, 'None', 0)

        Buttons = [[KeyboardButton("ارسال شماره تلفن 📞", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(Buttons, resize_keyboard=True)
        text = "لطفا برای استفاده از ربات دکمه پایین کلیک کنین و شمارتون بفرستین👇"
        if (get_settings())['sponser'] == "None":
            if ((get_settings())['phone'] == "on") and (check_user_phone_exist(chat_id) is False):
                message.reply_text(text, reply_markup=reply_markup)
            else:
                message.reply_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)
        else:
            try:
                chat_member = bot.get_chat_member((get_settings())['sponser'], chat_id)
                if ((get_settings())['phone'] == "on") and (check_user_phone_exist(chat_id) is False):
                    message.reply_text(text, reply_markup=reply_markup)
                else:
                    message.reply_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)

            except NotAcceptable:
                if ((get_settings())['phone'] == "on") and (check_user_phone_exist(chat_id) is False):
                    message.reply_text(text, reply_markup=reply_markup)
                else:
                    message.reply_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)

            except BadRequest as e:
                if "USER_NOT_PARTICIPANT" in str(e):
                    text = "برای استفاده از ربات اینجا باید جوین بشین:" + "\n\n" + (get_settings())['sponser']
                    keyboard = [[InlineKeyboardButton("جوین شدم✅", callback_data="JOIN")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text(text, reply_markup=reply_markup)
                else:
                    if ((get_settings())['phone'] == "on") and (check_user_phone_exist(chat_id) is False):
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
                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                try:
                    Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                    text = Session.User_info(get_settings()['dropbear'])
                    cb = host + "$" + user
                    keyboard = [
                        [InlineKeyboardButton("🔄تمدید کاربر", callback_data=('IDMNU&Update_' + cb)), InlineKeyboardButton("🗑حذف کاربر", callback_data=('IDMNU&Remove_' + cb))],
                        [InlineKeyboardButton("🟢 فعال کاربر", callback_data=('IDMNU&Active_' + cb)), InlineKeyboardButton("🔴 غیر فعال کاربر", callback_data=('IDMNU&Disable_' + cb))],
                        [InlineKeyboardButton("🆕ریست ترافیک", callback_data=('IDMNU&Reset_' + cb)), InlineKeyboardButton("➕افزایش ترافیک", callback_data=('IDMNU&Traffic_' + cb))],
                        [InlineKeyboardButton("💀Kill User", callback_data=('IDMNU&Kill_' + cb)), InlineKeyboardButton("🔑تغییر پسورد", callback_data=('IDMNU&PASSWORD_' + cb))]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.edit_message_text(chat_id, msg, text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                except:
                    bot.edit_message_text(chat_id, msg, "چیزی پیدا نشد:(")
            else:
                message.reply_text("Menu /start")
        else:
            message.reply_text("Menu /start")
    else:
        status = get_cache_status(chat_id)

        if (chat_id not in (admin_id)) and ((status == "config") or ("host_" in status) or ("support" in status) or ("USP_" in status) or ("USU_" in status) or ("userwpm" == status) or ("usergift" == status) or ("Uname_" in status)):
            if (status == "config"):
                try:
                    host, user = get_host_username(link)
                except:
                    host = None
                    user = None
                keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
                rm = True
                if host is not None:
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    settings = get_settings()
                    if check_exist_user(host, user) is False:
                        try:
                            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                            text = Session.User_info(settings['dropbear'])
                            try:
                                USERNAME = message.from_user.username
                            except:
                                USERNAME = "None"
                            add_user_db(chat_id, message.from_user.first_name, USERNAME, user, host)
                            cb = host + "$" + user
                            keyboard = [
                                [InlineKeyboardButton("🔑تغییر پسورد", callback_data=('SELFCPA_' + cb))],
                                [InlineKeyboardButton("📲 کد QR و لینک اتصال", callback_data=f'QRCODE_{cb}')]
                            ]
                            if (settings['buy'] == 'on') or (chat_id in seller_id):
                                keyboard[0].insert(1, InlineKeyboardButton("🔄تمدید", callback_data=("UPG_" + cb)))
                            if (settings['buy-traffic'] == 'on') or (chat_id in seller_id):
                                keyboard.append([InlineKeyboardButton("🔁 خرید ترافیک", callback_data=("UTGB_" + cb))])
                            keyboard.append([InlineKeyboardButton("<<", callback_data='back')])
                        except:
                            text = "چیزی پیدا نشد:("
                    else:
                        try:
                            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                            text = Session.User_info(settings['dropbear'])
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
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text(text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                if rm is True:
                    delete_cache(chat_id)

            elif ("host_" in status):
                host = status.split("host_")[1]
                host, st = Check_in_hosts(host)
                user = link
                keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if st is True:
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    settings = get_settings()
                    if check_exist_user(host, user) is False:
                        try:
                            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                            text = Session.User_info(settings['dropbear'])
                            try:
                                USERNAME = message.from_user.username
                            except:
                                USERNAME = "None"
                            add_user_db(chat_id, message.from_user.first_name, USERNAME, user, host)
                            cb = host + "$" + user
                            keyboard = [
                                [InlineKeyboardButton("🔑تغییر پسورد", callback_data=('SELFCPA_' + cb))],
                                [InlineKeyboardButton("📲 کد QR و لینک اتصال", callback_data=f'QRCODE_{cb}')]
                            ]
                            if (settings['buy'] == 'on') or (chat_id in seller_id):
                                keyboard[0].insert(1, InlineKeyboardButton("🔄تمدید", callback_data=("UPG_" + cb)))
                            if (settings['buy-traffic'] == 'on') or (chat_id in seller_id):
                                keyboard.append([InlineKeyboardButton("🔁 خرید ترافیک", callback_data=("UTGB_" + cb))])
                            keyboard.append([InlineKeyboardButton("<<", callback_data='back')])
                        except:
                            text = "چیزی پیدا نشد:("
                    else:
                        try:
                            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                            text = Session.User_info(settings['dropbear'])
                        except:
                            text = "چیزی پیدا نشد:("
                else:
                    text = "چیزی پیدا نشد:("
                message.reply_text(text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
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
                keyboard = [[InlineKeyboardButton("پاسخ به " + name, callback_data='ANS_' + str(chat_id))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                sleep(0.2)
                message.reply_text(text='🫡بزودی درخواستتون بررسی میشه', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data="back")]]))
                delete_cache(chat_id)

            elif ("Uname_" in status):
                data = status.split("_")[1]
                if len(link) <= 12:
                    if (link not in filter_name) and (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                        link = link.lower()
                        cb_cc = "CC_" + data + "?" + link
                        cb_tr = "TR_" + data + "?" + link
                        cb_bl = "BL_" + data + "?" + link
                        if check_seller_exist(chat_id) is True:
                            keyboard = [[InlineKeyboardButton("💰کیف پول", callback_data=cb_bl)]]
                        else:
                            keyboard = [
                                [InlineKeyboardButton("💳کارت به کارت", callback_data=cb_cc), InlineKeyboardButton("💲ترون", callback_data=cb_tr)],
                                [InlineKeyboardButton("💰کیف پول", callback_data=cb_bl)]
                            ]
                        keyboard.append([InlineKeyboardButton("<<", callback_data='buy')])
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        name, u, p, old_value = get_full_user_data_id(chat_id)
                        text = "روش پرداخت انتخاب کنین:\n\nموجودی: \n" + str(old_value) + " تومن"
                        message.reply_text(text, reply_markup=reply_markup)
                        delete_cache(chat_id)
                    else:
                        message.reply_text("این نام کاربری قابل قبول نیست! نام کاربری دیگه ای بفرستین")
                else:
                    message.reply_text("نام کاربری خیلی طولانیه حداقل بین 1 تا 12 کاراکتر باشه")

            elif ("USP_" in status):
                host = (status.split("_")[1]).split("$")[0]
                user = status.split("$")[1]
                passw = link
                if 4 <= len(passw) <= 16:
                    if (link not in filter_name) and (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                        try:
                            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                            text = Session.Password(passw)
                            if "Error" not in text:
                                text = f"پسورد اکانت {user} به {passw} تغییر پیدا کرد 🫵"
                            else:
                                text = "خطایی پیش اومد بعدا امتحان کنین😑"
                        except:
                            text = "خطایی پیش اومد بعدا امتحان کنین😑"
                        message.reply_text(text)
                        delete_cache(chat_id)
                    else:
                        message.reply_text("این پسورد قابل قبول نیست باید ترکیبی از حروف انگلیسی و اعداد باشه")
                elif len(passw) <= 3:
                    message.reply_text("پسورد خیلی کوتاهه! بین 4 تا 16 کاراکتر باید باشه")
                else:
                    message.reply_text("پسورد خیلی طولانیه! بین 4 تا 16 کاراکتر باید باشه")

            elif ("USU_" in status):
                host = (status.split("_")[1]).split("$")[0]
                user = status.split("$")[1]
                if len(link) <= 16:
                    if (link not in filter_name) and (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                        try:
                            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                            text = Session.Username(link)
                            if "Error" not in text:
                                text = f"نام کاربری اکانت {user} به {link} تغییر پیدا کرد 🫵"
                                update_user_username(user, link, host)
                            else:
                                text = "خطایی پیش اومد بعدا امتحان کنین😑"
                        except:
                            text = "خطایی پیش اومد بعدا امتحان کنین😑"
                        message.reply_text(text)
                        delete_cache(chat_id)
                    else:
                        message.reply_text("این نام کاربری قابل قبول نیست! نام کاربری دیگه ای بفرستین")
                else:
                    message.reply_text("نام کاربری خیلی طولانیه حداقل بین 1 تا 16 کاراکتر باشه")

            elif ("userwpm" == status):
                try:
                    deposit = int(link)
                    if deposit >= 10000:
                        if deposit <= 1000000000:
                            add_collector(chat_id, "deposit", [], [])
                            cache_list = [deposit]
                            delete_cache(chat_id)
                            add_cache(chat_id, "deposit")
                            cb_cc = "CUWPD_" + str(deposit)
                            cb_tr = "TUWPD_" + str(deposit)
                            keyboard = [
                                [InlineKeyboardButton("💳کارت به کارت", callback_data=cb_cc), InlineKeyboardButton("💲ترون", callback_data=cb_tr)],
                                [InlineKeyboardButton("<< back", callback_data='UWM')]
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            message.reply_text("روش پرداختو انتخاب کن:", reply_markup=reply_markup)
                            update_collector(chat_id, cache_list, [])
                        else:
                            message.reply_text("مبلغ خیلی بالاست عدد کمتری بفرست")
                    else:
                        message.reply_text("مبلغی که فرستادی خیلی کمه")
                except:
                    message.reply_text("مبلغ به عدد وارد کنین !")

            elif ("usergift" == status):
                keyboard = [[InlineKeyboardButton("<< back", callback_data='UWM')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if check_gift_code_exist(link) is True:
                    value, kind, count, users_id, timer_expiry = get_gift_code_full(link)
                    if (timer_expiry - int(time())) > 0:
                        if chat_id not in users_id:
                            if len(users_id) <= count:
                                name, u, phone, old_value = get_full_user_data_id(chat_id)
                                new_value = value + old_value
                                update_user_wallet(chat_id, new_value)
                                users_id.append(chat_id)
                                update_gift_code_by_chat_id(link, users_id)
                                message.reply_text("انجام شد ✅", reply_markup=reply_markup)
                            else:
                                message.reply_text("این دیگه قابل استفاده نیست", reply_markup=reply_markup)
                        else:
                            message.reply_text("شما قبلا از این کد استفاده کردین", reply_markup=reply_markup)
                    else:
                        message.reply_text("زمان استفاده از این کد به اتمام رسیده", reply_markup=reply_markup)
                else:
                    message.reply_text("این کد وجود نداره", reply_markup=reply_markup)
                delete_cache(chat_id)

            return

        if status == "name_none":
            if len(link) <= 16:
                if (link not in filter_name) and (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                    link = link.lower()
                    cache_list, host_cahce = get_collector_cache(chat_id)
                    message.reply_text("حجمو بفرستین فقط بصورت عدد مثلا 10 گیگ (0 = نامحدود) یا /cancel")
                    cache_list.append(link)
                    delete_cache(chat_id)
                    add_cache(chat_id, "GB_none")
                    update_collector(chat_id, cache_list, host_cahce)
                else:
                    message.reply_text("این نام کاربری قابل قبول نیست! نام کاربری دیگه ای بفرستین")
            else:
                message.reply_text("نام کاربری خیلی طولانیه حداقل بین 1 تا 16 کاراکتر باشه")

        elif status == "GB_none":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "connection_none")
                update_collector(chat_id, cache_list, host_cahce)
                message.reply_text("تعداد محدودیت کانکشن بفرستین یا /cancel")
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif status == "connection_none":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("خب حالا تعداد روز بفرستین")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "days_none")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif status == "days_none":
            try:
                try:
                    days = int(link)
                except:
                    message.reply_text("فقط میتونی عدد بفرستی")
                    return
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
                    t1 = f"💲فروشنده💲\nخرید \nserver: {host}\nuser: {user}\ndays: {days}\nGB: {traffic}\nConnection: {connection_limit}"
                    text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\ninfo buy:\n" + t1
                    cb = "Confirmed_" + code
                    no = "NO❌_" + code
                    keyboard = [[InlineKeyboardButton("Confirm✅", callback_data=cb), InlineKeyboardButton("NO❌", callback_data=no)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    for i in range(len(admin_id)):
                        try:
                            bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                        except:
                            pass
                    cache_list = [days, traffic, connection_limit, '90', name, user, host]
                    add_code_buy(chat_id, code, "check", cache_list)
                    message.reply_text("ادمین ها بزودی درخواستتون بررسی میکنن.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='back')]]))
                else:
                    msg = message.reply_text("Wait...").id
                    passw = str(randint(123456, 999999))
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                        description = f"[ Bot - Admin ] Date: ( {str(jdatetime.datetime.now()).split('.')[0]} )"
                        text = Session.Create(cache_list[1], passw, int(cache_list[-1]), int(link), int(cache_list[2]), description, False)
                        port, udgpw = Session.Ports()
                        HOST = ((text.split("SSH Host : ")[1]).split("\n")[0])
                        url = f'ssh://{cache_list[1]}:{passw}@{HOST}:{port}#{cache_list[1]}'
                        photo = QR_Maker(url)
                        text += "\n\nURL: " + "<pre>" + url + "</pre>"
                        bot.send_photo(chat_id, open(photo, 'rb'), text, parse_mode=enums.ParseMode.HTML)
                        os.remove(photo)
                        cb = "IDADMIN_" + host + "$" + cache_list[1]
                        keyboard = [[InlineKeyboardButton("اطلاعات کامل ℹ️", callback_data=cb)], [InlineKeyboardButton("<<", callback_data='back')]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        bot.send_message(chat_id, "برای دریافت اطلاعات کامل اکانت کلیک کن:", reply_markup=reply_markup)
                        bot.delete_messages(chat_id, msg)
                    except Exception as e:
                        bot.edit_message_text(chat_id, msg, "Error: " + str(e))
                delete_cache(chat_id)
                delete_collector(chat_id)
            except Exception as e:
                message.reply_text(f"Error: {str(e)}")

        elif status == "updatepassword":
            hosts, remarks = sshx.HOSTS()
            if link in hosts:
                delete_cache(chat_id)
                cache_list = []
                cache_list.append(link)
                add_collector(chat_id, "updatepassword-user", cache_list, [])
                add_cache(chat_id, "updatepassword-user")
                message.reply_text('نام کاربری رو بفرست')
            else:
                message.reply_text("این آدرس پنل وجود نداره, آدرس درستو بفرستین ")

        elif status == "updatepassword-user":
            user = link
            cache_list, host_cahce = get_collector_cache(chat_id)
            host = cache_list[0]
            if check_seller_exist(chat_id) is True:
                if check_exist_user(host, user) is False:
                    message.reply_text('There is not any user with this username, check capital or small letters or /cancel\nکاربری با این نام کاربری وجود نداره چک کنید حروف بزرگ و کوچیکو')
                    return
                else:
                    ID, Name, Username = get_all_user_data(host, user)
                    if ID != chat_id:
                        bot.edit_message_text(chat_id, msg, "نام کاربری پیدا نشد!", parse_mode=enums.ParseMode.HTML)
                        return
            if check_exist_user(cache_list[0], user) is True:
                cache_list.append(user)
                delete_cache(chat_id)
                add_cache(chat_id, "password")
                message.reply_text("پسورد جدیدو بفرستین")
                update_collector(chat_id, cache_list, [])
            else:
                message.reply_text("این نام کاربری وجود نداره نام کاربری دیگه ای رو بفرستین یا /cancel")

        elif status == "password":
            try:
                user = link
                text = ""
                cache_list, host_cahce = get_collector_cache(chat_id)
                host = cache_list[0]
                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                try:
                    Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                    text = Session.User_info(get_settings()['dropbear'])
                    if "Error" not in text:
                        message.reply_text("پسورد جدیدو بفرستین")
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
                if 4 <= len(passw) <= 16:
                    if (link not in filter_name) and (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                        cache_list, host_cahce = get_collector_cache(chat_id)
                        host = cache_list[0]
                        user = cache_list[1]
                        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                        Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                        text = Session.Password(passw)
                        message.reply_text(text)
                        delete_cache(chat_id)
                        delete_collector(chat_id)
                    else:
                        message.reply_text("این پسورد قابل قبول نیست باید ترکیبی از حروف انگلیسی و اعداد باشه")
                elif len(passw) <= 3:
                    message.reply_text("پسورد خیلی کوتاهه! بین 4 تا 16 کاراکتر بفرستین")
                else:
                    message.reply_text("پسورد خیلی طولانیه! بین 4 تا 16 کاراکتر بفرستین")
            except Exception as e:
                message.reply_text(f"Error: {str(e)}")
                delete_cache(chat_id)
                delete_collector(chat_id)

        elif status == "updateusername":
            hosts, remarks = sshx.HOSTS()
            if link in hosts:
                delete_cache(chat_id)
                cache_list = []
                cache_list.append(link)
                add_collector(chat_id, "updateusername-user", cache_list, [])
                add_cache(chat_id, "updateusername-user")
                message.reply_text('نام کاربری رو بفرست')
            else:
                message.reply_text("این آدرس پنل وجود نداره, آدرس درستو بفرستین ")

        elif status == "updateusername-user":
            user = link
            cache_list, host_cahce = get_collector_cache(chat_id)
            host = cache_list[0]
            if check_seller_exist(chat_id) is True:
                if check_exist_user(host, user) is False:
                    message.reply_text('There is not any user with this username, check capital or small letters or /cancel\nکاربری با این نام کاربری وجود نداره چک کنید حروف بزرگ و کوچیکو')
                    return
                else:
                    ID, Name, Username = get_all_user_data(host, user)
                    if ID != chat_id:
                        bot.edit_message_text(chat_id, msg, "نام کاربری پیدا نشد!", parse_mode=enums.ParseMode.HTML)
                        return
            if check_exist_user(cache_list[0], user) is True:
                cache_list.append(user)
                delete_cache(chat_id)
                add_cache(chat_id, "username")
                message.reply_text("نام کاربری جدیدو بفرستین")
                update_collector(chat_id, cache_list, [])
            else:
                message.reply_text("این نام کاربری وجود نداره نام کاربری دیگه ای رو بفرستین یا /cancel")

        elif status == "username":
            try:
                user = link
                text = ""
                cache_list, host_cahce = get_collector_cache(chat_id)
                host = cache_list[0]
                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                try:
                    Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                    text = Session.User_info(get_settings()['dropbear'])
                    if "Error" not in text:
                        message.reply_text("نام کاربری جدیدو بفرستین")
                        cache_list.append(link)
                        delete_cache(chat_id)
                        add_cache(chat_id, "CUsername")
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

        elif status == "CUsername":
            try:
                if len(link) <= 16:
                    if (link not in filter_name) and (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                        cache_list, host_cahce = get_collector_cache(chat_id)
                        host = cache_list[0]
                        user = cache_list[1]
                        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                        Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                        text = Session.Username(link)
                        if check_exist_user(host, user) is True:
                            update_user_username(user, link, host)
                        message.reply_text(text)
                        delete_cache(chat_id)
                        delete_collector(chat_id)
                    else:
                        message.reply_text("این نام کاربری قابل قبول نیست! نام کاربری دیگه ای بفرستین")
                else:
                    message.reply_text("نام کاربری خیلی طولانیه حداقل بین 1 تا 16 کاراکتر باشه")
            except Exception as e:
                message.reply_text(f"Error: {str(e)}")
                delete_cache(chat_id)
                delete_collector(chat_id)

        elif status == "name":
            if len(link) <= 16:
                if (link not in filter_name) and (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                    link = link.lower()
                    cache_list, host_cahce = get_collector_cache(chat_id)
                    message.reply_text("حجمو بفرستین فقط بصورت عدد مثلا 10 گیگ (0 = نامحدود) یا /cancel")
                    cache_list.append(link)
                    delete_cache(chat_id)
                    add_cache(chat_id, "GB")
                    update_collector(chat_id, cache_list, host_cahce)
                else:
                    message.reply_text("این نام کاربری قابل قبول نیست! نام کاربری دیگه ای بفرستین")
            else:
                message.reply_text("نام کاربری خیلی طولانیه حداقل بین 1 تا 16 کاراکتر باشه")

        elif status == "GB":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("خب یه پیام از کاربر فوروارد کنین")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "forward")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif status == 'forward':
            message.reply_text("یه پیام از کاربر مورد نظر فوروارد کن یا /cancel")

        elif status == "connection":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("خب حالا تعداد روز بفرستین")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "days")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

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
                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                try:
                    Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                    description = f"[ Bot - Admin ] Date: ( {str(jdatetime.datetime.now()).split('.')[0]} ), userID: {str(user_id)}, Username: {Username}"
                    text = Session.Create(cache_list[1], passw, int(cache_list[-1]), int(link), int(cache_list[2]), description, False)
                    port, udgpw = Session.Ports()
                    HOST = ((text.split("SSH Host : ")[1]).split("\n")[0])
                    url = f'ssh://{cache_list[1]}:{passw}@{HOST}:{port}#{cache_list[1]}'
                    photo = QR_Maker(url)
                    text += "\n\nURL: " + "<pre>" + url + "</pre>"
                    bot.send_photo(chat_id, open(photo, 'rb'), text, parse_mode=enums.ParseMode.HTML)
                    os.remove(photo)
                    cb = "IDADMIN_" + host + "$" + cache_list[1]
                    keyboard = [[InlineKeyboardButton("اطلاعات کامل ℹ️", callback_data=cb)], [InlineKeyboardButton("<<", callback_data='back')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.send_message(chat_id, "برای دریافت اطلاعات کامل اکانت کلیک کن:", reply_markup=reply_markup)
                    add_user_db(user_id, name, Username, cache_list[1], host)
                    bot.delete_messages(chat_id, msg)
                except Exception as e:
                    bot.edit_message_text(chat_id, msg, "Error: " + str(e))
                delete_cache(chat_id)
                delete_collector(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "remove_" in status:
            msg = message.reply_text("Wait...").id
            user = link
            host = status.split("remove_")[1]
            try:
                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                text = Session.Disable()
                Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                text = Session.Delete(user)
                if check_exist_user(host, user) is True:
                    delete_user(host, user)
                    text += "\n\nand Deleted from DB"
            except Exception as e:
                text = "Error: " + str(e)
            delete_cache(chat_id)
            bot.edit_message_text(chat_id, msg, text)

        elif status == "updatetraffic":
            hosts, remarks = sshx.HOSTS()
            if link in hosts:
                delete_cache(chat_id)
                cache_list = []
                cache_list.append(link)
                add_collector(chat_id, "plus", cache_list, [])
                add_cache(chat_id, "plus")
                message.reply_text('نام کاربری رو بفرست')
            else:
                message.reply_text("این آدرس پنل وجود نداره, آدرس درستو بفرستین ")

        elif status == "updatehost":
            hosts, remarks = sshx.HOSTS()
            if link in hosts:
                delete_cache(chat_id)
                add_cache(chat_id, "update_" + link)
                message.reply_text('نام کاربری رو بفرست')
            else:
                message.reply_text("این آدرس پنل وجود نداره, آدرس درستو بفرستین ")

        elif "update_" in status:
            user = link
            host = status.split("update_")[1]
            if check_seller_exist(chat_id) is True:
                if check_exist_user(host, user) is False:
                    message.reply_text('There is not any user with this username, check capital or small letters or /cancel\nکاربری با این نام کاربری وجود نداره چک کنید حروف بزرگ و کوچیکو')
                    return
                else:
                    ID, Name, Username = get_all_user_data(host, user)
                    if ID != chat_id:
                        bot.edit_message_text(chat_id, msg, "نام کاربری پیدا نشد!", parse_mode=enums.ParseMode.HTML)
                        return
            add_collector(chat_id, "update", [], [])
            cache_list = [host, user]
            delete_cache(chat_id)
            add_cache(chat_id, "GB-update")
            message.reply_text("حجمو به عدد بفرستین مثلا 10 گیگ (0 = نامحدود)")
            update_collector(chat_id, cache_list, [])

        elif status == "GB-update":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("خب حالا تعداد کانکشن بفرستین")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "connection-update")
                update_collector(chat_id, cache_list, [])
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif status == "connection-update":
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("خب حالا تعداد روز بفرستین")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "days-update")
                update_collector(chat_id, cache_list, [])
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

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
                    t1 = f"💲فروشنده💲\nتمدید\ndays: {days}\nGB: {traffic}\nConnection: {connection_limit}\nHost: {host}\nUser: {user}"
                    text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\ninfo buy:\n" + t1
                    cb = "ConfirmUPGRADE_" + code
                    no = "NO❌_" + code
                    keyboard = [[InlineKeyboardButton("Confirm✅", callback_data=cb), InlineKeyboardButton("NO❌", callback_data=no)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    for i in range(len(admin_id)):
                        try:
                            bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                        except:
                            pass
                    cache_list = [days, traffic, connection_limit, '90', user, host]
                    add_code_buy(chat_id, code, "checkup", cache_list)
                    message.reply_text("ادمین ها بزودی درخواستتون بررسی میکنن.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='back')]]))
                else:
                    msg = message.reply_text("Wait...").id
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, port, panel, 'User', cache_list[1])
                        text = Session.Update(int(cache_list[2]), days, int(cache_list[-1]))
                        try:
                            if cache_list[1] in checked_users:
                                checked_users.remove(cache_list[1])
                                checked_id.remove(checked_id[checked_users.index(cache_list[1])])
                        except Exception as e:
                            print("Error (line checked_id) : ", str(e))
                    except Exception as e:
                        text = "Error: " + str(e)
                    bot.edit_message_text(chat_id, msg, text)
                cache_list.clear()
                delete_cache(chat_id)
                delete_collector(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif status == "plus":
            cache_list, host_cahce = get_collector_cache(chat_id)
            host = cache_list[0]
            user = link
            if check_seller_exist(chat_id) is True:
                if check_exist_user(host, user) is False:
                    message.reply_text('There is not any user with this username, check capital or small letters or /cancel\nکاربری با این نام کاربری وجود نداره چک کنید حروف بزرگ و کوچیکو')
                    return
                else:
                    ID, Name, Username = get_all_user_data(host, user)
                    if ID != chat_id:
                        bot.edit_message_text(chat_id, msg, "نام کاربری پیدا نشد!", parse_mode=enums.ParseMode.HTML)
                        delete_cache(chat_id)
                        delete_collector(chat_id)
                        return
            cache_list.append(user)
            delete_cache(chat_id)
            add_cache(chat_id, "plus-Traffic")
            message.reply_text("حجمو به عدد بفرستین مثلا 10 گیگ (0 = نامحدود)")
            update_collector(chat_id, cache_list, [])

        elif status == "plus-Traffic":
            try:
                traffic = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                host = cache_list[0]
                user = cache_list[1]
                if check_seller_exist(chat_id) is True:
                    code = uuid4().hex[0:10]
                    name = message.from_user.first_name
                    try:
                        username = "@" + message.from_user.username
                    except:
                        username = 'Null'
                    t1 = f"💲فروشنده💲\nافزایش ترافیک 🔃\n\nGB: {str(traffic)}\nHost: {host}\nUser: {user}"
                    text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\ninfo buy:\n" + t1
                    cb = "ConfirmTraffic_" + code
                    no = "NO❌_" + code
                    keyboard = [[InlineKeyboardButton("Confirm✅", callback_data=cb), InlineKeyboardButton("NO❌", callback_data=no)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    for i in range(len(admin_id)):
                        try:
                            bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                        except:
                            pass
                    cache_list = [traffic, '0', user, host]
                    add_code_buy(chat_id, code, "checkup", cache_list)
                    message.reply_text("ادمین ها بزودی درخواستتون بررسی میکنن.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='back')]]))
                else:
                    msg = message.reply_text("Wait...").id
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                        text = Session.Update_Traffic(traffic)
                    except Exception as e:
                        text = "Error: " + str(e)
                    bot.edit_message_text(chat_id, msg, text)
                delete_cache(chat_id)
                delete_collector(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif status == "infohost":
            hosts, remarks = sshx.HOSTS()
            if link in hosts:
                delete_cache(chat_id)
                add_cache(chat_id, "userinfo_" + link)
                message.reply_text('نام کاربری رو بفرستین')
            else:
                message.reply_text("این آدرس پنل وجود نداره, آدرس درستو بفرستین ")

        elif "userinfo_" in status:
            msg = message.reply_text("Wait...").id
            user = link
            host = status.split("userinfo_")[1]
            try:
                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                if check_seller_exist(chat_id) is True:
                    if check_exist_user(host, user) is True:
                        ID, Name, Username = get_all_user_data(host, user)
                        if ID != chat_id:
                            bot.edit_message_text(chat_id, msg, "نام کاربری پیدا نشد!", parse_mode=enums.ParseMode.HTML)
                            return
                Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                text = Session.User_info(get_settings()['dropbear'])
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
            bot.edit_message_text(chat_id, msg, text, parse_mode=enums.ParseMode.HTML)

        elif status == "userconfigs":
            try:
                user_id = int(link)
                keyboard = []
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
                    message.reply_text(f"Founded by id \n\nChoose: ", reply_markup=reply_markup)
                else:
                    keyboard.append([InlineKeyboardButton("<< Back", callback_data='back_admin')])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text("پیدا نشد❌", reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("send only user ID or forward a message not username or anything else", reply_markup=reply_markup)

        elif status == "message":
            delete_cache(chat_id)
            msg = message.reply_text("Sending...").id
            fname = "All.txt"
            sent = 0
            with open(fname, 'r') as f:
                for usertxt in f:
                    try:
                        bot.send_message(int(usertxt.replace('\n', '')), link, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)
                        sent += 1
                    except:
                        continue
            bot.send_message(chat_id, f"به {str(sent)} کاربر فرستاده شدد")
            bot.delete_messages(chat_id, msg)

        elif status == "answer":
            cache_list, host_cahce = get_collector_cache(chat_id)
            try:
                keyboard = [[InlineKeyboardButton("✍️ پاسخ", callback_data=('SUPRT_' + str(chat_id)))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(int(cache_list[0]), link, reply_markup=reply_markup)
                message.reply_text("پیامت فرستاده شد")
            except:
                message.reply_text("کاربر رباتو بلاک کرده")
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
            message.reply_text("Done✔️", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='wallet')]]))

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
                message.reply_text("Done✔️", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='wallet')]]))
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif ("disable_" in status) or ("enable_" in status):
            msg = message.reply_text("Wait...").id
            try:
                if "disable" in status:
                    host = status.split("disable_")[1]
                else:
                    host = status.split("enable_")[1]
                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                uname = link
                if "</pre>" in uname:
                    uname = uname.split("</pre>")[0].split("<pre>")[1]
                Session = sshx.PANNEL(host, username, password, port, panel, 'User', uname)
                if "disable" in status:
                    bot.edit_message_text(chat_id, msg, Session.Disable(), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='Manager')]]))
                else:
                    bot.edit_message_text(chat_id, msg, Session.Enable(), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='Manager')]]))
            except Exception as e:
                bot.edit_message_text(chat_id, msg, "Error: " + str(e), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='Manager')]]))
            delete_cache(chat_id)

        elif status == "limit_seller":
            try:
                limit = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("مقدار موجودی فروشنده رو به صورت تومن و عددی بفرستین:")
                cache_list.append(limit)
                delete_cache(chat_id)
                add_cache(chat_id, "Balance_add_seller")
                update_collector(chat_id, cache_list, [])
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif status == "Balance_add_seller":
            try:
                cache_list, host_cahce = get_collector_cache(chat_id)
                balance = int(link)
                if check_user_exists_in_clients_table(int(cache_list[0])) is False:
                    add_client_db(int(cache_list[0]), cache_list[1], cache_list[2], 'None', 0)
                add_seller(int(cache_list[0]), cache_list[1], cache_list[2], cache_list[3])
                update_user_wallet(int(cache_list[0]), balance)
                delete_cache(chat_id)
                delete_collector(chat_id)
                keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                sellers_id_add_list()
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "Kill_" in status:
            msg = message.reply_text("Wait...", reply_markup=reply_markup).id
            keyboard = [[InlineKeyboardButton("<<", callback_data='Manager')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                user = link
                host = status.split("Kill_")[1]
                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                text, users = Session.Kill(user)
                bot.edit_message_text(chat_id, msg, text, reply_markup=reply_markup)
            except Exception as e:
                bot.edit_message_text(chat_id, msg, "Error: " + str(e), reply_markup=reply_markup)
            delete_cache(chat_id)

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
                message.reply_text("فقط میتونی عدد بفرستی")

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
                    message.reply_text("مقدار خیلی بالاست بین 1 تا 72 بفرستین")
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "ETM" == status:
            if len(link) <= 3900:
                settings = get_settings()
                settings['mac'] = fixed_link_json(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='Tutorials')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("این پیام خیلی طولانیه! پیام دیگه ای رو بفرستین یا /cancel", reply_markup=reply_markup)

        elif "ETW" == status:
            if len(link) <= 3900:
                settings = get_settings()
                settings['windows'] = fixed_link_json(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='Tutorials')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("این پیام خیلی طولانیه! پیام دیگه ای رو بفرستین یا /cancel", reply_markup=reply_markup)

        elif "ETA" == status:
            if len(link) <= 3900:
                settings = get_settings()
                settings['android'] = fixed_link_json(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='Tutorials')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("این پیام خیلی طولانیه! پیام دیگه ای رو بفرستین یا /cancel", reply_markup=reply_markup)

        elif "ETI" == status:
            if len(link) <= 3900:
                settings = get_settings()
                settings['ios'] = fixed_link_json(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='Tutorials')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("این پیام خیلی طولانیه! پیام دیگه ای رو بفرستین یا /cancel", reply_markup=reply_markup)

        elif "EAID" == status:
            if len(link) <= 3900:
                settings = get_settings()
                settings['support'] = fixed_link_json(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='SID')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("این پیام خیلی طولانیه! پیام دیگه ای رو بفرستین یا /cancel", reply_markup=reply_markup)

        elif "Start_message" == status:
            if len(link) <= 3900:
                settings = get_settings()
                settings['start'] = fixed_link_json(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='WSMSG')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("این پیام خیلی طولانیه! پیام دیگه ای رو بفرستین یا /cancel", reply_markup=reply_markup)

        elif "Price_message" == status:
            if len(link) <= 3900:
                settings = get_settings()
                settings['list'] = fixed_link_json(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='WLMSG')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("این پیام خیلی طولانیه! پیام دیگه ای رو بفرستین یا /cancel", reply_markup=reply_markup)

        elif "after_buy" == status:
            if len(link) <= 3900:
                settings = get_settings()
                settings['after_buy'] = fixed_link_json(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='PODSC')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("این پیام خیلی طولانیه! پیام دیگه ای رو بفرستین یا /cancel", reply_markup=reply_markup)

        elif "ETTR" == status:
            try:
                int(link)
                settings = get_settings()
                settings['test-traffic'] = int(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='TASET')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("فقط عدد میتونین بفرستین")

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
                    message.reply_text("🔴Error: ربات تو کانال یا گروه اد نشده")
                    delete_cache(chat_id)

                except BadRequest as e:
                    if "USER_NOT_PARTICIPANT" in str(e):
                        message.reply_text("🔴Error: توی چنل یا گروه نیستی")
                    else:
                        message.reply_text("🔴Error: گروه یا چنلی که فرستادی وجود نداره")
                    delete_cache(chat_id)

            else:
                message.reply_text("فرم درست بفرستین مثل: @channel")

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
                message.reply_text("فقط میتونی عدد بفرستی")

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
                message.reply_text("فقط میتونی عدد بفرستی")

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
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "invite" == status:
            try:
                referral = int(link)
                settings = get_settings()
                settings['referral'] = referral
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='INVS')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "S_Traffic_price" == status:
            try:
                price = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("خب حالا مقدار حجمو به عدد بفرستین مثلا 50 گیگ")
                cache_list.append(price)
                delete_cache(chat_id)
                add_cache(chat_id, "S_Traffic_GB")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "S_Traffic_GB" == status:
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                settings = get_settings()
                prices = settings['seller_plus_prices']
                prices.append(cache_list[0])
                settings['seller_plus_prices'] = prices
                traffic = settings['seller_plus_traffic']
                traffic.append(int(link))
                settings['seller_plus_traffic'] = traffic
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='ADTPR')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
                delete_collector(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "Traffic_price" == status:
            try:
                price = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("خب حالا مقدار حجمو به عدد بفرستین مثلا 50 گیگ")
                cache_list.append(price)
                delete_cache(chat_id)
                add_cache(chat_id, "Traffic_GB")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "Traffic_GB" == status:
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                settings = get_settings()
                prices = settings['plus-prices']
                prices.append(cache_list[0])
                settings['plus-prices'] = prices
                traffic = settings['plus-traffic']
                traffic.append(int(link))
                settings['plus-traffic'] = traffic
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='ADTPR')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
                delete_collector(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "A_price" == status:
            try:
                price = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("تعداد محدودیت اتصال کاربر به عدد بفرستین")
                cache_list.append(price)
                delete_cache(chat_id)
                add_cache(chat_id, "A_connections")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "A_connections" == status:
            try:
                connections = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("تعداد روز بفرستین")
                cache_list.append(connections)
                delete_cache(chat_id)
                add_cache(chat_id, "A_days")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "A_days" == status:
            try:
                days = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("مقدار ترافیک به عدد بفرستین مثلا 10 گیگ (0 = نامحدود)")
                cache_list.append(days)
                delete_cache(chat_id)
                add_cache(chat_id, "A_traffic")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "A_traffic" == status:
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                settings = get_settings()
                prices = settings['prices']
                prices.append(cache_list[0])
                settings['prices'] = prices
                connections = settings['connections']
                connections.append(cache_list[1])
                settings['connections'] = connections
                days = settings['days']
                days.append(cache_list[2])
                settings['days'] = days
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
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "S_price" == status:
            try:
                price = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("تعداد محدودیت اتصال کاربر به عدد بفرستین")
                cache_list.append(price)
                delete_cache(chat_id)
                add_cache(chat_id, "S_connections")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "S_connections" == status:
            try:
                connections = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("تعداد روز بفرستین")
                cache_list.append(connections)
                delete_cache(chat_id)
                add_cache(chat_id, "S_days")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "S_days" == status:
            try:
                days = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("مقدار ترافیک به عدد بفرستین مثلا 10 گیگ (0 = نامحدود)")
                cache_list.append(days)
                delete_cache(chat_id)
                add_cache(chat_id, "S_traffic")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "S_traffic" == status:
            try:
                int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                settings = get_settings()
                prices = settings['seller_prices']
                prices.append(cache_list[0])
                settings['seller_prices'] = prices
                connections = settings['seller_connections']
                connections.append(cache_list[1])
                settings['seller_connections'] = connections
                days = settings['seller_days']
                days.append(cache_list[2])
                settings['seller_days'] = days
                traffic = settings['seller_traffic']
                traffic.append(int(link))
                settings['seller_traffic'] = traffic
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='XSM')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
                delete_collector(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "proxy" == status:
            if "t.me/proxy?" in link:
                settings = get_settings()
                settings['proxy'] = fixed_link_json(link)
                update_settings(settings)
                keyboard = [[InlineKeyboardButton("<<", callback_data='Sprx')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("اینطوری پروکسیو بفرستین:\n https://t.me/proxy?server=... or /cancel")

        elif "Connectionmsg_" in status:
            if len(link) <= 128:
                host = status.split("Connectionmsg_")[1]
                hosts, remarks = sshx.HOSTS()
                if host in hosts:
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                        text = Session.Message(link)
                    except Exception as e:
                        text = "Error: " + str(e)
                else:
                    text = "سرور پیدا نشد"
                keyboard = [[InlineKeyboardButton("<< Menu", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text(text, reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("پیام خیلی طولانیه حداکثر 128 کاراکتر")

        elif "AutoRemove_" in status:
            try:
                days = int(link)
                host = status.split("AutoRemove_")[1]
                hosts, remarks = sshx.HOSTS()
                if host in hosts:
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                        text = Session.Auto_remove(days)
                    except Exception as e:
                        text = "Error: " + str(e)
                else:
                    text = "سرور پیدا نشد"
                keyboard = [[InlineKeyboardButton("<< Menu", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text(text, reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "Gift_" in status:
            try:
                days = int(link)
                host = status.split("Gift_")[1]
                hosts, remarks = sshx.HOSTS()
                if host in hosts:
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                        text = Session.Gift(days)
                    except Exception as e:
                        text = "Error: " + str(e)
                else:
                    text = "سرور پیدا نشد"
                keyboard = [[InlineKeyboardButton("<< Menu", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text(text, reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "Reset_" in status:
            try:
                user = link
                host = status.split("Reset_")[1]
                hosts, remarks = sshx.HOSTS()
                if host in hosts:
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    try:
                        Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
                        text = Session.Reset_traffic()
                    except Exception as e:
                        text = "Error: " + str(e)
                else:
                    text = "سرور پیدا نشد"
            except Exception as e:
                text = "Error: " + str(e)
            keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message.reply_text(text, reply_markup=reply_markup)
            delete_cache(chat_id)

        elif status == "AdminGiftDel":
            if check_gift_code_exist(link) is True:
                delete_gift_code(link)
                keyboard = [[InlineKeyboardButton("<<", callback_data='GUA')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("این کد وجود نداره یه کد دیگرو بفرست یا /cancel")

        elif status == "AdminGift":
            try:
                value = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("تعداد محدودیت استفاده از کد به صورت عدد بفرستین")
                cache_list.append(value)
                delete_cache(chat_id)
                add_cache(chat_id, "Glimit")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif status == "Glimit":
            try:
                limit = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("تعداد روز استفاده از کد به صورت عدد بفرستین")
                cache_list.append(limit)
                delete_cache(chat_id)
                add_cache(chat_id, "Dlimit")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif status == "Dlimit":
            try:
                limit = int(link)
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("کد هدیه رو بصورت انگلیسی تایپ کنین و بفرستین مثل: gift_code")
                cache_list.append(limit)
                delete_cache(chat_id)
                add_cache(chat_id, "Giftcode")
                update_collector(chat_id, cache_list, host_cahce)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "Giftcode" == status:
            if (link not in filter_name) and (sshx.ASCII_Check(link) is True):
                Gift_code = link
                if check_gift_code_exist(Gift_code) is False:
                    cache_list, host_cahce = get_collector_cache(chat_id)
                    #cache_list = [value, userlimit, daylimit]
                    days = int(time()) + (cache_list[2] * 86400)
                    add_gift_code(cache_list[0], cache_list[1], days, Gift_code)
                    keyboard = [[InlineKeyboardButton("<<", callback_data='GUA')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text("Done✔️", reply_markup=reply_markup)
                    delete_cache(chat_id)
                    delete_collector(chat_id)
                else:
                    message.reply_text("این کد وجود داره یه کد دیگرو بفرست یا /cancel")
            else:
                message.reply_text("کد مورد نظر قابل قبول نیست کد دیگه رو بفرست یا /cancel")

        elif status == "Adminuserbalance":
            keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                user_id = int(link)
                if check_user_exists_in_clients_table(user_id) is True:
                    name, u, phone, value = get_full_user_data_id(user_id)
                    keyboard = [
                        [InlineKeyboardButton("➖کاهش", callback_data=f'MAUB_{str(user_id)}'), InlineKeyboardButton("➕افزایش", callback_data=f'PAUB_{str(user_id)}')],
                        [InlineKeyboardButton("0️⃣صفر کردن موجودی", callback_data=f'ZAUB_{str(user_id)}')],
                        [InlineKeyboardButton("<<", callback_data='back_admin')]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text(f"موجودی: {str(value)} تومن.\n\nName: {name}\nUsername: {u}\nPhone: {phone}", reply_markup=reply_markup)
                    delete_cache(chat_id)
                else:
                    message.reply_text("🔵 این کاربر وجود نداره", reply_markup=reply_markup)
            except:
                message.reply_text("❌آیدی عددی کاربر یا یه پیام از کاربر فوروارد کنین")

        elif "MBalance_" in status:
            try:
                new_value = int(link)
                user_id = int(status.split("MBalance_")[1])
                name, u, phone, old_value = get_full_user_data_id(user_id)
                value = old_value - new_value
                update_user_wallet(user_id, value)
                keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "PBalance_" in status:
            try:
                new_value = int(link)
                user_id = int(status.split("PBalance_")[1])
                name, u, phone, old_value = get_full_user_data_id(user_id)
                value = old_value + new_value
                update_user_wallet(user_id, value)
                keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply_text("Done✔️", reply_markup=reply_markup)
                delete_cache(chat_id)
            except:
                message.reply_text("فقط میتونی عدد بفرستی")

        elif "MPST_" in status:
            delete_cache(chat_id)
            host = status.split("MPST_")[1]
            t0 = link
            hosts, remarks = sshx.HOSTS()
            if host in hosts:
                count = 0
                rec = get_all_users_in_host(host)
                msg = message.reply_text("Sending...").id
                for i in range(len(rec)):
                    ID = rec[i][0]
                    Account = rec[i][3]
                    try:
                        text = t0 + "\n\n" + "اکانت: " + Account
                        bot.send_message(ID, text, parse_mode=enums.ParseMode.HTML)
                        count += 1
                    except:
                        pass
                bot.send_message(chat_id, f"Send the specific msg from {host} to {str(count)}/{str(len(rec))} users.")
                bot.delete_messages(chat_id, msg)
            else:
                message.reply_text("این سرور وجود نداره")

        elif "EDD_" in status:
            hosts, remarks = sshx.HOSTS()
            old_host = status.split("EDD_")[1]
            new_host = link
            keyboard = [[InlineKeyboardButton("<<", callback_data=f'TTRS_{host}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if old_host in hosts:
                if new_host not in hosts:
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(old_host)
                    if sshx.Login(username, password, new_host, port, panel) is False:
                        message.reply_text("❌اطلاعات درستو بفرستین", reply_markup=reply_markup)
                        sshx.Login(username, password, old_host, port, panel)
                    else:
                        sm = sshx.Update_host(old_host, new_host)
                        update_host_users(old_host, new_host)
                        message.reply_text(sm, reply_markup=reply_markup)
                else:
                    message.reply_text("سروری که فرستادی توی لیست وجود داره", reply_markup=reply_markup)
            else:
                message.reply_text("سرور پیدا نشد", reply_markup=reply_markup)
            delete_cache(chat_id)

        elif "XQEC_" in status:
            if (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                host = status.split("XQEC_")[1]
                username = link
                hosts, remarks = sshx.HOSTS()
                if host in hosts:
                    port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                    delete_cache(chat_id)
                    if panel == "shahan":
                        cache_list = [host, username, "80"]
                        add_cache(chat_id, "EDUSPA")
                        message.reply_text("پسورد بفرستین")
                    else:
                        cache_list = [host, username]
                        add_cache(chat_id, "EDPPort")
                        message.reply_text("⚪️ پورت پنلو بفرستین:")
                    add_collector(chat_id, "EUP", cache_list, [])
                else:
                    message.reply_text("سرور وجود نداره")
                    delete_cache(chat_id)
            else:
                message.reply_text("این نام کاربری مورد قبول نیست فقط میتونه ترکیبی از حروف انگلیسی و عدد باشه :(\nاگه اشتباهی تایپ کردین دوباره یوزرنیم بفرستین یا \n\n/cancel")

        elif status == "EDPPort":
            if link.isdigit() is True:
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("پسورد بفرستین")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "EDUSPA")
                update_collector(chat_id, cache_list, host_cahce)
            else:
                message.reply_text("فقط عدد بفرستین یا /cancel")

        elif status == "EDUSPA":
            cache_list, host_cahce = get_collector_cache(chat_id)
            host = cache_list[0]
            new_username = cache_list[1]
            new_port = cache_list[2]
            new_password = link
            keyboard = [[InlineKeyboardButton("<<", callback_data=f'TTRS_{host}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            hosts, remarks = sshx.HOSTS()
            if host in hosts:
                old_port, old_username, old_password, panel, route_path, sshport, udgpw = sshx.HOST_INFO(old_host)
                if sshx.Login(new_username, new_password, host, new_port, panel) is False:
                    message.reply_text("❌اطلاعات درستو بفرستین", reply_markup=reply_markup)
                    sshx.Login(old_username, old_password, host, old_port, panel)
                else:
                    sm = sshx.Update_user_pass_port(host, new_port, new_username, new_password)
                    message.reply_text(sm, reply_markup=reply_markup)
            else:
                message.reply_text("سرور پیدا نشد", reply_markup=reply_markup)
            delete_collector(chat_id)
            delete_cache(chat_id)

        elif "ELIP_" in status:
            link = fixed_link_json(link)
            if (sshx.ASCII_Check(link) is True):
                new_host = link
                old_host = status.split(":")[1]
                panel = status.split("_")[1].split(":")[0]
                hosts, remarks = sshx.HOSTS()
                if old_host in hosts:
                    delete_cache(chat_id)
                    if panel == "shahan":
                        cache_list = [old_host, panel, new_host, "80", "path", "sshport", "udgpw"]
                        add_cache(chat_id, "AllEditremark")
                        message.reply_text("یه نام برای سرور بفرستین مثل (آمریکا-1 🇺🇸🦅)")
                    else:
                        cache_list = [old_host, panel, new_host]
                        add_cache(chat_id, "AllEditport")
                        message.reply_text("پورت پنل ؟")
                    add_collector(chat_id, "Editserver", cache_list, [])
                else:
                    keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply_text(f"سروری با آدرس {old_host} پیدا نشد ", reply_markup=reply_markup)
                    delete_cache(chat_id)
            else:
                message.reply_text("لطفا آدرس درست بفرستین یا /cancel")

        elif status == "AllEditport":
            if link.isdigit() is True:
                cache_list, host_cahce = get_collector_cache(chat_id)
                cache_list.append(link)
                cache_list.append("path")
                delete_cache(chat_id)
                if cache_list[1] == "rocket":
                    message.reply_text("یه نام برای سرور بفرستین مثل (آمریکا-1 🇺🇸🦅)")
                    cache_list.append("sshport")
                    cache_list.append("udgpw")
                    add_cache(chat_id, "AllEditremark")
                elif cache_list[1] == "xpanel":
                    message.reply_text("پورت ssh سرور رو بفرستین (فقط برای فرستادن اطلاعات اکانت به کاربر استفاده میشه)")
                    add_cache(chat_id, "AllEditsshport")
                update_collector(chat_id, cache_list, host_cahce)
            else:
                message.reply_text("فقط عدد بفرستین یا /cancel")

        elif status == "AllEditsshport":
            if link.isdigit() is True:
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("پورت udgpw رو بفرستین (اصولا 7300 یا 7301 بصورت پیش فرض هر سرور حتما فعال کنین)")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "AllEditudgpw")
                update_collector(chat_id, cache_list, host_cahce)
            else:
                message.reply_text("فقط عدد بفرستین یا /cancel")

        elif status == "AllEditudgpw":
            if link.isdigit() is True:
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("یه نام برای سرور بفرستین مثل (آمریکا-1 🇺🇸🦅)")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "AllEditremark")
                update_collector(chat_id, cache_list, host_cahce)
            else:
                message.reply_text("فقط عدد بفرستین یا /cancel")

        elif status == "AllEditremark":
            link = fixed_link_json(link)
            if (sshx.TXT_FILTER(link) is True):
                if len(link) <= 16:
                    cache_list, host_cahce = get_collector_cache(chat_id)
                    message.reply_text("نام کاربری پنل؟")
                    cache_list.append(link)
                    delete_cache(chat_id)
                    add_cache(chat_id, "AllEdituser")
                    update_collector(chat_id, cache_list, host_cahce)
                else:
                    message.reply_text("لطفا حداکثر 16 کاراکتر باشه تا قابل نمایش باشه :\n\n/cancel")
            else:
                message.reply_text("این کاراکتر ها مورد قبول نیست ی چیز دیگه رو بفرستین\n\n/cancel")

        elif status == "AllEdituser":
            link = fixed_link_json(link)
            if (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("پسورد ؟")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "AllEditpass")
                update_collector(chat_id, cache_list, host_cahce)
            else:
                message.reply_text("این نام کاربری مورد قبول نیست فقط میتونه ترکیبی از حروف انگلیسی و عدد باشه :(\nاگه اشتباهی تایپ کردین دوباره یوزرنیم بفرستین یا \n\n/cancel")

        elif status == "AllEditpass":
            if sshx.OTX_Check(link) is True:
                cache_list, host_cahce = get_collector_cache(chat_id)
                old_host = cache_list[0]
                panel = cache_list[1]
                host = cache_list[2]
                port = cache_list[3]
                route_path = cache_list[4]
                sshport = cache_list[5]
                udgpw = cache_list[6]
                remark = cache_list[7]
                username = cache_list[8]
                password = link
                keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                hosts, remarks = sshx.HOSTS()
                if old_host in hosts:
                    try:
                        if sshx.Login(username, password, host, port, panel) is False:
                            message.reply_text("❌اطلاعات درستو بفرستین", reply_markup=reply_markup)
                        else:
                            sshx.Update_Host_All_info(old_host, host, port, username, password, panel, route_path, sshport, udgpw, remark)
                            message.reply_text("✅ سرور چنج شد", reply_markup=reply_markup)
                            update_host_users(old_host, host)
                    except Exception as e:
                        message.reply_text("Error: " + str(e), reply_markup=reply_markup)
                else:
                    message.reply_text(f"سروری با آدرس {old_host} پیدا نشد ", reply_markup=reply_markup)
                delete_collector(chat_id)
                delete_cache(chat_id)
            else:
                message.reply_text("این پسورد مورد قبول نیست فقط میتونه ترکیبی از حروف انگلیسی و عدد و آندرلاین یا دش باشه :(\nاگه اشتباهی تایپ کردین دوباره یوزرنیم بفرستین یا \n\n/cancel")

        elif "EUDPport_" in status:
            if link.isdigit() is True:
                host = status.split("_")[1]
                keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                hosts, remarks = sshx.HOSTS()
                if host in hosts:
                    sm = sshx.Change_udp_port('xpanel', host, link)
                    message.reply_text(sm, reply_markup=reply_markup)
                else:
                    message.reply_text(f"سروری با این آدرس وجود نداره:\n\n{host}", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("فقط عدد بفرستین یا /cancel")

        elif "ESSHport_" in status:
            if link.isdigit() is True:
                host = status.split("_")[1]
                keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                hosts, remarks = sshx.HOSTS()
                if host in hosts:
                    sm = sshx.Change_ssh_port('xpanel', host, link)
                    message.reply_text(sm, reply_markup=reply_markup)
                else:
                    message.reply_text(f"سروری با این آدرس وجود نداره:\n\n{host}", reply_markup=reply_markup)
                delete_cache(chat_id)
            else:
                message.reply_text("فقط عدد بفرستین یا /cancel")

        elif "EDITRemark_" in status:
            link = fixed_link_json(link)
            if (sshx.TXT_FILTER(link) is True):
                if len(link) <= 16:
                    host = status.split("_")[1]
                    keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    hosts, remarks = sshx.HOSTS()
                    if host in hosts:
                        sm = sshx.Change_remark(host, link)
                        message.reply_text(sm, reply_markup=reply_markup)
                    else:
                        message.reply_text(f"سروری با این آدرس وجود نداره:\n\n{host}", reply_markup=reply_markup)
                    delete_cache(chat_id)
                else:
                    message.reply_text("لطفا حداکثر 16 کاراکتر باشه تا قابل نمایش باشه :\n\n/cancel")
            else:
                message.reply_text("این کاراکتر ها مورد قبول نیست ی چیز دیگه رو بفرستین\n\n/cancel")

        elif "AST_" in status:
            link = fixed_link_json(link)
            if (sshx.ASCII_Check(link) is True):
                host = link
                hosts, remarks = sshx.HOSTS()
                if host not in hosts:
                    delete_cache(chat_id)
                    panel = status.split("AST_")[1]
                    if panel == "shahan":
                        cache_list = [panel, host, "80", "path", "sshport", "udgpw"]
                        add_cache(chat_id, "serverremark")
                        message.reply_text("یه نام برای سرور بفرستین مثل (آمریکا-1 🇺🇸🦅)")
                    else:
                        cache_list = [panel, host]
                        add_cache(chat_id, "serverport")
                        message.reply_text("پورت پنل ؟")
                    add_collector(chat_id, "addserver", cache_list, [])
                else:
                    message.reply_text("این سرور وجود داره یه سرور دیگه بفرست")
            else:
                message.reply_text("لطفا آدرس درست بفرستین یا /cancel")

        elif status == "serverport":
            if link.isdigit() is True:
                cache_list, host_cahce = get_collector_cache(chat_id)
                cache_list.append(link)
                cache_list.append("path")
                delete_cache(chat_id)
                if cache_list[0] == "rocket":
                    message.reply_text("یه نام برای سرور بفرستین مثل (آمریکا-1 🇺🇸🦅)")
                    cache_list.append("sshport")
                    cache_list.append("udgpw")
                    add_cache(chat_id, "serverremark")
                elif cache_list[0] == "xpanel":
                    message.reply_text("پورت ssh سرور رو بفرستین (فقط برای فرستادن اطلاعات اکانت به کاربر استفاده میشه)")
                    add_cache(chat_id, "serversshport")
                update_collector(chat_id, cache_list, host_cahce)
            else:
                message.reply_text("فقط عدد بفرستین یا /cancel")

        elif status == "serversshport":
            if link.isdigit() is True:
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("پورت udgpw رو بفرستین (اصولا 7300 یا 7301 بصورت پیش فرض هر سرور حتما فعال کنین)")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "serverudgpw")
                update_collector(chat_id, cache_list, host_cahce)
            else:
                message.reply_text("فقط عدد بفرستین یا /cancel")

        elif status == "serverudgpw":
            if link.isdigit() is True:
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("یه نام برای سرور بفرستین مثل (آمریکا-1 🇺🇸🦅)")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "serverremark")
                update_collector(chat_id, cache_list, host_cahce)
            else:
                message.reply_text("فقط عدد بفرستین یا /cancel")

        elif status == "serverremark":
            link = fixed_link_json(link)
            if (sshx.TXT_FILTER(link) is True):
                if len(link) <= 16:
                    cache_list, host_cahce = get_collector_cache(chat_id)
                    message.reply_text("نام کاربری پنل؟")
                    cache_list.append(link)
                    delete_cache(chat_id)
                    add_cache(chat_id, "serveruser")
                    update_collector(chat_id, cache_list, host_cahce)
                else:
                    message.reply_text("لطفا حداکثر 16 کاراکتر باشه تا قابل نمایش باشه :\n\n/cancel")
            else:
                message.reply_text("این کاراکتر ها مورد قبول نیست ی چیز دیگه رو بفرستین\n\n/cancel")

        elif status == "serveruser":
            link = fixed_link_json(link)
            if (sshx.ASCII_Check(link) is True) and (sshx.Contains(link) is True):
                cache_list, host_cahce = get_collector_cache(chat_id)
                message.reply_text("پسورد ؟")
                cache_list.append(link)
                delete_cache(chat_id)
                add_cache(chat_id, "serverpass")
                update_collector(chat_id, cache_list, host_cahce)
            else:
                message.reply_text("این نام کاربری مورد قبول نیست فقط میتونه ترکیبی از حروف انگلیسی و عدد باشه :(\nاگه اشتباهی تایپ کردین دوباره یوزرنیم بفرستین یا \n\n/cancel")

        elif status == "serverpass":
            if sshx.OTX_Check(link) is True:
                cache_list, host_cahce = get_collector_cache(chat_id)
                panel = cache_list[0]
                host = cache_list[1]
                port = cache_list[2]
                route_path = cache_list[3]
                sshport = cache_list[4]
                udgpw = cache_list[5]
                remark = cache_list[6]
                username = cache_list[7]
                password = link
                keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                hosts, remarks = sshx.HOSTS()
                if host not in hosts:
                    try:
                        if sshx.Login(username, password, host, port, panel) is False:
                            message.reply_text("❌اطلاعات درستو بفرستین", reply_markup=reply_markup)
                        else:
                            message.reply_text("✅ سرور اضافه شد", reply_markup=reply_markup)
                            sshx.Add_Host(host, port, username, password, panel, route_path, sshport, udgpw, remark)
                    except Exception as e:
                        message.reply_text("Error: " + str(e), reply_markup=reply_markup)
                else:
                    message.reply_text("این سرور وجود داره نمیتونی دوباره اد کنی", reply_markup=reply_markup)
                delete_collector(chat_id)
                delete_cache(chat_id)
            else:
                message.reply_text("این پسورد مورد قبول نیست فقط میتونه ترکیبی از حروف انگلیسی و عدد و آندرلاین یا دش باشه :(\nاگه اشتباهی تایپ کردین دوباره یوزرنیم بفرستین یا \n\n/cancel")


@app.on_callback_query(filters.regex('back'))
def call_back(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    text = '🔻<b>خب برگشتیم</b>'
    if chat_id in admin_id:
        text += "\n\n/backup"
        query.edit_message_text(text=text, reply_markup=Admin_Tools_keys(), parse_mode=enums.ParseMode.HTML)
    elif chat_id in seller_id:
        query.edit_message_text(text=text, reply_markup=Seller_Tools_keys(), parse_mode=enums.ParseMode.HTML)
    else:
        query.edit_message_text(text=text, reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('servers'))
def call_servers(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    query.edit_message_text(text="Select? ", reply_markup=server_cb_creator("HOST_"))


@app.on_callback_query(filters.regex('HSMSC_'))
def call_HSMSC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("HSMSC_")[1]
    chat_id = query.message.chat.id
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, "Connectionmsg_" + host)
        bot.send_message(chat_id, "پیامتون بفرستین")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSAR_'))
def call_HSAR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("HSAR_")[1]
    chat_id = query.message.chat.id
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, "AutoRemove_" + host)
        bot.send_message(chat_id, "خب تعداد روز به عدد بفرستین")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSUGift_'))
def call_HSUGift(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("HSUGift_")[1]
    chat_id = query.message.chat.id
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, "Gift_" + host)
        bot.send_message(chat_id, "خب تعداد روز به عدد بفرستین")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSUL_'))
def call_HSUL(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("HSUL_")[1]
    chat_id = query.message.chat.id
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        keyboard = [
            [InlineKeyboardButton("✔️ Active", callback_data=f"ULA_{host}")],
            [InlineKeyboardButton("✖️ Disable", callback_data=f"ULD_{host}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id, f"محدودیت, server: {host}\nselect:", reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ULA_'))
def call_ULA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("ULA_")[1]
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            text = Session.Limit_on()
            keyboard = [[InlineKeyboardButton("🔙Back", callback_data=f"HSUL_{host}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=text, reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ULD_'))
def call_ULD(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("ULD_")[1]
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            text = Session.Limit_off()
            keyboard = [[InlineKeyboardButton("🔙Back", callback_data=f"HSUL_{host}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=text, reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}")
    else:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSOU_'))
def call_HSOU(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("HSOU_")[1]
    chat_id = query.message.chat.id
    keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            response, users, ips = Session.Online_clients()
            if "Error:" not in response:
                text = f"🟢 {str(len(users))} کاربر آنلاین\n\n"
                if len(users) >= 1:
                    for i in range(len(users)):
                        text += f"{str(i + 1)}. {users[i]}  {ips[i]}\n"
                    if len(text) > 4095:
                        for x in range(0, len(text), 4095):
                            sleep(0.2)
                            bot.send_message(chat_id, text[x:x+4095])
                    else:
                        bot.send_message(chat_id, text)
                    keyboard = [[InlineKeyboardButton("💀Kill", callback_data=f"HSKU_{host}")], [InlineKeyboardButton("🔙Back", callback_data="servers")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.send_message(chat_id, "برای کیل یوزر دکمه پایینو کلیک کنین:", reply_markup=reply_markup)
                else:
                    bot.send_message(chat_id, "هیچکسی آنلاین نیست")
            else:
                query.edit_message_text(text=response, reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSKU_'))
def call_HSKU(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("HSKU_")[1]
    chat_id = query.message.chat.id
    keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            response, users, ips = Session.Online_clients()
            if "Error:" not in response:
                if len(users) >= 1:
                    query.edit_message_text(text="Choose a user to 💀Kill:", reply_markup=Reply_Kill(host, users))
                else:
                    query.edit_message_text(text="هیچکسی آنلاین نیست", reply_markup=reply_markup)
            else:
                query.edit_message_text(text=response, reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HKR_'))
def call_HKR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = (rt.split("HKR_")[1]).split("$")[0]
    user = rt.split("$")[1]
    chat_id = query.message.chat.id
    keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            response, users = Session.Kill(user)
            if "Error:" not in response:
                if len(users) >= 1:
                    query.edit_message_text(text=f"{response}\n{randomized_text()}Choose another user to 💀Kill:", reply_markup=Reply_Kill(host, users))
                else:
                    query.edit_message_text(text=f"{response}\n{randomized_text()}هیچکسی آنلاین نیست", reply_markup=reply_markup)
            else:
                query.edit_message_text(text=response, reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSDU_'))
def call_HSDU(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("HSDU_")[1]
    chat_id = query.message.chat.id
    keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, ips, descriptions, server_traffic, online_c, done = Session.info()
            if done is True:
                count_inactive_clients = 0
                text = ""
                for i in range(len(usernames)):
                    if status[i] != "فعال":
                        text += f"👤username: {usernames[i]}\nExpire: {expires[i]}\nTraffics: {traffics[i]}\n🔄Usage: {usages[i]} GB\n\n➖"
                        count_inactive_clients += 1
                t1 = f"\n\n🔴 {str(count_inactive_clients)} کاربر غیرفعال"
                text += t1
                if len(text) > 4095:
                    for x in range(0, len(text), 4095):
                        sleep(0.2)
                        bot.send_message(chat_id, text[x:x+4095])
                else:
                    bot.send_message(chat_id, text)
            else:
                query.edit_message_text(text="🔴 Unknown Error", reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HSCU_'))
def call_HSCU(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("HSCU_")[1]
    chat_id = query.message.chat.id
    keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, ips, descriptions, server_traffic, online_c, done = Session.info()
            if done is True:
                count_close_to_disable = 0
                text = ""
                for i in range(len(usernames)):
                    if status[i] == "فعال":
                        if (0 < int(days_left[i]) <= 3) or ((("نامحدود" != traffics[i]) and (usages[i] != "0.0")) and (float(usages[i]) >= (float(traffics[i].split("گیگابایت")[0])) - 2.0)):
                            text += f"👤username: {usernames[i]}\nExpire: {expires[i]}\nTraffics: {traffics[i]}\n🔄Usage: {usages[i]} GB\n\n➖"
                            count_close_to_disable += 1
                t1 = f"\n\n⚠️ {str(count_close_to_disable)} کاربر نزدیک اتمام"
                text += t1
                if len(text) > 4095:
                    for x in range(0, len(text), 4095):
                        sleep(0.2)
                        bot.send_message(chat_id, text[x:x+4095])
                else:
                    bot.send_message(chat_id, text)
            else:
                query.edit_message_text(text="🔴 Unknown Error", reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره, احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HOST_'))
def call_hosts(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    query.edit_message_text(text="Wait...")
    rt = query.data
    host = rt.split("HOST_")[1]
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            text = Session.Panel_Short_info()
            text += f"\n\nName: {remark}\nLogin info User: {username}\nPass: {password}"
            if "Premium: ✔️" in text:
                keyboard = [
                    [InlineKeyboardButton("✉️پیام اتصال", callback_data=f"HSMSC_{host}"), InlineKeyboardButton("🔒محدودیت کاربر", callback_data=f"HSUL_{host}")],
                    [InlineKeyboardButton("🎁هدیه روزانه", callback_data=f"HSUGift_{host}"), InlineKeyboardButton("🟢کاربران آنلاین", callback_data=f"HSOU_{host}")],
                    [InlineKeyboardButton("🔴کاربران غیرفعال", callback_data=f"HSDU_{host}"), InlineKeyboardButton("⚠️کاربران نزدیک اتمام", callback_data=f"HSCU_{host}")],
                    [InlineKeyboardButton("❌حذف کاربران منقضی براساس روز سپری شده", callback_data=f"HSAR_{host}")],
                    [InlineKeyboardButton("🔙Back", callback_data="servers")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text=text, reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("⚠️کاربران نزدیک اتمام", callback_data=f"HSCU_{host}")],
                    [InlineKeyboardButton("🔴کاربران غیرفعال", callback_data=f"HSDU_{host}"), InlineKeyboardButton("🟢کاربران آنلاین", callback_data=f"HSOU_{host}")]
                ]
                keyboard.append([InlineKeyboardButton("🔙Back", callback_data="servers")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text=text, reply_markup=reply_markup)
        except Exception as e:
            keyboard = [[InlineKeyboardButton("🔙Back", callback_data="servers")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=("Error: " + str(e)), reply_markup=reply_markup)
    else:
        query.answer("The host not found", show_alert=True)


@app.on_callback_query(filters.regex('checker'))
def call_checker(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [[InlineKeyboardButton("🔙Back", callback_data="back_admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if cache[0] is True:
        query.edit_message_text(text="Processing Please wait this operation takes so much time..", reply_markup=reply_markup)
        return
    settings = get_settings()
    maximum = settings['maximum']
    cache[0] = True
    msg = query.edit_message_text(text="درحال انجام...").id
    chat_id = query.message.chat.id
    start = int(time())
    count_servers, checked_servers, online_servers, offline_servers, full_servers, count_clients, count_active_clients, count_inactive_clients, close_to_disabled, count_online_clients, count_deleted_clients, servers_traffic, notify, allowed_connections, remain_clients = (0,)*15
    total_usage = 0.0
    logs = ""
    test_usernames = get_test_usernames()
    hosts, remarks = sshx.HOSTS()
    for host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        do = True
        count_servers += 1
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, ips, descriptions, server_traffic, online_c, done = Session.info()
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
            text = f"ℹ️ {str(count_servers)}. server info \n🔗url: {host}\nUsername: {username}\nPass: {password}\n🔵 Clients: {str(len(usernames))}\n\n"
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
                        if (int(days_left[i]) <= -(settings['auto_delete'])) or (usernames[i] in test_usernames):
                            SessionDIS = sshx.PANNEL(host, username, password, port, panel, 'User', usernames[i])
                            text = SessionDIS.Disable()
                            if "❌Deleted" in Session.Delete(usernames[i]):
                                text += f"❌Deleted user {usernames[i]} & Days: {str(days_left[i])} ❌\n\n"
                                count_deleted_clients += 1
                                if check_exist_user(host, usernames[i]) is True:
                                    ID, Name, Username = get_all_user_data(host, usernames[i])
                                    if usernames[i] in test_usernames:
                                        NTX = f"❌اکانت: {usernames[i]} تست به اتمام رسید"
                                    else:
                                        NTX = f"❌اکانت: {usernames[i]}به علت گذشت چند روز و نشدن تمدید حذف شد"
                                    delete_user(host, usernames[i])
                                    if checker_notify(str(ID)) is True:
                                        try:
                                            bot.send_message(ID, NTX)
                                        except:
                                            pass
                        else:
                            count_inactive_clients += 1
                    else:
                        count_active_clients += 1
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
                if "❌" in text:
                    bot.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
                checked_servers += 1
        except Exception as e:
            offline_servers += 1
            logs += f"\n⭕️ Connection Error: {host}, {str(e)}"
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
    text = f"🖥Servers: {str(count_servers)}\n☑️Checked: {str(checked_servers)}\n⚫️Full servers: {str(full_servers)}\n{logs}\n👤Clients: {str(count_clients)}\n✔️Active: {str(count_active_clients)}\n🔴Inactive: {str(count_inactive_clients)}\n🟢Online: {str(count_online_clients)}\n⚪️Remain: {str(remain_clients)}\n🔵Connections: {str(allowed_connections)}\n⚠️Alerts: {str(close_to_disabled)}\n❌Deleted: {str(count_deleted_clients)}\n🗳Notify: {str(notify)}\n\n🔁Server Usage: {total_usage_vps}\n🔄Clients Usage: {totat_usage_clients}\n\n⏳Time: {str(int(time() - start))}s\n\n{logs}"
    bot.send_message(chat_id, text, reply_markup=reply_markup)
    cache[0] = False
    bot.delete_messages(chat_id, msg)


@app.on_callback_query(filters.regex('stats'))
def call_stats(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    chat_id = query.message.chat.id
    if check_seller_exist(chat_id) is False:
        keyboard = [[InlineKeyboardButton("🔙Back", callback_data="back_admin"), InlineKeyboardButton("⚫️Full Servers", callback_data='full')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="درحال انجام... ممکنه طول بکشه")
        start = int(time())
        logs = ""
        sellers = get_all_sellers()
        sales = 0
        if sellers != []:
            for i in range(len(sellers)):
                accounts, hosts, status = get_all_accounts_by_chat_id(sellers[i][0])
                sales += len(accounts)
        count_servers, checked_servers, online_servers, offline_servers, full_servers, count_clients, count_active_clients, count_online_clients, count_inactive_clients, servers_traffic, clients_traffic, remain_clients = (0,)*12
        settings = get_settings()
        maximum = settings['maximum']
        hosts, remarks = sshx.HOSTS()
        for host in hosts:
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            count_servers += 1
            try:
                Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                info = Session.Short_info()
                traffic_data = info.split("Storage: ")[1].split('👤Clients')[0]
                if "GB" in traffic_data.split('Clients Traffic')[0]:
                    server_traffic = float(traffic_data.split("Server Traffic: ")[1].split(" GB")[0])
                else:
                    server_traffic = float(traffic_data.split("Traffic: ")[1].split(" TB")[0]) * 1024
                if "GB" in traffic_data.split('Clients Traffic')[1]:
                    client_traffic = float(traffic_data.split("Clients Traffic: ")[1].split(" GB")[0])
                else:
                    client_traffic = float(traffic_data.split("Clients Traffic: ")[1].split(" TB")[0]) * 1024
                clients_traffic += client_traffic
                servers_traffic += server_traffic
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
                logs += f"⭕️ Connection Error: {host} | {str(e)}"
            if (checked_servers % 5 == 0):
                query.edit_message_text(text=f"Collected data from {str(checked_servers)} servers...")
        if len(str(int(servers_traffic))) >= 3:
            total_usage_vps = f"{str('{:.2f}'.format(float(servers_traffic) / 1024))} TB"
        else:
            total_usage_vps = f"{str('{:.2f}'.format(float(servers_traffic)))} GB"
        if len(str(int(clients_traffic))) >= 3:
            total_clients_traffic = f"{str('{:.2f}'.format(float(clients_traffic) / 1024))} TB"
        else:
            total_clients_traffic = f"{str('{:.2f}'.format(float(clients_traffic)))} GB"
        text = f"📊Stats\n\n🖥Servers: {str(count_servers)}\n☑️Checked: {str(checked_servers)}\n⚫️Full: {str(full_servers)}\n{logs}\n👤 Clients: {str(count_clients)}\n✔️Active: {str(count_active_clients)}\n🔴Inactive: {str(count_inactive_clients)}\n🟢Online: {str(count_online_clients)}\n⚪️Remain: {str(remain_clients)}\n🔁Servers Traffic: {total_usage_vps}\n🔄Clients Traffic: {total_clients_traffic}\n\n👥Bot users: {str(countuser_m())}\n🧪All Test: {str(get_count_test_users())}\n💲Sellers: {str(len(sellers))}\n🏷Sales: {str(sales)}\n\n⏳Time: {str(int(time() - start))}s"
        query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("<<", callback_data='back_seller')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
        ID, Name, Username, Limit = get_seller_info(chat_id)
        name, u, phone, old_value = get_full_user_data_id(chat_id)
        text = "🏷تعداد فروش: " + str(len(accounts)) + "\n🔻محدودیت: " + str(Limit) + "\n💰موجودی:  " + str(old_value) + " تومن"
        query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex('Filtering'))
def call_filtering(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [[InlineKeyboardButton("<< back", callback_data="back_admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="درحال انجام...")
    start = int(time())
    FS = ""
    logs = ""
    count_servers, checked_servers, blocked_servers, online_servers = (0,)*4
    hosts, remarks = sshx.HOSTS()
    for host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        count_servers += 1
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            status, server_msg = Session.IP_Check()
            if status is True:
                if check_host_api(host) is True:
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
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [[InlineKeyboardButton("<< back", callback_data="SMT")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="درحال انجام...")
    start = int(time())
    FS = ""
    logs = ""
    count_servers, checked_servers, full_servers, remain_clients, count_clients = (0,)*5
    settings = get_settings()
    maximum = settings['maximum']
    hosts, remarks = sshx.HOSTS()
    for host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        count_servers += 1
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
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
    chat_id = query.message.chat.id
    Buttons = [[KeyboardButton("ارسال شماره تلفن 📞", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(Buttons, resize_keyboard=True)
    text = "لطفا برای استفاده از ربات دکمه پایین کلیک کنین و شمارتون بفرستین👇"
    if (get_settings())['sponser'] == "None":
        if ((get_settings())['phone'] == "on") and (check_user_phone_exist(chat_id) is False):
            bot.send_message(chat_id, text, reply_markup=reply_markup)
        else:
            query.edit_message_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)
    else:
        try:
            chat_member = bot.get_chat_member((get_settings())['sponser'], query.message.chat.id)
            if ((get_settings())['phone'] == "on") and (check_user_phone_exist(chat_id) is False):
                bot.send_message(chat_id, text, reply_markup=reply_markup)
            else:
                query.edit_message_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)

        except NotAcceptable:
            if ((get_settings())['phone'] == "on") and (check_user_phone_exist(chat_id) is False):
                bot.send_message(chat_id, text, reply_markup=reply_markup)
            else:
                query.edit_message_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)

        except BadRequest as e:
            if "USER_NOT_PARTICIPANT" in str(e):
                query.answer("جوین نشدی😑", show_alert=True)
            else:
                if ((get_settings())['phone'] == "on") and (check_user_phone_exist(chat_id) is False):
                    bot.send_message(chat_id, text, reply_markup=reply_markup)
                else:
                    query.edit_message_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('AKill'))
def call_AKill(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_seller_exist(chat_id) is False:
        query.edit_message_text(text="سرور مورد نظر برای کیل یوزر انتخاب کنین", reply_markup=server_cb_creator("KUA_"))
    else:
        add_cache(chat_id, "K-host")
        query.edit_message_text(text="آدرس سرورو بفرست")


@app.on_callback_query(filters.regex('KUA_'))
def call_KUA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("KUA_")[1]
    if check_cache(chat_id) is False:
        add_cache(chat_id, "Kill_" + host)
        query.edit_message_text(text='نام کاربری رو بفرستین')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('disable'))
def call_disable(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_seller_exist(chat_id) is False:
        query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("DIS_"))
    else:
        accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
        if status is False:
            query.answer("سرویسی پیدا نشد!", show_alert=True)
        else:
            query.edit_message_text(text="یکی از اکانت هارو انتخاب کن:", reply_markup=Reply_action_sellers(hosts, accounts, "DIXS_"))


@app.on_callback_query(filters.regex('DIXS_'))
def call_DIXS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("DIXS_")[1].split("$")[0]
    user = rt.split("$")[1]
    keyboard = [[InlineKeyboardButton("<<", callback_data='back_seller')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if check_exist_user(host, user) is True:
        query.edit_message_text(text="wait...")
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            query.edit_message_text(text=Session.Disable(), reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}", reply_markup=reply_markup)
    else:
        query.answer("نام کاربری پیدا نشد", show_alert=True)


@app.on_callback_query(filters.regex('DIS_'))
def call_DIS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("DIS_")[1]
    if check_cache(chat_id) is False:
        add_cache(chat_id, "disable_" + host)
        query.edit_message_text(text='نام کاربری رو بفرستین')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('ENA_'))
def call_ENA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("ENA_")[1]
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        add_cache(chat_id, "enable_" + host)
        query.edit_message_text(text='نام کاربری رو بفرستین')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('enable'))
def call_enable(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_seller_exist(chat_id) is False:
        query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("ENA_"))
    else:
        accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
        if status is False:
            query.answer("سرویسی پیدا نشد!", show_alert=True)
        else:
            query.edit_message_text(text="یکی از اکانت هارو انتخاب کن:", reply_markup=Reply_action_sellers(hosts, accounts, "EIXS_"))


@app.on_callback_query(filters.regex('EIXS_'))
def call_EIXS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("EIXS_")[1].split("$")[0]
    user = rt.split("$")[1]
    keyboard = [[InlineKeyboardButton("<<", callback_data='back_seller')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if check_exist_user(host, user) is True:
        query.edit_message_text(text="wait...")
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            query.edit_message_text(text=Session.Enable(), reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}", reply_markup=reply_markup)
    else:
        query.answer("نام کاربری پیدا نشد", show_alert=True)


@app.on_callback_query(filters.regex('CAPASS_'))
def call_CAPASS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        domain = data.split("CAPASS_")[1]
        cache_list = []
        cache_list.append(domain)
        add_collector(chat_id, "password", cache_list, [])
        add_cache(chat_id, "password")
        query.edit_message_text(text="نام کاربری؟")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('ADPASS'))
def call_ADPASS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("CAPASS_"))
        else:
            add_cache(query.message.chat.id, "updatepassword")
            query.edit_message_text(text="آدرس سرور بفرستین")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('CAUSER_'))
def call_CAUSER(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        domain = data.split("CAUSER_")[1]
        cache_list = []
        cache_list.append(domain)
        add_collector(chat_id, "username", cache_list, [])
        add_cache(chat_id, "username")
        query.edit_message_text(text="نام کاربری؟")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('ADUSER'))
def call_ADUSER(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("CAUSER_"))
        else:
            add_cache(query.message.chat.id, "updateusername")
            query.edit_message_text(text="آدرس سرور بفرستین")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('RTRF_'))
def call_RTRF(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        data = query.data
        domain = data.split("RTRF_")[1]
        add_cache(chat_id, "Reset_" + domain)
        query.edit_message_text(text="نام کاربری؟")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('TrfRes'))
def call_TrfRes(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(query.message.chat.id) is False:
        query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("RTRF_"))
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('CTRPLUS_'))
def call_CTRPLUS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        data = query.data
        domain = data.split("CTRPLUS_")[1]
        cache_list = []
        cache_list.append(domain)
        add_collector(chat_id, "plus", cache_list, [])
        add_cache(chat_id, "plus")
        query.edit_message_text(text="نام کاربری؟")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('TrfPlus'))
def call_TrfPlus(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("CTRPLUS_"))
        else:
            settings = get_settings()
            if settings['seller_custom'] == "off":
                accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
                keyboard = []
                if status is False:
                    query.answer("سرویسی پیدا نشد!", show_alert=True)
                else:
                    if len(accounts) >= 2:
                        if len(accounts) % 2 == 0:
                            for i in range(0, len(accounts) - 1, 2):
                                keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("UTGB_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("UTGB_" + hosts[i + 1] + "$" + accounts[i + 1]))])
                        else:
                            for i in range(0, len(accounts) - 1, 2):
                                keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("UTGB_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("UTGB_" + hosts[i + 1] + "$" + accounts[i + 1]))])
                            keyboard.append([InlineKeyboardButton(accounts[-1], callback_data=("UTGB_" + hosts[-1] + "$" + accounts[-1]))])
                    else:
                        keyboard.append([InlineKeyboardButton(accounts[0], callback_data=("UTGB_" + hosts[0] + "$" + accounts[0]))])
                    keyboard.append([InlineKeyboardButton("<<", callback_data='back')])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    query.edit_message_text(text="یکی برای تمدید انتخاب کن", reply_markup=reply_markup)
            else:
                add_cache(query.message.chat.id, "updatetraffic")
                query.edit_message_text(text="آدرس سرور بفرستین")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('DM_'))
def call_DM(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
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
            query.edit_message_text(text="یه نام کاربری بفرستین")
        else:
            query.answer(f"⚠️این سرور به {str(maximum)} کاربر رسیده. یه سرور دیگه انتخاب کنین یا تو تنظیمات تغییر بدید", show_alert=True)
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('create'))
def call_create(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(query.message.chat.id) is False:
        query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("DM_"))
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('DMNONE_'))
def call_DMNONE(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
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
            query.edit_message_text(text="یه نام کاربری بفرستین")
        else:
            if chat_id in seller_id:
                query.answer("ظرفیت این سرور پر شده یه سرور دیگه رو انتخاب کن", show_alert=True)
            else:
                query.answer(f"⚠️این سرور به {str(maximum)} کاربر رسیده. یه سرور دیگه انتخاب کنین یا تو تنظیمات تغییر بدید", show_alert=True)
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('Create_none'))
def call_create(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("DMNONE_"))
        else:
            ID, Name, Username, Limit = get_seller_info(chat_id)
            accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
            if (Limit == 0) or (Limit >= len(accounts)):
                settings = get_settings()
                if settings['seller_custom'] == "off":
                    keyboard = [[InlineKeyboardButton("🌎Direct", callback_data='buy')]]
                else:
                    keyboard = [[InlineKeyboardButton("🌎Direct", callback_data="SCC_D")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text="انتخاب کنین:", reply_markup=reply_markup)
            else:
                query.answer(f"⚠️شما به محدودیت  {str(Limit)} ساخت اکانت رسیدین. ", show_alert=True)
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('SCC_'))
def call_SCC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in seller_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    chat_id = query.message.chat.id
    status = data.split("SCC_")[1]
    settings = get_settings()
    if settings['select_server_sellers'] == "on":
        query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("DMNONE_"))
    else:
        hosts, remarks = sshx.HOSTS()
        if hosts != []:
            cache_list = []
            cache_list.append("random")
            add_collector(chat_id, "domain_none", cache_list, [])
            delete_cache(chat_id)
            add_cache(chat_id, "name_none")
            query.edit_message_text(text="نام کاربریو بفرستین")
        else:
            query.answer("سرور ها همگی پر هستن❕ میتونین از تنظیمات تغییر بدین مقدارو", show_alert=True)


@app.on_callback_query(filters.regex('UP_'))
def call_up(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        data = query.data
        host = data.split("UP_")[1]
        add_cache(chat_id, "update_" + host)
        query.edit_message_text(text='نام کاربریو بفرستین')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('update'))
def call_update(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("UP_"))
        else:
            settings = get_settings()
            if settings['seller_custom'] == "off":
                accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
                keyboard = []
                if status is False:
                    query.answer("سرویسی پیدا نشد!", show_alert=True)
                else:
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
                add_cache(query.message.chat.id, "updatehost")
                query.edit_message_text(text="آدرس سرور بفرستین")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('RM_'))
def call_RM(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        data = query.data
        host = data.split("RM_")[1]
        add_cache(chat_id, "remove_" + host)
        query.edit_message_text(text='نام کاربریو بفرستین')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('remove'))
def call_remove(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        if check_seller_exist(chat_id) is False:
            query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("RM_"))
        else:
            accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
            if status is False:
                query.answer("سرویسی پیدا نشد!", show_alert=True)
            else:
                query.edit_message_text(text="یکی از اکانت هارو انتخاب کن:", reply_markup=Reply_action_sellers(hosts, accounts, "RIXS_"))
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('RIXS_'))
def call_RIXS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("RIXS_")[1].split("$")[0]
    user = rt.split("$")[1]
    keyboard = [[InlineKeyboardButton("<<", callback_data='back_seller')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if check_exist_user(host, user) is True:
        query.edit_message_text(text="wait...")
        try:
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            text = Session.Disable()
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            text = Session.Delete(user)
            if check_exist_user(host, user) is True:
                delete_user(host, user)
                text += "\n\nand Deleted from DB"
        except Exception as e:
            text = "Error: " + str(e)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        query.answer("نام کاربری پیدا نشد", show_alert=True)


@app.on_callback_query(filters.regex('UI_'))
def call_UI(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        data = query.data
        host = data.split("UI_")[1]
        add_cache(chat_id, "userinfo_" + host)
        query.edit_message_text(text='نام کاربریو بفرستین')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('userinfo'))
def call_userinfo(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in (admin_id + seller_id):
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(query.message.chat.id) is False:
        if check_seller_exist(query.message.chat.id) is False:
            query.edit_message_text(text="سرور مورد نظر انتخاب کنین:", reply_markup=server_cb_creator("UI_"))
        else:
            add_cache(query.message.chat.id, "infohost")
            query.edit_message_text(text="آدرس سرور بفرستین")
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('userconfigs'))
def call_userconfigs(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "userconfigs")
    keyboard = [[InlineKeyboardButton("<< Back", callback_data='back_admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text='خب یه پیام از کاربر فوروارد کنین. (اگه کاربر هیدن باشه کار نمیکنه) or User ID', reply_markup=reply_markup)


@app.on_callback_query(filters.regex('MIOU_'))
def call_MIOU(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    delete_collector(chat_id)
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    keyboard = [[InlineKeyboardButton("<< Back", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if check_exist_user(host, user) is True:
        try:
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            text = Session.User_info(get_settings()['dropbear'])
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except:
            query.answer("⚠️Error: بعدا تلا کنین یا به پشتیبانی پیام بدین", show_alert=True)
    else:
        query.edit_message_text(text="چیزی پیدا نشد!", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('IDADMIN_'))
def call_IDADMIN(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    delete_collector(chat_id)
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    try:
        cb = data.split("_")[1]
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
        text = Session.User_info(get_settings()['dropbear'])
        keyboard = [
            [InlineKeyboardButton("🔄تمدید کاربر", callback_data=('IDMNU&Update_' + cb)), InlineKeyboardButton("🗑حذف کاربر", callback_data=('IDMNU&Remove_' + cb))],
            [InlineKeyboardButton("🟢 فعال کاربر", callback_data=('IDMNU&Active_' + cb)), InlineKeyboardButton("🔴 غیر فعال کاربر", callback_data=('IDMNU&Disable_' + cb))],
            [InlineKeyboardButton("🆕ریست ترافیک", callback_data=('IDMNU&Reset_' + cb)), InlineKeyboardButton("➕افزایش ترافیک", callback_data=('IDMNU&Traffic_' + cb))],
            [InlineKeyboardButton("💀Kill User", callback_data=('IDMNU&Kill_' + cb)), InlineKeyboardButton("🔑تغییر پسورد", callback_data=('IDMNU&PASSWORD_' + cb))],
            [InlineKeyboardButton("<<", callback_data='back_admin')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    except:
        keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="⚠️Error: Maybe user not found or connection Lost", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('IDMNU&'))
def call_IDMNU(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    cb = data.split("_")[1]
    try:
        chat_id = query.message.chat.id
        status = (data.split("&")[1]).split("_")[0]
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        if (status != "Update") and (status != "Remove") and (status != "PASSWORD") and (status != "Traffic") and (status != "Kill") and (status != "USERNAME"):
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
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
            text = "حجمو به عدد بفرستین مثلا 10 گیگ (0 = نامحدود)"
            update_collector(chat_id, cache_list, [])

        elif status == "Kill":
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            text, users = Session.Kill(user)

        elif status == "Remove":
            SessionDIS = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            text = SessionDIS.Disable()
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            text = Session.Delete(user)
            if check_exist_user(host, user) is True:
                delete_user(host, user)

        elif status == "USERNAME":
            add_collector(chat_id, "username", [], [])
            cache_list = [host, user]
            delete_cache(chat_id)
            add_cache(chat_id, "CUsername")
            text = "نام کاربری جدیدو بفرست"
            update_collector(chat_id, cache_list, [])

        elif status == "PASSWORD":
            add_collector(chat_id, "password", [], [])
            cache_list = [host, user]
            delete_cache(chat_id)
            add_cache(chat_id, "CPassword")
            text = "پسورد جدیدو بفرست"
            update_collector(chat_id, cache_list, [])

        elif status == "Update":
            add_collector(chat_id, "update", [], [])
            cache_list = [host, user]
            delete_cache(chat_id)
            add_cache(chat_id, "GB-update")
            text = "حجمو به عدد بفرستین مثلا 10 گیگ (0 = نامحدود)"
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
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        add_cache(chat_id, "change_wallet")
        query.edit_message_text(text="آدرس ولت ترون بفرست")
    else:
        query.answer("Please /cancel it first", show_alert=True)


@app.on_callback_query(filters.regex('OFT'))
def call_OFT(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['trx_buy'] == 'on':
        settings['trx_buy'] = 'off'
        update_settings(settings)
        keyboard = [[InlineKeyboardButton("<<", callback_data='wallet')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Done✔️", reply_markup=reply_markup)
    else:
        query.answer("Already OFF", show_alert=True)


@app.on_callback_query(filters.regex('ONT'))
def call_ONT(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['trx_buy'] == 'off':
        settings['trx_buy'] = 'on'
        update_settings(settings)
        keyboard = [[InlineKeyboardButton("<<", callback_data='wallet')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Done✔️", reply_markup=reply_markup)
    else:
        query.answer("Already ON", show_alert=True)


@app.on_callback_query(filters.regex('wallet'))
def call_wallet(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("🔧Change", callback_data='ChangeWallet')],
        [InlineKeyboardButton("🔴 Off", callback_data='OFT'), InlineKeyboardButton("🟢 On", callback_data='ONT')],
        [InlineKeyboardButton("<< Back", callback_data='ZBSHP')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    name, username, wallet, crypto = get_wallet_info()
    settings = get_settings()
    if settings['trx_buy'] == "off":
        status = "🔴 OFF"
    else:
        status = "🟢 ON"
    text = f"💳Wallet: <pre>{str(wallet)}</pre>\n\n👤آخرین ادمینی که اطلاعات ادیت کرد \nName: {name}\nusername: @{username}\nStatus: {status}\n\nمیتونین با خاموش روشن کردن این بخش فروش با این روش پرداخت فعال و غیرفعال کنین"
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('OFC'))
def call_OFC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['card_buy'] == 'on':
        settings['card_buy'] = 'off'
        update_settings(settings)
        keyboard = [[InlineKeyboardButton("<<", callback_data='Card')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Done✔️", reply_markup=reply_markup)
    else:
        query.answer("Already OFF", show_alert=True)


@app.on_callback_query(filters.regex('ONC'))
def call_ONC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['card_buy'] == 'off':
        settings['card_buy'] = 'on'
        update_settings(settings)
        keyboard = [[InlineKeyboardButton("<<", callback_data='Card')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Done✔️", reply_markup=reply_markup)
    else:
        query.answer("Already ON", show_alert=True)


@app.on_callback_query(filters.regex('Card'))
def call_card(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("🔧Change", callback_data='Change')],
        [InlineKeyboardButton("🔴 Off", callback_data='OFC'), InlineKeyboardButton("🟢 On", callback_data='ONC')],
        [InlineKeyboardButton("<< Back", callback_data='ZBSHP')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    name, username, card = get_card_info()
    settings = get_settings()
    if settings['card_buy'] == "off":
        status = "🔴 OFF"
    else:
        status = "🟢 ON"
    text = f"💳Card: <pre>{str(card)}</pre>\n\n👤Last admin changed the info \nName: {name}\nusername: @{username}\nStatus: {status}\n\nمیتونین با خاموش روشن کردن این بخش فروش با این روش پرداخت فعال و غیرفعال کنین"
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Change'))
def call_change(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        add_cache(chat_id, "change")
        query.edit_message_text(text="خب شماره کارتتون بفرستین (فقط شماره کارت)")
    else:
        query.answer("Please /cancel it first", show_alert=True)


@app.on_callback_query(filters.regex('ANS_'))
def call_ANS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        data = query.data
        cache_list = [data.split("ANS_")[1]]
        add_collector(chat_id, "answer", cache_list, [])
        add_cache(chat_id, "answer")
        bot.send_message(chat_id, "پیامتون بفرستین  یا ")
    else:
        bot.send_message(chat_id, "Please /cancel it first")


@app.on_callback_query(filters.regex("RLS_"))
def call_RLS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    chat_id = int(data.split("RLS_")[1])
    keyboard = [[InlineKeyboardButton("<<", callback_data='sellers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update_user_wallet(chat_id, 0)
    delete_seller(chat_id)
    sellers_id_add_list()
    query.edit_message_text(text="Removed✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex("ELS_"))
def call_ELS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    chat_id = int(data.split("ELS_")[1])
    text = "Ok send only a number\n\n0 = unlimited\n10 = 10 clients"
    keyboard = [[InlineKeyboardButton("<<", callback_data=('SLM_' + str(chat_id)))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup)
    delete_cache(query.message.chat.id)
    add_cache(query.message.chat.id, ("Edit_limit#" + str(chat_id)))


@app.on_callback_query(filters.regex("BLS_"))
def call_BLS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    user_id = int(data.split("BLS_")[1])
    name, u, phone, value = get_full_user_data_id(user_id)
    keyboard = [
        [InlineKeyboardButton("➖کاهش", callback_data=f'MAUB_{str(user_id)}'), InlineKeyboardButton("➕افزایش", callback_data=f'PAUB_{str(user_id)}')],
        [InlineKeyboardButton("0️⃣صفر کردن موجودی", callback_data=f'ZAUB_{str(user_id)}')],
        [InlineKeyboardButton("<<", callback_data='back_admin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"موجودی: {str(value)} تومن.\n\nName: {name}\nUsername: {u}\nPhone: {phone}", reply_markup=reply_markup)


@app.on_callback_query(filters.regex("ALS_"))
def call_ALS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    user_id = int(data.split("ALS_")[1])
    keyboard = []
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
        query.edit_message_text(text=f"Founded by id \n\nChoose: ", reply_markup=reply_markup)
    else:
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='back_admin')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="پیدا نشد❌", reply_markup=reply_markup)


@app.on_callback_query(filters.regex("SLM_"))
def call_SLM(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(query.message.chat.id)
    data = query.data
    chat_id = int(data.split("SLM_")[1])
    accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
    ID, Name, Username, Limit = get_seller_info(chat_id)
    try:
        if check_user_exists_in_clients_table(chat_id) is False:
            add_client_db(chat_id, Name, Username, 'None', 0)
        name, u, phone, old_value = get_full_user_data_id(chat_id)
        Balance = str(old_value) + " Toman"
    except:
        Balance = "Error: remove and add seller again"
    text = f"ID: {str(chat_id)}\nName: {Name}\nUsername: @{Username}\n\n🏷sales: {str(len(accounts))}\n🔻Limit: {Limit}\n💰Balance: {Balance}\n\nبا حذف فروشنده اکانت های فروشنده حذف نمیشن"
    keyboard = [
        [InlineKeyboardButton("🗑حذف ", callback_data=('RLS_' + str(chat_id))), InlineKeyboardButton("✏️تغییر محدودیت", callback_data=("ELS_" + str(chat_id)))],
        [InlineKeyboardButton("💰 مدیریت موجودی", callback_data=("BLS_" + str(chat_id)))],
        [InlineKeyboardButton("👤اکانت های فروشنده", callback_data=("ALS_" + str(chat_id)))],
        [InlineKeyboardButton("<<", callback_data='sellers')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex("ADDSELLER"))
def call_ADDSELLER(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(query.message.chat.id)
    add_cache(query.message.chat.id, "add_seller")
    keyboard = [[InlineKeyboardButton("<<", callback_data='sellers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="یه پیام از فروشنده فوروارد کنین اگه پروفایل هیدن باشه کار نمیکنه.", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('sellers'))
def call_sellers(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
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
    keyboard.append([InlineKeyboardButton("➕ افزودن فروشنده", callback_data='ADDSELLER')])
    keyboard.append([InlineKeyboardButton("<<", callback_data='back_admin')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="🔻Select: ", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('price'))
def call_price(bot, query):
    settings = get_settings()
    if settings['list_status'] == "off":
        query.answer("🔴 چیزی وجود نداره. ", show_alert=True)
        return
    keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
    if settings['buy'] == 'on':
        keyboard[0].insert(1, InlineKeyboardButton("🛒 خرید", callback_data='buy'))
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = settings['list']
    query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex('CUWPD_'))
def call_CUWPD(bot, query):
    if get_settings()['card_buy'] == "off":
        query.answer("این روش پرداخت توسط ادمین غیرفعال شده", show_alert=True)
        return
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    if check_cache(chat_id) is False:
        data = query.data
        price = data.split("CUWPD_")[1]
        name, username, card = get_card_info()
        add_cache(chat_id, "userdeposit")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='UWM_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [price]
        add_code_buy(chat_id, Code, "userdeposit", cache_list)
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


@app.on_callback_query(filters.regex('TUWPD_'))
def call_TUWPD(bot, query):
    if get_settings()['trx_buy'] == "off":
        query.answer("این روش پرداخت توسط ادمین غیرفعال شده", show_alert=True)
        return
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    if check_cache(chat_id) is False:
        data = query.data
        price = data.split("TUWPD_")[1]
        name, username, wallet, crypto = get_wallet_info()
        add_cache(chat_id, "userdeposit")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='UWM_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [price]
        add_code_buy(chat_id, Code, "userdeposit", cache_list)
        price = trx_price(price)
        text = f"""
مبلغ:
{price}

به آدرس ترون :
<pre>{wallet}</pre>
واریز کنین و سپس رسید عکس خودرا بفرستید
یکبار روی آدرس بزنین کپی میشه


برای کنسل کردن دکمه  بک بزنید
قیمت دلار: {str(Toman_USD())}
            """
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)


@app.on_callback_query(filters.regex('traffic'))
def call_traffic(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    data = query.data
    if "_" in data:
        code = data.split('traffic_')[1]
        delete_code_buy(code)
    accounts, hosts, status = get_all_accounts_by_chat_id(chat_id)
    keyboard = []
    settings = get_settings()
    if status is False:
        query.answer("سرویسی پیدا نشد. اگه سرویسی دارین دکمه اطلاعات سرویس بزنین و بفرستین 🙂", show_alert=True)
    else:
        if settings['buy-traffic'] == 'on':
            if len(accounts) >= 2:
                if len(accounts) % 2 == 0:
                    for i in range(0, len(accounts) - 1, 2):
                        keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("UTGB_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("UTGB_" + hosts[i + 1] + "$" + accounts[i + 1]))])
                else:
                    for i in range(0, len(accounts) - 1, 2):
                        keyboard.append([InlineKeyboardButton(accounts[i], callback_data=("UTGB_" + hosts[i] + "$" + accounts[i])), InlineKeyboardButton(accounts[i + 1], callback_data=("UTGB_" + hosts[i + 1] + "$" + accounts[i + 1]))])
                    keyboard.append([InlineKeyboardButton(accounts[-1], callback_data=("UTGB_" + hosts[-1] + "$" + accounts[-1]))])
            else:
                keyboard.append([InlineKeyboardButton(accounts[0], callback_data=("UTGB_" + hosts[0] + "$" + accounts[0]))])
            keyboard.append([InlineKeyboardButton("<<", callback_data='back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text="یکی برای تمدید انتخاب کن", reply_markup=reply_markup)
        else:
            keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text="فروش ترافیک غیرفعاله", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('UTGB_'))
def call_UTGB(bot, query):
    chat_id = query.message.chat.id
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    if check_exist_user(host, user) is True:
        settings = get_settings()
        keyboard = []
        query.edit_message_text(text="wait...")
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
        text = "اطلاعات سرویس :\n\n" + Session.User_info(settings['dropbear'])
        if "Error" in text:
            text = "مشکلی پیش اومده بعدا تلاش کنین یا به پشتیبانی اطلاع بدین"
        else:
            if "نامحدود" in text:
                text += "\n\nاکانت شما ترافیکش نامحدوده نمیتونید ترافیک اضافه بخرید"
            else:
                text += "\n\nبرای افزایش ترافیک یکی از گزینه هارو انتخاب کنین🙂"
                if chat_id in seller_id:
                    for i in range(len(settings['seller_plus_traffic'])):
                        tcb = f"{str(settings['seller_plus_traffic'][i])} گیگابایت - {str(settings['seller_plus_prices'][i])} تومن"
                        cb = f"LTPB_{str(settings['seller_plus_traffic'][i])}-{str(settings['seller_plus_prices'][i])}:{user}@{host}"
                        keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
                else:
                    for i in range(len(settings['plus-traffic'])):
                        tcb = f"{str(settings['plus-traffic'][i])} گیگابایت - {str(settings['plus-prices'][i])} تومن"
                        cb = f"TBP_{str(settings['plus-traffic'][i])}-{str(settings['plus-prices'][i])}:{user}@{host}"
                        keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("سرویسی پیدا نشد☹️", show_alert=True)


@app.on_callback_query(filters.regex('TBP_'))
def call_TBP(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("TBP_")[1]
        cb_cc = "CTPB_" + data
        cb_tr = "TTPB_" + data
        cb_bl = "LTPB_" + data
        keyboard = [
            [InlineKeyboardButton("💳کارت به کارت", callback_data=cb_cc), InlineKeyboardButton("💲ترون", callback_data=cb_tr)],
            [InlineKeyboardButton("💰کیف پول", callback_data=cb_bl)],
        ]
        keyboard.append([InlineKeyboardButton("<<", callback_data='traffic')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(text="روش پرداختو انتخاب کن:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except:
            query.edit_message_text(text="📃روش پرداختو انتخاب کن:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)


@app.on_callback_query(filters.regex('CTPB_'))
def call_CTPB(bot, query):
    if get_settings()['card_buy'] == "off":
        query.answer("این روش پرداخت توسط ادمین غیرفعال شده", show_alert=True)
        return
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("CTPB_")[1]
        GB = data.split("-")[0]
        price = data.split("-")[1].split(":")[0]
        user = (data.split("@")[0]).split(":")[1]
        host = data.split("@")[1]
        name, username, card = get_card_info()
        add_cache(chat_id, "traffic")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='traffic_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [GB, price, user, host]
        add_code_buy(chat_id, Code, "traffic", cache_list)
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


@app.on_callback_query(filters.regex('LTPB_'))
def call_LTPB(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    if check_cache(chat_id) is False:
        name, u, p, old_value = get_full_user_data_id(chat_id)
        data = query.data
        data = data.split("LTPB_")[1]
        GB = int(data.split("-")[0])
        price = data.split("-")[1].split(":")[0]
        user = (data.split("@")[0]).split(":")[1]
        host = data.split("@")[1]
        if old_value - price < 0:
            query.answer("موجودی کافی نیست ☹️", show_alert=True)
            return
        keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            server_msg = Session.Update_Traffic(GB)
            text += server_msg
            if "Error" not in server_msg:
                value = old_value - price
                update_user_wallet(chat_id, value)
                keyboard = [[InlineKeyboardButton("آموزش اتصال📡", callback_data='help')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id, f"🥰ترافیک اکانتتون با موفقیت افزایش پیدا کرد\n{user}\n\nبرای آموزش وصل شدن به سرویس دکمه پایینو بزنین", reply_markup=reply_markup)
            else:
                query.edit_message_text(text="خطایی پیش اومد بعدا امتحان کنین😑", reply_markup=reply_markup)
        except:
            query.edit_message_text(text="خطایی پیش اومد بعدا امتحان کنین😑", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('TTPB_'))
def call_TTPB(bot, query):
    if get_settings()['trx_buy'] == "off":
        query.answer("این روش پرداخت توسط ادمین غیرفعال شده", show_alert=True)
        return
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("TTPB_")[1]
        GB = int(data.split("-")[0])
        price = data.split("-")[1].split(":")[0]
        user = (data.split("@")[0]).split(":")[1]
        host = data.split("@")[1]
        name, username, wallet, crypto = get_wallet_info()
        add_cache(chat_id, "traffic")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='traffic_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [GB, price, user, host]
        add_code_buy(chat_id, Code, "traffic", cache_list)
        price = trx_price(price)
        text = f"""
مبلغ:
{price}

به آدرس ترون :
<pre>{wallet}</pre>
واریز کنین و سپس رسید عکس خودرا بفرستید
یکبار روی آدرس بزنین کپی میشه


برای کنسل کردن دکمه  بک بزنید
قیمت دلار: {str(Toman_USD())}
            """
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)


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
    if (settings['buy'] == 'on'):
        text = "یکی از گزینه هارو انتخاب کنین:\n\n"
        if chat_id in seller_id:
            for i in range(len(settings['seller_prices'])):
                if settings['seller_traffic'][i] == 0:
                    traffic = "نامحدود"
                else:
                    traffic = str(settings['seller_traffic'][i]) + " گیگ"
                #text += f"{str(i + 1)}. {traffic} - {str(settings['seller_connections'][i])} کاربر - {str(settings['seller_days'][i])} روزه - {str(settings['seller_prices'][i])} تومن\n"
                tcb = f"{str(settings['seller_days'][i])} روزه - {str(settings['seller_connections'][i])} کاربر - {traffic} - {str(settings['seller_prices'][i])} تومن"
                cb = f"BU_{str(settings['seller_days'][i])}-{str(settings['seller_traffic'][i])}#{str(settings['seller_connections'][i])}&{str(settings['seller_prices'][i])}"
                keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
        else:
            for i in range(len(settings['prices'])):
                if settings['traffic'][i] == 0:
                    traffic = "نامحدود"
                else:
                    traffic = str(settings['traffic'][i]) + " گیگ"
                #text += f"{str(i + 1)}. {traffic} - {str(settings['connections'][i])} کاربر - {str(settings['days'][i])} روزه - {str(settings['prices'][i])} تومن\n"
                tcb = f"{str(settings['days'][i])} روزه - {str(settings['connections'][i])} کاربر - {traffic} - {str(settings['prices'][i])} تومن"
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
    if get_settings()['card_buy'] == "off":
        query.answer("این روش پرداخت توسط ادمین غیرفعال شده", show_alert=True)
        return
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("CC_")[1]
        days = data.split("-")[0]
        GB = data.split("-")[1].split("#")[0]
        client = data.split("#")[1].split("&")[0]
        price = (data.split("&")[1]).split("!")[0]
        Selected_host = (data.split("!")[1]).split("?")[0]
        UNAME = data.split("?")[1]
        name, username, card = get_card_info()
        add_cache(chat_id, "buy")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='buy_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [days, GB, client, price, query.message.chat.first_name, UNAME, Selected_host]
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
    if get_settings()['trx_buy'] == "off":
        query.answer("این روش پرداخت توسط ادمین غیرفعال شده", show_alert=True)
        return
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("TR_")[1]
        days = data.split("-")[0]
        GB = data.split("-")[1].split("#")[0]
        client = data.split("#")[1].split("&")[0]
        price = (data.split("&")[1]).split("!")[0]
        Selected_host = (data.split("!")[1]).split("?")[0]
        UNAME = data.split("?")[1]
        name, username, wallet, crypto = get_wallet_info()
        add_cache(chat_id, "buy")
        keyboard = []
        Code = uuid4().hex[0:10]
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='buy_' + Code)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cache_list = [days, GB, client, price, query.message.chat.first_name, UNAME, Selected_host]
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
قیمت دلار: {str(Toman_USD())}
            """
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)


@app.on_callback_query(filters.regex('BL_'))
def call_BL(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    if check_cache(chat_id) is False:
        name, u, p, old_value = get_full_user_data_id(chat_id)
        data = query.data
        data = data.split("BL_")[1]
        days = int(data.split("-")[0])
        GB = int(data.split("-")[1].split("#")[0])
        connection_limit = int(data.split("#")[1].split("&")[0])
        price = int((data.split("&")[1]).split("!")[0])
        Selected_host = (data.split("!")[1]).split("?")[0]
        UNAME = data.split("?")[1]
        if old_value - price < 0:
            query.answer("موجودی کافی نیست ☹️", show_alert=True)
            return
        query.edit_message_text(text="درحال انتخاب سرور...")
        if Selected_host == "random":
            host = get_random_server()
        else:
            host = Selected_host
            hosts, remarks = sshx.HOSTS()
            if host not in hosts:
                host = None
        keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            USERNAME = "@" + query.message.chat.username
        except:
            USERNAME = "None"
        if host is not None:
            settings = get_settings()
            query.edit_message_text(text="درحال ساخت...")
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            passw = str(randint(214254, 999999))
            try:
                Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                if UNAME == "random":
                    user = host.split('.')[0] + "a" + str(randint(1243, 6523))
                else:
                    user = UNAME
                    response, Status = Session.Exist(user)
                    if "Error" not in response:
                        if Status is True:
                            user = UNAME + str(randint(12, 350))
                    else:
                        user = UNAME + str(randint(123, 350))
                t0 = "🥰مرسی از خریدتون\n\n"
                if chat_id in seller_id:
                    creator = "SELLER"
                else:
                    creator = "USER"
                description = f"[ Bot - {creator} ] Date: ( {str(jdatetime.datetime.now()).split('.')[0]} ), userID: {str(chat_id)}, Username: {USERNAME}"
                if settings['first_connect'] == 'on':
                    first_connect = True
                else:
                    first_connect = False
                text = t0 + Session.Create(user, passw, connection_limit, days, GB, description, first_connect)
                if "Error" not in text:
                    port, udgpw = Session.Ports()
                    HOST = ((text.split("SSH Host : ")[1]).split("\n")[0])
                    url = f"ssh://{user}:{passw}@{HOST}:{port}#{user}"
                    photo = QR_Maker(url)
                    text += "\n\nURL: " + "<pre>" + url + "</pre>"
                    add_user_db(chat_id, name, USERNAME, user, host)
                    value = old_value - price
                    update_user_wallet(chat_id, value)
                    bot.send_photo(chat_id, open(photo, 'rb'), text, parse_mode=enums.ParseMode.HTML)
                    os.remove(photo)
                    cb = "ID_" + host + "$" + user
                    keyboard = [
                        [InlineKeyboardButton("ℹ️ اطلاعات کامل", callback_data=cb), InlineKeyboardButton("آموزش اتصال📡", callback_data='help')],
                        [InlineKeyboardButton("<<", callback_data='back')]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.send_message(chat_id, settings['after_buy'], reply_markup=reply_markup)
                else:
                    query.edit_message_text(text="خطایی پیش اومد بعدا امتحان کنین😑", reply_markup=reply_markup)
            except:
                query.edit_message_text(text="خطایی پیش اومد بعدا امتحان کنین😑", reply_markup=reply_markup)
        else:
            query.edit_message_text(text="ظرفیت پر شده بعدا امتحان کنین😑", reply_markup=reply_markup)
            for admin in admin_id:
                bot.send_message(admin, "Error to creating account for user: Add a host or change the maximum number in the settings imminently")


@app.on_callback_query(filters.regex('Uname?'))
def call_Uname(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        selected = (data.split("?")[1]).split("_")[0]
        data = data.split("_")[1]
        if selected == "C":
            keyboard = [[InlineKeyboardButton("<<", callback_data='buy')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text="نام کاربری مورد نظرتو بفرست (فقط اعداد و حروف انگلیسی و کمتر از 12 کاراکتر)", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            add_cache(chat_id, "Uname_" + data)
        else:
            cb_cc = "CC_" + data + "?random"
            cb_tr = "TR_" + data + "?random"
            cb_bl = "BL_" + data + "?random"
            if check_seller_exist(chat_id) is True:
                keyboard = [[InlineKeyboardButton("💰کیف پول", callback_data=cb_bl)]]
            else:
                keyboard = [
                    [InlineKeyboardButton("💳کارت به کارت", callback_data=cb_cc), InlineKeyboardButton("💲ترون", callback_data=cb_tr)],
                    [InlineKeyboardButton("💰کیف پول", callback_data=cb_bl)]
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


@app.on_callback_query(filters.regex('XVPSS_'))
def call_XVPSS(bot, query):
    chat_id = query.message.chat.id
    if chat_id in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    host = data.split("!")[1]
    settings = get_settings()
    maximum = settings['maximum']
    if check_domain_reached_maximum(host) is False:
        data = data.split("XVPSS_")[1]
        cb_custom = "Uname?C_" + data
        cb_random = "Uname?R_" + data
        keyboard = [
            [InlineKeyboardButton("✏️دلخواه ", callback_data=cb_custom), InlineKeyboardButton("🔄رندوم", callback_data=cb_random)],
            [InlineKeyboardButton("<<", callback_data='buy')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(text="نام کاربری ؟\nمیتونید نام کاربری دلخواه خودتون بفرستین یا بصورت رندوم انتخاب میشه\n\nیکی از گزینه هارو انتخاب کنین:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except:
            query.edit_message_text(text="📃نام کاربری ؟\nمیتونید نام کاربری دلخواه خودتون بفرستین یا بصورت رندوم انتخاب میشه\n\nیکی از گزینه هارو انتخاب کنین:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("⚠️ظرفیت این سرور پر شده. یه سرور دیگه انتخاب کنین", show_alert=True)


@app.on_callback_query(filters.regex('BU_'))
def call_BU(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is False:
        data = query.data
        data = data.split("BU_")[1]
        cb_custom = "Uname?C_" + data + "!random"
        cb_random = "Uname?R_" + data + "!random"
        keyboard = [
            [InlineKeyboardButton("✏️دلخواه ", callback_data=cb_custom), InlineKeyboardButton("🔄رندوم", callback_data=cb_random)],
            [InlineKeyboardButton("<<", callback_data='buy')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        settings = get_settings()
        if chat_id in seller_id:
            if settings['select_server_sellers'] == "on":
                query.edit_message_text(text="یکی از سرور هارو انتخاب کنین:", reply_markup=server_cb_creator_user("XVPSS_", data))
            else:
                query.edit_message_text(text="نام کاربری ؟\nمیتونید نام کاربری دلخواه خودتون بفرستین یا بصورت رندوم انتخاب میشه\n\nیکی از گزینه هارو انتخاب کنین:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        else:
            if settings['select_server_users'] == "on":
                query.edit_message_text(text="یکی از سرور هارو انتخاب کنین:", reply_markup=server_cb_creator_user("XVPSS_", data))
            else:
                query.edit_message_text(text="نام کاربری ؟\nمیتونید نام کاربری دلخواه خودتون بفرستین یا بصورت رندوم انتخاب میشه\n\nیکی از گزینه هارو انتخاب کنین:", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)


@app.on_callback_query(filters.regex("Confirmed_"))
def call_Confirmed(bot, query):
    if query.message.chat.id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    code = data.split("Confirmed_")[1]
    if "*" in code:
        code = code.replace("*", "")
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
        UNAME = cache_list[5]
        Selected_host = cache_list[6]
        USERNAME = "None"
        msg = bot.send_message(query.message.chat.id, "wait...").id
        try:
            settings = get_settings()
            if (Selected_host == "random") or ("*" in data):
                host = get_random_server()
            else:
                host = Selected_host
                hosts, remarks = sshx.HOSTS()
                if host not in hosts:
                    keyboard = [[InlineKeyboardButton("تایید بصورت سرور رندوم", callback_data=f'{data}*')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.edit_message_text(query.message.chat.id, msg, "سرور انتخابی کاربر وجود نداره", reply_markup=reply_markup)
                    return
            if host is None:
                query.answer(f"Error: Add a host", show_alert=True)
                return
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            if UNAME == "random":
                user = host.split('.')[0] + "a" + str(randint(1243, 6523))
            else:
                user = UNAME
                response, Status = Session.Exist(user)
                if "Error" not in response:
                    if Status is True:
                        user = UNAME + str(randint(12, 350))
                else:
                    user = UNAME + str(randint(123, 350))
            passw = str(randint(214254, 999999))
            t0 = "🥰مرسی از خریدتون\n\n"
            if chat_id in seller_id:
                creator = "SELLER"
            else:
                creator = "USER"
            description = f"[ Bot - {creator} ] Date: ( {str(jdatetime.datetime.now()).split('.')[0]} ), userID: {str(chat_id)}, Username: {USERNAME}"
            if settings['first_connect'] == 'on':
                first_connect = True
            else:
                first_connect = False
            text = t0 + Session.Create(user, passw, connection_limit, days, GB, description, first_connect)
            if "Error" not in text:
                add_check_admin(query.message.chat.id, query.message.chat.first_name, username_admin, code, "Yes", int(time()))
                port, udgpw = Session.Ports()
                HOST = ((text.split("SSH Host : ")[1]).split("\n")[0])
                url = f"ssh://{user}:{passw}@{HOST}:{port}#{user}"
                photo = QR_Maker(url)
                text += "\n\nURL: " + "<pre>" + url + "</pre>"
                bot.send_photo(chat_id, open(photo, 'rb'), text, parse_mode=enums.ParseMode.HTML)
                os.remove(photo)
                add_user_db(chat_id, name, USERNAME, user, host)
                cb = "ID_" + host + "$" + user
                keyboard = [
                    [InlineKeyboardButton("ℹ️ اطلاعات کامل", callback_data=cb), InlineKeyboardButton("آموزش اتصال📡", callback_data='help')],
                    [InlineKeyboardButton("<<", callback_data='back')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id, settings['after_buy'], reply_markup=reply_markup)
                delete_code_buy(code)
                bot.edit_message_text(query.message.chat.id, msg, "اطلاعات به کاربر ارسال شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='back_admin')]]))
            else:
                bot.edit_message_text(query.message.chat.id, msg, f"Error: {text}")
        except Exception as e:
            bot.edit_message_text(query.message.chat.id, msg, f"Error: {str(e)}")
    else:
        if check_admin_confirm(code) is True:
            Name, Username, Confirm, Checked = get_check_admin_data(code)
            query.answer(f"Checked by {Name}, Username: {Username}, Confirm: {Confirm}", show_alert=True)
        else:
            query.answer("The user cancel it.", show_alert=True)


@app.on_callback_query(filters.regex("NO❌_"))
def call_NO(bot, query):
    if query.message.chat.id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
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
        query.answer("اطلاعات به کاربر ارسال شد", show_alert=True)
    else:
        if check_admin_confirm(code) is True:
            Name, Username, Confirm, Checked = get_check_admin_data(code)
            query.answer(f"Checked by {Name}, Username: {Username}, Confirm: {Confirm}", show_alert=True)
        else:
            query.answer("The user cancel it.", show_alert=True)


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
    chat_id = query.message.chat.id
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    if check_exist_user(host, user) is True:
        keyboard = []
        query.edit_message_text(text="wait...")
        try:
            settings = get_settings()
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            text = "اطلاعات سرویس :\n\n" + Session.User_info(settings['dropbear'])
            if "Error" in text:
                text = "مشکلی پیش اومده بعدا تلاش کنین یا به پشتیبانی اطلاع بدین"
            else:
                text += "\n\nبرای تمدید یکی از گزینه هارو انتخاب کنین🙂"
                keyboard = []
                if chat_id in seller_id:
                    for i in range(len(settings['seller_prices'])):
                        if settings['seller_traffic'][i] == 0:
                            traffic = "نامحدود"
                        else:
                            traffic = str(settings['seller_traffic'][i]) + " گیگ"
                        tcb = f"{str(settings['seller_days'][i])} روزه - {str(settings['seller_connections'][i])} کاربر - {traffic} - {str(settings['seller_prices'][i])} تومن"
                        cb = f"UPKIF_{str(settings['seller_days'][i])}-{str(settings['seller_traffic'][i])}#{str(settings['seller_connections'][i])}&{str(settings['seller_prices'][i])}:{user}@{host}"
                        keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
                else:
                    for i in range(len(settings['prices'])):
                        if settings['traffic'][i] == 0:
                            traffic = "نامحدود"
                        else:
                            traffic = str(settings['traffic'][i]) + " گیگ"
                        tcb = f"{str(settings['days'][i])} روزه - {str(settings['connections'][i])} کاربر - {traffic} - {str(settings['prices'][i])} تومن"
                        cb = f"UPB_{str(settings['days'][i])}-{str(settings['traffic'][i])}#{str(settings['connections'][i])}&{str(settings['prices'][i])}:{user}@{host}"
                        keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
        except:
            text = "⚠️خطا"
        keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
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
        cb_bl = "UPKIF_" + data
        keyboard = [
            [InlineKeyboardButton("💳کارت به کارت", callback_data=cb_cc), InlineKeyboardButton("💲ترون", callback_data=cb_tr)],
            [InlineKeyboardButton("💰کیف پول", callback_data=cb_bl)],
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


@app.on_callback_query(filters.regex('UPKIF_'))
def call_UPKIF(bot, query):
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    if check_cache(chat_id) is False:
        name, u, p, old_value = get_full_user_data_id(chat_id)
        data = query.data
        data = data.split("UPKIF_")[1]
        days = int(data.split("-")[0])
        GB = int(data.split("-")[1].split("#")[0])
        connection_limit = int(data.split("#")[1].split("&")[0])
        price = int(data.split("&")[1].split(":")[0])
        user = (data.split("@")[0]).split(":")[1]
        host = data.split("@")[1]
        if old_value - price < 0:
            query.answer("موجودی کافی نیست ☹️", show_alert=True)
            return
        keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            settings = get_settings()
            if settings['upgrade_days'] == "on":
                try:
                    data = Session.User_info(settings['dropbear'])
                    old_days = int((data.split('Days : ')[1]).split("\n")[0])
                    if old_days >= 1:
                        days += old_days
                except:
                    pass
            server_msg = Session.Update(GB, days, connection_limit)
            text += server_msg
            if "Error" not in server_msg:
                value = old_value - price
                update_user_wallet(chat_id, value)
                keyboard = [[InlineKeyboardButton("آموزش اتصال📡", callback_data='help')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id, f"🥰اکانتتون تمدید شد:\n{user}\n\nبرای آموزش وصل شدن به سرویس دکمه پایینو بزنین", reply_markup=reply_markup)
                try:
                    if user in checked_users:
                        checked_users.remove(user)
                        checked_id.remove(checked_id[checked_users.index(user)])
                except Exception as e:
                    print("Error (line checked_id) : ", str(e))
            else:
                query.edit_message_text(text="خطایی پیش اومد بعدا امتحان کنین😑", reply_markup=reply_markup)
        except:
            query.edit_message_text(text="خطایی پیش اومد بعدا امتحان کنین😑", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('UPTXR_'))
def call_UPTXR(bot, query):
    if get_settings()['trx_buy'] == "off":
        query.answer("این روش پرداخت توسط ادمین غیرفعال شده", show_alert=True)
        return
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
قیمت دلار: {str(Toman_USD())}
            """
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("دوباره تلاش کنید", show_alert=True)
        delete_cache(chat_id)


@app.on_callback_query(filters.regex('UPC_'))
def call_UPC(bot, query):
    if get_settings()['card_buy'] == "off":
        query.answer("این روش پرداخت توسط ادمین غیرفعال شده", show_alert=True)
        return
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
    if query.message.chat.id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
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
        msg = bot.send_message(query.message.chat.id, "wait...").id
        try:
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            text = f"🥰مرسی از خریدتون\n\n"
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            settings = get_settings()
            if settings['upgrade_days'] == "on":
                try:
                    data = Session.User_info(settings['dropbear'])
                    old_days = int((data.split('Days : ')[1]).split("\n")[0])
                    if old_days >= 1:
                        days += old_days
                except:
                    pass
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
                bot.edit_message_text(query.message.chat.id, msg, "اطلاعات به کاربر ارسال شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='back_admin')]]))
                try:
                    if user in checked_users:
                        checked_users.remove(user)
                        checked_id.remove(checked_id[checked_users.index(user)])
                except Exception as e:
                    print("Error (line checked_id) : ", str(e))
            else:
                bot.edit_message_text(query.message.chat.id, msg, f"Error: {server_msg}")
        except Exception as e:
            bot.edit_message_text(query.message.chat.id, msg, f"Error: {str(e)}")
    else:
        if check_admin_confirm(code) is True:
            Name, Username, Confirm, Checked = get_check_admin_data(code)
            query.answer(f"Checked by {Name}, Username: {Username}, Confirm: {Confirm}", show_alert=True)
        else:
            query.answer("The user cancel it.", show_alert=True)


@app.on_callback_query(filters.regex("ConfirmTraffic_"))
def call_Confirmed_Traffic(bot, query):
    if query.message.chat.id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    code = data.split("ConfirmTraffic_")[1]
    if check_code_exists(code) is True:
        chat_id, cache_list = get_code_buy_data(code)
        try:
            username_admin = "@" + query.message.chat.username
        except:
            username_admin = "Null"
        GB = int(cache_list[0])
        user = cache_list[2]
        host = cache_list[3]
        msg = bot.send_message(query.message.chat.id, "wait...").id
        try:
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            process_codes.append(code)
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            server_msg = Session.Update_Traffic(GB)
            if "Error" not in server_msg:
                add_check_admin(query.message.chat.id, query.message.chat.first_name, username_admin, code, "Yes", int(time()))
                if check_seller_exist(chat_id) is False:
                    keyboard = [[InlineKeyboardButton("آموزش اتصال📡", callback_data='help')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.send_message(chat_id, f"🥰ترافیک اکانتتون افزایش پیدا کرد:\n{user}\n\nبرای آموزش وصل شدن به سرویس دکمه پایینو بزنین", reply_markup=reply_markup)
                else:
                    bot.send_message(chat_id, f"✅ترافیک افزایش پیدا کرد\n\nUsername : {user}\nSSH Host : {host}")
                delete_code_buy(code)
                process_codes.remove(code)
                bot.edit_message_text(query.message.chat.id, msg, "اطلاعات به کاربر ارسال شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='back_admin')]]))
                try:
                    if user in checked_users:
                        checked_users.remove(user)
                        checked_id.remove(checked_id[checked_users.index(user)])
                except Exception as e:
                    print("Error (line checked_id) : ", str(e))
            else:
                bot.edit_message_text(query.message.chat.id, msg, f"Error: {server_msg}")
        except Exception as e:
            bot.edit_message_text(query.message.chat.id, msg, f"Error: {str(e)}")
    else:
        if check_admin_confirm(code) is True:
            Name, Username, Confirm, Checked = get_check_admin_data(code)
            query.answer(f"Checked by {Name}, Username: {Username}, Confirm: {Confirm}", show_alert=True)
        else:
            query.answer("The user cancel it.", show_alert=True)


@app.on_callback_query(filters.regex("ConfirmDeposit_"))
def call_Confirmed_deposit(bot, query):
    if query.message.chat.id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    code = data.split("ConfirmDeposit_")[1]
    if check_code_exists(code) is True:
        chat_id, cache_list = get_code_buy_data(code)
        try:
            username_admin = "@" + query.message.chat.username
        except:
            username_admin = "Null"
        new_value = int(cache_list[0])
        try:
            name, u, phone, old_value = get_full_user_data_id(chat_id)
            value = new_value + old_value
            update_user_wallet(chat_id, value)
            add_check_admin(query.message.chat.id, query.message.chat.first_name, username_admin, code, "Yes", int(time()))
            keyboard = [[InlineKeyboardButton("💰کیف پول", callback_data='UWM')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id, "کیف پولتون با موفقیت شارژ شد ✔️🥰", reply_markup=reply_markup)
            delete_code_buy(code)
            query.answer("اطلاعات به کاربر ارسال شد", show_alert=True)
        except Exception as e:
            query.answer(f"Error: {str(e)}", show_alert=True)
    else:
        if check_admin_confirm(code) is True:
            Name, Username, Confirm, Checked = get_check_admin_data(code)
            query.answer(f"Checked by {Name}, Username: {Username}, Confirm: {Confirm}", show_alert=True)
        else:
            query.answer("The user cancel it.", show_alert=True)


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
Udgpw : 7301
Username : user124
...


یا آدرس سرور سرویستون بفرستین
مثلا:
sub.domain.com
        """
        query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        query.edit_message_text(text="لطفا /cancel را بفرستید ")


@app.on_callback_query(filters.regex('ADUB'))
def call_ADUB(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        add_cache(chat_id, "Adminuserbalance")
        query.edit_message_text(text='خب آیدی عددی کاربر یا یه پیام ازش فوروارد کن ')
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('GUA'))
def call_GUA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("New ➕", callback_data='NGA'), InlineKeyboardButton("Remove ➖", callback_data='RGA')],
        [InlineKeyboardButton("All Gift Codes", callback_data='AGA')]
    ]
    keyboard.append([InlineKeyboardButton("<<", callback_data='Manager')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text='کاربرا با استفاده از کد هدیه مبلغی توی کیف پولشون ذخیره میشه', reply_markup=reply_markup)


@app.on_callback_query(filters.regex('AGA'))
def call_AGA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    text = "🎁 Gift codes: \nCode Count Used Value\n\n"
    codes = get_all_gift_codes()
    for i in range(len(codes)):
        value, kind, count, users_id, timer_expiry = get_gift_code_full(codes[i])
        text += f"{str(i + 1)}. {codes[i]} {str(count)} {str(len(users_id))} {str(value)}\n"
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='GUA')]]))


@app.on_callback_query(filters.regex('RGA'))
def call_RGA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        add_cache(chat_id, "AdminGiftDel")
        query.edit_message_text(text='کد مورد نظر بفرستین:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='GUA')]]))
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('NGA'))
def call_NGA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        add_cache(chat_id, "AdminGift")
        add_collector(chat_id, "AdminGift", [], [])
        query.edit_message_text(text='مبلغ به تومن بفرستین: ', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data='GUA')]]))
    else:
        query.edit_message_text(text="Please /cancel it first")


@app.on_callback_query(filters.regex('Manager'))
def call_Manager(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("🔴 غیر فعال کاربر", callback_data='disable'), InlineKeyboardButton("🟢 فعال کاربر", callback_data='enable')],
        [InlineKeyboardButton("🔄تمدید کاربر ", callback_data='update'), InlineKeyboardButton("🗑حذف اکانت", callback_data='remove')],
        [InlineKeyboardButton("👤اطلاعات اکانت", callback_data='userinfo'), InlineKeyboardButton("📄اکانت های کاربر", callback_data='userconfigs')],
        [InlineKeyboardButton("🚻ریست ترافیک", callback_data='TrfRes'), InlineKeyboardButton("➕افزایش ترافیک", callback_data='TrfPlus')],
        [InlineKeyboardButton("🔑تغییر پسورد اکانت", callback_data='ADPASS'), InlineKeyboardButton("👝موجودی کاربر", callback_data='ADUB')],
        [InlineKeyboardButton("🛠ساخت اکانت یوزر تلگرام", callback_data='create'), InlineKeyboardButton("🛠ساخت اکانت", callback_data='Create_none')],
        [InlineKeyboardButton("💀Kill User", callback_data='AKill')]
    ]
    keyboard.append([InlineKeyboardButton("<<", callback_data='back_admin')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '<b>👤 Account Manager</b>\n\nدکمه اکانت های کاربر:\nمیتونین ببینین یه کاربر چند تا اکانت داره و تغییرات رو اکانتشون اعمال کنین (تمدید, غیر فعال, افزایش ترافیک, تغییر پسورد...)\nبرای اینکار کافیه دکمه رو بزنین و یه پیام از کاربر فوروارد کنین (برای کاربرایی که هیدنن کار نمیکنه)\n\nفرق بین دکمه ساخت اکانت و ساخت اکانت یوزر تلگرام وقتی میخواین برای یه کاربر خارج از تلگرام اکانت بسازین دکمه ساخت اکانت بزنین ولی اگه داخل تلگرام بود میتونین دکمه ساخت اکانت یوزر تلگرام بزنین و وقتی کاربر دکمه سرویس های من بزنه اکانت اونجا نمایش داده میشه'
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('RST'))
def call_rst(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    query.edit_message_text(text="سرور مورد نظرو انتخاب کنین )این بخش اکانت های کاربر از ربات حذف میکنه و هم سرور از لیست ربات)", reply_markup=server_cb_creator("DTRS_"))


@app.on_callback_query(filters.regex('DTRS_'))
def call_DTRS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("DTRS_")[1]
    chat_id = query.message.chat.id
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="SMT")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        text = sshx.Remove_Host(host)
        if "Error host" not in text:
            delete_host_users_accounts(host)
        bot.send_message(chat_id, text, reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('MST'))
def call_MST(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    query.edit_message_text(text="سرور مورد نظرتون انتخاب کنین", reply_markup=server_cb_creator("MPST_"))


@app.on_callback_query(filters.regex('MPST_'))
def call_MPST(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("MPST_")[1]
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        chat_id = query.message.chat.id
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, rt)
        keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='پیامتون بفرستین (فقط بصورت تکست)', reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف کردین", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="SMT")]]))


@app.on_callback_query(filters.regex('TST'))
def call_TST(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    query.edit_message_text(text="سرور مورد نظرتون انتخاب کنین:", reply_markup=server_cb_creator("TTRS_"))


@app.on_callback_query(filters.regex('TTRS_'))
def call_TTRS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("TTRS_")[1]
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        try:
            query.edit_message_text(text='Login test Wait...')
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            url, r = sshx.open_session(host, port)
            if sshx.Test(r, host, port, panel, 'updater') is True:
                status = "🟢 Online"
            else:
                status = "🔴 Offline: Please check the username or password or port"
            chat_id = query.message.chat.id
            keyboard = [
                [InlineKeyboardButton("🌐 Edit Domain", callback_data=f"EDD_{host}")],
                [InlineKeyboardButton("🔐 Edit Username and Password and Port", callback_data=f"XQEC_{host}")],
                [InlineKeyboardButton("♾ Edit All", callback_data=f"EAl_{host}")],
                [InlineKeyboardButton("🔙 Back", callback_data="SMT")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = f"Current ⬇️\n\n🖥 Host: {host}\nUser: {username}\nPassword: {password}\nPort: {port}\n📁 Panel: {panel}\n🔄 Status: {status}\n\n" + "برای تغییر دامین کافیه گزینه اول بزنین (فقط برای تغییر دامین یا آدرس آیپی)\nبرای تغییر یوزرنیم و پسورد و پورت گزینه دوم\n\nبرای تغییر کلی آدرس و یوزنیم و پسورد و پورت همه یجا گزینه سوم"
            query.edit_message_text(text=text, reply_markup=reply_markup)
        except Exception as e:
            query.edit_message_text(text=f"Error: {str(e)}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="SMT")]]))
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف کردین", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="SMT")]]))


@app.on_callback_query(filters.regex('EAl_'))
def call_EAl(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("EAl_")[1]
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        keyboard = [
            [InlineKeyboardButton("Shahan", callback_data=f'ELIP_shahan:{host}'), InlineKeyboardButton("XPanel", callback_data=f'ELIP_xpanel:{host}')],
            [InlineKeyboardButton("Rocket", callback_data=f'ELIP_rocket:{host}')],
            [InlineKeyboardButton("<<", callback_data=f'TTRS_{host}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "یکی از پنل های زیر انتخاب کنین :\n"
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف کردین", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="SMT")]]))


@app.on_callback_query(filters.regex('ELIP_'))
def call_ELIP(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split(":")[1]
    panel = rt.split("_")[1].split(":")[0]
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, rt)
        keyboard = [[InlineKeyboardButton("<<", callback_data=f"EAl_{host}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='آدرس سرورو بفرستین', reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف شده", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="SMT")]]))


@app.on_callback_query(filters.regex('XQEC_'))
def call_EUP(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("XQEC_")[1]
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        chat_id = query.message.chat.id
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, rt)
        keyboard = [[InlineKeyboardButton("<<", callback_data=f'TTRS_{host}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='نام کاربری بفرستین', reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف کردین", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="SMT")]]))


@app.on_callback_query(filters.regex('EDD_'))
def call_EDD(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    rt = query.data
    host = rt.split("EDD_")[1]
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        chat_id = query.message.chat.id
        if check_cache(chat_id) is True:
            delete_cache(chat_id)
        add_cache(chat_id, rt)
        keyboard = [[InlineKeyboardButton("<<", callback_data=f'TTRS_{host}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='آدرس سرور جدید بفرستین', reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف کردین", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="SMT")]]))


@app.on_callback_query(filters.regex('AST'))
def call_AST(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("Shahan", callback_data='CHSA_shahan'), InlineKeyboardButton("XPanel", callback_data='CHSA_xpanel')],
        [InlineKeyboardButton("Rocket", callback_data='CHSA_rocket')],
        [InlineKeyboardButton("<<", callback_data='SMT')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    t_persian = "یکی از پنل های زیر انتخاب کنین :\n"
    t_english = '<a href="https://github.com/HamedAp/Ssh-User-management">Shahan</a>\n<a href="https://github.com/xpanel-cp/XPanel-SSH-User-Management">XPanel</a>\n<a href="https://github.com/mahmoud-ap/rocket-ssh">Rocket</a>'
    query.edit_message_text(text=(t_persian + t_english), reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)


@app.on_callback_query(filters.regex('CHSA_'))
def call_CHSA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    panel = data.split("_")[1]
    add_cache(chat_id, "AST_" + panel)
    keyboard = [[InlineKeyboardButton("<<", callback_data='AST')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text='آدرس پنل سرور بفرستین | بدون هیچ پورت یا آدرس کاملی فقط خود آدرس مثل :\nsub.example.com\n\nحتما دقت کنین که پورت 80 برای پنل شاهان باز باشه و اینکه ssl فعال کردین تست کنین که با http وارد پنل میشه یا نه اگه شد ادامه بدین (تو آپدیتای بعدی این مشکل حل میشه)', reply_markup=reply_markup)


@app.on_callback_query(filters.regex('XESSP'))
def call_XESSP(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    query.edit_message_text(text="برای تغییر پورت ssh یکی از سرور های زیر انتخاب کنین (فقط ایکس پنل)", reply_markup=server_cb_creator("ESPOT_"))


@app.on_callback_query(filters.regex('ESPOT_'))
def call_ESPOT(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    host = data.split("_")[1]
    keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        if panel == 'xpanel':
            add_cache(chat_id, "ESSHport_" + host)
            query.edit_message_text(text='پورت ssh بفرستین:', reply_markup=reply_markup)
        else:
            query.answer("این گزینه فقط برای ایکس پنل هست", show_alert=True)
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('UXEP'))
def call_UXEP(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    query.edit_message_text(text="برای تغییر پورت udp یکی از سرور های زیر انتخاب کنین (فقط ایکس پنل)", reply_markup=server_cb_creator("UEPOT_"))


@app.on_callback_query(filters.regex('UEPOT_'))
def call_UEPOT(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    host = data.split("_")[1]
    keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        if panel == 'xpanel':
            add_cache(chat_id, "EUDPport_" + host)
            query.edit_message_text(text='پورت udp بفرستین:', reply_markup=reply_markup)
        else:
            query.answer("این گزینه فقط برای ایکس پنل هست", show_alert=True)
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('FSLJC'))
def call_FSLJC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    query.edit_message_text(text="برای تغییر اسم یکی از سرور های زیر انتخاب کنین :", reply_markup=server_cb_creator("LKXHC_"))


@app.on_callback_query(filters.regex('LKXHC_'))
def call_LKXHC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    host = data.split("_")[1]
    keyboard = [[InlineKeyboardButton("<<", callback_data='SMT')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    hosts, remarks = sshx.HOSTS()
    if host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        add_cache(chat_id, "EDITRemark_" + host)
        query.edit_message_text(text='یه نام برای سرور بفرستین مثل (آمریکا-1 🇺🇸🦅):', reply_markup=reply_markup)
    else:
        query.edit_message_text(text="این سرور وجود نداره! احتمالا قبلا از لیست حذف کردین", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('SMT'))
def call_SMT(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("🔧 تنظیم و اطلاعات کامل یک سرور", callback_data='servers')],
        [InlineKeyboardButton("⚫️ظرفیت سرورها", callback_data='full')],
        [InlineKeyboardButton("➖ حذف", callback_data='RST'), InlineKeyboardButton("➕ افزودن", callback_data='AST')],
        [InlineKeyboardButton("تغییر پورت ssh", callback_data='XESSP'), InlineKeyboardButton("تغییر پورت udp", callback_data='UXEP')],
        [InlineKeyboardButton("تغییر نام سرور 🏳️", callback_data='FSLJC')],
        [InlineKeyboardButton("🔄 تغییر دامین و یوزر و پسورد و پورت پنل", callback_data='TST')],
        [InlineKeyboardButton("📩 ارسال پیام به کاربران خاص یک سرور", callback_data='MST')]
    ]
    keyboard.append([InlineKeyboardButton("<<", callback_data='back_admin')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '<b>🖥 Server Manager</b>' + "\n\n-دکمه تنظیم و اطلاعات کامل یک سرور:\nمیتونین اطلاعات کامل سرور ببینین و کاربرای آنلاین و غیرفعال و نزدیک به منقضی شدن ببینین. اگه سرور شما لایسنس دار باشه امکانات بیشتری داره\n-دکمه ظرفیت سرورها:\nبهتون میگه رو هر سرور چند کاربر وجود داره\nتغییر تغییر پورت اس اس اچ و یو دی پی فقط برای ایکس پنل هست\n\nبرای تغییر سرور هم کافیه دکمه تغییر آدرس و یوزنیم و پسورد بزنین که کاربرارو انتقال بدین به اون آدرس... دقت کنین که فقط کاربرای داخل ربات آدرس سرورشون عوض میشه مواقعی که انتقال دادین کاربرا به ی سرور دیگه از این گزینه استفاده کنین یا یوزرنیم و پسورد یا آدرس سرور رو تغییر دادین"
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('message'))
def call_message(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is False:
        add_cache(chat_id, "message")
        keyboard = [[InlineKeyboardButton("<<", callback_data='back_admin')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='پیامتون بفرستین (تکست, وویس, فیلم, عکس, فایل با کپشن یا بدون کپشن) و یا میتونین فوروارد کنین', reply_markup=reply_markup)
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
        if chat_id in seller_id:
            query.answer("چیزی پیدا نشد")
        else:
            query.answer("سرویسی پیدا نشد. اگه سرویسی دارین دکمه اطلاعات سرویس بزنین و بفرستین 🙂", show_alert=True)


@app.on_callback_query(filters.regex('SELFCPA_'))
def call_SELFCPA(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    cb = host + "$" + user
    add_cache(chat_id, "USP_" + cb)
    keyboard = [[InlineKeyboardButton("<<", callback_data=f'ID_{cb}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text='خب پسورد جدیدتون بفرستین', reply_markup=reply_markup)


@app.on_callback_query(filters.regex('SELFCUA_'))
def call_SELFCUA(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    cb = host + "$" + user
    add_cache(chat_id, "USU_" + cb)
    keyboard = [[InlineKeyboardButton("<<", callback_data=f'ID_{cb}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text='خب نام کاربری جدیدتون بفرستین', reply_markup=reply_markup)


@app.on_callback_query(filters.regex('QRCODE_'))
def call_QRCODE(bot, query):
    chat_id = query.message.chat.id
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    cb = host + "$" + user
    msg = query.edit_message_text(text='Wait...').id
    keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
        text = Session.User_info(get_settings()['dropbear']) + randomized_text()
        Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
        port, udgpw = Session.Ports()
        HOST = ((text.split("SSH Host : ")[1]).split("\n")[0])
        passw = ((text.split("Password : ")[1]).split("\n")[0])
        url = f"ssh://{user}:{passw}@{HOST}:{port}#{user}"
        photo = QR_Maker(url)
        text = "URL: " + "<pre>" + url + "</pre>"
        bot.send_photo(chat_id, open(photo, 'rb'), text, parse_mode=enums.ParseMode.HTML)
        os.remove(photo)
        if check_seller_exist(chat_id) is False:
            keyboard = [[InlineKeyboardButton("آموزش اتصال📡", callback_data='help')], [InlineKeyboardButton("<<", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id, "برای آموزش وصل شدن به سرویس دکمه پایینو بزنین", reply_markup=reply_markup)
    except:
        bot.send_message(chat_id, "⚠️خطا لطفا بعدا تلاش کنین", reply_markup=reply_markup)
    bot.delete_messages(chat_id, msg)


@app.on_callback_query(filters.regex('DJVYS_'))
def call_DJVYS(bot, query):
    chat_id = query.message.chat.id
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    cb = host + "$" + user
    keyboard = [[InlineKeyboardButton("آره ✔️", callback_data=f'DJXVY_{cb}')], [InlineKeyboardButton("نه ✖️", callback_data=f'ID_{cb}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="تایید میکنی که اکانت حذف بشه و دیگه این کار قابل بازگشت نیست!", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('DJXVY_'))
def call_DJXVY(bot, query):
    chat_id = query.message.chat.id
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    cb = host + "$" + user
    query.edit_message_text(text='Wait...')
    keyboard = [[InlineKeyboardButton("<<", callback_data='service')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        SessionDIS = sshx.PANNEL(host, username, password, port, panel, 'User', user)
        text = SessionDIS.Disable()
        Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
        text = Session.Delete(user)
        if check_exist_user(host, user) is True:
            delete_user(host, user)
        if "Error" not in text:
            query.edit_message_text(text='اکانت شما با موفقیت حذف شد. ❌', reply_markup=reply_markup)
        else:
            query.edit_message_text(text='⚠️ خطا ', reply_markup=reply_markup)
    except:
        query.edit_message_text(text='⚠️خطا لطفا بعدا تلاش کنین', reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ID_'))
def call_ID(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    host = (data.split("_")[1]).split("$")[0]
    user = data.split("$")[1]
    cb = host + "$" + user
    if check_exist_user(host, user) is True:
        try:
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            Session = sshx.PANNEL(host, username, password, port, panel, 'User', user)
            settings = get_settings()
            text = Session.User_info(settings['dropbear']) + randomized_text()
            keyboard = [
                [InlineKeyboardButton("🔑تغییر پسورد", callback_data=('SELFCPA_' + cb))],
                [InlineKeyboardButton("📲 کد QR و لینک اتصال", callback_data=f'QRCODE_{cb}')]
            ]
            if (settings['buy'] == 'on') or (chat_id in seller_id):
                keyboard[0].insert(1, InlineKeyboardButton("🔄تمدید", callback_data=("UPG_" + cb)))
            if (settings['buy-traffic'] == 'on') or (chat_id in seller_id):
                keyboard[1].insert(1, InlineKeyboardButton("🔁 خرید ترافیک", callback_data=("UTGB_" + cb)))
            if (settings['delete_user'] == 'on') or (chat_id in seller_id):
                keyboard.append([InlineKeyboardButton("❌حذف اکانت ", callback_data=("DJVYS_" + cb))])
            keyboard.append([InlineKeyboardButton("<<", callback_data='service')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except:
            query.answer("⚠️خطا لطفا بعدا تلاش کنین", show_alert=True)
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
        settings = get_settings()
        if settings['support_status'] == "off":
            query.answer("🔴 پشتیبانی غیرفعال هست. ", show_alert=True)
            return
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
        if settings['support'] == "None":
            sm = ""
        else:
            sm = settings['support']
        query.edit_message_text(text=f"{sm}\n\n🫡یکی از گزینه هارو انتخاب کنین", reply_markup=reply_markup)


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


@app.on_callback_query(filters.regex('test'))
def call_test(bot, query):
    chat_id = query.message.chat.id
    keyboard = [[InlineKeyboardButton("<<", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    settings = get_settings()
    if settings['test'] == "off":
        query.answer("این بخش غیرفعاله!", show_alert=True)
    else:
        if check_test_exists(chat_id) is False:
            try:
                msg = query.edit_message_text(text="Wait...").id
                host = get_random_server()
                if host is None:
                    query.answer("ظرفیت پر شده بعدا امتحان کنین", show_alert=True)
                    return
                try:
                    USERNAME = "@" + query.message.chat.username
                except:
                    USERNAME = "None"
                user = host.split('.')[0] + "a" + str(randint(1243, 6523))
                passw = str(randint(214254, 999999))
                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                t0 = "اکانت تست شما ❤️\n\n"
                GB = float(str("{:.2f}".format(float((settings['test-traffic'] / 1024)))))
                description = f"[ BOT - TEST ] Date: ( {str(jdatetime.datetime.now()).split('.')[0]} ), userID: {str(chat_id)}, Username: {USERNAME}"
                text = t0 + Session.Create(user, passw, 1, 1, GB, description, False)
                if "Error" not in text:
                    add_test_user(chat_id, user)
                    port, udgpw = Session.Ports()
                    HOST = ((text.split("SSH Host : ")[1]).split("\n")[0])
                    url = f"ssh://{user}:{passw}@{HOST}:{port}#{user}"
                    photo = QR_Maker(url)
                    text += "\n\nURL: " + "<pre>" + url + "</pre>"
                    bot.send_photo(chat_id, open(photo, 'rb'), text, parse_mode=enums.ParseMode.HTML)
                    os.remove(photo)
                    try:
                        USERNAME = "@" + query.message.chat.username
                    except:
                        USERNAME = "None"
                    name = query.message.chat.first_name
                    add_user_db(chat_id, name, USERNAME, user, host)
                    cb = "ID_" + host + "$" + user
                    keyboard = [
                        [InlineKeyboardButton("ℹ️ اطلاعات کامل", callback_data=cb), InlineKeyboardButton("آموزش اتصال📡", callback_data='help')],
                        [InlineKeyboardButton("<<", callback_data='back')]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.send_message(chat_id, "برای آموزش وصل شدن به سرویس دکمه پایینو بزنین", reply_markup=reply_markup)
                else:
                    bot.send_message(chat_id, f"Error: {text}")
            except Exception as e:
                bot.send_message(chat_id, "خطایی پیش اومد بعدا امتحان کنین😑")
            bot.delete_messages(chat_id, msg)
        else:
            query.answer("شما قبلا از اکانت تست استفاده کردین", show_alert=True)


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
    query.edit_message_text(text=get_settings()['ios'], reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Android'))
def call_Android(bot, query):
    keyboard = [[InlineKeyboardButton("<<", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=get_settings()['android'], reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Mac'))
def call_Mac(bot, query):
    keyboard = [[InlineKeyboardButton("<<", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=get_settings()['mac'], reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Windows'))
def call_Windows(bot, query):
    keyboard = [[InlineKeyboardButton("<<", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=get_settings()['windows'], reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('referral'))
def call_referral(bot, query):
    if get_settings()['invite'] == "off":
        query.answer("در حال حاضر امکان استفاده از این قابلیت وجود نداره", show_alert=True)
        return
    chat_id = query.message.chat.id
    if botusername == []:
        botusername.append((bot.get_me()).username)
    link = "https://t.me/" + botusername[0] + '?start=' + str(chat_id)
    if check_referral_exists(chat_id) is False:
        try:
            username = "@" + query.message.chat.username
        except:
            username = "Null"
        add_referral(chat_id, query.message.chat.first_name, username, [])
    name, referrals = get_referral_info(chat_id)
    text = f"با دعوت هر یه نفر به ربات {str(get_settings()['referral'])} تومن هدیه بگیرین 🫡🎁\n\nتعداد دعوت های شما: {str(len(referrals))}\n\nلینک دعوت : \n{link}"
    keyboard = []
    keyboard.append([InlineKeyboardButton("<< Back", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, disable_web_page_preview=True)


@app.on_callback_query(filters.regex('ZAUB_'))
def call_ZAUB(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    user_id = int(data.split("_")[1])
    update_user_wallet(user_id, 0)
    keyboard = [
        [InlineKeyboardButton("➖کاهش", callback_data=f'MAUB_{str(user_id)}'), InlineKeyboardButton("➕افزایش", callback_data=f'PAUB_{str(user_id)}')],
        [InlineKeyboardButton("0️⃣صفر کردن موجودی", callback_data=f'ZAUB_{str(user_id)}')],
        [InlineKeyboardButton("<< Menu", callback_data='back_admin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup, disable_web_page_preview=True)


@app.on_callback_query(filters.regex('MAUB_'))
def call_MAUB(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    user_id = int(data.split("_")[1])
    text = "یه عدد بفرست یا  /cancel"
    add_cache(chat_id, "MBalance_" + str(user_id))
    query.edit_message_text(text=text)


@app.on_callback_query(filters.regex('PAUB_'))
def call_PAUB(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    data = query.data
    user_id = int(data.split("_")[1])
    text = "یه عدد بفرست یا  /cancel"
    add_cache(chat_id, "PBalance_" + str(user_id))
    query.edit_message_text(text=text)


@app.on_callback_query(filters.regex('UWPM'))
def call_UWPM(bot, query):
    settings = get_settings()
    if settings['buy'] == 'on':
        chat_id = query.message.chat.id
        delete_cache(chat_id)
        text = "مبلغ مورد نظرتون به تومن بفرستین (حداقل 10000):"
        add_cache(chat_id, "userwpm")
        keyboard = [[InlineKeyboardButton("<< back", callback_data='UWM')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("افزایش موجودی و خرید غیرفعاله", show_alert=True)


@app.on_callback_query(filters.regex('UGift'))
def call_UGift(bot, query):
    chat_id = query.message.chat.id
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    text = "کد هدیتون بفرستین"
    add_cache(chat_id, "usergift")
    keyboard = [[InlineKeyboardButton("<< back", callback_data='UWM')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('UWM'))
def call_UWM(bot, query):
    chat_id = query.message.chat.id
    data = query.data
    if "_" in data:
        code = data.split("UWM_")[1]
        delete_code_buy(code)
    delete_cache(chat_id)
    name, u, phone, old_value = get_full_user_data_id(chat_id)
    text = f"💰 موجودی کیف پول:\n{str(old_value)} تومن "
    keyboard = [
        [InlineKeyboardButton("کد هدیه 🎁", callback_data='UGift'), InlineKeyboardButton("افزایش موجودی➕", callback_data='UWPM')],
        [InlineKeyboardButton("<<", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('CTBKup'))
def call_bktimer(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "backup_timer")
    text = "OK send a number 1-72"
    keyboard = [[InlineKeyboardButton("<<", callback_data='Backup')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('BKupON'))
def call_bkon(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if os.stat("Pannels.txt").st_size == 0:
        query.edit_message_text(text="هیچ سروری وجود نداره, یه سرور اد کنین", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ADD", callback_data='AST')]]))
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
                            hosts, remarks = sshx.HOSTS()
                            for host in hosts:
                                port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                                do = True
                                count_all += 1
                                session = 'ssh/' + host + ".session"
                                if Path(session).is_file() is False:
                                    if sshx.Login(username, password, host, port, panel) is False:
                                        do = False
                                if do is True:
                                    try:
                                        Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                                        status, content = Session.Backup_content()
                                        if status is True:
                                            f = folder + "/" + host + ".sql"
                                            if Path(f).is_file() is True:
                                                os.remove(f)
                                            with open(f, 'wb') as file:
                                                file.write(content)
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
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if backup[0] is True:
        backup.clear()
        backup.append(False)
        run_backup.clear()
        run_backup.append(False)
        keyboard = [[InlineKeyboardButton("<<", callback_data='Backup')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="متوقف شد.", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("Already OFF", show_alert=True)


@app.on_callback_query(filters.regex('BKupBot'))
def call_bkbot(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    msg = query.edit_message_text(text="Sending...").id
    files = ["All.txt", "ssh.db", "data.json", "Pannels.txt", "logs.txt", "nohup.out"]
    logs = "Done✔️\n\nLogs:\n\n"
    for file in files:
        try:
            bot.send_document(chat_id, document=open(file, 'rb'), file_name=file)
        except Exception as e:
            logs += ("File: " + file + " " + str(e) + "\n")
        sleep(0.5)
    bot.send_message(chat_id, logs)
    bot.delete_messages(chat_id, msg)


@app.on_callback_query(filters.regex('UPLOAD'))
def call_UPLOAD(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "upload_panels")
    text = "خب فایل Pannels.txt رو بفرستین (دارین فوروارد میکنین تیک show sender name خاموش باشه):"
    keyboard = [[InlineKeyboardButton("<<", callback_data='Backup')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Backup'))
def call_backup(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("🕔 تغییر تایم بکاپ ", callback_data='CTBKup')],
        [InlineKeyboardButton("🔴 خاموش", callback_data='BKupOFF'), InlineKeyboardButton("🟢 روشن", callback_data='BKupON')],
        [InlineKeyboardButton("🤖 بکاپ ربات", callback_data='BKupBot')],
        [InlineKeyboardButton("📁 آپلود فایل بکاپ ربات", callback_data='UPLOAD')]
    ]
    settings = get_settings()
    if backup[0] is False:
        backup_status = "OFF ❌"
    else:
        backup_status = "ON ✅"
    text = '<b>Backup Settings</b>\n\n(فقط برای ادمینی که این گزینه رو روشن میکنه کار میکنه)' + "\n\n<a href='https://t.me/deltabots_gp/10/955'>آموزش انتقال ربات به سرور جدید</a>" + "\n\n🔄Status\n\n" + "Backup: " + backup_status + "\n" + "🕔Timer: " + str(settings['backup']) + " hours"
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('WSMSG'))
def call_WSMSG(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
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
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_cache(chat_id, "Start_message")
    text = "پیامتون بفرستین"
    keyboard = [[InlineKeyboardButton("<<", callback_data='WSMSG')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('WLMSG'))
def call_WLMSG(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    settings = get_settings()
    if settings['list_status'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ELMSG')],
        [InlineKeyboardButton(f"Show Button: {cb} {emoji_cb}", callback_data=f'OWQZC_{cb}')]
    ]
    text = '<b>Price MSG Settings</b>\n\n' + "Text:\n\n" + settings['list'] + "\n\nStatus: " + settings['list_status'] + " " + emoji
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('OWQZC_'))
def call_OWQZC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    ls = data.split("OWQZC_")[1]
    settings = get_settings()
    settings['list_status'] = ls
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='WLMSG')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ELMSG'))
def call_ELMSG(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_cache(chat_id, "Price_message")
    text = "پیامتون بفرستین"
    keyboard = [[InlineKeyboardButton("<<", callback_data='WLMSG')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('sponser'))
def call_sponser(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ESship')],
        [InlineKeyboardButton("Delete✖️", callback_data='Delship')],
    ]
    settings = get_settings()
    text = '<b>Sponser Settings</b>\n\n' + "Current: " + settings['sponser'] + "\n\nجوین اجباری کانال حتما باید اول ربات ادمین چنل یا گروه پابلیک باشه و بعد دکمه ادیت بزنین و آیدی رو بفرستین"
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Delship'))
def call_Delship(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    settings['sponser'] = "None"
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='sponser')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('ESship'))
def call_ESship(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_cache(chat_id, "Sponser")
    text = "ربات تو گروه یا چنلتون ادمین کنین, حتما باید پابلیک باشه, آیدی چنل یا گروه به این صورت بفرست: @channel"
    keyboard = [[InlineKeyboardButton("<<", callback_data='sponser')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('AutoDelete'))
def call_AutoDelete(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='EADel')],
    ]
    settings = get_settings()
    text = '<b>Auto Delete Settings</b>\n\n' + 'بر اساس تعداد روز سپری شده ای که شما تعیین میکنین کاربر منقضی که تمدید نکرده رو از سرور پاک میکنه (این آپشن زمانی کار میکنه که دکمه "چکر" رو بزنین یا تو تنظیمات دکمه "چکر و اطلاع رسانی حجم تاریخ به کاربر" روشن باشه)\n\nCurrent: ' + str(settings['auto_delete']) + " Days"
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EADel'))
def call_EADel(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_cache(chat_id, "AutoDelete")
    text = "OK send only number"
    keyboard = [[InlineKeyboardButton("<<", callback_data='AutoDelete')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('USD'))
def call_USD(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    query.edit_message_text(text="wait...")
    chat_id = query.message.chat.id
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit Default✏️", callback_data='Edollar')],
    ]
    status, value = GET_USD()
    if status is True:
        value = str(value) + " تومن"
    else:
        value = "API Error: iran websites blocked by the server, change the rules"
    settings = get_settings()
    text = '<b>USD Settings</b>\n\n' + "پیش فرض: " + str(settings['usd']) + " تومن\n" + "الان: " + value
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Edollar'))
def call_Edollar(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_cache(chat_id, "USD")
    text = "OK send only number\n\nبه تومن بفرستین مثل 50000"
    keyboard = [[InlineKeyboardButton("<<", callback_data='USD')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('maximum'))
def call_maximum(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='EMXM')],
    ]
    settings = get_settings()
    text = '<b>Maximum Settings</b>\n\n' + "کاربرد این گزینه : وقتی شما مثلا عدد 50  کاربر تنظیم میکنین برای هر سرور... وقتی که فروش فعال باشه و کاربر اکانت بخره. سرور وقتی رسید به 50 تا کاربر دیگه اکانت نمیسازه و میره از سرور بعدی میسازه ولی وقتی که هیچ سرور دیگه ای نباشه یا همه سرورا رسیده باشن به 50 کاربر شما باید سرور جدید به ربات اضافه کنین یا مقدارو تغییر بدین هر موقع که خواستین و این هم برای گزینه برای دکمه ظرفیت سرور ها کاربرد داره و میگه که کدوم سرورا رسیدن به 50 تا اکانت. برای تغییر مقدار دکمه ادیت بزنین\n\nCurrent: " + str(settings['maximum']) + " Clients"
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EMXM'))
def call_EMXM(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_cache(chat_id, "maximum")
    text = "OK send only number"
    keyboard = [[InlineKeyboardButton("<<", callback_data='maximum')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('ZQUC'))
def call_ZQUC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['upgrade_days'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    keyboard = [
        [InlineKeyboardButton(f"{cb} {emoji_cb}", callback_data=f'JDXSF_{cb}')],
    ]
    text = '<b>Upgrade Settings</b>\n\n' + "وقتی که کاربر یه اکانتی داره و سه روز دیگه مونده اکانتش تموم بشه و تمدید کنه, و مثلا سی روزه تمدید کنه و این گزینه هم روشن باشه , تعداد روز باقی مونده + روز خریداری شده تمدید میشه یعنی: 33 روزه میشه\n\nاین گزینه خاموش باشه همون 30 روز تمدید میشه\n\nنکته این گزینه فقط برای فروشنده ها و کاربرا هست و اگه ادمین تمدید کنه تعداد همون روزی که داده شده ثبت میشه." + "\n\nCurrent: " + settings['upgrade_days'] + " " + emoji
    keyboard.append([InlineKeyboardButton("<<", callback_data='ZBSHP')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('JDXSF_'))
def call_JDXSF(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    status = data.split("JDXSF_")[1]
    settings = get_settings()
    settings['upgrade_days'] = status
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='ZQUC')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('PODSC'))
def call_PODSC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='EPCSD')],
    ]
    settings = get_settings()
    text = '<b>Buy MSG Settings</b>\n\n' + "میتونین پیام تنظیم کنین که بعد از خرید کاربر بهشون چیزیو ک میخواید بگین" + "\n\nText:\n\n" + settings['after_buy']
    keyboard.append([InlineKeyboardButton("<<", callback_data='ZBSHP')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EPCSD'))
def call_EPCSD(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_cache(chat_id, "after_buy")
    text = "پیامتون بفرستین"
    keyboard = [[InlineKeyboardButton("<<", callback_data='PODSC')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('ZBSHP'))
def call_ZBSHP(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['first_connect'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    keyboard = [
        [InlineKeyboardButton("💵 ولت ترون", callback_data='wallet'), InlineKeyboardButton("💳 کارت", callback_data='Card')],
        [InlineKeyboardButton("🛒قیمت ترافیک", callback_data='ADTPR'), InlineKeyboardButton("🛒قیمت ها", callback_data='ADMINPRICES')],
        [InlineKeyboardButton("🚦 وضعیت خرید ترافیک", callback_data='BTOPtion'), InlineKeyboardButton("🔐وضعیت خرید اکانت", callback_data='BSOPtion')],
        [InlineKeyboardButton("🔄تنظیم تمدید کاربر ", callback_data='ZQUC')],
        [InlineKeyboardButton("📃 پیام بعد از خرید اکانت کاربر ", callback_data='PODSC')],
        [InlineKeyboardButton(f"ساخت از اولین اتصال : {cb} {emoji_cb}", callback_data=f'VKDLS_{cb}')]
    ]
    t0 = "\n\nCurrent: " + settings['first_connect'] + " " + emoji
    text = '<b>Shop Settings</b>\n\n' + "تنظیمات خرید و تمدید اکانت و ترافیک\n\nاگه گزینه روشن باشه 🟢 on کاربر یا فروشنده وقتی اکانتی رو میخره از اولین اتصال روز اکانت درست میشه و اگه خاموش باشه از همون لحظه شروع میشه " + t0
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('VKDLS_'))
def call_VKDLS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    first_connect = data.split("VKDLS_")[1]
    settings = get_settings()
    settings['first_connect'] = first_connect
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='ZBSHP')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('BSOPtion'))
def call_BSOPtion(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
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
        [InlineKeyboardButton(f"وضعیت خرید {cb} {emoji_cb}", callback_data=f'EBS_{cb}')]
    ]
    text = '<b>Shop Status Settings</b>\n\n' + "میتونین با خاموش و روشن کردن این گزینه خرید یا تمدید غیرفعال یا فعال کنین" + "\n\nCurrent: " + settings['buy'] + " " + emoji
    keyboard.append([InlineKeyboardButton("<<", callback_data='ZBSHP')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EBS_'))
def call_EBS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
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
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
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
    keyboard.append([InlineKeyboardButton("<<", callback_data='ZBSHP')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('AAPR'))
def call_AAPR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_collector(chat_id, "domain_none", [], [])
    delete_cache(chat_id)
    add_cache(chat_id, "A_price")
    text = "خب قیمت مورد نظرو بصورت عدد بفرست مثلا : 50000 تومن "
    query.edit_message_text(text=text, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('DAPR'))
def call_DAPR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if len(settings['traffic']) == 0:
        query.answer("هیچی وجود نداره, تعرفه جدید اد کنین", show_alert=True)
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
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
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
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if os.stat("Pannels.txt").st_size == 0:
        query.edit_message_text(text="هیچ سروری وجود نداره, یه سرور اد کنین", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ADD", callback_data='AST')]]))
    else:
        if True:
            if Filtering_system[0] is False:
                chat_id = query.message.chat.id
                keyboard = [[InlineKeyboardButton("<<", callback_data='FILCH')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text=f"Started✔️", reply_markup=reply_markup)
                Filtering_system.clear()
                Filtering_system.append(True)
                run_filtering.clear()
                run_filtering.append(True)
                while True:
                    if run_filtering[0] is True:
                        hosts, remarks = sshx.HOSTS()
                        for host in hosts:
                            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                            do = True
                            session = 'ssh/' + host + ".session"
                            if Path(session).is_file() is False:
                                if sshx.Login(username, password, host, port, panel) is False:
                                    do = False
                            if do is True:
                                try:
                                    Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                                    status, content = Session.IP_Check()
                                    if (status is True) and (host not in checked_filtering):
                                        # try again
                                        for i in range(2):
                                            status, content = Session.IP_Check()
                                            if (status is True) and (i == 1):
                                                if check_host_api(host) is True:
                                                    text = "🔴Blocked in IRAN: " + host
                                                    checked_filtering.append(host)
                                                    for admin in admin_id:
                                                        bot.send_message(admin, text)
                                                    break
                                            elif status is False:
                                                break
                                            sleep(1)
                                    else:
                                        if "Error" not in content:
                                            if host in checked_filtering:
                                                checked_filtering.remove(host)
                                                text = "🟢Back online [IP Check]: " + host
                                                for admin in admin_id:
                                                    bot.send_message(admin, text)
                                            if host in checked_connections:
                                                checked_connections.remove(host)
                                                text = "🟢Back online [Bot Connection]: " + host
                                                for admin in admin_id:
                                                    bot.send_message(admin, text)
                                        else:
                                            if host not in checked_connections:
                                                text = "🔴Connection Error: " + host + "\nLog:\n" + content
                                                checked_connections.append(host)
                                                for admin in admin_id:
                                                    bot.send_message(admin, text)
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
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if Filtering_system[0] is True:
        Filtering_system.clear()
        Filtering_system.append(False)
        run_filtering.clear()
        run_filtering.append(False)
        keyboard = [[InlineKeyboardButton("<<", callback_data='FILCH')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="متوقف شد.", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("Already OFF", show_alert=True)


@app.on_callback_query(filters.regex('FILCH'))
def call_FILCH(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("ON 🟢", callback_data='FLCHON')],
        [InlineKeyboardButton("OFF 🔴", callback_data='FLCHOFF')]
    ]
    if Filtering_system[0] is False:
        status = "OFF ❌"
    else:
        status = "ON ✅"
    text = '<b>Filtering System Checker Settings</b>\n\nهر 5 دقیقه یه بار بررسی میشه و بهت اطلاع میده که کدوم سرور فیلتر شده (فقط برای ادمینی که این گزینه رو روشن میکنه کار میکنه)\nنکته باید ICMP فعال باشه وگرنه سرور ممکنه فیلتر نباشه و بهت میگه فیلتره و اینکه بصورت دیفالت فعال هست ولی اگه غیرفعال بود باید فعال کنین برای تستم برین به سایت check-host.net پینگ بگیرین اگه از همه کشورا تایم اوت داد یعنی اینکه غیرفعاله' + "\n\n🔄Status: " + status
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('APRX'))
def call_APRX(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    add_cache(chat_id, "proxy")
    text = "پروکسی رو بفرست"
    keyboard = [[InlineKeyboardButton("<<", callback_data='Sprx')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('DPRX'))
def call_DPRX(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    settings['proxy'] = "None"
    update_settings(settings)
    text = "Done✔️"
    keyboard = [[InlineKeyboardButton("<<", callback_data='Sprx')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Sprx'))
def call_Sprx(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    settings = get_settings()
    if settings['proxy'] == "None":
        keyboard = [[InlineKeyboardButton("Add➕", callback_data='APRX')]]
    else:
        keyboard = [
            [InlineKeyboardButton("Edit✏️", callback_data='APRX')],
            [InlineKeyboardButton("Delete✖️", callback_data='DPRX')],
        ]
    text = '<b>Proxy Settings</b>\n\n' + "میتونین پروکسی خودتون تو ربات اد کنین و کاربرا بتونن استفاده کنن از این آپشن \n\nCurrent: \n" + settings['proxy']
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('NUSYS'))
def call_NUSYS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("ON 🟢", callback_data='SNON')],
        [InlineKeyboardButton("OFF 🔴", callback_data='SNFF')]
    ]
    if notify_system[0] is False:
        status = "OFF ❌"
    else:
        status = "ON ✅"
    tp = """هر 30 دقیقه یه بار بررسی میشه و به کاربرای که نزدیکه حجم یا تاریخ اکانتشون تموم بشه اطلاع میده
این دکمه مشابه دکمه چکر هست ولی دکمه چکر فقط یه بار اطلاع رسانی میکنه و کاربرای منقضی بر اساس روز سپری شده ای که داخل تنظیمات تنظیم کردین رو حذف میکنه

هر بار که ربات آپدیت شد یا دوباره کامند نصب زدید باید دوباره روشن کنین

⚪️ نکته !
برای اینکه کاربران تست حذف بشن یا دکمه چکر بزنین یا
 خودکار حذف بشن باید حتما این گزینه روشن باشه"""
    text = '<b>Notify System Checker Settings</b>\n\n' + tp + "\n\n🔄Status: " + status + "\n📃Notified: " + str(len(checked_id))
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('SNON'))
def call_SNON(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if os.stat("Pannels.txt").st_size == 0:
        query.edit_message_text(text="هیچ سروری وجود نداره, یه سرور اد کنین", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ADD", callback_data='AST')]]))
    else:
        if True:
            if notify_system[0] is False:
                chat_id = query.message.chat.id
                keyboard = [[InlineKeyboardButton("<<", callback_data='NUSYS')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text=f"Started✔️", reply_markup=reply_markup)
                notify_system.clear()
                notify_system.append(True)
                run_notify.clear()
                run_notify.append(True)
                while True:
                    if run_filtering[0] is True:
                        settings = get_settings()
                        test_usernames = get_test_usernames()
                        hosts, remarks = sshx.HOSTS()
                        for host in hosts:
                            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
                            do = True
                            session = 'ssh/' + host + ".session"
                            if Path(session).is_file() is False:
                                if sshx.Login(username, password, host, port, panel) is False:
                                    do = False
                            if do is True:
                                try:
                                    Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
                                    expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, ips, descriptions, server_traffic, online_c, done = Session.info()
                                    if done is True:
                                        DB_usernames = get_db(host)
                                        for DB_username in DB_usernames:
                                            if DB_username not in usernames:
                                                delete_user(host, DB_username)
                                        if status[i] != "فعال":
                                            if (int(days_left[i]) <= -(settings['auto_delete'])) or (usernames[i] in test_usernames):
                                                SessionDIS = sshx.PANNEL(host, username, password, port, panel, 'User', usernames[i])
                                                svs = SessionDIS.Disable()
                                                if "❌Deleted" in Session.Delete(usernames[i]):
                                                    if check_exist_user(host, usernames[i]) is True:
                                                        ID, Name, Username = get_all_user_data(host, usernames[i])
                                                        if usernames[i] in test_usernames:
                                                            NTX = f"❌اکانت: {usernames[i]} تست به اتمام رسید"
                                                        else:
                                                            NTX = f"❌اکانت: {usernames[i]}به علت گذشت چند روز و نشدن تمدید حذف شد"
                                                        delete_user(host, usernames[i])
                                                        if checker_notify(str(ID)) is True:
                                                            try:
                                                                bot.send_message(ID, NTX)
                                                            except:
                                                                pass
                                        else:
                                            if (0 < int(days_left[i]) <= 3) or ((("نامحدود" != traffics[i]) and (usages[i] != "0.0")) and (float(usages[i]) >= (float(traffics[i].split("گیگابایت")[0])) - 2.0)):
                                                if check_exist_user(host, usernames[i]) is True:
                                                    ID, Name, Username = get_all_user_data(host, usernames[i])
                                                    if (checker_notify(str(ID)) is True) and ((ID not in checked_id) or (usernames[i] not in checked_users)):
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
                                                            checked_users.append(usernames[i])
                                                            checked_id.append(ID)
                                                        except:
                                                            pass
                                except:
                                    pass
                        sleep(1800)
                    else:
                        break
            else:
                query.answer("Already ON", show_alert=True)


@app.on_callback_query(filters.regex('SNFF'))
def call_SNFF(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if notify_system[0] is True:
        notify_system.clear()
        notify_system.append(False)
        run_notify.clear()
        run_notify.append(False)
        checked_id.clear()
        checked_users.clear()
        keyboard = [[InlineKeyboardButton("<<", callback_data='NUSYS')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="متوقف شد.", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        query.answer("Already OFF", show_alert=True)


@app.on_callback_query(filters.regex('INVS'))
def call_INVS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    settings = get_settings()
    if settings['invite'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ENVS')],
        [InlineKeyboardButton(f"{cb} {emoji_cb}", callback_data=f'XNVS_{cb}')]
    ]
    text = '<b>Referrals Settings</b>\n\n' + "با دعوت هر یه نفر به ربات با لینک توسط یه کاربر یه مبلغی به کیف پولش اضافه میشه . دکمه ادیت بزنین و مبلغ مورد نظرتون به تومن بفرستین\n\nمیتونید این قابلیت برای کاربرا خاموش کنین\n\nCurrent: " + str(settings['referral']) + " تومن\n" + settings['invite'] + " " + emoji
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('XNVS_'))
def call_XNVS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    invite = data.split("XNVS_")[1]
    settings = get_settings()
    settings['invite'] = invite
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='INVS')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ENVS'))
def call_ENVS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "invite")
    text = "عدد مورد نظرتو بفرست:r"
    keyboard = [[InlineKeyboardButton("<<", callback_data='INVS')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('SID'))
def call_SID(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    settings = get_settings()
    if settings['support_status'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='EAID'), InlineKeyboardButton("Delete✖️", callback_data='DAID')],
        [InlineKeyboardButton(f"Support: {cb} {emoji_cb}", callback_data=f'VSQBX_{cb}')]
    ]
    text = '<b>Support Settings</b>\n\n' + "میتونین یه پیام پشتیبانی رو قرار بدین و وقتی کاربر دکمه پشتیبانی رو بزنه پیامی که تنظیم کردین نمایش داده بشه \n\nCurrent: " + settings['support'] + "\n\nStatus: " + settings['support_status'] + " " + emoji
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('VSQBX_'))
def call_VSQBX(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    sups = data.split("VSQBX_")[1]
    settings = get_settings()
    settings['support_status'] = sups
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='SID')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('DAID'))
def call_DAID(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    settings['support'] = "None"
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='SID')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EAID'))
def call_EAID(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "EAID")
    text = "پیامتون بفرستین"
    keyboard = [[InlineKeyboardButton("<<", callback_data='SID')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Tutorials'))
def call_Tutorials(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("IOS🍏", callback_data='CTI'), InlineKeyboardButton("Android🤖", callback_data='CTA')],
        [InlineKeyboardButton("Mac🍎", callback_data='CTM'), InlineKeyboardButton("Windows💻", callback_data='CTW')]
    ]
    text = '<b>Tutorials Settings</b>\n\n' + "یکی از گزینه هارو انتخاب کنین"
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('CTI'))
def call_CTI(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ETI')],
    ]
    settings = get_settings()
    text = '<b>IOS🍏</b>\n\n' + "Current: \n\n" + str(settings['ios'])
    keyboard.append([InlineKeyboardButton("<<", callback_data='Tutorials')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)


@app.on_callback_query(filters.regex('ETI'))
def call_ETI(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "ETI")
    text = "پیامتون بفرستین"
    keyboard = [[InlineKeyboardButton("<<", callback_data='CTI')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('CTA'))
def call_CTA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ETA')],
    ]
    settings = get_settings()
    text = '<b>Android🤖</b>\n\n' + "Current: \n\n" + str(settings['android'])
    keyboard.append([InlineKeyboardButton("<<", callback_data='Tutorials')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)


@app.on_callback_query(filters.regex('ETA'))
def call_ETA(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "ETA")
    text = "پیامتون بفرستین"
    keyboard = [[InlineKeyboardButton("<<", callback_data='CTA')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('CTM'))
def call_CTM(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ETM')],
    ]
    settings = get_settings()
    text = '<b>Mac🍎</b>\n\n' + "Current: \n\n" + str(settings['mac'])
    keyboard.append([InlineKeyboardButton("<<", callback_data='Tutorials')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)


@app.on_callback_query(filters.regex('ETM'))
def call_ETM(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "ETM")
    text = "پیامتون بفرستین"
    keyboard = [[InlineKeyboardButton("<<", callback_data='CTM')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('CTW'))
def call_CTW(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Edit✏️", callback_data='ETW')],
    ]
    settings = get_settings()
    text = '<b>Windows💻</b>\n\n' + "Current: \n\n" + str(settings['windows'])
    keyboard.append([InlineKeyboardButton("<<", callback_data='Tutorials')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)


@app.on_callback_query(filters.regex('ETW'))
def call_ETW(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "ETW")
    text = "پیامتون بفرستین"
    keyboard = [[InlineKeyboardButton("<<", callback_data='CTW')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('TASET'))
def call_TASET(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['test'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    keyboard = [
        [InlineKeyboardButton(f"{cb} {emoji_cb}", callback_data=f'ETOR_{cb}')],
        [InlineKeyboardButton("Edit Traffic✏️", callback_data='ETTR')],
        [InlineKeyboardButton("حذف تمام کاربران اکانت تست ✖️", callback_data='DTAC')],
    ]
    text = '<b>TEST Settings</b>\n\n' + "با خاموش روشن کردن این گزینه کاربرا میتونن اکانت تست دریافت یا دریافت نکنن" + "\n\nCurrent: " + settings['test'] + " " + emoji + "\nTraffic: " + str(settings['test-traffic']) + "MB\nHours: 24h\nConnections: 1\nUsers test: " + str(get_count_test_users())
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('DTAC'))
def call_DTAC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    text = "با این کار تمامی کاربران اکانت تست حذف میشن و دوباره میتونن اکانت تست دریافت کنن"
    keyboard = [
        [InlineKeyboardButton("🗑حذف", callback_data='DLATU')],
        [InlineKeyboardButton("<<", callback_data='TASET')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex('DLATU'))
def call_DLATU(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_test_users()
    keyboard = [[InlineKeyboardButton("<<", callback_data='TASET')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ETOR_'))
def call_ETOR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    test = data.split("ETOR_")[1]
    settings = get_settings()
    settings['test'] = test
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='TASET')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ETTR'))
def call_ETTR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    if check_cache(chat_id) is True:
        delete_cache(chat_id)
    add_cache(chat_id, "ETTR")
    text = "حجمو به مگابایت بفرست"
    keyboard = [[InlineKeyboardButton("<<", callback_data='TASET')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('BTOPtion'))
def call_BTOPtion(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['buy-traffic'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    keyboard = [
        [InlineKeyboardButton(f"{cb} {emoji_cb}", callback_data=f'EBT_{cb}')],
    ]
    text = '<b>Traffic shop Settings</b>\n\n' + "میتونین با خاموش و روشن کردن این گزینه خرید ترافیک غیرفعال یا فعال کنین" + "\n\nCurrent: " + settings['buy-traffic'] + " " + emoji
    keyboard.append([InlineKeyboardButton("<<", callback_data='ZBSHP')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EBT_'))
def call_EBT(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    buy = data.split("EBT_")[1]
    settings = get_settings()
    settings['buy-traffic'] = buy
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='BTOPtion')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ADTPR'))
def call_ADTPR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Delete✖️", callback_data='DeATPR')],
        [InlineKeyboardButton("Add➕", callback_data='AdATPR')]
    ]
    settings = get_settings()
    currnet = ""
    for i in range(len(settings['plus-traffic'])):
        currnet += f"{str(i + 1)}. {str(settings['plus-traffic'][i])} گیگابایت - {str(settings['plus-prices'][i])} تومن\n"
    text = '<b>Traffic Prices Settings</b>\n\n\n' + "Current: \n" + currnet
    keyboard.append([InlineKeyboardButton("<<", callback_data='ZBSHP')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('AdATPR'))
def call_AdATPR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_collector(chat_id, "Traffic_price", [], [])
    delete_cache(chat_id)
    add_cache(chat_id, "Traffic_price")
    text = "خب قیمت مورد نظرو بصورت عدد بفرست مثلا : 50000 "
    query.edit_message_text(text=text, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('DeATPR'))
def call_DeATPR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if len(settings['plus-traffic']) == 0:
        query.answer("هیچی وجود نداره, تعرفه جدید اد کنین", show_alert=True)
    else:
        keyboard = []
        for i in range(len(settings['plus-traffic'])):
            tcb = f"{str(settings['plus-traffic'][i])} گیگابایت - {str(settings['plus-prices'][i])} تومن"
            cb = "TPDSEL_" + str(i)
            keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
        keyboard.append([InlineKeyboardButton("<<", callback_data='ADTPR')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Ok choose to delete:", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('TPDSEL_'))
def call_TPDSEL(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    i = int(data.split("TPDSEL_")[1])
    settings = get_settings()
    prices = settings['plus-prices']
    del prices[i]
    traffic = settings['plus-traffic']
    del traffic[i]
    settings['plus-prices'] = prices
    settings['plus-traffic'] = traffic
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='ADTPR')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('PNS'))
def call_PNS(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['phone'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"

    if settings['irphone'] == "on":
        emoji_2 = "🟢"
        cb_2 = 'off'
        emoji_cb_2 = "🔴"
    else:
        emoji_2 = "🔴"
        cb_2 = 'on'
        emoji_cb_2 = "🟢"
    keyboard = [
        [InlineKeyboardButton(f"Phone {cb} {emoji_cb}", callback_data=f'EWPN_{cb}')],
        [InlineKeyboardButton(f"IRAN {cb_2} {emoji_cb_2}", callback_data=f'EIPN_{cb_2}')],
    ]
    text = f"<b>Phone number Settings</b>\n\nبا روشن بودن گزینه phone کاربرا باید برای استفاده از ربات شمارشون بفرستن و با روشن بودن گزینه iran فقط کاربرای ایرانی میتونن از امکانات ربات استفاده کنن  \n\n<b>Current</b>\nGet Phone number: {settings['phone']} {emoji}\nOnly Iran phone numbers: {settings['irphone']} {emoji_2} "
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('EWPN_'))
def call_EWPN(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    phone = data.split("EWPN_")[1]
    settings = get_settings()
    settings['phone'] = phone
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='PNS')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('EIPN_'))
def call_EIPN(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    irphone = data.split("EIPN_")[1]
    settings = get_settings()
    settings['irphone'] = irphone
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='PNS')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('XSM'))
def call_XSM(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['seller_custom'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    if settings['select_server_sellers'] == "on":
        emoji_2 = "🟢"
        cb_2 = 'off'
        emoji_cb_2 = "🔴"
    else:
        emoji_2 = "🔴"
        cb_2 = 'on'
        emoji_cb_2 = "🟢"
    keyboard = [
        [InlineKeyboardButton(f"Custom: {cb} {emoji_cb}", callback_data=f'ESM_{cb}')],
        [InlineKeyboardButton(f"Server selection: {cb_2} {emoji_cb_2}", callback_data=f'OSKSC_{cb_2}')],
        [InlineKeyboardButton("لیست قیمت خرید و تمدید اکانت", callback_data='SPBAL')],
        [InlineKeyboardButton("لیست خرید ترافیک", callback_data='SPBTL')],
    ]
    t0 = "\n\nCurrent: " + settings['seller_custom'] + " " + emoji + "\n\nServer selection: " + settings['select_server_sellers'] + " " + emoji_2
    text = '<b>Sellers Settings</b>\n\n' + "با روشن کردن دکمه اولی فروشنده میتونه آزادانه اکانت مورد نظرشو بسازه و نیاز به تایید شما هست.\nبا خاموش بودن این دکمه کاربر باید از لیستی که شما تعیین کردین خرید انجام بده و اتوماتیک از کیف پولش برداشت میشه و نیازی به تایید شما نیست\n\nبا روشن بودن دکمه دوم فروشنده میتونه سرور به دلخواه انتخاب کنه و با خاموش بودن بصورت رندوم سرور انتخاب میشه." + t0
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('OSKSC_'))
def call_OSKSC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    Access = data.split("OSKSC_")[1]
    settings = get_settings()
    settings['select_server_sellers'] = Access
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='XSM')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('ESM_'))
def call_ESM(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    seller_custom = data.split("ESM_")[1]
    settings = get_settings()
    settings['seller_custom'] = seller_custom
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='XSM')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('SPBTL'))
def call_SPBTL(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Delete✖️", callback_data='DeSTPR')],
        [InlineKeyboardButton("Add➕", callback_data='AdSTPR')]
    ]
    settings = get_settings()
    currnet = ""
    for i in range(len(settings['seller_plus_traffic'])):
        currnet += f"{str(i + 1)}. {str(settings['seller_plus_traffic'][i])} گیگابایت - {str(settings['seller_plus_prices'][i])} تومن\n"
    text = '<b>Sellers Traffic Prices Settings</b>\n\n\n' + "Current: \n" + currnet
    keyboard.append([InlineKeyboardButton("<<", callback_data='XSM')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('AdSTPR'))
def call_ASATPR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_collector(chat_id, "S_Traffic_price", [], [])
    delete_cache(chat_id)
    add_cache(chat_id, "S_Traffic_price")
    text = "خب قیمت مورد نظرو بصورت عدد بفرست مثلا : 50000 "
    query.edit_message_text(text=text, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('DeSTPR'))
def call_DeSTPR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if len(settings['seller_plus_traffic']) == 0:
        query.answer("هیچی وجود نداره, تعرفه جدید اد کنین", show_alert=True)
    else:
        keyboard = []
        for i in range(len(settings['seller_plus_traffic'])):
            tcb = f"{str(settings['seller_plus_traffic'][i])} گیگابایت - {str(settings['seller_plus_prices'][i])} تومن"
            cb = "TPSDSEL_" + str(i)
            keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
        keyboard.append([InlineKeyboardButton("<<", callback_data='XSM')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Ok choose to delete:", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('TPSDSEL_'))
def call_TPSDSEL(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    i = int(data.split("TPSDSEL_")[1])
    settings = get_settings()
    prices = settings['seller_plus_prices']
    del prices[i]
    traffic = settings['seller_plus_traffic']
    del traffic[i]
    settings['seller_plus_prices'] = prices
    settings['seller_plus_traffic'] = traffic
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='XSM')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('SPBAL'))
def call_SPBAL(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    delete_cache(chat_id)
    keyboard = [
        [InlineKeyboardButton("Delete✖️", callback_data='DSPR')],
        [InlineKeyboardButton("Add➕", callback_data='ASPR')]
    ]
    settings = get_settings()
    currnet = ""
    for i in range(len(settings['seller_prices'])):
        if settings['seller_traffic'][i] == 0:
            traffic = "نامحدود"
        else:
            traffic = str(settings['seller_traffic'][i]) + " گیگ"
        currnet += f"{str(i + 1)}. {traffic} - {str(settings['seller_connections'][i])} کاربر - {str(settings['seller_days'][i])} روزه - {str(settings['seller_prices'][i])} تومن\n"
    text = '<b>Sellers Prices Settings</b>\n\n' + "Current: \n" + currnet
    keyboard.append([InlineKeyboardButton("<<", callback_data='XSM')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('ASPR'))
def call_ASPR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    add_collector(chat_id, "Sdomain_none", [], [])
    delete_cache(chat_id)
    add_cache(chat_id, "S_price")
    text = "خب قیمت مورد نظرو بصورت عدد بفرست مثلا : 50000 تومن "
    query.edit_message_text(text=text, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('DSPR'))
def call_DSPR(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if len(settings['seller_traffic']) == 0:
        query.answer("هیچی وجود نداره, تعرفه جدید اد کنین", show_alert=True)
    else:
        keyboard = []
        for i in range(len(settings['seller_prices'])):
            if settings['seller_traffic'][i] == 0:
                traffic = "نامحدود"
            else:
                traffic = str(settings['seller_traffic'][i]) + " گیگ"
            tcb = f"{traffic} - {str(settings['seller_connections'][i])} کاربر - {str(settings['seller_days'][i])} روزه - {str(settings['seller_prices'][i])} تومن"
            cb = "DelSELP_" + str(i)
            keyboard.append([InlineKeyboardButton(tcb, callback_data=cb)])
        keyboard.append([InlineKeyboardButton("<<", callback_data='XSM')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Ok choose to delete:", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('DelSELP_'))
def call_DelSELP(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    i = int(data.split("DelSELP_")[1])
    settings = get_settings()
    prices = settings['seller_prices']
    del prices[i]
    connections = settings['seller_connections']
    del connections[i]
    days = settings['seller_days']
    del days[i]
    traffic = settings['seller_traffic']
    del traffic[i]
    settings['seller_prices'] = prices
    settings['seller_connections'] = connections
    settings['seller_days'] = days
    settings['seller_traffic'] = traffic
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='XSM')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('RWUAD'))
def call_RWUAD(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    settings = get_settings()
    if settings['delete_user'] == "on":
        emoji = "🟢"
        cb = 'off'
        emoji_cb = "🔴"
    else:
        emoji = "🔴"
        cb = 'on'
        emoji_cb = "🟢"
    if settings['select_server_users'] == "on":
        emoji_2 = "🟢"
        cb_2 = 'off'
        emoji_cb_2 = "🔴"
    else:
        emoji_2 = "🔴"
        cb_2 = 'on'
        emoji_cb_2 = "🟢"
    if settings['dropbear'] == "on":
        emoji_3 = "🟢"
        cb_3 = 'off'
        emoji_cb_3 = "🔴"
    else:
        emoji_3 = "🔴"
        cb_3 = 'on'
        emoji_cb_3 = "🟢"
    keyboard = [
        [InlineKeyboardButton(f"Delete: {cb} {emoji_cb}", callback_data=f'JDOSSK_{cb}')],
        [InlineKeyboardButton(f"Server selection: {cb_2} {emoji_cb_2}", callback_data=f'CJSLC_{cb_2}')],
        [InlineKeyboardButton(f"Dropbear Port: {cb_3} {emoji_cb_3}", callback_data=f'Dropbear_{cb_3}')]
    ]
    t0 = "\n\nCurrent: \nDelete by user: " + settings['delete_user'] + " " + emoji + "\nServer selection: " + settings['select_server_users'] + " " + emoji_2 + "\nDropbear Port: " + settings['dropbear'] + " " + emoji_3
    text = '<b>Users Access Settings</b>\n\n' + "با گزینه اول میتونین دسترسی کاربر برای دلیت اکانت محدود کنین که خاموش باشه دکمه حذف اکانت برای کاربر نمایش داده نمیشه و نمیتونه حذف کنه اکانت خودشو و اگه روشن باشه میتونه اینکارو انجام بده\n\nگزینه دوم اگه روشن باشه کاربر میتونه سرور دلبخواه رو انتخاب کنه و اگه خاموش باشه بصورت رندوم بهش داده میشه (هیچ آدرسی فرستاده نمیشه قبل خرید)\n\nگزینه سوم برای پورت دراپ بیر هست که اگه روشن باشه پورت دراپ بیر برای کاربر میفرسته" + t0
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('Dropbear_'))
def call_Dropbear(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    Dropbear = data.split("Dropbear_")[1]
    settings = get_settings()
    settings['dropbear'] = Dropbear
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='RWUAD')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('CJSLC_'))
def call_CJSLC(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    Access = data.split("CJSLC_")[1]
    settings = get_settings()
    settings['select_server_users'] = Access
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='RWUAD')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('JDOSSK_'))
def call_JDOSSK(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    data = query.data
    Access = data.split("JDOSSK_")[1]
    settings = get_settings()
    settings['delete_user'] = Access
    update_settings(settings)
    keyboard = [[InlineKeyboardButton("<<", callback_data='RWUAD')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Done✔️", reply_markup=reply_markup)


@app.on_callback_query(filters.regex('HOW'))
def call_HOW(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = []
    text = '<b>How to use?</b>\n\nبرای اینکه یه کاربر سریعتر مدیریت کنین کافیه کپی کانفیگی که داخل پنل زده بودین و به کاربر فرستادینو مستقیم به ربات بفرستین:\n\nSSH Host: domain\nUsername : username\n\n\nبرای درست کردن لیست قیمت کافیه دکمه قیمت ها رو بزنین\n\nکانال ربات :/n@delta_bcc\nگروه رفع باگ و سوالا:\n@deltabots_gp'
    keyboard.append([InlineKeyboardButton("<<", callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('settings'))
def call_settings(bot, query):
    chat_id = query.message.chat.id
    if chat_id not in admin_id:
        query.answer("Access denied", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("🛒تنظیمات خرید ", callback_data='ZBSHP'), InlineKeyboardButton("تنظیم دسترسی 🔐", callback_data='RWUAD')],
        [InlineKeyboardButton("💲 تنظیمات فروشنده ها", callback_data='XSM')],
        [InlineKeyboardButton("📃پیام استارت", callback_data='WSMSG'), InlineKeyboardButton("🏷 پیام تعرفه قیمت", callback_data='WLMSG')],
        [InlineKeyboardButton("❔ بخش آموزش کاربر", callback_data='Tutorials'), InlineKeyboardButton("📩 تنظیم پشتیبانی", callback_data='SID')],
        [InlineKeyboardButton("🗑حذف خودکار کاربر", callback_data='AutoDelete'), InlineKeyboardButton("💲قیمت دلار", callback_data='USD')],
        [InlineKeyboardButton("📢اسپانسر", callback_data='sponser'), InlineKeyboardButton("📡پروکسی", callback_data='Sprx')],
        [InlineKeyboardButton("🌐چکر فیلترینگ", callback_data='FILCH'), InlineKeyboardButton("📥بکاپ", callback_data='Backup')],
        [InlineKeyboardButton("🆘راهنما", callback_data='HOW'), InlineKeyboardButton("🎁دعوت کاربر", callback_data='INVS')],
        [InlineKeyboardButton("🆓 اکانت تست ", callback_data='TASET'), InlineKeyboardButton("📞شماره تلفن", callback_data='PNS')],
        [InlineKeyboardButton("ℹ️ چکر و اطلاع رسانی حجم و تاریخ به کاربر", callback_data='NUSYS')],
        [InlineKeyboardButton("👤محدودیت تعداد کاربر در هر سرور", callback_data='maximum')]
    ]
    keyboard.append([InlineKeyboardButton("<<", callback_data='back_admin')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '<b>تنظیمات 🔧</b>'
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.private & filters.contact)
def contact_update(bot, message):
    chat_id = message.chat.id
    phone_number = str(message.contact.phone_number)
    if chat_id == message.contact.user_id:
        if (get_settings()['irphone'] == 'on'):
            if ("+98" in phone_number) or ("+ 98" in phone_number) or (phone_number[0:3] == "+98"):
                message.reply_text("‎✅", reply_markup=ReplyKeyboardRemove())
                message.reply_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)
                if check_user_phone_exist(chat_id) is False:
                    update_phone_number(chat_id, phone_number)
            else:
                message.reply_text("فقط شماره های ایران مورد قبول هست", reply_markup=ReplyKeyboardRemove())
        else:
            message.reply_text("‎✅", reply_markup=ReplyKeyboardRemove())
            message.reply_text((get_settings())['start'], reply_markup=User_Tools_keys(), parse_mode=enums.ParseMode.HTML)
            if check_user_phone_exist(chat_id) is False:
                update_phone_number(chat_id, phone_number)
    else:
        message.reply_text("شماره فرستاده شده برای اکانت شما نیست!")


@app.on_message(filters.chat(admin_id) & filters.voice)
def admin_voice(bot, message):
    chat_id = message.chat.id
    if check_cache(chat_id) is True:
        file_id = message.voice.file_id
        try:
            caption = message.caption
        except:
            caption = None
        status = get_cache_status(chat_id)
        if status == "message":
            delete_cache(chat_id)
            msg = message.reply_text("Sending...").id
            fname = "All.txt"
            sent = 0
            with open(fname, 'r') as f:
                for usertxt in f:
                    try:
                        if caption is None:
                            bot.send_voice(int(usertxt.replace('\n', '')), file_id)
                        else:
                            bot.send_voice(int(usertxt.replace('\n', '')), file_id, caption=caption)
                        sent += 1
                    except:
                        continue
            bot.send_message(chat_id, f"sent to {str(sent)} users")
            bot.delete_messages(chat_id, msg)


@app.on_message(filters.chat(admin_id) & filters.video)
def admin_video(bot, message):
    chat_id = message.chat.id
    if check_cache(chat_id) is True:
        file_id = message.video.file_id
        try:
            caption = message.caption
        except:
            caption = None
        status = get_cache_status(chat_id)
        if status == "message":
            delete_cache(chat_id)
            msg = message.reply_text("Sending...").id
            fname = "All.txt"
            sent = 0
            with open(fname, 'r') as f:
                for usertxt in f:
                    try:
                        if caption is None:
                            bot.send_video(int(usertxt.replace('\n', '')), file_id)
                        else:
                            bot.send_video(int(usertxt.replace('\n', '')), file_id, caption=caption)
                        sent += 1
                    except:
                        continue
            bot.send_message(chat_id, f"sent to {str(sent)} users")
            bot.delete_messages(chat_id, msg)


@app.on_message(filters.chat(admin_id) & filters.document)
def admin_document(bot, message):
    chat_id = message.chat.id
    if check_cache(chat_id) is True:
        file_id = message.document.file_id
        try:
            caption = message.caption
        except:
            caption = None
        status = get_cache_status(chat_id)
        if status == "message":
            delete_cache(chat_id)
            msg = message.reply_text("Sending...").id
            fname = "All.txt"
            sent = 0
            with open(fname, 'r') as f:
                for usertxt in f:
                    try:
                        if caption is None:
                            bot.send_document(int(usertxt.replace('\n', '')), file_id)
                        else:
                            bot.send_document(int(usertxt.replace('\n', '')), file_id, caption=caption)
                        sent += 1
                    except:
                        continue
            bot.send_message(chat_id, f"sent to {str(sent)} users")
            bot.delete_messages(chat_id, msg)

        elif status == "upload_panels":
            if message.document.file_name == "Pannels.txt":
                try:
                    message.download("/root/bot/Pannels-backup.txt")
                    if Path("Pannels-backup.txt").is_file() is True:
                        os.remove("Pannels.txt")
                        os.rename("Pannels-backup.txt", "Pannels.txt")
                        delete_cache(chat_id)
                        add_cache(chat_id, "upload_All")
                        message.reply_text("حالا فایل All.txt رو بفرستین:")
                    else:
                        message.reply_text("🔴Error: incorrect file path")
                        delete_cache(chat_id)
                except Exception as e:
                    message.reply_text(f"Error: {str(e)}")
                    delete_cache(chat_id)
            else:
                message.reply_text("این فایل اشتباست ")

        elif status == "upload_All":
            if message.document.file_name == "All.txt":
                try:
                    message.download("/root/bot/All-backup.txt")
                    if Path("All-backup.txt").is_file() is True:
                        os.remove("All.txt")
                        os.rename("All-backup.txt", "All.txt")
                        delete_cache(chat_id)
                        add_cache(chat_id, "upload_db")
                        message.reply_text("حالا فایل ssh.db رو بفرستین:")
                    else:
                        message.reply_text("🔴Error: incorrect file path")
                        delete_cache(chat_id)
                except Exception as e:
                    message.reply_text(f"Error: {str(e)}")
                    delete_cache(chat_id)
            else:
                message.reply_text("این فایل اشتباست ")

        elif status == "upload_db":
            if message.document.file_name == "ssh.db":
                try:
                    message.download("/root/bot/backup.db")
                    if Path("backup.db").is_file() is True:
                        message.reply_text("خب حالا وارد سرور ربات بشین و دوباره دستور نصب بزنین تا مرحله بکاپ تموم شه")
                    else:
                        message.reply_text("🔴Error: incorrect file path")
                except Exception as e:
                    message.reply_text(f"Error: {str(e)}")
                delete_cache(chat_id)
            else:
                message.reply_text("این فایل اشتباست ")


@app.on_message(filters.private & filters.photo)
def image_users(bot, message):
    chat_id = message.chat.id
    if check_cache(chat_id) is True:
        status = get_cache_status(chat_id)
        msg_id = message.id
        if (status == "message") and (chat_id in admin_id):
            file_id = message.photo.file_id
            try:
                caption = message.caption
            except:
                caption = None
            delete_cache(chat_id)
            msg = message.reply_text("Sending...").id
            fname = "All.txt"
            sent = 0
            with open(fname, 'r') as f:
                for usertxt in f:
                    try:
                        if caption is None:
                            bot.send_photo(int(usertxt.replace('\n', '')), file_id)
                        else:
                            bot.send_photo(int(usertxt.replace('\n', '')), file_id, caption=caption)
                        sent += 1
                    except:
                        continue
            bot.send_message(chat_id, f"sent to {str(sent)} users")
            bot.delete_messages(chat_id, msg)

        elif "support" in status:
            n = int(status.split("support ")[1])
            bot.forward_messages(admin_id[n], chat_id, msg_id)
            name = message.from_user.first_name
            try:
                username = "@" + message.from_user.username
            except:
                username = 'Null'
            text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username
            keyboard = [[InlineKeyboardButton("پاسخ به " + name, callback_data='ANS_' + str(chat_id))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(admin_id[n], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            sleep(0.2)
            message.reply_text(text='بزودی درخواستتون بررسی میکنیم🫡', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data="back")]]))

        elif status == "buy":
            name = message.from_user.first_name
            try:
                username = "@" + message.from_user.username
            except:
                username = 'Null'
            code, cache_list = get_code_buy_info(chat_id, "add")
            delete_all_buy(chat_id, "add")
            add_code_buy(chat_id, code, "add", cache_list)
            t1 = f"server: {cache_list[6]}\nuser: {cache_list[5]}\ndays: {cache_list[0]}\nGB: {cache_list[1]}\nConnection: {cache_list[2]}\nprice: {cache_list[3]} Toman"
            text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\nاطلاعات خرید اکانت\n" + t1
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
            message.reply_text(text='بزودی درخواستتون بررسی میکنیم🫡', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data="back")]]))

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
            text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\nاطلاعات تمدید:\n" + t1
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
            message.reply_text(text='بزودی درخواستتون بررسی میکنیم🫡', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data="back")]]))

        elif status == "traffic":
            name = message.from_user.first_name
            try:
                username = "@" + message.from_user.username
            except:
                username = 'Null'
            code, cache_list = get_code_buy_info(chat_id, "traffic")
            delete_all_buy(chat_id, "traffic")
            add_code_buy(chat_id, code, "traffic", cache_list)
            t1 = f"🔄افزایش ترافیک\n\nGB: {cache_list[0]}\nprice: {cache_list[1]} Toman\nHost: {cache_list[3]}\nUser: {cache_list[2]}"
            text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\nاطلاعات تمدید:\n" + t1
            cb = "ConfirmTraffic_" + code
            no = "NO❌_" + code
            keyboard = [[InlineKeyboardButton("Confirm✅", callback_data=cb), InlineKeyboardButton("NO❌", callback_data=no)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            for i in range(len(admin_id)):
                try:
                    bot.forward_messages(admin_id[i], chat_id, msg_id)
                    bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                except:
                    pass
            update_code_status(code, "checktraffic")
            message.reply_text(text='بزودی درخواستتون بررسی میکنیم🫡', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data="back")]]))

        elif status == "userdeposit":
            name = message.from_user.first_name
            try:
                username = "@" + message.from_user.username
            except:
                username = 'Null'
            code, cache_list = get_code_buy_info(chat_id, "userdeposit")
            delete_all_buy(chat_id, "userdeposit")
            add_code_buy(chat_id, code, "userdeposit", cache_list)
            t1 = f"💰افزایش موجودی کیف پول\n\nPrice: {cache_list[0]}"
            text = "id: <pre>" + str(chat_id) + "</pre>\nName: " + name + '\nUsername: ' + username + "\n\nاطلاعات خرید:\n" + t1
            cb = "ConfirmDeposit_" + code
            no = "NO❌_" + code
            keyboard = [[InlineKeyboardButton("Confirm✅", callback_data=cb), InlineKeyboardButton("NO❌", callback_data=no)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            for i in range(len(admin_id)):
                try:
                    bot.forward_messages(admin_id[i], chat_id, msg_id)
                    bot.send_message(admin_id[i], text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                except:
                    pass
            update_code_status(code, "checkdeposit")
            message.reply_text(text='بزودی درخواستتون بررسی میکنیم🫡', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data="back")]]))

        delete_cache(chat_id)

app.run()
