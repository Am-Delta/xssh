import requests, pickle
import json
import os
import re
import ast
import paramiko
import ipaddress
import jdatetime
import traceback
from pathlib import Path
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
from datetime import datetime
from time import time, sleep
from uuid import uuid4


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
node1 = "ir1.node.check-host.net"
node2 = "ir3.node.check-host.net"
node3 = "ir5.node.check-host.net"
node4 = "de1.node.check-host.net"
node5 = "fr2.node.check-host.net"
node6 = "us1.node.check-host.net"
headers = {
    'accept': 'application/json',
    'user-agent': user_agent
}

http_panels = ['shahan', 'xpanel', 'rocket', 'sanaie']
ssh_panels = ['dragon']
v2ray_panels = ['sanaie']
supported_protocols = ['vless']


shortcut_isp_json = {
    "Mobile Communication Company of Iran PLC": "همراه اول",
    "Information Technology Company (ITC)": "مخابرات",
    "Iran Cell Service and Communication Company": "ایرانسل",
    '"Rightel Communication Service Company PJS"': "رایتل",
    'Rightel Communication Service Company PJS': "رایتل",
    "Iran Telecommunication Company PJS": "مخابرات",
    "Aria Shatel Company Ltd": "شاتل",
    "Shiraz Hamyar Co.": "همیارنت",
    "Pars Online PJS": "پارس آنلاین",
    "Pishgaman Toseeh Ertebatat Company (Private Joint Stock)": "پیشگامان",
    "Asiatech Data Transmission company": "آسیاتک",
    "Sefroyek Pardaz Engineering PJSC": "صفرویک",
    "Datak Company LLC": "رهام داتک",
    "Parvaresh Dadeha Co. Private Joint Stock": "صبانت",
    "ANDISHE SABZ KHAZAR CO. P.J.S.": "اندیشه سبز",
    "Dade Samane Fanava Company (PJS)": "فن آوا",
    "Rayaneh Danesh Golestan Complex P.J.S. Co.": "های وب",
    "Mobin Net Communication Company (Private Joint Stock)": "مبین نت",
    "Noyan Abr Arvan Co. ( Private Joint Stock)": "آروان",
    "Afranet": "افرانت",
    "Sepanta Communication Development Co. Ltd": "سپنتا",
    "Fanava Group": "فن آوا"
}


def Shortcut_isp(isp):
    if shortcut_isp_json.get(isp, None) is not None:
        return shortcut_isp_json[isp]
    else:
        return isp


def ISP(target):
    with open("ir.csv", "r", encoding="utf-8") as f:
        for i in f.readlines():
            if i != "\n":
                data = i.replace("\n", "").split(",")
                from_range = data[0]
                to_range = data[1]
                isp = data[4]
                start_ip = ipaddress.IPv4Address(from_range)
                end_ip = ipaddress.IPv4Address(to_range)
                num_addresses = int(end_ip) - int(start_ip)
                subnet_bits = 32 - num_addresses.bit_length()
                ip_network = from_range + "/" + str(subnet_bits)
                try:
                    if ipaddress.ip_address(target) in ipaddress.ip_network(ip_network):
                        return Shortcut_isp(isp)
                except:
                    pass
    return ""


def IP_INFO(query):
    url = f"http://ip-api.com/json/{query}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,timezone,isp,org,as"
    try:
        r = requests.get(url, headers=headers)
        data = json.loads(r.text)
        if data['status'] == "success":
            text = f"🌎Continent: {data['continent']} ({data['continentCode']})\n🏳️Country: {data['country']} ({data['countryCode']})\n📍Region: {data['region']} ({data['regionName']})\n🗺City: {data['city']}\n⌚️Time zone: {data['timezone']}\n🌐ISP: {data['isp']}\n🏢Organization: {data['org']}\n🛜AS: {data['as']}"
            return text
        else:
            return data['message']
    except Exception as e:
        return "Error: " + str(e)


def check_host_json_results(results):
    for result in results[node1][0]:
        if result[0] == "OK":
            return False
    for result in results[node2][0]:
        if result[0] == "OK":
            return False
    try:
        for result in results[node3][0]:
            if result[0] == "OK":
                return False
    except:
        pass
    for result in results[node4][0]:
        if result[0] == "OK":
            return True
    for result in results[node5][0]:
        if result[0] == "OK":
            return True
    for result in results[node6][0]:
        if result[0] == "OK":
            return True


def check_host_api(host):
    try:
        url = f"https://check-host.net/check-ping?host={host}&node={node1}&node={node2}&node={node3}&node={node4}&node={node5}&node={node6}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            request_id = json.loads(r.text)['request_id']
            sleep(7)
            data = requests.get("https://check-host.net/check-result/" + request_id, headers=headers)
            if data.status_code == 200:
                results = json.loads(data.text)
                return check_host_json_results(results)
            else:
                return False
        else:
            return False
    except:
        return False


def open_session(host, port):
    r = requests.session()
    session = "ssh/" + host + ".session"
    with open(session, 'rb') as f:
        r.cookies.update(pickle.load(f))
    troubleshooting(host)
    protocol = get_protocol_cache(host)
    if (port == "80") and (protocol == "https"):
        port = "443"
    url = protocol + "://" + host + ":" + port
    return url, r


def get_token(req):
    html = HTMLParser(req)
    for data in html.css('meta'):
        if data.attributes.get("name", None) is not None:
            if data.attributes['name'] == "csrf-token":
                return data.attributes['content']


def ssh_status(host, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, int(port), username, password, banner_timeout=200)
        return "🟢 Online"
    except Exception as e:
        return "🔴 Offline: Please check the username or password or port : " + str(e)


def Force_string(stdout):
    timeout = 1.5
    endtime = time() + timeout
    while not stdout.channel.eof_received:
        sleep(0.2)
        if time() > endtime:
            stdout.channel.close()
            break
    return stdout


def Clean_string(dirty):
    cleaned = re.sub('\[[0-9;]+[a-zA-Z]',' ', dirty)
    cleaned = cleaned.replace('\x1b', "")
    return cleaned


def get_ips_of_users_dragon(ssh, usernames):
    cmd = "ps -ef | grep ssh"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    datas = ssh_stdout.read().decode()
    datas = datas.split("\n")
    pids = []
    gotted = []
    for data in datas:
        cache = data.split(" ")
        cache = list(filter(None, cache))
        if cache != []:
            if cache[0] in usernames:
                if cache[0] not in gotted:
                    pids.append(cache[1])
                    gotted.append(cache[0])
            elif cache[0][-1] == "+":
                if len(cache) == 9:
                    if cache[8] in usernames:
                        if cache[8] not in gotted:
                            pids.append(cache[1])
                            gotted.append(cache[8])
    ips = []
    users = []

    for pid in pids:
        cmd = f"lsof -p {pid} | grep TCP"
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        datas = ssh_stdout.read().decode()
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', datas)
        if ip == []:
            break
        elif len(ip) == 1:
            ips.append(ip[0])
            users.append(gotted[pids.index(pid)])
        else:
            ips.append(ip[1])
            users.append(gotted[pids.index(pid)])

    return ips, users


def check_lang_details(html):
    for span in html.css('span.pc-mtext'):
        if "داشبورد" in span.text():
            return "Fa"
        elif "Dashboard" in span.text():
            return "En"
    return "Fa"


def check_panel_protocol(host):
    url = 'https://' + host
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            if response.url.startswith("https://"):
                return "https"
            elif response.url.startswith("http://"):
                return "http"
            else:
                #Unknown
                return "http"
        else:
            return "http"
    except:
        return "http"


def troubleshooting(host):
    if (Path("protocol-cache.txt").is_file() is False) or (get_protocol_cache(host) is None):
        protocol = check_panel_protocol(host)
        add_protocol_cache(host, protocol)


def add_protocol_cache(host, protocol):
    with open("protocol-cache.txt", 'a+') as f:
        if host not in f.read():
            f.writelines(f"{host}:{protocol}\n")


def remove_protocol_cache(host):
    with open("protocol-cache.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        if host in line:
            Line = line.replace("\n", "")
            break
    try:
        with open("protocol-cache.txt", "w") as f:
            for line in lines:
                if line.strip("\n") != Line:
                    f.write(line)
    except Exception as e:
        os.remove("protocol-cache.txt")
        with open("protocol-cache.txt", "a+") as f:
            for line in lines:
                f.writelines(line)


def get_protocol_cache(host):
    with open("protocol-cache.txt", 'r') as f:
        for data in f.readlines():
            if host in data:
                return data.split(':')[1].replace('\n', '')
    return None


def Test(r, host, port, panel, status):
    if panel == "shahan":
        protocol = check_panel_protocol(host)
        s = r.get(f"{protocol}://{host}/p/index.php").text
        html = HTMLParser(s)
        for button in html.css('button'):
            if button.attributes.get("name", None) is not None:
                if "login" in button.attributes['name']:
                    return False
        return True

    elif panel == "rocket":
        if status == 'updater':
            protocol = check_panel_protocol(host + ':' + port)
            s = r.get(f"{protocol}://{host}:{port}/settings").text
            html = HTMLParser(s)
            for form in html.css('form'):
                if form.attributes.get("action", None) is not None:
                    if "/login" in form.attributes['action']:
                        return False
        return True

    elif panel == "xpanel":
        protocol = check_panel_protocol(host + ':' + port)
        s = r.get(f"{protocol}://{host}:{port}/cp/users").text
        html = HTMLParser(s)
        for form in html.css('form'):
            if form.attributes.get("action", None) is not None:
                if "/login" in form.attributes['action']:
                    return False
        try:
            if check_lang_details(html) != "en":
                r.get(f"{protocol}://{host}:{port}/cp/settings/lang/en")
        except:
            pass
        return True

    elif panel == "sanaie":
        protocol = check_panel_protocol(host + ':' + port)
        try:
            s = r.post(f"{protocol}://{host}:{port}/server/status", allow_redirects=False)
            if s.status_code == 200:
                return True
            elif s.status_code == 301:
                return False
            else:
                return False
        except Exception as e:
            print(e, "sanaie test")
            return False
        return True


def Login(username, password, host, port, panel):
    if panel in http_panels:
        r = requests.session()
        if panel == "shahan":
            protocol = check_panel_protocol(host)
            login_path = f"{protocol}://{host}/p/login.php"
            data = {'username': username, 'password': password, "loginsubmit": ""}

        elif panel == "xpanel":
            protocol = check_panel_protocol(host + ':' + port)
            login_path = f"{protocol}://{host}:{port}/login"
            data = {'_token': get_token(r.get(login_path).text), 'username': username, 'password': password}

        elif panel == "rocket":
            protocol = check_panel_protocol(host + ':' + port)
            login_path = f"{protocol}://{host}:{port}/ajax/login"
            data = {'username': username, 'password': password, "remember": ""}

        elif panel == "sanaie":
            protocol = check_panel_protocol(host + ':' + port)
            data = {'username': username, 'password': password}
            login_path = f"{protocol}://{host}:{port}/login"

        session = "ssh/" + host + ".session"
        try:
            with open(session, 'wb') as f:
                responde = r.post(login_path, data=data)
                pickle.dump(r.cookies, f)
                if responde.status_code <= 302:
                    if Test(r, host, port, panel, 'login') is True:
                        print(f"Login and saved session at {host} | Code: ", responde.status_code)
                        if Path("protocol-cache.txt").is_file() is False:
                            add_protocol_cache(host, protocol)
                        else:
                            if get_protocol_cache(host) is not None:
                                remove_protocol_cache(host)
                            add_protocol_cache(host, protocol)
                        return True
                    else:
                        print("Error : Test")
                        return False
                else:
                    print("Error : ", responde.status_code)
                    return False
        except Exception as e:
            print("Login Error: ", e)
            return False
        r.close()

    elif panel in ssh_panels:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if panel == "dragon":
                ssh.connect(host, port, username, password, banner_timeout=200)
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("menu")
                ssh_stdin.flush()
                dirty = Force_string(ssh_stdout).read().decode()
                cleaned = Clean_string(dirty)
                if "DRAGON VPS MANAGER" in cleaned:
                    return True
                else:
                    return False
        except Exception as e:
            print("Login Error: ", e)
            return False
        ssh.close()


#>>     Domain:Panelport @ User:Password ? Panel:path & sshport:udgpw & remark
#>>     Domain:Panelport @ User:Password ? Panel:default & default:default & remark
def HOSTS():
    hosts = []
    remarks = []
    with open("Pannels.txt", "r", encoding="utf-8") as f:
        for data in f.readlines():
            data = data.replace("\n", "")
            hosts.append(data.split(":")[0])
            remarks.append(data.split("&")[2])
    return hosts, remarks


def HOST_INFO(target):
    with open("Pannels.txt", "r", encoding="utf-8") as f:
        for data in f.readlines():
            data = data.replace("\n", "")
            host = data.split(":")[0]
            if target == host:
                port = data.split("@")[0].split(":")[1]
                username = data.split("@")[1].split(":")[0]
                password = data.split("?")[0].split("@")[1].split(":")[1]
                panel = data.split("?")[1].split(":")[0]
                route_path = data.split("&")[0].split("?")[1].split(":")[1]
                sshport = data.split("&")[1].split(":")[0]
                udgpw = data.split("&")[1].split(":")[1]
                remark = data.split("&")[2]
                return port, username, password, panel, route_path, sshport, udgpw, remark
    return None, None, None, None, None, None, None, None


def get_port_xpanel(host):
    port, username, password, panel, route_path, sshport, udgpw, remark = HOST_INFO(host)
    return sshport, udgpw


def get_port_dragon(host):
    port, username, password, panel, route_path, sshport, udgpw, remark = HOST_INFO(host)
    return sshport, udgpw


def Remove_Host(host, full):
    text = "Done:\n"
    if full is True:
        try:
            session = "ssh/" + host + ".session"
            os.remove(session)
            text += "Session has been removed\n"
        except Exception as e:
            text += f"Error Session removing: {str(e)}\n"
    with open("Pannels.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    Line = None
    for line in lines:
        if host in line:
            Line = line.replace("\n", "")
            break
    if Line is not None:
        try:
            with open("Pannels.txt", "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip("\n") != Line:
                        f.write(line)
            text += "host has been removed from the list"
        except Exception as e:
            os.remove("Pannels.txt")
            with open("Pannels.txt", "a+", encoding="utf-8") as f:
                for line in lines:
                    f.writelines(line)
            text += f"Error host list removing: {str(e)}"
    else:
        text += f"Error: host not found in List"
    return text


def Add_Host(host, port, username, password, panel, route_path, sshport, udgpw, remark):
    with open("Pannels.txt", 'a+', encoding="utf-8") as txt:
        data = f"{host}:{port}@{username}:{password}?{panel}:{route_path}&{sshport}:{udgpw}&{remark}"
        txt.writelines(data + "\n")


def host_to_end(host):
    port, username, password, panel, route_path, sshport, udgpw, remark = HOST_INFO(host)
    if "host has been removed from the list" in Remove_Host(host, False):
        Add_Host(host, port, username, password, panel, route_path, sshport, udgpw, remark)
        return "Done✔️"
    else:
        return "Error"


def Update_host(old_host, new_host):
    port, username, password, panel, route_path, sshport, udgpw, remark = HOST_INFO(old_host)
    if "host has been removed from the list" in Remove_Host(old_host, True):
        Add_Host(new_host, port, username, password, panel, route_path, sshport, udgpw, remark)
        return "Done✔️"
    else:
        return "Error"


def Update_user_pass_port(host, new_port, new_username, new_password):
    port, username, password, panel, route_path, sshport, udgpw, remark = HOST_INFO(host)
    if "host has been removed from the list" in Remove_Host(host, True):
        Add_Host(host, new_port, new_username, new_password, panel, route_path, sshport, udgpw, remark)
        return "Done✔️"
    else:
        return "Error"


def Update_Host_All_info(old_host, host, port, username, password, panel, route_path, sshport, udgpw, remark):
    if "host has been removed from the list" in Remove_Host(old_host, True):
        Add_Host(host, port, username, password, panel, route_path, sshport, udgpw, remark)
        return "Done✔️"
    else:
        return "Error"


def Change_udp_port(host, udgpw):
    port, username, password, panel, route_path, sshport, old_udgpw, remark = HOST_INFO(host)
    if "host has been removed from the list" in Remove_Host(host, False):
        Add_Host(host, port, username, password, panel, route_path, sshport, udgpw, remark)
        return "Done✔️"
    else:
        return "Error"


def Change_ssh_port(host, sshport):
    port, username, password, panel, route_path, old_sshport, udgpw, remark = HOST_INFO(host)
    if "host has been removed from the list" in Remove_Host(host, False):
        Add_Host(host, port, username, password, panel, route_path, sshport, udgpw, remark)
        return "Done✔️"
    else:
        return "Error"


def Change_remark(host, remark):
    port, username, password, panel, route_path, sshport, udgpw, old_remark = HOST_INFO(host)
    if "host has been removed from the list" in Remove_Host(host, False):
        Add_Host(host, port, username, password, panel, route_path, sshport, udgpw, remark)
        return "Done✔️"
    else:
        return "Error"


def ASCII_Check(text):
    for c in text:
        if 0 <= ord(c) <= 127:
            pass
        else:
            return False
    return True


def Contains(text):
    if text.isdigit() is True:
        return True
    elif text.isalpha() is True:
        return True
    else:
        if bool(re.match("^(?=.*[a-zA-Z])(?=.*[\d])[a-zA-Z\d]+$", text)) is False:
            return False
        else:
            return True


def TXT_FILTER(text):
    special_characters = ['?', '@', '&', ':']
    for char in special_characters:
        if char in text:
            return False
    return True


def OTX_Check(text):
    return bool(re.match("^[A-Za-z0-9_-]*$", text))


def get_cache_xpanel(html):
    def get_usage(tdx):
        if "MB" in tdx:
            Usage = ('{:.2f}'.format(float(tdx.split("MB")[0]) / 1024)) + " " + " گیگابایت"
        elif "GB" in tdx:
            Usage = tdx.split("GB")[0] + " " + " گیگابایت"
        return Usage
    cache = []
    for td in html.css('td'):
        if td.attributes.get('style', None) is not None:
            cache.append(td.text().replace("\n", "").replace("        ", "").replace('    ', ""))
        elif "Unlimited" in td.text():
            cache.append("Unlimited")
            tdx = td.text().split("Unlimited")[1].replace(" ", '').replace("\n", '')
            cache.append(((get_usage(tdx)).split(" گیگابایت")[0]).replace(" ", ""))
        elif "Unlimit" in td.text():
            cache.append("Unlimit")
        elif "-" in td.text():
            tdx = td.text().replace(" ", "").replace("\n", "")
            cache.append(tdx)
        elif "Expired" in td.text():
            cache.append("Deactive")
        elif "فعال" == td.text():
            cache.append("Active")
        elif "غیرفعال" == td.text():
            cache.append("Deactive")
        elif "GB" in td.text():
            tdx = td.text().replace(" ", "").replace("\n", "")
            if tdx.count('GB') == 2:
                f1 = tdx.split("GB")[0] + "GB"
                f2 = tdx.split("GB")[1] + "GB"
            else:
                f1 = tdx.split("GB")[0] + "GB"
                f2 = tdx.split("GB")[1]
            cache.append(get_usage(f1))
            cache.append(((get_usage(f2)).split(" گیگابایت")[0]).replace(" ", ""))
        elif "MB" in td.text():
            tdx = td.text().replace(" ", "").replace("\n", "")
            f1 = tdx.split("MB")[0] + "MB"
            f2 = tdx.split("MB")[1] + "MB"
            cache.append(get_usage(f1))
            cache.append(((get_usage(f2)).split(" گیگابایت")[0]).replace(" ", ""))
        elif "\n" not in td.text():
            tdx = td.text().replace(" ", "")
            if (ASCII_Check(tdx) is True):
                cache.append(tdx)
        elif "\n" in td.text():
            tdx = td.text().replace(" ", "").replace("\n", "")
            if (ASCII_Check(tdx) is True) and (Contains(tdx) is True):
                if (len(tdx) <= 5) and (tdx != ""):
                    cache.append(tdx)
    return cache


def get_users_data_sanaie(s):
    inbounds, uids, remarks, connection_limits, traffics, usages, expires, days_left, status = ([] for i in range(9))
    obj = json.loads(s)['obj']
    for i in range(len(obj)):
        if (obj[i]['protocol'] in supported_protocols):
            if len(obj[i]['clientStats']) >= 1:
                data_list = obj[i]
                inbound_id = str(obj[i]['id'])
                clients = json.loads(data_list['settings'].replace('\\', ''))["clients"]
                for n in range(len(clients)):
                    inbounds.append(inbound_id)
                    uids.append(clients[n]['id'])
                    remarks.append(clients[n]['email'])
                    usage = (data_list['clientStats'][n]['up'] + data_list['clientStats'][n]['down'])
                    usages.append(str("{:.2f}".format(float(usage / 1024 / 1024 / 1024))))
                    if clients[n]['totalGB'] == 0:
                        traffics.append("نامحدود")
                    else:
                        tr = str("{:.2f}".format(float(clients[n]['totalGB'] / 1024 / 1024 / 1024))) + " گیگابایت"
                        traffics.append(tr)
                    if clients[n]['expiryTime'] == 0:
                        days_left.append("0")
                        expires.append("♾Unlimited")
                    else:
                        expirytime = int(str(clients[n]['expiryTime'])[:-3])
                        expiry = datetime.fromtimestamp(expirytime)
                        now = datetime.fromtimestamp(time())
                        remain_time = (str(expiry - now)).split(' ')
                        remaining_days = '0'
                        if len(remain_time) > 2:
                            remaining_days = remain_time[0]
                        days_left.append(remaining_days)
                        expires.append(str(expiry).split(" ")[0])
                    if clients[n]['enable'] is False:
                        status.append("غیرفعال")
                    else:
                        if clients[n]['expiryTime'] != 0:
                            if int(str(clients[n]['expiryTime'])[:-3]) - int(time()) < -1:
                                status.append("منقضی")
                            else:
                                status.append("فعال")
                        else:
                            status.append("فعال")
                    if clients[n].get(['limitIp'], None) is not None:
                        connection_limits.append(clients[n]['limitIp'])
                    else:
                        connection_limits.append("0")
    return inbounds, uids, remarks, connection_limits, traffics, usages, expires, days_left, status


def get_users_data_dragon(ssh):
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("menu")
    dirty = Force_string(ssh_stdout).read().decode()
    cleaned = Clean_string(dirty)
    cleaned = cleaned.split('◇ㅤOnline: ')[1].split('\n')[0]
    counter = int(cleaned.split("Total: ")[1])
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("menu")
    ssh_stdin.write('9\n')
    ssh_stdin.flush()
    if counter >= 20:
        sleep(counter // 20)
    dirty = Force_string(ssh_stdout).read().decode()
    cleaned = Clean_string(dirty)
    cleaned = cleaned.split('◇User        ◇Password      ◇limit     ◇validity')[1].split('◇ TOTAL USERS')[0]

    usernames, passwords, connection_limits, days, status = ([] for i in range(5))
    datas = cleaned.split("\n")
    for data in datas:
        cache = data.split(" ")
        cache = list(filter(None, cache))
        if 4 <= len(cache) <= 5:
            if (cache[1] != "Null"):
                usernames.append(cache[0])
                passwords.append(cache[1])
                connection_limits.append(cache[2])
                if cache[3] in ["Nunca", "Venceu"]:
                    status.append('غیرفعال')
                    days.append("0")
                else:
                    status.append('فعال')
                    days.append(cache[3])
    return usernames, passwords, connection_limits, days, status


def Get_user_info_shahan(html, uname):
    ips, ports, udgpws, usernames, passwords, connection_limits, traffics, usages, expires, days_left, days_left_trubleshoots, descriptions, tuics, dropbears, status = ([] for i in range(15))
    for data in html.css('td'):
        if data.attributes.get("name", None) is None:
            if 'روز' in data.text():
                if 'گذشته' in data.text():
                    days_left.append('-' + (data.text()).split("روز")[0])
                else:
                    days_left.append((data.text()).split("روز")[0])
            elif "نامحدود" == data.text():
                if '<td>نامحدود</td>' == data.html:
                    days_left.append("9999")
            elif "فعال نشده" in data.text():
                days_left.append("inactive")
        else:
            if 'expire' in data.attributes['name']:
                expires.append(data.text())
            if 'multilogin' in data.attributes['name']:
                connection_limits.append(data.text())
            if 'username' in data.attributes['name']:
                usernames.append(data.text())
            if 'password' in data.attributes['name']:
                passwords.append(data.text())
            if 'traffic' in data.attributes['name']:
                traffics.append(data.text())
            if 'ip' in data.attributes['name']:
                ips.append(data.text())
            if 'drop' in data.attributes['name']:
                dropbears.append(data.text())
            if 'tuic' in data.attributes['name']:
                tuics.append(data.text())
            if 'port' in data.attributes['name']:
                if (data.attributes['name']).split("port")[0] == "udp":
                    if "badvpn" in data.text():
                        udgpw = (data.text()).split("badvpn")[0]
                    elif "localhost" in data.text():
                        udgpw = (data.text()).split("localhost")[0]
                    elif "127.0.0.1" in data.text():
                        udgpw = (data.text()).split("127.0.0.1")[0]
                    else:
                        try:
                            udgpw = data.text()
                        except:
                            udgpw = ""
                    udgpws.append(udgpw)
                else:
                    ports.append(data.text())
    for a in html.css('a'):
        href = a.attributes.get("href", None)
        if href is not None:
            if "index.php?sortby=" in href:
                if "active" in href:
                    status.append('فعال')
                else:
                    status.append('غیرفعال')
    del status[:4]
    if len(usernames) != len(status):
        del status[:2]
    for button in html.css('button'):
        if button.attributes.get("type", None) is not None:
            if button.attributes['type'] == "button":
                if "/" in button.text():
                    usages.append((button.text()).split(" /")[0])
                elif ("گیگابایت" in button.text()) or ("نامحدود" in button.text()):
                    usages.append('0.0')
    for inp in html.css("input.form-control"):
        if inp.attributes.get("placeholder", None) is not None:
            if inp.attributes['placeholder'] == "روز اعتبار":
                if inp.attributes.get("name", None) is not None:
                    if "edituserfinishdate" in inp.attributes['name']:
                        if inp.attributes.get("value", None) is not None:
                            days_left_trubleshoots.append(inp.attributes['value'])
                        else:
                            days_left_trubleshoots.append('9999')
    for textarea in html.css("textarea"):
        if textarea.attributes.get("name", None) is not None:
            if "edituserinfo" in textarea.attributes['name']:
                descriptions.append(textarea.text())
    if len(days_left_trubleshoots) == len(usernames):
        days_left = days_left_trubleshoots
    for username in usernames:
        if username == uname:
            n = usernames.index(uname)
            days = days_left[n]
            if len(ports) == len(dropbears):
                dropbear = dropbears[n]
            else:
                dropbear = ""
            if len(ports) == len(tuics):
                tuic = tuics[n]
            else:
                tuic = ""
            return passwords[n], traffics[n], int(connection_limits[n]), ips[n], days, status[n], usages[n], expires[n], descriptions[n], ports[n], udgpws[n], dropbear, tuic


def Get_user_info_rocket(datas, uname, r, url):
    for data in datas['data']:
        if uname == data['username']:
            if "GB" in data['traffic_format']:
                traffic = data['traffic_format'].replace("GB", "گیگابایت")
            elif "MB" in data['traffic_format']:
                traffic = ('{:.2f}'.format(float(data['traffic_format'].split(" ")[0]) / 1024)) + " گیگابایت"
            else:
                traffic = data['traffic_format']
            usage = str('{:.2f}'.format(float(int(data['consumer_traffic'])) / 1024))
            Date = data['end_date']
            if str(Date) == '0':
                kind = "days"
            else:
                kind = "expiry"
            days = data['remaining_days']
            s = r.get(f"{url}/ajax-views/users/{str(data['id'])}/edit?_={str(int(time()))}").text
            s = json.loads(s)['html']
            html = HTMLParser(s)
            description = ''
            for textarea in html.css("textarea"):
                if textarea.attributes.get("name", None) is not None:
                    if "desc" in textarea.attributes['name']:
                        description = textarea.text()
                        break
            if data['end_date'] == 0:
                for inp in html.css('input'):
                    if inp.attributes.get("name", None) is not None:
                        if inp.attributes['name'] == "exp_days":
                            days = inp.attributes['value']
                            break
            s = r.get(f"{url}/ajax-views/users/{str(data['id'])}/info?_={str(int(time()))}").text
            s = json.loads(s)['html']
            html = HTMLParser(s)
            public_link = ""
            for a in html.css('a'):
                if a.attributes.get("href", None) is not None:
                    if "/account/" in a.attributes['href']:
                        public_link = a.attributes['href']
            port = ""
            udgpw = ""
            for button in html.css('button'):
                if button.attributes.get("data-config", None) is not None:
                    try:
                        data_config = json.loads(button.attributes['data-config'].replace("\\", ""))
                        port = data_config['ssh_port']
                        udgpw = data_config['udp_port']
                        break
                    except:
                        pass
            return data['password'], traffic, int(data['limit_users']), int(days), data['status_label'], usage, data['id'], kind, Date, description, public_link, port, udgpw


def Get_user_info_xpanel(html, uname):
    expires = []
    connection_limits = []
    usernames = []
    passwords = []
    traffics = []
    usages = []
    days_left = []
    status = []
    descriptions = []
    cache = get_cache_xpanel(html)
    for i in range(0, len(cache), 10):
        usernames.append(cache[i + 2])
        passwords.append(cache[i + 3])
        traffic = cache[i + 4]
        if traffic == "Unlimited":
            traffic = "نامحدود"
        traffics.append(traffic)
        usages.append(cache[i + 5])
        connection_limits.append(cache[i + 6])
        days = cache[i + 7]
        if days == 'Unlimit':
            days_left.append("9999")
            expires.append("?")
        elif days.isdigit() is True:
            expires.append(str(datetime.fromtimestamp(time() + (int(days) * 86400))).split(" ")[0])
            days_left.append(days)
        elif "ExpiredDate:" in days:
            end = days.split("ExpiredDate:")[-1]
            if end.count("-") == 2:
                start = str(datetime.now()).split(" ")[0]
                expires.append(end)
                date_format = "%Y-%m-%d"
                a = datetime.strptime(start, date_format)
                b = datetime.strptime(end, date_format)
                delta = b - a
                days_left.append(str(delta.days))
            else:
                expires.append("?")
                days_left.append("0")
        else:
            expires.append("?")
            days_left.append("0")
        if cache[i + 8] == "Active":
            status.append('فعال')
        else:
            status.append('غیرفعال')
        descriptions.append(cache[i + 9])
    dropbear = ""
    for a in html.css('a'):
        if a.attributes.get('data-drop', None) is not None:
            URI = a.attributes['data-drop']
            dropbear = URI.split('@')[1].split(':')[1].split("/")[0]
            break
    for i in range(len(usernames)):
        if uname == usernames[i]:
            if expires[i] == "?":
                kind = "days"
            else:
                kind = "expiry"
            return passwords[i], traffics[i], int(connection_limits[i]), int(days_left[i]), status[i], usages[i], kind, expires[i], descriptions[i], dropbear


def Get_user_info_sanaie(s, uid):
    inbounds, uids, remarks, connection_limits, traffics, usages, expires, days_left, status = get_users_data_sanaie(s)
    for i in range(len(uids)):
        if uid == uids[i]:
            return inbounds[i], uids[i], remarks[i], connection_limits[i], traffics[i], usages[i], expires[i], days_left[i], status[i]


def Get_user_info_dragon(ssh, uname):
    usernames, passwords, connection_limits, days, status = get_users_data_dragon(ssh)
    for i in range(len(usernames)):
        if uname == usernames[i]:
            return passwords[i], connection_limits[i], days[i], status[i]


def Get_list_users_only_shahan(html):
    usernames = []
    for data in html.css('td'):
        if data.attributes.get("name", None) is not None:
            if 'username' in data.attributes['name']:
                usernames.append(data.text())
    return usernames


def Get_list_users_only_rocket(datas):
    usernames = []
    for data in datas['data']:
        usernames.append(data['username'])
    return usernames


def Get_list_users_only_xpanel(html):
    cache = get_cache_xpanel(html)
    usernames = []
    for i in range(0, len(cache), 9):
        usernames.append(cache[i + 2])
    return usernames


def Get_list_shahan(html):
    ips = []
    expires = []
    connection_limits = []
    usernames = []
    passwords = []
    ports = []
    traffics = []
    usages = []
    days_left = []
    days_left_trubleshoots = []
    status = []
    descriptions = []
    server_traffic = 0
    online_clients = 0
    for setr in html.css('small.pull-left'):
        if "گیگابایت" in setr.text():
            server_traffic = float(((setr.text()).split("گیگابایت")[0]).replace(" ", ''))
            break
        elif "ترابایت" in setr.text():
            server_traffic = float(((setr.text()).split("ترابایت")[0]).replace(" ", '')) * 1024
            break
    for textarea in html.css("textarea"):
        if textarea.attributes.get("name", None) is not None:
            if "edituserinfo" in textarea.attributes['name']:
                descriptions.append(textarea.text())
    for data in html.css('td'):
        if data.attributes.get("name", None) is None:
            if 'روز' in data.text():
                if 'گذشته' in data.text():
                    days_left.append('-' + (data.text()).split("روز")[0])
                else:
                    days_left.append((data.text()).split("روز")[0])
            elif "نامحدود" == data.text():
                if '<td>نامحدود</td>' == data.html:
                    days_left.append("9999")
            elif "فعال نشده" in data.text():
                days_left.append("inactive")
        else:
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
            if 'ip' in data.attributes['name']:
                ips.append(data.text())
    for button in html.css('button'):
        if button.attributes.get("type", None) is not None:
            if button.attributes['type'] == "button":
                if "/" in button.text():
                    usages.append((button.text()).split(" /")[0])
                elif ("گیگابایت" in button.text()) or ("نامحدود" in button.text()):
                    usages.append('0.0')
    for a in html.css('a'):
        href = a.attributes.get("href", None)
        if href is not None:
            if "index.php?sortby=" in href:
                if "active" in href:
                    status.append('فعال')
                else:
                    status.append('غیرفعال')
    del status[:4]
    if len(usernames) != len(status):
        del status[:2]
    info = []
    for data in html.css('span.info-box-number'):
        info.append((data.text()).replace(" کاربر", ""))
    for inp in html.css("input.form-control"):
        if inp.attributes.get("placeholder", None) is not None:
            if inp.attributes['placeholder'] == "روز اعتبار":
                if inp.attributes.get("name", None) is not None:
                    if "edituserfinishdate" in inp.attributes['name']:
                        if inp.attributes.get("value", None) is not None:
                            days_left_trubleshoots.append(inp.attributes['value'])
                        else:
                            days_left_trubleshoots.append('9999')
    for i in range(len(days_left)):
        if days_left[i] == "inactive":
            if len(days_left) == len(days_left_trubleshoots):
                days_left[i] = days_left_trubleshoots[i]
            else:
                days_left[i] = "27784"
    if len(days_left_trubleshoots) == len(usernames):
        days_left = days_left_trubleshoots
    return expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, ips, descriptions,server_traffic, int(info[1]), True


def Get_list_rocket(datas, ip, info, r, url):
    ips = []
    expires = []
    connection_limits = []
    usernames = []
    passwords = []
    ports = []
    traffics = []
    usages = []
    days_left = []
    status = []
    descriptions = []
    server_traffic = 0.0
    online_clients = 0
    for data in datas['data']:
        ips.append(ip)
        usernames.append(data['username'])
        passwords.append(data['password'])
        connection_limits.append(str(data['limit_users']))
        #status.append(data['status'])
        status.append(data['status_label'])
        usages.append(str('{:.2f}'.format(float(int(data['consumer_traffic'])) / 1024)))
        if "GB" in data['traffic_format']:
            traffics.append(data['traffic_format'].replace("GB", "گیگابایت"))
        elif "MB" in data['traffic_format']:
            traffics.append(('{:.2f}'.format(float(data['traffic_format'].split(" ")[0]) / 1024)) + " گیگابایت")
        else:
            traffics.append(data['traffic_format'])
        if data['end_date'] == 0:
            s = r.get(f"{url}/ajax-views/users/{str(data['id'])}/edit?_={str(int(time()))}").text
            s = json.loads(s)['html']
            html = HTMLParser(s)
            for inp in html.css('input'):
                if inp.attributes.get("name", None) is not None:
                    if inp.attributes['name'] == "exp_days":
                        days_left.append(str(inp.attributes['value']))
                        break
        else:
            days_left.append(str(data['remaining_days']))
        expires.append(str(data['end_date']))
        online_clients += len(data['online_users'])

    traffic_data = info.split("Storage: ")[1].split('👤Clients')[0]
    if "GB" in traffic_data.split('Clients Traffic')[0]:
        server_traffic = float(traffic_data.split("Server Traffic: ")[1].split(" GB")[0])
    else:
        server_traffic = float(traffic_data.split("Traffic: ")[1].split(" TB")[0]) * 1024

    return expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, ips, descriptions,server_traffic, online_clients, True


def Get_list_xpanel(html, ip, info, r, url):
    ips = []
    expires = []
    connection_limits = []
    usernames = []
    passwords = []
    ports = []
    traffics = []
    usages = []
    days_left = []
    status = []
    descriptions = []
    server_traffic = 0
    online_clients = 0
    cache = get_cache_xpanel(html)
    for i in range(0, len(cache), 10):
        usernames.append(cache[i + 2])
        passwords.append(cache[i + 3])
        traffic = cache[i + 4]
        if traffic == "Unlimited":
            traffic = "نامحدود"
        traffics.append(traffic)
        usages.append(cache[i + 5])
        connection_limit = cache[i + 6]
        if connection_limit == '0':
            connection_limit = "0"
        connection_limits.append(connection_limit)
        days = cache[i + 7]
        if days == 'Unlimit':
            days_left.append("9999")
            expires.append("?")
        elif days.isdigit() is True:
            expires.append(str(datetime.fromtimestamp(time() + (int(days) * 86400))).split(" ")[0])
            days_left.append(days)
        elif "ExpiredDate:" in days:
            end = days.split("ExpiredDate:")[-1]
            if (end.count("-") == 2):
                start = str(datetime.now()).split(" ")[0]
                expires.append(end)
                date_format = "%Y-%m-%d"
                a = datetime.strptime(start, date_format)
                b = datetime.strptime(end, date_format)
                delta = b - a
                days_left.append(str(delta.days))
            else:
                expires.append("?")
                days_left.append("0")
        else:
            expires.append("?")
            days_left.append("0")
        if cache[i + 8] == "Active":
            status.append('فعال')
        else:
            status.append('غیرفعال')
        ips.append(ip)
        descriptions.append(cache[i + 9])
    '''traffic_data = info.split("Storage: ")[1].split('👤Clients')[0]
    if "GB" in traffic_data.split('Clients Traffic')[0]:
        server_traffic = float(traffic_data.split("Server Traffic: ")[1].split(" GB")[0])
    else:
        server_traffic = float(traffic_data.split("Traffic: ")[1].split(" TB")[0]) * 1024
    online_clients = int(info.split("Online: ")[1])'''
    server_traffic = 0
    Online_clients = 0
    return expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, ips, descriptions, server_traffic, online_clients, True


def get_traffic_rocket(band_info):
    if "TB" in band_info[0]:
        down_server = float(band_info[0].split("TB")[0]) * 1024
    elif "GB" in band_info[0]:
        down_server = float(band_info[0].split("GB")[0])
    else:
        down_server = 0
    if "TB" in band_info[1]:
        up_server = float(band_info[1].split("TB")[0]) * 1024
    elif "GB" in band_info[1]:
        up_server = float(band_info[1].split("GB")[0])
    else:
        up_server = 0
    if "TB" in band_info[2]:
        down_client = float(band_info[2].split("TB")[0]) * 1024
    elif "GB" in band_info[2]:
        down_client = float(band_info[2].split("GB")[0])
    else:
        down_client = 0
    if "TB" in band_info[3]:
        up_client = float(band_info[3].split("TB")[0]) * 1024
    elif "GB" in band_info[3]:
        up_client = float(band_info[3].split("GB")[0])
    else:
        up_client = 0
    server_traffic = str('{:.2f}'.format(float(up_server + down_server))) + " GB"
    clients_usage = str('{:.2f}'.format(float(up_client + down_client))) + " GB"
    return server_traffic, clients_usage


def get_traffic_xpanel(band_info):
    if "TB" in band_info[0]:
        server_traffic = str('{:.2f}'.format(float(band_info[0].split("TB")[0]) * 1024)) + " GB"
    elif "GB" in band_info[0]:
        server_traffic = str(float(band_info[0].split("GB")[0])) + " GB"
    else:
        server_traffic = "0 GB"
    if "TB" in band_info[1]:
        clients_usage = str('{:.2f}'.format(float(band_info[1].split("TB")[0]) * 1024)) + " GB"
    elif "GB" in band_info[1]:
        clients_usage = str(float(band_info[1].split("GB")[0])) + " GB"
    else:
        clients_usage = "0 GB"
    return server_traffic, clients_usage


def get_real_days_shahan(stat, file, days, user):
    if stat is True:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if "INSERT INTO `users` VALUES " in line:
                        line = line.split("INSERT INTO `users` VALUES ")[1].replace("\n", "")[:-1]
                        line = line.replace('Null', 'None').replace('NULL', 'None')
                        datas = list(ast.literal_eval(line))
                        for data in datas:
                            if data[1] == user:
                                days = data[14]
                                break
                        break
            os.remove(file)
        except Exception as e:
            print("Function get_real_days_shahan Error: ", e)
    return days


def check_premium_spliter(html):
    for a in html.css('a.waves-effect'):
        href = a.attributes.get("href", None)
        if href is None:
            return True, "Yes"
        elif "shahanpanel.online" in href:
            return False, "NO"
        else:
            return True, "YES"


def request_more(r, url):
    s = ""
    for i in range(3):
        s = r.get(url).text
        if s != "":
            return s
    return s


class PANNEL:
    def __init__(self, host, username, password, port, panel, job, uname):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.panel = panel
        #self.route_path = "cp"
        if panel in http_panels:
            self.url, self.r = open_session(host, port)
        elif panel in ssh_panels:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, int(port), username, password, banner_timeout=200)
            self.ssh = ssh

        if job == 'User':
            self.dropbear = ""
            self.uname = uname
            if panel == "shahan":
                s = self.r.get(self.url + "/p/index.php").text
                html = HTMLParser(s)
                self.req = self.url + "/p/newuser.php"
                self.passwd, self.traffic, self.connection_limit, self.ip, self.days, self.status, self.usage, self.Date, self.description, self.SPort, self.Sudgpw, self.dropbear, self.tuic = Get_user_info_shahan(html, uname)

            elif panel == "rocket":
                s = self.r.post(self.url + "/ajax/users/list").text
                if "<br" in s:
                    s = s.split("<br")[0]
                datas = json.loads(s)
                self.req = self.url + "/ajax/users/"
                self.passwd, self.traffic, self.connection_limit, self.days, self.status, self.usage, self.uid, self.kind, self.Date, self.description, self.public_link, self.SPort, self.Sudgpw = Get_user_info_rocket(datas, uname, self.r, self.url)
                self.ip = host

            elif self.panel == "xpanel":
                s = self.r.get(self.url + "/cp/users").text
                html = HTMLParser(s)
                self.req = self.url + "/cp/user/edit"
                self.token = get_token(s)
                self.passwd, self.traffic, self.connection_limit, self.days, self.status, self.usage, self.kind, self.Date, self.description, self.dropbear = Get_user_info_xpanel(html, uname)
                self.ip = host

            elif self.panel == "sanaie":
                s = self.r.post(self.url + "/panel/inbound/list").text
                self.inbound_id, self.uid, self.remark, self.connection_limit, self.traffic, self.usage, self.Date, self.days, self.status = Get_user_info_sanaie(s, uname)

            elif self.panel == "dragon":
                self.ip = host
                self.passwd, self.connection_limit, self.days, self.status = Get_user_info_dragon(ssh, uname)

    def Ports(self):
        if self.panel == "shahan":
            s = self.r.get(self.url + "/p/setting.php").text
            html = HTMLParser(s)
            port = ""
            udgpw = ""
            dropbear = ""
            for inp in html.css('input'):
                alt = inp.attributes.get("name", None)
                if alt is not None:
                    if 'port' == inp.attributes['name']:
                        if inp.attributes.get('value', None) is not None:
                            port = str(inp.attributes.get('value', None))
                    elif 'udpport' == inp.attributes['name']:
                        if inp.attributes.get('value', None) is not None:
                            if "badvpn" in inp.attributes.get('value', None):
                                udgpw = str(inp.attributes.get('value', None)).split("badvpn")[0]
                            elif "localhost" in inp.attributes.get('value', None):
                                udgpw = str(inp.attributes.get('value', None)).split("localhost")[0]
                            elif "127.0.0.1" in inp.attributes.get('value', None):
                                udgpw = str(inp.attributes.get('value', None)).split("127.0.0.1")[0]
                            else:
                                udgpw = str(inp.attributes.get('value', None))
                    elif 'dropport' == inp.attributes['name']:
                        dropbear = str(inp.attributes.get('value', None))
            return port, udgpw, dropbear

        elif self.panel == "rocket":
            s = self.r.get(self.url + "/settings").text
            html = HTMLParser(s)
            port = ""
            udgpw = ""
            for inp in html.css('input'):
                if inp.attributes.get("name", None) is not None:
                    if inp.attributes['name'] == "ssh_port":
                        port = inp.attributes['value']
                    if inp.attributes['name'] == "udp_port":
                        udgpw = inp.attributes['value']
            return port, udgpw, ""

        elif self.panel == "xpanel":
            port, udgpw = get_port_xpanel(self.host)
            return port, udgpw, ""

        elif self.panel == "dragon":
            port, udgpw = get_port_dragon(self.host)
            return port, udgpw, ""

    def Backup_content(self):
        if self.panel == "shahan":
            try:
                s = request_more(self.r, self.url + "/p/setting.php")
                html = BeautifulSoup(s, 'html.parser')
                urls = []
                for a in html.find_all('a', href=True):
                    if ("/p/backup/" in a['href']) and ("sql" in a['href']):
                        urls.append(a['href'])
                for delete in urls:
                    file = delete.split('/p/backup/')[1]
                    payload = {"delete": file}
                    self.r.get(self.url + "/p/setting.php?delete=" + file, data=payload)
                for i in range(5):
                    dt = (str(datetime.fromtimestamp(time()))).split(' ')[0]
                    date = dt + "-554"
                    payload = {"backupfull": date}
                    self.r.get(self.url + "/p/setting.php?backupfull=" + date, data=payload).text
                    s = request_more(self.r, self.url + "/p/setting.php")
                    html = BeautifulSoup(s, 'html.parser')
                    urls = []
                    for a in html.find_all('a', href=True):
                        if ("/p/backup/" in a['href']) and ("sql" in a['href']):
                            urls.append(a['href'])
                    if len(urls) >= 1:
                        break
                rec = self.r.get(self.url + urls[0]).content
                return True, rec
            except Exception as e:
                return False, str(e)

        elif self.panel == "rocket":
            try:
                s = self.r.get(self.url + "/settings/backup").text
                html = BeautifulSoup(s, 'html.parser')
                urls = []
                for a in html.find_all('a', href=True):
                    if ("/assets/backup/" in a['href']):
                        urls.append(a['href'])
                for delete in urls:
                    file = delete.split('/assets/backup/')[1]
                    payload = {"filename": file}
                    self.r.delete(self.url + "/ajax/settings/backup/export", data=payload)
                self.r.post(self.url + "/ajax/settings/backup/export")
                s = self.r.get(self.url + "/settings/backup").text
                html = BeautifulSoup(s, 'html.parser')
                urls = []
                for a in html.find_all('a', href=True):
                    if ("/assets/backup/" in a['href']):
                        urls.append(a['href'])
                rec = self.r.get(self.url + "/assets/backup/" + (urls[0]).split('/assets/backup/')[1]).content
                return True, rec
            except Exception as e:
                return False, str(e)

        elif self.panel == "xpanel":
            try:
                s = self.r.get(self.url + "/cp/settings/backup").text
                html = BeautifulSoup(s, 'html.parser')
                urls = []
                for a in html.find_all('a', href=True):
                    if ("/backup/dl/" in a['href']):
                        urls.append(a['href'])
                for delete in urls:
                    file = delete.replace('/dl/', '/delete/')
                    self.r.get(file)
                self.r.post(self.url + "/cp/settings/backup/make", data={"_token": get_token(s)})
                s = self.r.get(self.url + "/cp/settings/backup").text
                html = BeautifulSoup(s, 'html.parser')
                urls = []
                for a in html.find_all('a', href=True):
                    if ("/backup/dl/" in a['href']):
                        urls.append(a['href'])
                rec = self.r.get(self.url + "/cp/settings/backup/dl/" + (urls[0]).split('/dl/')[1]).content
                return True, rec
            except Exception as e:
                return False, str(e)

        elif self.panel == "sanaie":
            try:
                rec = self.r.get(self.url + "/server/getDb").content
                return True, rec
            except Exception as e:
                return False, str(e)

        elif self.panel == "dragon":
            for i in range(2):
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                ssh_stdin.write('15\n')
                ssh_stdin.flush()
                sleep(0.05)
                ssh_stdin.write('1\n')
                ssh_stdin.flush()
                ssh_stdin.write('s\n')
                if i == 0:
                    sleep(15)
                else:
                    sleep(50)
                ssh_stdin.flush()
                dirty = Force_string(ssh_stdout).read().decode()
                cleaned = Clean_string(dirty)
                try:
                    link = cleaned.split("LINK :")[1].split("\n")[0].replace(" ", "")
                    try:
                        rec = requests.get(link, timeout=15).content
                        return True, rec
                    except:
                        link = f"http://{self.host}:8888/backup/backup.vps"
                        rec = requests.get(link, timeout=30).content
                        return True, rec
                except Exception as e:
                    if i == 1:
                        return False, str(e)

    def Check(self):
        if self.panel == "shahan":
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

    def Change_lang(self):
        if self.panel == "xpanel":
            self.r.get(self.url + "/cp/settings/lang/en")

    def Check_lang(self):
        if self.panel == "xpanel":
            s = self.r.get(self.url + "/cp/dashboard").text
            html = HTMLParser(s)
            return check_lang_details(html)

    def Backup(self):
        if self.panel in ssh_panels:
            f = uuid4().hex[0:8] + ".vps"
        elif self.panel in v2ray_panels:
            f = uuid4().hex[0:8] + ".db"
        else:
            f = uuid4().hex[0:8] + ".sql"
        try:
            with open(f, 'wb') as file:
                status, rec = self.Backup_content()
                file.write(rec)
            return True, f
        except Exception as e:
            return False, str(e)

    def Short_info(self):
        server_traffic = 0
        clients_usage = 0
        counter = 1
        cpu = "?"
        ram = "?"
        storage = "?"
        if self.panel == "shahan":
            try:
                s = request_more(self.r, self.url + "/p/index.php")
                html = HTMLParser(s)
                for setr in html.css('small.pull-left'):
                    if counter == 1:
                        ram = setr.text()
                    elif counter == 2:
                        cpu = setr.text()
                    elif counter == 3:
                        storage = setr.text()
                    elif counter == 4:
                        if "گیگابایت" in setr.text():
                            server_traffic = str('{:.2f}'.format(float(float(((setr.text()).split("گیگابایت")[0]).replace(" ", ''))))) + " GB"
                        elif "ترابایت" in setr.text():
                            server_traffic = str('{:.2f}'.format(float(float(((setr.text()).split("ترابایت")[0]).replace(" ", ''))))) + " TB"
                    elif counter == 5:
                        if "گیگابایت" in setr.text():
                            clients_usage = str('{:.2f}'.format(float(float(((setr.text()).split("گیگابایت")[0]).replace(" ", ''))))) + " GB"
                        elif "ترابایت" in setr.text():
                            clients_usage = str('{:.2f}'.format(float(float(((setr.text()).split("ترابایت")[0]).replace(" ", ''))))) + " TB"
                        break
                    counter += 1
                info = []
                for data in html.css('span.info-box-number'):
                    info.append(data.text())
                onlines = info[1]
                if "کاربر" in onlines:
                    onlines = onlines.replace("کاربر", "").replace("\n", "").replace(" ", "")
                Clients = str(info[0]).replace('\n', '').replace(' ', '')
                Active = str(info[2]).replace('\n', '').replace(' ', '')
                Disabled = str(info[3]).replace('\n', '').replace(' ', '')
                text = f'🖥Host: {self.host}\nCPU: {cpu}\nRAM: {ram}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {Clients}\n✔️Active: {Active}\n🔴Disabled: {Disabled}\n🟢Online: {str(onlines)}'
                return text
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "rocket":
            try:
                s = self.r.get(self.url + "/dashboard").text
                html = HTMLParser(s)
                info = []
                for sec in html.css('h5'):
                    info.append(sec.text())
                clients = info[0]
                onlines = info[1]
                active = info[2]
                disabled = info[3]
                sys_info = []
                for sec in html.css('div.mt-2'):
                    if "%" in sec.text():
                        sys_info.append(sec.text())
                cpu = (sys_info[1]).replace("\n", "").replace("     ", "")
                ram = (sys_info[0]).replace("\n", "").replace("     ", "")
                storage = (sys_info[2]).replace("\n", "").replace("     ", "")
                band_info = []
                for sec in html.css("small"):
                    if sec.attributes.get("title", None) is not None:
                        if (sec.attributes['title'] == "دانلود") or (sec.attributes['title'] == "آپلود"):
                            band_info.append((sec.text()).replace(" ", "").replace("\n", "").replace(",", ""))
                server_traffic, clients_usage = get_traffic_rocket(band_info)
                text = f"🖥Host: {self.host}\nCPU: {cpu}\nRAM: {ram}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {str(clients)}\n✔️Active: {str(active)}\n🔴Disabled: {str(disabled)}\n🟢Online: {str(onlines)}"
                return text
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            try:
                s = self.r.get(self.url + "/cp/dashboard").text
                html = HTMLParser(s)
                info = []
                for sec in html.css('h6'):
                    info.append(sec.text())
                clients = (info[10]).replace("All User: ", "").replace("تمام کاربران: ", "")
                onlines = info[9]
                active = info[5]
                disabled = info[8]
                band_info = []
                for sec in html.css("h5"):
                    t = sec.text()
                    if ("Server" in t) or ("سرور" in t):
                        t = t.replace("Server", "").replace("سرور", "")
                    elif ("Client" in t) or ("کلاینت" in t):
                        t = t.replace("Client", "").replace("کلاینت", "")
                    band_info.append(t)
                server_traffic, clients_usage = get_traffic_xpanel(band_info)
                text = f"🖥Host: {self.host}\nCPU: {cpu}\nRAM: {ram}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {str(clients)}\n✔️Active: {str(active)}\n🔴Disabled: {str(disabled)}\n🟢Online: {str(onlines)}"
                return text
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "sanaie":
            try:
                status_json = json.loads(self.r.post(self.url + "/server/status").text)['obj']
                cpu_percentage = str("{:.2f}".format(float(status_json['cpu'])))
                cpu_cores = str(status_json['cpuCores'])
                cpu_max_speed = str(int(status_json['cpuSpeedMhz'])) + "Mhz"
                memory = str(status_json['mem']['current'] // 1024 // 1024) + "/" + str(status_json['mem']['total'] // 1024 // 1024) + " MB"
                storage = str("{:.2f}".format(float(status_json['disk']['current'] / 1024 / 1024 / 1024))) + "/" + str("{:.2f}".format(float(status_json['disk']['total'] / 1024 / 1024 / 1024))) + " GB"
                x_ray = status_json['xray']['version']
                uptime = status_json['uptime']
                if uptime >= 86400:
                    uptime = str(uptime // 86400) + "d"
                else:
                    uptime = str(uptime // 3600) + "h"
                server_traffic = str("{:.2f}".format(float((status_json['netTraffic']['sent'] + status_json['netTraffic']['recv']) / 1024 / 1024 / 1024))) + " GB"

                s = self.r.post(self.url + "/panel/inbound/list").text
                obj = json.loads(s)['obj']
                active, disabled, onlines, clients_c, data_down, data_up = (0,)*6
                for i in range(len(obj)):
                    if obj[i].get('clientStats', None) is not None:
                        if len(obj[i]['clientStats']) >= 1:
                            data_list = obj[i]
                            data_up += data_list['up']
                            data_down += data_list['down']
                            clients_c += len(data_list['clientStats'])
                            clients = json.loads(data_list['settings'].replace('\\', ''))["clients"]
                            for n in range(len(clients)):
                                if (clients[n]['enable'] is True):
                                    if clients[n]['expiryTime'] != 0:
                                        if (int(str(clients[n]['expiryTime'])[:-3]) > int(time())) or (clients[n]['totalGB'] == 0) or ((data_list['clientStats'][n]['up'] + data_list['clientStats'][n]['down']) >= clients[n]['totalGB']):
                                            active += 1
                                        else:
                                            disabled += 1
                                    else:
                                        active += 1
                                else:
                                    disabled += 1
                up = float(str("{:.2f}".format(float(data_up // 1024 // 1024 / 1024))))
                down = float(str("{:.2f}".format(float(data_down // 1024 // 1024 / 1024))))
                clients_usage = str("{:.2f}".format(float(up + down))) + " GB"
                clients = clients_c
                text = f"🖥Host: {self.host}\nUptime: {uptime}\nX-ray version: {x_ray}\nCPU: {cpu_percentage}%\nCore/s: {cpu_cores}\nMax speed: {cpu_max_speed}\nRAM: {memory}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {str(clients)}\n✔️Active: {str(active)}\n🔴Disabled: {str(disabled)}\n🟢Online: {str(onlines)}"
                return text
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
            ssh_stdin.flush()
            dirty = Force_string(ssh_stdout).read().decode()
            cleaned = Clean_string(dirty)
            system_info = cleaned.split("Up Time:")[1].split("\n")[0]
            cpu = system_info.split("In use:")[2].replace(" ", "")
            ram = system_info.split("In use:")[1].replace(" ", "")
            uptime = system_info.split("In use:")[0].replace(" ", "")
            clients_info = cleaned.split("Online:")[1].split("\n")[0]
            clients = clients_info.split("Total:")[1].replace(" ", "")
            onlines = clients_info.split("◇ㅤexpired:")[0].replace(" ", "")
            disabled = clients_info.split("◇ㅤexpired:")[1].split("◇ㅤTotal:")[0].replace(" ", "")
            active = int(clients) - int(disabled)
            text = f"🖥Host: {self.host}\nCPU: {cpu}\nRAM: {ram}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {str(clients)}\n✔️Active: {str(active)}\n🔴Disabled: {str(disabled)}\n🟢Online: {str(onlines)}"
            return text

    def Panel_Short_info(self):
        server_traffic = 0
        clients_usage = 0
        counter = 1
        cpu = "?"
        ram = "?"
        storage = "?"
        if self.panel == "shahan":
            try:
                s = request_more(self.r, self.url + "/p/index.php")
                html = HTMLParser(s)
                for setr in html.css('small.pull-left'):
                    if counter == 1:
                        ram = setr.text()
                    elif counter == 2:
                        cpu = setr.text()
                    elif counter == 3:
                        storage = setr.text()
                    elif counter == 4:
                        if "گیگابایت" in setr.text():
                            server_traffic = str('{:.2f}'.format(float(float(((setr.text()).split("گیگابایت")[0]).replace(" ", ''))))) + " GB"
                        elif "ترابایت" in setr.text():
                            server_traffic = str('{:.2f}'.format(float(float(((setr.text()).split("ترابایت")[0]).replace(" ", ''))))) + " TB"
                    elif counter == 5:
                        if "گیگابایت" in setr.text():
                            clients_usage = str('{:.2f}'.format(float(float(((setr.text()).split("گیگابایت")[0]).replace(" ", ''))))) + " GB"
                        elif "ترابایت" in setr.text():
                            clients_usage = str('{:.2f}'.format(float(float(((setr.text()).split("ترابایت")[0]).replace(" ", ''))))) + " TB"
                        break
                    counter += 1
                info = []
                for data in html.css('span.info-box-number'):
                    info.append(data.text())
                onlines = info[1]
                if "کاربر" in onlines:
                    onlines = onlines.replace("کاربر", "").replace("\n", "").replace(" ", "")
                #Bool, status = self.IP_Check()
                stats = self.Stats()
                if "Error" in stats:
                    stats = "Update your Panel to get the stats"
                #t0 = f"\n\nIP Check: {status}\n{stats}"
                t0 = "\n\n" + stats
                Clients = str(info[0]).replace('\n', '').replace(' ', '')
                Active = str(info[2]).replace('\n', '').replace(' ', '')
                Disabled = str(info[3]).replace('\n', '').replace(' ', '')
                text = f'🖥Host: {self.host}\nCPU: {cpu}\nRAM: {ram}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {Clients}\n✔️Active: {Active}\n🔴Disabled: {Disabled}\n🟢Online: {str(onlines)}'
                return text + t0
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "rocket":
            try:
                s = self.r.get(self.url + "/dashboard").text
                html = HTMLParser(s)
                info = []
                for sec in html.css('h5'):
                    info.append(sec.text())
                clients = info[0]
                onlines = info[1]
                active = info[2]
                disabled = info[3]
                sys_info = []
                for sec in html.css('div.mt-2'):
                    if "%" in sec.text():
                        sys_info.append(sec.text())
                cpu = (sys_info[1]).replace("\n", "").replace("     ", "")
                ram = (sys_info[0]).replace("\n", "").replace("     ", "")
                storage = (sys_info[2]).replace("\n", "").replace("     ", "")
                band_info = []
                for sec in html.css("small"):
                    if sec.attributes.get("title", None) is not None:
                        if (sec.attributes['title'] == "دانلود") or (sec.attributes['title'] == "آپلود"):
                            band_info.append((sec.text()).replace(" ", "").replace("\n", "").replace(",", ""))
                server_traffic, clients_usage = get_traffic_rocket(band_info)
                text = f"🖥Host: {self.host}\nCPU: {cpu}\nRAM: {ram}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {str(clients)}\n✔️Active: {str(active)}\n🔴Disabled: {str(disabled)}\n🟢Online: {str(onlines)}"
                #Bool, status = self.IP_Check()
                #t0 = f"\n\nIP Check: {status}"
                t0 = ""
                return text + t0
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            try:
                s = self.r.get(self.url + "/cp/dashboard").text
                html = HTMLParser(s)
                info = []
                for sec in html.css('h6'):
                    info.append(sec.text())
                clients = (info[10]).replace("All User: ", "").replace("تمام کاربران: ", "")
                onlines = info[9]
                active = info[5]
                disabled = info[8]
                band_info = []
                for sec in html.css("h5"):
                    t = sec.text()
                    if ("Server" in t) or ("سرور" in t):
                        t = t.replace("Server", "").replace("سرور", "")
                    elif ("Client" in t) or ("کلاینت" in t):
                        t = t.replace("Client", "").replace("کلاینت", "")
                    band_info.append(t)
                server_traffic, clients_usage = get_traffic_xpanel(band_info)
                text = f"🖥Host: {self.host}\nCPU: {cpu}\nRAM: {ram}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {str(clients)}\n✔️Active: {str(active)}\n🔴Disabled: {str(disabled)}\n🟢Online: {str(onlines)}"
                #Bool, status = self.IP_Check()
                #t0 = f"\n\nIP Check: {status}"
                t0 = ""
                return text + t0
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "sanaie":
            try:
                status_json = json.loads(self.r.post(self.url + "/server/status").text)['obj']
                cpu_percentage = str("{:.2f}".format(float(status_json['cpu'])))
                cpu_cores = str(status_json['cpuCores'])
                cpu_max_speed = str(int(status_json['cpuSpeedMhz'])) + "Mhz"
                memory = str(status_json['mem']['current'] // 1024 // 1024) + "/" + str(status_json['mem']['total'] // 1024 // 1024) + " MB"
                storage = str("{:.2f}".format(float(status_json['disk']['current'] / 1024 / 1024 / 1024))) + "/" + str("{:.2f}".format(float(status_json['disk']['total'] / 1024 / 1024 / 1024))) + " GB"
                x_ray = status_json['xray']['version']
                uptime = status_json['uptime']
                if uptime >= 86400:
                    uptime = str(uptime // 86400) + "d"
                else:
                    uptime = str(uptime // 3600) + "h"
                server_traffic = str("{:.2f}".format(float((status_json['netTraffic']['sent'] + status_json['netTraffic']['recv']) / 1024 / 1024 / 1024))) + " GB"

                s = self.r.post(self.url + "/panel/inbound/list").text
                obj = json.loads(s)['obj']
                active, disabled, onlines, clients_c, data_down, data_up = (0,)*6
                for i in range(len(obj)):
                    if obj[i].get('clientStats', None) is not None:
                        if len(obj[i]['clientStats']) >= 1:
                            data_list = obj[i]
                            data_up += data_list['up']
                            data_down += data_list['down']
                            clients_c += len(data_list['clientStats'])
                            clients = json.loads(data_list['settings'].replace('\\', ''))["clients"]
                            for n in range(len(clients)):
                                if (clients[n]['enable'] is True):
                                    if clients[n]['expiryTime'] != 0:
                                        if (int(str(clients[n]['expiryTime'])[:-3]) > int(time())) or (clients[n]['totalGB'] == 0) or ((data_list['clientStats'][n]['up'] + data_list['clientStats'][n]['down']) >= clients[n]['totalGB']):
                                            active += 1
                                        else:
                                            disabled += 1
                                    else:
                                        active += 1
                                else:
                                    disabled += 1
                up = float(str("{:.2f}".format(float(data_up // 1024 // 1024 / 1024))))
                down = float(str("{:.2f}".format(float(data_down // 1024 // 1024 / 1024))))
                clients_usage = str("{:.2f}".format(float(up + down))) + " GB"
                clients = clients_c
                text = f"🖥Host: {self.host}\nUptime: {uptime}\nX-ray version: {x_ray}\nCPU: {cpu_percentage}%\nCore/s: {cpu_cores}\nMax speed: {cpu_max_speed}\nRAM: {memory}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {str(clients)}\n✔️Active: {str(active)}\n🔴Disabled: {str(disabled)}\n🟢Online: {str(onlines)}"
                return text
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
            ssh_stdin.flush()
            dirty = Force_string(ssh_stdout).read().decode()
            cleaned = Clean_string(dirty)
            system_info = cleaned.split("Up Time:")[1].split("\n")[0]
            cpu = system_info.split("In use:")[2].replace(" ", "")
            ram = system_info.split("In use:")[1].replace(" ", "")
            uptime = system_info.split("In use:")[0].replace(" ", "")
            clients_info = cleaned.split("Online:")[1].split("\n")[0]
            clients = clients_info.split("Total:")[1].replace(" ", "")
            onlines = clients_info.split("◇ㅤexpired:")[0].replace(" ", "")
            disabled = clients_info.split("◇ㅤexpired:")[1].split("◇ㅤTotal:")[0].replace(" ", "")
            active = int(clients) - int(disabled)
            text = f"🖥Host: {self.host}\nCPU: {cpu}\nRAM: {ram}\nStorage: {storage}\nServer Traffic: {str(server_traffic)}\nClients Traffic: {str(clients_usage)}\n👤Clients: {str(clients)}\n✔️Active: {str(active)}\n🔴Disabled: {str(disabled)}\n🟢Online: {str(onlines)}"
            return text

    def Count_Clients(self):
        if self.panel == "shahan":
            try:
                s = request_more(self.r, self.url + "/p/index.php")
                html = HTMLParser(s)
                info = []
                for data in html.css('span.info-box-number'):
                    info.append(data.text())
                return str(info[0]).replace("\n", "").replace(" ", "")
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "rocket":
            try:
                s = self.r.get(self.url + "/dashboard").text
                html = HTMLParser(s)
                info = []
                for sec in html.css('h5'):
                    info.append(sec.text())
                return str(info[0])
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            try:
                s = self.r.get(self.url + "/cp/dashboard").text
                html = HTMLParser(s)
                info = []
                for sec in html.css('h6'):
                    info.append(sec.text())
                return str((info[10]).replace("All User: ", "").replace("تمام کاربران: ", ""))
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "sanaie":
            try:
                s = self.r.post(self.url + "/panel/inbound/list").text
                obj = json.loads(s)['obj']
                clients_c = 0
                for i in range(len(obj)):
                    if obj[i].get('clientStats', None) is not None:
                        if len(obj[i]['clientStats']) >= 1:
                            data_list = obj[i]
                            data_up += data_list['up']
                            data_down += data_list['down']
                            clients_c += len(data_list['clientStats'])
                return clients_c
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            usernames, passwords, connection_limits, days, status = get_users_data_dragon(self.ssh)
            return str(len(usernames))

    def info(self):
        if self.panel == "shahan":
            try:
                s = request_more(self.r, self.url + "/p/index.php")
                html = HTMLParser(s)
                return Get_list_shahan(html)
            except Exception:
                print(traceback.format_exc())
                return [], [], [], [], [], [], [], [], [], [], [], 0, 0, False

        elif self.panel == "rocket":
            try:
                s = self.r.post(self.url + "/ajax/users/list").text
                if "<br" in s:
                    s = s.split("<br")[0]
                data = json.loads(s)
                text = self.Short_info()
                return Get_list_rocket(data, self.host, text, self.r, self.url)
            except Exception:
                print(traceback.format_exc())
                return [], [], [], [], [], [], [], [], [], [], [], 0, 0, False

        elif self.panel == "xpanel":
            try:
                s = self.r.get(self.url + "/cp/users").text
                html = HTMLParser(s)
                text = self.Short_info()
                return Get_list_xpanel(html, self.host, text, self.r, self.url)
            except Exception:
                print(traceback.format_exc())
                return [], [], [], [], [], [], [], [], [], [], [], 0, 0, False

        elif self.panel == "dragon":
            try:
                usernames, passwords, connection_limits, days_left, status = get_users_data_dragon(self.ssh)
                ips, usages, expires, ports, descriptions, traffics = ([] for i in range(6))
                for i in range(len(usernames)):
                    usages.append("0.0")
                    traffics.append("نامحدود")
                    ips.append(self.host)
                    if days_left[i] == "0":
                        expire = "منقضی شده"
                    else:
                        expire = (str(jdatetime.datetime.fromtimestamp(time() + (int(days_left[i]) * 86400))).split(" ")[0]).replace("-", "/")
                    expires.append(expire)

                return expires, connection_limits, usernames, passwords, ports, traffics, usages, days_left, status, ips, descriptions, 0, 0, True
            except Exception:
                print(traceback.format_exc())
                return [], [], [], [], [], [], [], [], [], [], [], 0, 0, False

    def Check_Premium(self):
        if self.panel == "shahan":
            try:
                s = self.r.get(self.url + "/p/setting.php").text
                html = HTMLParser(s)
                return check_premium_spliter(html)
            except Exception as e:
                return False, "Error: " + str(e)

    def Online_clients(self):
        users = []
        ips = []
        data = []
        if self.panel == "shahan":
            try:
                s = request_more(self.r, self.url + "/p/online.php")
                html = HTMLParser(s)
                for span in html.css('span.font-medium'):
                    data.append(span.text())
                for i in range(1, len(data) + 1, 2):
                    users.append(data[i - 1])
                    ips.append(data[i])
                return "Good", users, ips
            except Exception as e:
                return "Error: " + str(e), [], []

        elif self.panel == "rocket":
            try:
                s = self.r.get(self.url + "/users/online").text
                html = HTMLParser(s)
                for span in html.css('span'):
                    if "." in span.text():
                        ips.append(span.text())
                for td in html.css('td'):
                    data.append(td.text())
                for i in range(2, len(data), 5):
                    users.append(data[i - 1])
                if users == []:
                    s = self.r.post(self.url + "/ajax/users/list").text
                    if "<br" in s:
                        s = s.split("<br")[0]
                    datas = json.loads(s)
                    for data in datas['data']:
                        for i in range(len(data['online_users'])):
                            if data['online_users'][i].get("ip", None) is not None:
                                ips.append(data['online_users'][i]['ip'])
                                users.append(data['username'])
                return "Good", users, ips
            except Exception as e:
                return "Error: " + str(e), [], []

        elif self.panel == "xpanel":
            try:
                s = self.r.get(self.url + "/cp/online").text
                html = HTMLParser(s)
                for td in html.css('td'):
                    if "." in td.text():
                        ips.append((td.text()).split('Protocol')[0])
                for a in html.css('a'):
                    if a.attributes.get("href", None) is not None:
                        if "/online/user/" in a.attributes['href']:
                            users.append((a.attributes['href']).split("/online/user/")[1])
                return "Good", users, ips
            except Exception as e:
                return "Error: " + str(e), [], []

        elif self.panel == "dragon":
            try:
                usernames, passwords, connection_limits, days, status = get_users_data_dragon(self.ssh)
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                ssh_stdin.write('4\n')
                sleep(1)
                ssh_stdin.flush()
                dirty = Force_string(ssh_stdout).read().decode()
                cleaned = Clean_string(dirty)
                cleaned = cleaned.split('◇ㅤUser       ◇ㅤStatus     ◇ㅤConnection   ◇ㅤTime')[1].split('◇ ENTER  to return to  MENU!')[0]
                datas = cleaned.split("\n")
                for data in datas:
                    cache = data.split(" ")
                    cache = list(filter(None, cache))
                    if 4 == len(cache):
                        if cache[0] in usernames:
                            if cache[1] == "Online":
                                users.append(cache[0])
                                ips.append("127.0.0.1")
                ips_catched, users_catched = get_ips_of_users_dragon(self.ssh, users)
                if len(ips_catched) == len(users):
                    ips = ips_catched
                    users = users_catched
                return "Good", users, ips
            except Exception as e:
                return "Error: " + str(e), [], []

    def IP_Check(self):
        if self.panel == "shahan":
            for i in range(2):
                if i == 1:
                    port, username, password, panel, route_path, sshport, udgpw, remark = HOST_INFO(self.host)
                    Login(username, password, self.host, port, panel)
                    self.url, self.r = open_session(self.host, port)
                try:
                    s = self.r.get(self.url + "/p/checkip.php").text
                    html = HTMLParser(s)
                    count = 0
                    if "checkip" not in s:
                        raise
                    for td in html.css('td.checkip'):
                        try:
                            if "فیلتر شده" in td.text():
                                count += 1
                        except:
                            pass
                    if count >= 4:
                        return True, "Offline ❌"
                    else:
                        return False, "Online ✅"
                except Exception as e:
                    if i == 1:
                        return False, "Error: " + str(e)

        elif self.panel == "rocket":
            for i in range(2):
                if i == 1:
                    port, username, password, panel, route_path, sshport, udgpw, remark = HOST_INFO(self.host)
                    Login(username, password, self.host, port, panel)
                    self.url, self.r = open_session(self.host, port)
                try:
                    s = self.r.get(self.url + "/ajax/pages/filtering?_=" + str(int(time()))).text
                    datas = json.loads(s)
                    world = False
                    for data in datas:
                        if (data['flag'] != 'ir') and (world is False):
                            world = True
                        elif (data['flag'] == 'ir'):
                            if data['status'] == 'online':
                                return False, "Online ✅"
                    return True, "Offline ❌"
                except Exception as e:
                    if i == 1:
                        return False, "Error: " + str(e)

        elif self.panel == "xpanel":
            for i in range(2):
                if i == 1:
                    port, username, password, panel, route_path, sshport, udgpw, remark = HOST_INFO(self.host)
                    Login(username, password, self.host, port, panel)
                    self.url, self.r = open_session(self.host, port)
                try:
                    s = self.r.get(self.url + "/cp/checkip").text
                    html = HTMLParser(s)
                    checked = []
                    for div in html.css('div.col-6'):
                        if ("Online" in div.text()) or ("Filter" in div.text()):
                            checked.append((div.text()).replace(' ', "").replace('\n', ''))
                    if checked.count('Filter') >= 4:
                        return True, "Offline ❌"
                    else:
                        return False, "Online ✅"
                except Exception as e:
                    if i == 1:
                        return False, "Error: " + str(e)

        elif self.panel == "dragon":
            try:
                url = f"https://check-host.net/check-ping?host={self.host}&node={node1}&node={node2}&node={node3}&node={node4}&node={node5}&node={node6}"
                cmd = f"""curl -H 'Accept: application/json' \
                     '{url}'"""
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd)
                sleep(0.2)
                out = ssh_stdout.read().decode()
                data = json.loads(out)
                sleep(4)
                request_id = data['request_id']
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                headers = {'accept': 'application/json', 'user-agent': user_agent}
                data = requests.get("https://check-host.net/check-result/" + request_id, headers=headers)
                if data.status_code == 200:
                    results = json.loads(data.text)
                    try:
                        if check_host_json_results(results) is True:
                            return True, "Offline ❌"
                        else:
                            return False, "Online ✅"
                    except:
                        return False, "Error: Panel is okay but check host not available for now"
                else:
                    return False, f"Error: Check Host HTTP {str(data.status_code)}"
            except Exception as e:
                return False, "Error: " + str(e)

    def Stats(self):
        if self.panel == "shahan":
            try:
                s = self.r.get(self.url + "/p/serverstatus.php").text
                html = HTMLParser(s)
                IPv6 = "?"
                IPv4 = "?"
                stats = ""
                counter = 1
                for td in html.css('td.checkip'):
                    try:
                        if ":" in td.text():
                            IPv6 = td.text()
                        elif "." in td.text():
                            IPv4 = td.text()
                            break
                        if counter == 2:
                            if "غیرفعال" in td.text():
                                status = "✖️"
                            else:
                                status = "✔️"
                            stats += f"Premium: {status}"
                    except:
                        pass
                    counter += 1
                responde = (f"IPv6: {IPv6}\nIPv4: {IPv4}\n{stats}").replace("\n\n", "\n")
                return responde
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "rocket":
            return None

        elif self.panel == "xpanel":
            return None

        elif self.panel == "dragon":
            return None

    def Exist(self, user):
        if self.panel == "shahan":
            try:
                s = request_more(self.r, self.url + "/p/index.php")
                html = HTMLParser(s)
                usernames = Get_list_users_only_shahan(html)
                if user in usernames:
                    return "Good", True
                else:
                    return "Good", False
            except Exception as e:
                print("Error: " + str(e))
                return "Error: " + str(e), False

        elif self.panel == "rocket":
            try:
                s = self.r.post(self.url + "/ajax/users/list").text
                if "<br" in s:
                    s = s.split("<br")[0]
                data = json.loads(s)
                usernames = Get_list_users_only_rocket(data)
                if user in usernames:
                    return "Good", True
                else:
                    return "Good", False
            except Exception as e:
                print("Error: " + str(e))
                return "Error: " + str(e), False

        elif self.panel == "xpanel":
            try:
                s = self.r.get(self.url + "/cp/users").text
                html = HTMLParser(s)
                usernames = Get_list_users_only_xpanel(html)
                if user in usernames:
                    return "Good", True
                else:
                    return "Good", False
            except Exception as e:
                print("Error: " + str(e))
                return "Error: " + str(e), False

        elif self.panel == "dragon":
            try:
                usernames, passwords, connection_limits, days, status = get_users_data_dragon(self.ssh)
                if user in usernames:
                    return "Good", True
                else:
                    return "Good", False
            except Exception as e:
                print("Error: " + str(e))
                return "Error: " + str(e), False

    def Kill(self, user):
        if self.panel == "shahan":
            try:
                status, users, ips = self.Online_clients()
                if status == "Good":
                    if user in users:
                        s = self.r.get(self.url + "/p/online.php?username=" + user)
                        if s.status_code == 200:
                            users.remove(user)
                            return "Killed✅", users
                        else:
                            return "Error: " + str(s.status_code), []
                    else:
                        return "The user is not Online", users
                else:
                    return status, []
            except Exception as e:
                return "Error: " + str(e), []

        elif self.panel == "rocket":
            try:
                s = self.r.get(self.url + "/users/online").text
                html = HTMLParser(s)
                users = []
                data = []
                for td in html.css('td'):
                    data.append(td.text())
                for i in range(2, len(data), 5):
                    users.append(data[i - 1])
                pids = []
                for button in html.css('button'):
                    if button.attributes.get("data-pid", None) is not None:
                        if button.attributes['data-pid'] not in pids:
                            pids.append(button.attributes['data-pid'])
                if user in users:
                    pid = int(pids[users.index(user)])
                    payload = {"pids[]": pid}
                    s = self.r.post(self.url + "/ajax/users/kill-pid", data=payload)
                    if s.status_code == 200:
                        users.remove(user)
                        return "Killed✅", users
                    else:
                        return "Error: " + str(s.status_code), []
                else:
                    return "The user is not Online", users
                return "Good", users
            except Exception as e:
                return "Error: " + str(e), []

        elif self.panel == "xpanel":
            try:
                users = []
                s = self.r.get(self.url + "/cp/online").text
                html = HTMLParser(s)
                for a in html.css('a'):
                    if a.attributes.get("href", None) is not None:
                        if "/online/user/" in a.attributes['href']:
                            users.append((a.attributes['href']).split("/online/user/")[1])
                if user in users:
                    s = self.r.get(self.url + "/cp/online/user/" + user)
                    if s.status_code <= 302:
                        users.remove(user)
                        return "Killed✅", users
                    else:
                        return "Error: " + str(s.status_code), []
                else:
                    return "The user is not Online", users
                return "Good", users
            except Exception as e:
                return "Error: " + str(e), []

        elif self.panel == "dragon":
            try:
                status, users, ips = self.Online_clients()
                if user in users:
                    cmd = f"ps -e -o user,pid | grep '^{user} ' | awk" + " '{ print $2 }' | xargs"
                    ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd)
                    out = ssh_stdout.read().decode()
                    if out not in ['\n', '']:
                        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(f"pkill -u {user}\n")
                        users.remove(user)
                        return "Killed✅", users 
                    else:
                        return "The user is not Online", users
                else:
                    return "The user is not Online", users
            except Exception as e:
                return "Error: " + str(e), []

    def Auto_remove(self, days):
        if self.panel == "shahan":
            try:
                days = int(days)
            except:
                return "Error: only numbers"
            payload = {
                'rmexpday': days,
                'removeexpired': 'removeexpired'
            }
            try:
                s = self.r.post(self.url + "/p/setting.php", data=payload)
                if s.status_code == 200:
                    return "Done ✔️"
                else:
                    return "Error: " + str(s.status_code)
            except Exception as e:
                return "Error: " + str(e)

    def Message(self, bannermsg):
        if self.panel == "shahan":
            payload = {
                "banner": bannermsg,
                "bannermsg": "bannermsg"
            }
            try:
                s = self.r.post(self.url + "/p/setting.php", data=payload)
                if s.status_code == 200:
                    return "Done ✔️"
                else:
                    return "Error: " + str(s.status_code)
            except Exception as e:
                return "Error: " + str(e)

    def Gift(self, days):
        if self.panel == "shahan":
            try:
                days = int(days)
            except:
                return "Error: only numbers"
            payload = {
                "giftday": days,
                "giftuser": "giftuser"
            }
            try:
                s = self.r.post(self.url + "/p/setting.php", data=payload)
                if s.status_code == 200:
                    return "Done ✔️"
                else:
                    return "Error: " + str(s.status_code)
            except Exception as e:
                return "Error: " + str(e)

    def Limit_status(self):
        if self.panel == "shahan":
            try:
                s = self.r.post(self.url + "/p/setting.php").text
                html = HTMLParser(s)
                for inp in html.css('input.form-control'):
                    if "غیرفعال" == inp.attributes['name']:
                        return False
                    elif "فعال" == inp.attributes['name']:
                        return True
            except Exception as e:
                return False
            return False

    def Limit_on(self):
        if self.panel == "shahan":
            payload = {
                "limitusers": "changeport"
            }
            try:
                status = self.Limit_status()
                if status is False:
                    s = self.r.post(self.url + "/p/setting.php", data=payload)
                    if s.status_code == 200:
                        return "Done ✔️"
                    else:
                        return "Error: " + str(s.status_code)
                else:
                    return "🟢Already ON"
            except Exception as e:
                return "Error: " + str(e)

    def Limit_off(self):
        if self.panel == "shahan":
            payload = {
                "notlimitusers": "changeport"
            }
            try:
                status = self.Limit_status()
                s = self.r.post(self.url + "/p/setting.php", data=payload)
                if s.status_code == 200:
                    if status is False:
                        return "🔴Already OFF"
                    else:
                        return "Done ✔️"
                else:
                    return "Error: " + str(s.status_code)
            except Exception as e:
                return "Error: " + str(e)

    def Delete(self, uname):
        if self.panel == "shahan":
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

        elif self.panel == "rocket":
            try:
                s = self.r.post(self.url + "/ajax/users/list").text
                if "<br" in s:
                    s = s.split("<br")[0]
                datas = json.loads(s)
                for data in datas['data']:
                    if uname == data['username']:
                        s = self.r.delete(self.url + "/ajax/users/" + str(data['id']))
                        if s.status_code == 200:
                            return "❌Deleted"
                        else:
                            return "Error: 404 HTTP"
                return "Error: 403 not found"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            try:
                server_msg, status = self.Exist(uname)
                if "Error" not in server_msg:
                    if status is True:
                        s = self.r.get(self.url + "/cp/user/delete/" + uname)
                        if s.status_code <= 302:
                            return "❌Deleted"
                        else:
                            return "Error: 404 HTTP"
                    else:
                        return "Error: 403 HTTP the user not found"
                else:
                    return server_msg
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            try:
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                ssh_stdin.write('3\n')
                ssh_stdin.flush()
                sleep(0.05)
                ssh_stdin.write('1\n')
                ssh_stdin.flush()
                dirty = Force_string(ssh_stdout).read().decode()
                cleaned = Clean_string(dirty)
                cleaned = cleaned.split('LIST OF USERS:')[1].split('Enter or select a user')[0]
                usernames, numbers = ([] for i in range(2))
                datas = cleaned.split("\n")
                for data in datas:
                    cache = data.split(" ")
                    cache = list(filter(None, cache))
                    if len(cache) == 5:
                        usernames.append(cache[4])
                        if cache[1][0] == "0":
                            numbers.append(cache[1].replace("0", ""))
                        else:
                            numbers.append(cache[1])
                if uname in usernames:
                    ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                    ssh_stdin.write('3\n')
                    ssh_stdin.flush()
                    sleep(0.05)
                    ssh_stdin.write('1\n')
                    ssh_stdin.flush()
                    ssh_stdin.write(f'{numbers[usernames.index(uname)]}\n')
                    sleep(0.3)
                    ssh_stdin.flush()
                    dirty = Force_string(ssh_stdout).read().decode()
                    cleaned = Clean_string(dirty)
                    if f"User {uname} successfully removed!" in cleaned:
                        return "❌Deleted"
                    elif "User is empty or invalid!" in cleaned:
                        return "Error: User is empty or invalid!"
                    else:
                        return "Error: unknown"
                else:
                    return f"Error: The user {uname} does not exist"
            except Exception as e:
                return "Error: " + str(e)

    def Create(self, uname, passw, connection_limit, days, traffic, description, first, DP):
        if DP == "on":
            drop = True
        else:
            drop = False
        if self.panel == "shahan":
            if traffic == 0:
                traffic = ""
            if first is True:
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
                    'newuserfirstlogin': 'newuserfirstlogin',
                    'newuserinfo': description,
                    'newusersubmit': 'ثبت'
                }
            else:
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
                    'newuserinfo': description,
                    'newusersubmit': 'ثبت'
                }
            try:
                s = self.r.post(self.url + "/p/newuser.php", data=payload)
                DROP = ""
                dropbear = ""
                if s.status_code == 200:
                    if traffic == '':
                        traffic = "نامحدود"
                    try:
                        s = self.r.get(self.url + "/p/index.php").text
                        html = HTMLParser(s)
                        PASSW, TRAFFIC, CONNECTION_LIMIT, IP, DAYS, STATUS, USAGE, DATE, DESCRIPTION, PORT, UDGPW, DROP, TUIC = Get_user_info_shahan(html, uname)
                    except:
                        IP = self.host
                        PORT, UDGPW, DROP = self.Ports()
                    if UDGPW == "":
                        PORT, UDGPW, DROP = self.Ports()
                    if (drop is True):
                        if DROP == "":
                            PORT, UDGPW, DROP = self.Ports()
                        dropbear = f"\nDropbear Port: <code>{DROP}</code>"
                    return f"SSH Host : <code>{IP}</code>\nPort : <code>{PORT}</code>{dropbear}\nUdgpw : <code>{UDGPW}</code>\nUsername : <code>{uname}</code>\nPassword : <code>{passw}</code>\n\nConnection limit: {str(connection_limit)}\nDays : {str(days)}\nTraffic: {str(traffic)}"
                else:
                    return "Error: Code " + str(s.status_code)
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "rocket":
            '''
            >>> ex = "1402-07-24"
            >>> d = jdatetime.strptime(ex, "%Y-%m-%d")
            >>> d = jdatetime.datetime.strptime(ex, "%Y-%m-%d")
            >>> jdatetime.datetime(1402, 7, 24, 0, 0)
            >>> d.timestamp()
            1697401800.0
            '''
            if first is True:
                Date = ""
                payload = {
                    'username': uname,
                    'password': passw,
                    'email': "",
                    'mobile': "",
                    'limit_users': connection_limit,
                    'traffic': traffic,
                    'expiry_type': 'days',
                    'exp_days': days,
                    'exp_date': '',
                    'desc': description,
                }
            else:
                Date = (str(jdatetime.datetime.fromtimestamp(time() + (days * 86400))).split(" ")[0]).replace("-", "/")
                payload = {
                    'username': uname,
                    'password': passw,
                    'email': "",
                    'mobile': "",
                    'limit_users': connection_limit,
                    'traffic': traffic,
                    'expiry_type': 'date',
                    'exp_days': "",
                    'exp_date': Date,
                    'desc': description
                }
            try:
                s = self.r.post(self.url + "/ajax/users", data=payload)
                try:
                    if "تاریخ پایان نمی تواند کوچکتر از تاریخ فعلی باشد" in str(json.loads(s.text)):
                        Date = (str(jdatetime.datetime.fromtimestamp(time() + ((days + 1) * 86400))).split(" ")[0]).replace("-", "/")
                        payload = {'username': uname, 'password': passw, 'email': "", 'mobile': "", 'limit_users': connection_limit, 'traffic': traffic, 'expiry_type': 'date', 'exp_days': "", 'exp_date': Date, 'desc': description}
                        s = self.r.post(self.url + "/ajax/users", data=payload)
                except:
                    pass
                if s.status_code == 200:
                    if traffic == 0:
                        traffic = "نامحدود"
                    port, udgpw, dropbear = self.Ports()
                    if (port == "") or (udgpw == ""):
                        s = self.r.post(self.url + "/ajax/users/list").text
                        if "<br" in s:
                            s = s.split("<br")[0]
                        PASS, TRAFFIC, CONNECTION_LIMIT, DAYS, STATUS, USAGE, UID, KIND, DATE, DESCRIPTION, PUBLIC_LINK, port, udgpw = Get_user_info_rocket(json.loads(s), uname, self.r, self.url)
                    return f"SSH Host : <code>{self.host}</code>\nPort : <code>{port}</code>\nUdgpw : <code>{udgpw}</code>\nUsername : <code>{uname}</code>\nPassword : <code>{passw}</code>\n\nConnection limit: {str(connection_limit)}\nDays : {str(days)}\nExpiry : {Date}\nTraffic: {str(traffic)}"
                else:
                    return "Error: Code " + str(s.status_code)
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            if first is True:
                Date = ""
                payload = {
                    '_token': get_token(self.r.get(self.url + "/cp/users").text),
                    'username': uname,
                    'password': passw,
                    'email': '',
                    'mobile': '',
                    'multiuser': connection_limit,
                    'connection_start': days,
                    'traffic': traffic,
                    'type_traffic': 'gb',
                    'expdate': '',
                    'desc': description,
                }
            else:
                days -= 1
                Date = str(datetime.fromtimestamp(time() + (days * 86400))).split(" ")[0]
                payload = {
                    '_token': get_token(self.r.get(self.url + "/cp/users").text),
                    'username': uname,
                    'password': passw,
                    'email': '',
                    'mobile': '',
                    'multiuser': connection_limit,
                    'connection_start': '',
                    'traffic': traffic,
                    'type_traffic': 'gb',
                    'expdate': Date,
                    'desc': description,
                }
            try:
                s = self.r.post(self.url + "/cp/users", data=payload)
                if s.status_code <= 302:
                    if traffic == 0:
                        traffic = "Unlimited♾"
                    port, udgpw, dropbear = self.Ports()
                    try:
                        if "-" in Date:
                            dt = jdatetime.datetime.strptime(Date, '%Y-%m-%d')
                            Date = str(jdatetime.date.fromgregorian(day=dt.day, month=dt.month, year=dt.year))
                    except:
                        pass
                    return f"SSH Host : <code>{self.host}</code>\nPort : <code>{port}</code>\nUdgpw : <code>{udgpw}</code>\nUsername : <code>{uname}</code>\nPassword : <code>{passw}</code>\n\nConnection limit: {str(connection_limit)}\nDays : {str(days)}\nExpiry : {Date}\nTraffic: {str(traffic)}"
                else:
                    return "Error: Code " + str(s.status_code)
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            try:
                #if "BOT - TEST" in description:
                    #write 2 the test minutes
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                ssh_stdin.write('1\n')
                ssh_stdin.flush()
                ssh_stdin.write(f'{uname}\n')
                ssh_stdin.flush()
                ssh_stdin.write(f'{passw}\n')
                ssh_stdin.flush()
                ssh_stdin.write(f'{str(days)}\n')
                ssh_stdin.flush()
                ssh_stdin.write(f'{str(connection_limit)}\n')
                sleep(0.05)
                ssh_stdin.flush()
                dirty = Force_string(ssh_stdout).read().decode()
                cleaned = Clean_string(dirty)
                if "◈─────⪧ SSH ACCOUNT ⪦─────◈" in cleaned:
                    if ("DropBear ⌁" in cleaned) and (drop is True):
                        DROP = cleaned.split("DropBear ⌁")[1].split("\n")[0].replace(" ", "")
                        dropbear = f"\nDropbear Port: <code>{DROP}</code>"
                    else:
                        dropbear = ""
                    port, udgpw, DROP = self.Ports()
                    traffic = "نامحدود"
                    Date = (str(jdatetime.datetime.fromtimestamp(time() + (int(days) * 86400))).split(" ")[0]).replace("-", "/")
                    return f"SSH Host : <code>{self.host}</code>\nPort : <code>{port}</code>{dropbear}\nUdgpw : <code>{udgpw}</code>\nUsername : <code>{uname}</code>\nPassword : <code>{passw}</code>\n\nConnection limit: {str(connection_limit)}\nDays : {str(days)}\nExpiry : {Date}\nTraffic: {str(traffic)}"
                else:
                    return "Error: cannot create the user try another username"
            except Exception as e:
                return "Error: " + str(e)

    def Password(self, password):
        if self.panel == "shahan":
            if "گیگابایت" in self.traffic:
                Traffic = (self.traffic).replace("گیگابایت", "")
                try:
                    Traffic = int(Traffic)
                except:
                    Traffic = float(Traffic)
            elif "نامحدود" in self.traffic:
                Traffic = ""
            if self.Date == "فعال نشده":
                stat, file = self.Backup()
                self.days = get_real_days_shahan(stat, file, self.days, self.uname)
            payload = {
                'edituserusername': self.uname,
                'edituserpassword': password,
                'editusermobile': '',
                'edituseremail': '',
                'editusertraffic': Traffic,
                'editusermultiuser': self.connection_limit,
                'edituserfinishdate': self.days,
                'edituserreferral': '',
                'edituserinfo': self.description,
                'editusersubmit': 'ثبت'
            }
            try:
                s = self.r.post(self.url + "/p/newuser.php", data=payload)
                if s.status_code == 200:
                    return f"🟢 Successfully changed to {password}"
                else:
                    return "Error: 404"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "rocket":
            if "گیگابایت" in self.traffic:
                Traffic = (self.traffic).replace("گیگابایت", "")
                try:
                    Traffic = int(Traffic)
                except:
                    Traffic = float(Traffic)
            elif "نامحدود" in self.traffic:
                Traffic = 0
            if self.kind == "days":
                payload = {
                    'password': password,
                    'email': "",
                    'mobile': "",
                    'limit_users': self.connection_limit,
                    'traffic': Traffic,
                    'expiry_type': self.kind,
                    'exp_days': self.days,
                    'exp_date': "",
                    'desc': self.description
                }
            else:
                payload = {
                    'password': password,
                    'email': "",
                    'mobile': "",
                    'limit_users': self.connection_limit,
                    'traffic': Traffic,
                    'exp_days': self.days,
                    'exp_date': self.Date,
                    'desc': self.description
                }
            try:
                s = self.r.put(self.req + str(self.uid), data=payload)
                if s.status_code == 200:
                    return f"🟢 Successfully changed to {password}"
                else:
                    return "Error: 404"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            if "گیگابایت" in self.traffic:
                Traffic = (self.traffic).replace("گیگابایت", "")
                try:
                    Traffic = int(Traffic)
                except:
                    Traffic = float(Traffic)
            elif "نامحدود" in self.traffic:
                Traffic = 0
            if 'فعال' in self.status:
                status = "active"
            else:
                status = "deactive"
            if self.kind == "days":
                payload = {
                    '_token': self.token,
                    'username': self.uname,
                    'password': password,
                    'email': '',
                    'mobile': '',
                    'multiuser': self.connection_limit,
                    'traffic': Traffic,
                    'type_traffic': 'gb',
                    'expdate': '',
                    'activate': status,
                    'desc': self.description,
                    'submit': 'submit'
                }
            else:
                payload = {
                    '_token': self.token,
                    'username': self.uname,
                    'password': password,
                    'email': '',
                    'mobile': '',
                    'multiuser': self.connection_limit,
                    'traffic': Traffic,
                    'type_traffic': 'gb',
                    'expdate': self.Date,
                    'activate': status,
                    'desc': self.description,
                    'submit': 'submit'
                }
            try:
                s = self.r.post(self.req, data=payload)
                if s.status_code <= 302:
                    return f"🟢 Successfully changed to {password}"
                else:
                    return "Error: 404"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            try:
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                ssh_stdin.write('7\n')
                sleep(0.05)
                ssh_stdin.flush()
                dirty = Force_string(ssh_stdout).read().decode()
                cleaned = Clean_string(dirty)
                cleaned = cleaned.split('LIST OF USERS AND THEIR PASSWORDS:')[1].split('Enter or select a user')[0]
                usernames, numbers = ([] for i in range(2))
                datas = cleaned.split("\n")
                for data in datas:
                    cache = data.split(" ")
                    cache = list(filter(None, cache))
                    if len(cache) == 8:
                        usernames.append(cache[4])
                        if cache[1][0] == "0":
                            numbers.append(cache[1].replace("0", ""))
                        else:
                            numbers.append(cache[1])
                if self.uname in usernames:
                    ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                    ssh_stdin.write('7\n')
                    ssh_stdin.flush()
                    sleep(0.05)
                    ssh_stdin.write(f'{numbers[usernames.index(self.uname)]}\n')
                    ssh_stdin.flush()
                    sleep(0.01)
                    ssh_stdin.write(f'{password}\n')
                    ssh_stdin.flush()
                    sleep(0.1)
                    dirty = Force_string(ssh_stdout).read().decode()
                    cleaned = Clean_string(dirty)

                    if f"User password {self.uname} has been changed to: {password}" in cleaned:
                        return f"User password {self.uname} has been changed to: {password}"
                    elif "User is empty or invalid!" in cleaned:
                        return "Error: User is empty or invalid!"
                    else:
                        return "Error: unknown error"
                else:
                    return f"Error: The user {self.uname} does not exist"
            except Exception as e:
                return "Error: " + str(e)

    def Username(self, username):
        if self.panel == "shahan":
            if "گیگابایت" in self.traffic:
                Traffic = int((self.traffic).replace("گیگابایت", ""))
            elif "نامحدود" in self.traffic:
                Traffic = ""
            payload = {
                'edituserusername': username,
                'edituserpassword': self.passwd,
                'editusermobile': '',
                'edituseremail': '',
                'editusertraffic': Traffic,
                'editusermultiuser': self.connection_limit,
                'edituserfinishdate': self.days,
                'edituserreferral': '',
                'edituserinfo': self.description,
                'editusersubmit': 'ثبت'
            }
            try:
                s = self.r.post(self.url + "/p/newuser.php", data=payload)
                if s.status_code == 200:
                    return f"🟢 Successfully changed to {username}"
            except Exception as e:
                return "Error: " + str(e)

    def Update(self, traffic, days, connection_limit):
        if self.panel == "shahan":
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
                'edituserinfo': self.description,
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

        elif self.panel == "rocket":
            Traffic = int(traffic)
            if connection_limit == 0:
                connection_limits = 9999
            if self.kind == "days":
                payload = {
                    'password': self.passwd,
                    'email': "",
                    'mobile': "",
                    'limit_users': connection_limit,
                    'traffic': Traffic,
                    'expiry_type': self.kind,
                    'exp_days': days,
                    'exp_date': "",
                    'desc': self.description
                }
            else:
                Date = (str(jdatetime.datetime.fromtimestamp(time() + (days * 86400))).split(" ")[0]).replace("-", "/")
                payload = {
                    'password': self.passwd,
                    'email': "",
                    'mobile': "",
                    'limit_users': connection_limit,
                    'traffic': Traffic,
                    'exp_days': days,
                    'exp_date': Date,
                    'desc': self.description
                }
            try:
                if self.r.put(self.req + str(self.uid), data=payload).status_code == 200:
                    if self.status == "فعال":
                        return "🟢Updated successfully"
                    else:
                        if self.r.put(self.req + str(self.uid) + '/toggle-active').status_code == 200:
                            return "🟢Updated successfully and Activated successfully"
                        else:
                            return "Error: Updated but not activated"
                else:
                    return "Error: 404 HTTP"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            Traffic = int(traffic)
            Date = str(datetime.fromtimestamp(time() + (days * 86400))).split(" ")[0]
            payload = {
                '_token': self.token,
                'username': self.uname,
                'password': self.passwd,
                'email': '',
                'mobile': '',
                'multiuser': connection_limit,
                'traffic': Traffic,
                'type_traffic': 'gb',
                'expdate': Date,
                'activate': "active",
                'desc': self.description,
                'submit': 'submit'
            }
            try:
                s = self.r.post(self.req, data=payload)
                if s.status_code <= 302:
                    return "🟢Updated successfully and Activated successfully"
                else:
                    return "Error: 404"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            try:
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                ssh_stdin.write('5\n')
                ssh_stdin.flush()
                sleep(0.1)
                dirty = Force_string(ssh_stdout).read().decode()
                cleaned = Clean_string(dirty)
                cleaned = cleaned.split('LIST OF USERS AND EXPIRY DATE:')[1].split('Enter or select a user')[0]
                usernames, numbers = ([] for i in range(2))
                datas = cleaned.split("\n")
                for data in datas:
                    cache = data.split(" ")
                    cache = list(filter(None, cache))
                    if len(cache) == 7:
                        usernames.append(cache[4])
                        if cache[1][0] == "0":
                            numbers.append(cache[1].replace("0", ""))
                        else:
                            numbers.append(cache[1])
                if self.uname in usernames:
                    ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                    ssh_stdin.write('5\n')
                    ssh_stdin.flush()
                    sleep(0.1)
                    ssh_stdin.write(f'{numbers[usernames.index(self.uname)]}\n')
                    ssh_stdin.flush()
                    sleep(2)
                    date = str(datetime.fromtimestamp(time() + (int(days) * 86400))).split(" ")[0].split("-")
                    fixed_date = f"{date[2]}/{date[1]}/{date[0]}"
                    ssh_stdin.write(f'{fixed_date}\n')
                    ssh_stdin.flush()
                    sleep(1)
                    ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("menu")
                    ssh_stdin.write('6\n')
                    ssh_stdin.flush()
                    sleep(0.1)
                    ssh_stdin.write(f'{numbers[usernames.index(self.uname)]}\n')
                    ssh_stdin.flush()
                    sleep(0.5)
                    ssh_stdin.write(f'{str(connection_limit)}\n')
                    ssh_stdin.flush()
                    sleep(0.5)
                    dirty = Force_string(ssh_stdout).read().decode()
                    cleaned = Clean_string(dirty)
                    if f"Limit applied to the user {self.uname} foi {str(connection_limit)}" in cleaned:
                        return "🟢Updated successfully"
                    elif "User is empty or invalid!" in cleaned:
                        return "Error: User is empty or invalid!"
                    else:
                        return "Error: unknown error"
                else:
                    return f"Error: The user {self.uname} does not exist"
            except Exception as e:
                return "Error: " + str(e)

    def Reset_traffic(self):
        if self.panel == "shahan":
            payload = {'edituserusername': self.uname, 'resettrafficsubmit': 'submitted H a m e d A p'}
            try:
                if self.r.post(self.req, data=payload).status_code == 200:
                    return "🟢Reseted successfully"
                else:
                    return "Error: 404 HTTP"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "rocket":
            try:
                if self.r.put(self.req + str(self.uid) + '/reset-traffic').status_code == 200:
                    return "🟢Reseted successfully"
                else:
                    return "Error: 404 HTTP"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            try:
                if self.r.get(self.url + "/cp/user/reset/" + self.uname).status_code <= 302:
                    return "🟢Reseted successfully"
                else:
                    return "Error: 404 HTTP"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            return "Error: traffic reset not supported"

    def Enable(self):
        if self.panel == "shahan":
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

        elif self.panel == "rocket":
            if self.status == "فعال":
                return "🟢 Already Enabled"
            else:
                try:
                    if self.r.put(self.req + str(self.uid) + '/toggle-active').status_code == 200:
                        return "🟢 Enabled successfully"
                    else:
                        return "Error: 404 HTTP"
                except Exception as e:
                    return "Error: " + str(e)

        elif self.panel == "xpanel":
            if self.status == "فعال":
                return "🟢 Already Enabled"
            else:
                try:
                    if self.r.get(self.url + "/cp/user/active/" + self.uname).status_code <= 302:
                        return "🟢 Enabled successfully"
                    else:
                        return "Error: 404 HTTP"
                except Exception as e:
                    return "Error: " + str(e)

        elif self.panel == "dragon":
            return "Error: not supported"

    def Disable(self):
        if self.panel == "shahan":
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

        elif self.panel == "rocket":
            if self.status == "فعال":
                try:
                    if self.r.put(self.req + str(self.uid) + '/toggle-active').status_code == 200:
                        return "🔴 Disabled successfully"
                    else:
                        return "Error: 404 HTTP"
                except Exception as e:
                    return "Error: " + str(e)
            else:
                return "🔴 Already Disabled"

        elif self.panel == "xpanel":
            if self.status == "فعال":
                try:
                    if self.r.get(self.url + "/cp/user/deactive/" + self.uname).status_code <= 302:
                        return "🔴 Disabled successfully"
                    else:
                        return "Error: 404 HTTP"
                except Exception as e:
                    return "Error: " + str(e)
            else:
                return "🔴 Already Disabled"

        elif self.panel == "dragon":
            return "Error: not supported"

    def User_info(self, DROP, TUIC):
        if (DROP == "on") and (self.dropbear != ""):
            drop = f"\nDropbear Port : <code>{self.dropbear}</code>"
        else:
            drop = ""
        if self.panel == "shahan":
            try:
                if (TUIC == "on") and (self.tuic != ""):
                    tuic = f"\nTuic5 : <code>{self.tuic}</code>"
                else:
                    tuic = ""
                port = self.SPort
                udgpw = self.Sudgpw
                if udgpw == "":
                    port, udgpw, self.dropbear = self.Ports()
                if (DROP == "on") and (self.dropbear == ""):
                    port, udgpw, self.dropbear = self.Ports()
                    drop = f"\nDropbear Port : <code>{self.dropbear}</code>"
                if str(self.days) == "9999":
                    days = "Unlimited♾"
                else:
                    days = str(self.days)
                usage = self.usage + " GB"
                status = self.status
                if "فعال" == status:
                    status += "🟢"
                else:
                    status += "🔴"
                return f"SSH Host : <code>{self.ip}</code>\nPort : <code>{port}</code>{drop}\nUdgpw : <code>{udgpw}</code>\nUsername : <code>{self.uname}</code>\nPassword : <code>{self.passwd}</code>\n\nConnection limit: {str(self.connection_limit)}\nDays : {days}\nتاریخ انقضا : {self.Date}\nTraffic: {str(self.traffic)}\nUsage: {str(usage)}\nStatus: {status}{tuic}"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "rocket":
            try:
                port, udgpw, dropbear = self.Ports()
                if (port == "") or (udgpw == ""):
                    port = self.SPort
                    udgpw = self.Sudgpw
                usage = self.usage + " GB"
                status = self.status
                if "فعال" == status:
                    status += "🟢"
                else:
                    status += "🔴"
                return f"SSH Host :  <code>{self.ip}</code>\nPort : <code>{port}</code>{drop}\nUdgpw : <code>{udgpw}</code>\nUsername : <code>{self.uname}</code>\nPassword : <code>{self.passwd}</code>\n\nConnection limit: {str(self.connection_limit)}\nDays : {str(self.days)}\nExpiry : {self.Date}\nTraffic: {str(self.traffic)}\nUsage: {str(usage)}\nStatus: {status}\nPublic Link: {self.public_link}"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            try:
                port, udgpw, dropbear = self.Ports()
                if str(self.days) == "9999":
                    days = "Unlimited♾ or not started yet"
                else:
                    days = str(self.days)
                usage = self.usage + " GB"
                status = self.status
                if "فعال" == status:
                    status += "🟢"
                else:
                    status += "🔴"
                try:
                    if "-" in self.Date:
                        dt = jdatetime.datetime.strptime(self.Date, '%Y-%m-%d')
                        date = str(jdatetime.date.fromgregorian(day=dt.day, month=dt.month, year=dt.year))
                    else:
                        date = self.Date
                except:
                    date = self.Date
                return f"SSH Host : <code>{self.ip}</code>\nPort : <code>{port}</code>{drop}\nUdgpw : <code>{udgpw}</code>\nUsername : <code>{self.uname}</code>\nPassword : <code>{self.passwd}</code>\n\nConnection limit: {str(self.connection_limit)}\nDays : {days}\nExpiry : {date}\nTraffic: {str(self.traffic)}\nUsage: {str(usage)}\nStatus: {status}"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            try:
                port, udgpw, dropbear = self.Ports()
                date = (str(jdatetime.datetime.fromtimestamp(time() + (int(self.days) * 86400))).split(" ")[0]).replace("-", "/")
                traffic = "نامحدود"
                return f"SSH Host : <code>{self.ip}</code>\nPort : <code>{port}</code>{drop}\nUdgpw : <code>{udgpw}</code>\nUsername : <code>{self.uname}</code>\nPassword : <code>{self.passwd}</code>\n\nConnection limit: {str(self.connection_limit)}\nDays : {self.days}\nExpiry : {date}\nTraffic: {traffic}\nStatus: {self.status}"
            except Exception as e:
                return "Error: " + str(e)

    def Update_Traffic(self, traffic):
        if self.panel == "shahan":
            if traffic == 0:
                traffic = ''
            elif traffic <= -1:
                traffic = -traffic
            else:
                if "گیگابایت" in self.traffic:
                    Traffic = (self.traffic).replace("گیگابایت", "")
                    try:
                        traffic = int(Traffic) + traffic
                    except:
                        traffic = float(Traffic) + traffic
            if self.Date == "فعال نشده":
                stat, file = self.Backup()
                self.days = get_real_days_shahan(stat, file, self.days, self.uname)
            payload = {
                'edituserusername': self.uname,
                'edituserpassword': self.passwd,
                'editusermobile': '',
                'edituseremail': '',
                'editusertraffic': traffic,
                'editusermultiuser': self.connection_limit,
                'edituserfinishdate': self.days,
                'edituserreferral': '',
                'edituserinfo': self.description,
                'editusersubmit': 'ثبت'
            }
            try:
                if self.r.post(self.req, data=payload).status_code == 200:
                    return "Updated"
                else:
                    return "Error: 404 HTTP"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "rocket":
            if traffic <= -1:
                traffic = -traffic
            if "گیگابایت" in self.traffic:
                Traffic = (self.traffic).replace("گیگابایت", "")
                try:
                    traffic = int(Traffic) + traffic
                except:
                    traffic = float(Traffic) + traffic
            Traffic = int(traffic)
            if self.kind == "days":
                payload = {
                    'password': self.passwd,
                    'email': "",
                    'mobile': "",
                    'limit_users': self.connection_limit,
                    'traffic': Traffic,
                    'expiry_type': self.kind,
                    'exp_days': self.days,
                    'exp_date': "",
                    'desc': self.description
                }
            else:
                payload = {
                    'password': self.passwd,
                    'email': "",
                    'mobile': "",
                    'limit_users': self.connection_limit,
                    'traffic': Traffic,
                    'exp_days': self.days,
                    'exp_date': self.Date,
                    'desc': self.description
                }
            try:
                s = self.r.put(self.req + str(self.uid), data=payload)
                if s.status_code == 200:
                    return "Updated"
                else:
                    return "Error: 404"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "xpanel":
            if traffic <= -1:
                traffic = -traffic
            if "گیگابایت" in self.traffic:
                Traffic = (self.traffic).replace("گیگابایت", "")
                try:
                    traffic = int(Traffic) + traffic
                except:
                    traffic = float(Traffic) + traffic
            Traffic = int(traffic)
            if 'فعال' in self.status:
                status = "active"
            else:
                status = "deactive"
            if self.kind == "days":
                payload = {
                    '_token': self.token,
                    'username': self.uname,
                    'password': self.passwd,
                    'email': '',
                    'mobile': '',
                    'multiuser': self.connection_limit,
                    'traffic': Traffic,
                    'type_traffic': 'gb',
                    'expdate': '',
                    'activate': status,
                    'desc': self.description,
                    'submit': 'submit'
                }
            else:
                payload = {
                    '_token': self.token,
                    'username': self.uname,
                    'password': self.passwd,
                    'email': '',
                    'mobile': '',
                    'multiuser': self.connection_limit,
                    'traffic': Traffic,
                    'type_traffic': 'gb',
                    'expdate': self.Date,
                    'activate': status,
                    'desc': self.description,
                    'submit': 'submit'
                }
            try:
                s = self.r.post(self.req, data=payload)
                if s.status_code <= 302:
                    return "Updated"
                else:
                    return "Error: 404"
            except Exception as e:
                return "Error: " + str(e)

        elif self.panel == "dragon":
            return "Error: not supported"
