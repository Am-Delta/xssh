import os
import sshx
from time import sleep
from pathlib import Path

folder = 'backup'
sleeper = 3600 * 6

if os.path.isdir(folder) is False:
    os.makedirs(folder)


def main():
    hosts, remarks = sshx.HOSTS()
    for host in hosts:
        port, username, password, panel, route_path, sshport, udgpw, remark = sshx.HOST_INFO(host)
        try:
            Session = sshx.PANNEL(host, username, password, port, panel, 'Other', 'uname')
            status, content = Session.Backup_content()
            if status is True:
                if panel in ['dragon']:
                    f = folder + "/" + host + ".vps"
                else:
                    f = folder + "/" + host + ".sql"
                if Path(f).is_file() is True:
                    os.remove(f)
                with open(f, 'wb') as file:
                    file.write(content)
            else:
                print("[-] Backup Error: " + content + " | " + host)
        except Exception as e:
            print("[-] Backup Error: " + str(e) + " | " + host)
while True:
    main()
    sleep(sleeper)
