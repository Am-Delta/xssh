import sshx
from pathlib import Path
from os import remove
from time import sleep
from datetime import datetime

sleeper = 600

if Path('logs.txt').is_file() is True:
    remove('logs.txt')


def main():
    with open('logs.txt', 'a+') as logs:
        hosts = sshx.HOSTS()
        for host in hosts:
            port, username, password, panel, route_path, sshport, udgpw = sshx.HOST_INFO(host)
            do = True
            session = 'ssh/' + host + ".session"
            if Path(session).is_file() is False:
                if sshx.Login(username, password, host, port, panel) is False:
                    do = False
            if do is True:
                try:
                    url, r = sshx.open_session(host, port)
                    if sshx.Test(r, host, port, panel, 'updater') is False:
                        remove(session)
                        print(sshx.Login(username, password, host, port, panel))
                        logs.writelines("[+] Login: " + host + "  " + panel + "  " + str(datetime.now()) + "\n")
                except Exception as e:
                    logs.writelines("[-] Error: " + str(e) + "    " + str(datetime.now()) + "\n")
            else:
                logs.writelines("[-] Error: " + str(e) + "    " + str(datetime.now()) + "\n")

while True:
    main()
    sleep(sleeper)
