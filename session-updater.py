import os
import sshx
import psutil
from pathlib import Path
from time import sleep
from datetime import datetime
from random import randint


if Path('logs.txt').is_file() is True:
    os.remove('logs.txt')


def bot_checker():
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            if "python" in p.name():
                if "bot.py" in p.cmdline():
                    return
        except:
            pass
    os.system("nohup python3 -u bot.py &")


def main():
    bot_checker()
    with open('logs.txt', 'a+') as logs:
        hosts, remarks = sshx.HOSTS()
        for host in hosts:
            port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
            if panel not in ['dragon']:
                do = True
                session = 'ssh/' + host + ".session"
                if Path(session).is_file() is False:
                    if sshx.Login(username, password, host, port, panel) is False:
                        do = False
                elif os.stat(session).st_size == 0:
                    os.remove(session)
                    if sshx.Login(username, password, host, port, panel) is False:
                        do = False
                if (Path("protocol-cache.txt").is_file() is False) or (sshx.get_protocol_cache(host) is None):
                    protocol = sshx.check_panel_protocol(host)
                    sshx.add_protocol_cache(host, protocol)
                if do is True:
                    for i in range(3):
                        try:
                            protocol_cache = sshx.get_protocol_cache(host)
                            protocol_check = sshx.check_panel_protocol(host)
                            if protocol_check != protocol_cache:
                                sshx.remove_protocol_cache(host)
                                sshx.add_protocol_cache(host, protocol_check)
                            url, r = sshx.open_session(host, port)
                            if sshx.Test(r, host, port, panel, 'updater') is False:
                                sshx.Login(username, password, host, port, panel)
                                logs.writelines("[+] Login: " + host + "  " + panel + "  " + str(datetime.now()) + "\n")
                            break
                        except Exception as e:
                            sleep(2)
                            if i == 2:
                                logs.writelines("[-] Session Error: " + str(e) + "    " + str(datetime.now()) + "\n")
                else:
                    logs.writelines("[-] Login Error: " + host + "    " + str(datetime.now()) + "\n")

while True:
    main()
    sleep(randint(120, 360))
