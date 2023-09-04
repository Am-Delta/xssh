import os
import re
import json
import sqlite3
from termcolor import colored
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
    settings = json.loads(s)
    if settings.get('proxy', None) is None:
        add_dict = {
            "plus-traffic": [10, 20],
            "plus-prices": [20000, 35000],
            "proxy": "None"
        }
        settings.update(add_dict)
        cur.execute("UPDATE Settings SET settings = ? WHERE ID =?", (str(settings), 1))
        conn.commit()
    conn.commit()
    cur.close()
    conn.close()


def run():
    if Path("Pannels.txt").is_file() is False:
        open("Pannels.txt", "w")
    if Path("All.txt").is_file() is False:
        with open("All.txt", "a+") as f:
            f.writelines("1" + "\n")
    if Path("ssh.db").is_file() is False:
        os.system('python3 sshdb.py')
        print("Database Created, change the settings in the bot")
    db_update()
    print(colored("\nRunning the bot... if you see any issues run the command again.\n\nif you want stop to the bot use this command:\n\npkill -9 python3 or pkill -9 python\n\nYou can now close the window.", 'white'))
    os.system('nohup python3 session-updater.py &')
    os.system('nohup python3 backup-ssh.py &')
    os.system('nohup python3 bot.py &')


def settings():
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

    print(colored("\nif you want send your api_id or (default: n)", 'white'))
    while True:
        data = input(": ")
        if data == "n" or data == "":
            api_id = "24467048"
            api_hash = "7e81e7df9b9b66deab287cb47bbc6d8a"
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
    print(colored("\nBot Token: ", 'white'))
    Token = input("")

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
        settings()
        run()
    else:
        run()
else:
    settings()
    run()
