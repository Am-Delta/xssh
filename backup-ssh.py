import sshx
from os import makedirs, remove
from time import sleep
from pathlib import Path

folder = 'backup'
sleeper = 3600 * 6

try:
    makedirs(folder)
except:
    pass

#host@username:passwd   <------------------------------------ #


def main():
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
                    Session = sshx.PANNEL(host, username, password, 'Other', 'uname')
                    status, content = Session.Backup_content()
                    if status is True:
                        f = folder + "/" + host + ".sql"
                        if Path(f).is_file() is True:
                            remove(f)
                        with open(f, 'wb') as file:
                            file.write(content)
                        sleep(1)
                    else:
                        print("[-] Error: " + content + " | " + host)
                except Exception as e:
                    print("[-] Error: " + str(e) + " | " + host)
            else:
                print("[-] Error To Login: " + host)


while True:
    main()
    sleep(sleeper)
