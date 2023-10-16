import sshx
from pathlib import Path
from os import remove
from time import sleep
from datetime import datetime
from random import randint

if Path('logs.txt').is_file() is True:
    remove('logs.txt')


def main():
    with open('logs.txt', 'a+') as logs:
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
                    url, r = sshx.open_session(host, port)
                    if sshx.Test(r, host, port, panel, 'updater') is False:
                        sshx.Login(username, password, host, port, panel)
                        if Path(session).is_file() is False:
                            remove(session)
                        logs.writelines("[+] Login: " + host + "  " + panel + "  " + str(datetime.now()) + "\n")
                except Exception as e:
                    logs.writelines("[-] Session Error: " + str(e) + "    " + str(datetime.now()) + "\n")
            else:
                logs.writelines("[-] Session Error: " + str(e) + "    " + str(datetime.now()) + "\n")

while True:
    main()
    sleep(randint(300, 600))
