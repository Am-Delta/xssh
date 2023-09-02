import requests, pickle
import json
import os
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
from datetime import datetime
from time import time
from uuid import uuid4


#just for this PC
proxy = {'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'}


def open_session(host):
    r = requests.session()
    session = "ssh/" + host + ".session"
    with open(session, 'rb') as f:
        r.cookies.update(pickle.load(f))
    url = "http://" + host
    return url, r


def Login(username, password, host):
    data = {'username': username, 'password': password, "loginsubmit": ""}
    r = requests.session()
    session = "ssh/" + host + ".session"
    try:
        with open(session, 'wb') as f:
            responde = r.post(f"http://{host}/p/login.php", data=data)
            pickle.dump(r.cookies, f)
            if responde.status_code <= 302:
                print(f"Login and saved session at ssh/{host}.session | Code: ", responde.status_code)
            else:
                print("Error : ", responde.status_code)
                return False
        return True
    except Exception as e:
        print(e)
        return False
    r.close()


def Get_user_info(html, uname):
    connection_limits = []
    usernames = []
    passwords = []
    traffics = []
    days_left = []
    for data in html.css('td'):
        if 'روز' in data.text():
            if 'گذشته' in data.text():
                days_left.append('-' + (data.text()).split("روز")[0])
            else:
                days_left.append((data.text()).split("روز")[0])
        alt = data.attributes.get("name", None)
        if alt is not None:
            if 'multilogin' in data.attributes['name']:
                connection_limits.append(data.text())
            if 'username' in data.attributes['name']:
                usernames.append(data.text())
            if 'password' in data.attributes['name']:
                passwords.append(data.text())
            if 'traffic' in data.attributes['name']:
                traffics.append(data.text())
    status = []
    for a in html.css('a'):
        href = a.attributes.get("href", None)
        if href is not None:
            if "index.php?sortby=" in href:
                status.append(a.text())
    del status[:4]
    usages = []
    for a in html.css('a.pull-left'):
        if "/" in a.text():
            usages.append((a.text()).split(" /")[0])
        elif ("گیگابایت" in a.text()) or ("نامحدود" in a.text()):
            usages.append('0.0')
    for username in usernames:
        if username == uname:
            n = usernames.index(uname)
            return passwords[n], traffics[n], int(connection_limits[n]), days_left[n], status[n], usages[n]


def Get_list(html):
    expires = []
    connection_limits = []
    usernames = []
    passwords = []
    ports = []
    traffics = []
    usages = []
    days_left = []
    status = []
    server_traffic = 0
    online_clients = 0
    for setr in html.css('small.pull-left'):
        if "گیگابایت" in setr.text():
            server_traffic = float(((setr.text()).split("گیگابایت")[0]).replace(" ", ''))
            break
        elif "ترابایت" in setr.text():
            server_traffic = float(((setr.text()).split("ترابایت")[0]).replace(" ", '')) * 1024
            break
    for data in html.css('td'):
        if 'روز' in data.text():
            if 'گذشته' in data.text():
                days_left.append('-' + (data.text()).split("روز")[0])
            else:
                days_left.append((data.text()).split("روز")[0])
        alt = data.attributes.get("name", None)
        if alt is not None:
            if 'expire' in data.attributes['name']:
                expires.append(data.text())
            if 'multilogin' in data.attributes['name']:
                connection_limits.append(data.text())
            if 'username' in data.attributes['name']:
                usernames.append(data.text())
            if 'password' in data.attributes['name']:
                passwords.append(data.text())
            if 'port' in data.attributes['name']:
                if (data.attributes['name']).split("port")[0] != "udp":
                    ports.append(data.text())
            if 'traffic' in data.attributes['name']:
                traffics.append(data.text())
    for a in html.css('a.pull-left'):
        if "/" in a.text():
            usages.append((a.text()).split(" /")[0])
        elif ("گیگابایت" in a.text()) or ("نامحدود" in a.text()):
            usages.append('0.0')
    for a in html.css('a'):
        href = a.attributes.get("href", None)
        if href is not None:
            if "index.php?sortby=" in href:
                status.append(a.text())
    del status[:4]
    info = []
    for data in html.css('span.info-box-number'):
        info.append((data.text()).replace(" کاربر", ""))
    return expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, server_traffic, int(info[1]), True


class PANNEL:
    def __init__(self, host, username, password, job, uname):
        self.host = host
        self.username = username
        self.password = password
        self.url, self.r = open_session(host)
        '''s = self.r.get(self.url + "/p/index.php").text
        html = HTMLParser(s)
        for a in html.css('a'):
            href = a.attributes.get("href", None)
            if href is not None:
                if "login.php" in href:
                    os.remove("ssh/" + host + ".session")
                    print(Login(username, password, host))
                    self.url, self.r = open_session(host)'''
        if job == 'User':
            self.uname = uname
            s = self.r.get(self.url + "/p/index.php").text
            html = HTMLParser(s)
            self.req = self.url + "/p/newuser.php"
            self.passwd, self.traffic, self.connection_limit, self.days, self.status, self.usage = Get_user_info(html, uname)

    def Ports(self):
        s = self.r.get(self.url + "/p/setting.php").text
        html = HTMLParser(s)
        for inp in html.css('input'):
            alt = inp.attributes.get("name", None)
            if alt is not None:
                if 'port' == inp.attributes['name']:
                    return inp.attributes['value']
        return port

    def Backup_content(self):
        try:
            s = self.r.get(self.url + "/p/setting.php").text
            html = BeautifulSoup(s, 'html.parser')
            urls = []
            for a in html.find_all('a', href=True):
                if ("/p/backup/" in a['href']) and ("20" in a['href']):
                    urls.append(a['href'])
            for delete in urls:
                file = delete.split('/p/backup/')[1]
                payload = {"delete": file}
                self.r.get(self.url + "/p/setting.php?delete=" + file, data=payload)
            dt = (str(datetime.fromtimestamp(time()))).split(' ')[0]
            date = dt + "-554"
            payload = {"backupfull": date}
            self.r.get(self.url + "/p/setting.php?backupfull=" + date, data=payload).text
            s = self.r.get(self.url + "/p/setting.php").text
            html = BeautifulSoup(s, 'html.parser')
            urls = []
            for a in html.find_all('a', href=True):
                if ("/p/backup/" in a['href']) and ("20" in a['href']):
                    urls.append(a['href'])
            rec = self.r.get(self.url + urls[0]).content
            return True, rec
        except Exception as e:
            return False, str(e)

    def Check(self):
        s = self.r.get(self.url + "/p/index.php").text
        html = HTMLParser(s)
        info = []
        for data in html.css('span.info-box-number'):
            info.append(data.text())
        count = 0
        for h3 in html.css('h3.profile-username'):
            count += 1 if "" != h3.text() else 0
        print("over view: ", info[0])
        print("All available: ", count)

    def Backup(self):
        f = uuid4().hex[0:8] + ".sql"
        try:
            with open(f, 'wb') as file:
                status, rec = Backup_content()
                file.write(rec)
            return True, f
        except Exception as e:
            return False, str(e)

    def Short_info(self):
        try:
            s = self.r.get(self.url + "/p/index.php").text
            html = HTMLParser(s)
            server_traffic = 0
            for setr in html.css('small.pull-left'):
                if "گیگابایت" in setr.text():
                    server_traffic = float(((setr.text()).split("گیگابایت")[0]).replace(" ", ''))
                    break
                elif "ترابایت" in setr.text():
                    server_traffic = float(((setr.text()).split("ترابایت")[0]).replace(" ", '')) * 1024
                    break
            info = []
            for data in html.css('span.info-box-number'):
                info.append(data.text())
            text = f"🖥Host: {self.host}\n🔃Traffic: {str('{:.2f}'.format(float(server_traffic)))} GB\n👤Clients: {str(info[0])}\n✔️Active: {str(info[2])}\n🔴Disabled: {str(info[3])}\n🟢Online: {str(info[1])}"
            return text
        except Exception as e:
            return "Error: " + str(e)

    def Count_Clients(self):
        try:
            s = self.r.get(self.url + "/p/index.php").text
            html = HTMLParser(s)
            info = []
            for data in html.css('span.info-box-number'):
                info.append(data.text())
            return str(info[0])
        except Exception as e:
            return "Error: " + str(e)

    def info(self):
        try:
            s = self.r.get(self.url + "/p/index.php").text
            html = HTMLParser(s)
            return Get_list(html)
        except Exception as e:
            print("Error: " + str(e))
            return [], [], [], [], [], [], [], [], [], [], 0, False

    def Delete(self, uname):
        payload = {
            'edituserusername': uname,
            'delusersubmit': 'submitted H a m e d A p'
        }
        try:
            s = self.r.post(self.url + "/p/newuser.php", data=payload)
            if s.status_code == 200:
                return "❌Deleted"
            else:
                return "Error: 404 HTTP"
        except Exception as e:
            return "Error: " + str(e)

    def Create(self, uname, passw, connection_limit, days, traffic):
        if traffic == 0:
            traffic = ""
        payload = {
            'newuserusername': uname,
            'newuserpassword': passw,
            'newusermobile': '',
            'newuseremail': '',
            'newusertraffic': traffic,
            'newusermultiuser': connection_limit,
            'newuserfinishdate': days,
            'newuserreferral': '',
            'newusertelegramid': '',
            'newuserinfo': '',
            'newusersubmit': 'ثبت'
        }
        try:
            s = self.r.post(self.url + "/p/newuser.php", data=payload)
            if s.status_code == 200:
                if traffic == '':
                    traffic = "Unlimited♾"
                #port = self.Ports()
                port = "22"
                return f"SSH Host : {self.host}\nPort : {port}\nUdgpw : 7301-7309\nUsername : {uname}\nPassword : {passw}\n\nConnection limit: {str(connection_limit)}\nDays : {str(days)}\nTraffic: {str(traffic)}"
        except Exception as e:
            return "Error: " + str(e)

    def Update(self, traffic, days, connection_limit):
        if traffic == 0:
            traffic = ''
        payload = {
            'edituserusername': self.uname,
            'edituserpassword': self.passwd,
            'editusermobile': '',
            'edituseremail': '',
            'editusertraffic': traffic,
            'editusermultiuser': connection_limit,
            'edituserfinishdate': days,
            'edituserreferral': '',
            'edituserinfo': '',
            'editusersubmit': 'ثبت'
        }
        try:
            if self.r.post(self.req, data=payload).status_code == 200:
                payload = {'edituserusername': self.uname, 'edituserpassword': self.passwd, 'activeusersubmit': 'submitted H a m e d A p'}
                if self.r.post(self.req, data=payload).status_code == 200:
                    return "🟢Updated successfully and Activated successfully"
                else:
                    return "Error: Updated but not activated"
            else:
                return "Error: 404 HTTP"
        except Exception as e:
            return "Error: " + str(e)

    def Reset_traffic(self):
        payload = {'edituserusername': self.uname, 'resettrafficsubmit': 'submitted H a m e d A p'}
        try:
            if self.r.post(self.req, data=payload).status_code == 200:
                return "🟢Reseted successfully"
            else:
                return "Error: 404 HTTP"
        except Exception as e:
            return "Error: " + str(e)

    def Enable(self):
        if "فعال" != self.status:
            payload = {'edituserusername': self.uname, 'edituserpassword': self.passwd, 'activeusersubmit': 'submitted H a m e d A p'}
            try:
                if self.r.post(self.req, data=payload).status_code == 200:
                    return "🟢 Enabled successfully"
                else:
                    return "Error: 404 HTTP"
            except Exception as e:
                return "Error: " + str(e)
        else:
            return "🟢 Already Enabled"

    def Disable(self):
        if "فعال" == self.status:
            payload = {'edituserusername': self.uname, 'edituserpassword': self.passwd, 'deactiveusersubmit': 'submitted H a m e d A p'}
            try:
                if self.r.post(self.req, data=payload).status_code == 200:
                    return "🔴 Disabled successfully"
                else:
                    return "Error: 404 HTTP"
            except Exception as e:
                return "Error: " + str(e)
        else:
            return "🔴 Already Disabled"

    def User_info(self):
        try:
            port = self.Ports()
            usage = self.usage + " GB"
            status = self.status
            if "فعال" == status:
                status += "🟢"
            else:
                status += "🔴"
            return f"SSH Host : {self.host}\nPort : {port}\nUdgpw : 7301-7309\nUsername : {self.uname}\nPassword : {self.passwd}\n\nConnection limit: {str(self.connection_limit)}\nDays : {str(self.days)}\nTraffic: {str(self.traffic)}\nUsage: {str(usage)}\nStatus: {status}"
        except Exception as e:
            return "Error: " + str(e)

    def Update_Traffic(self, traffic):
        if traffic == 0:
            traffic = ''
        payload = {
            'edituserusername': self.uname,
            'edituserpassword': self.passwd,
            'editusermobile': '',
            'edituseremail': '',
            'editusertraffic': traffic,
            'editusermultiuser': self.connection_limit,
            'edituserfinishdate': self.days,
            'edituserreferral': '',
            'edituserinfo': '',
            'editusersubmit': 'ثبت'
        }
        try:
            if self.r.post(self.req, data=payload).status_code == 200:
                return "Updated"
            else:
                return "Error: 404 HTTP"
        except Exception as e:
            return "Error: " + str(e)
