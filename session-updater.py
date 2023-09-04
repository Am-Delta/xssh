import sshx
from pathlib import Path
from os import remove
from selectolax.parser import HTMLParser
from time import sleep
from datetime import datetime

sleeper = 600


if Path('logs.txt').is_file() is True:
    remove('logs.txt')


def main():
    with open('logs.txt', 'a+') as logs:
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
                    try:
                        url, r = sshx.open_session(host)
                        s = r.get(url + "/p/index.php").text
                        html = HTMLParser(s)
                        for a in html.css('a'):
                            href = a.attributes.get("href", None)
                            if href is not None:
                                if "login.php" in href:
                                    remove(session)
                                    print(sshx.Login(username, password, host))
                                    logs.writelines("[+] Login: " + host + "    " + str(datetime.now()) + "\n")
                    except Exception as e:
                        logs.writelines("[-] Error: " + str(e) + "    " + str(datetime.now()) + "\n")
                else:
                    logs.writelines("[-] Error: " + str(e) + "    " + str(datetime.now()) + "\n")

while True:
    main()
    sleep(sleeper)
