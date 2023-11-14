import json
import requests
from random import randint
from unidecode import unidecode
from selectolax.parser import HTMLParser

API_main_address = "http://hd.ladokpro.pw:5000/usd"

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
headers_json = {"Content-Type": "application/json"}
headers = {"user-agent": user_agent}


base_plisio_url = "https://plisio.net/api/v1/"


def check_valid_api_plisio(API):
    forced = "?api_key=" + API
    url = base_plisio_url + "operations" + forced
    try:
        r = requests.get(url, headers=headers_json)
    except Exception as e:
        return False, "Error: " + str(e)

    if r.status_code == 200:
        return True, "Good"
    elif r.status_code == 401 or r.status_code == 403:
        return False, "Error: API Authentication Error"
    else:
        return False, "Error: " + str(r.status_code)


def new_invoice_plisio(API, amount):
    order = str(randint(12345, 95325))
    url = f"{base_plisio_url}invoices/new?source_currency=USD&source_amount={amount}&order_number={order}&order_name=buy{order}&api_key={API}"
    try:
        r = requests.get(url, headers=headers_json)
    except Exception as e:
        return "Error: " + str(e), "", "", 0, False
    if r.status_code == 200:
        data = json.loads(r.text)
        if data['status'] == "success":
            data = data['data']
            txn_id = data['txn_id']
            invoice_url = data['invoice_url']
            invoice_total_sum = data['invoice_total_sum']
            return "Good", txn_id, invoice_url, invoice_total_sum, True
        else:
            return "Error: " + data['status'], "", "", 0, False
    else:
        return "Error: " + str(r.status_code), "", "", 0, False


def check_status_invoice_plisio(API, txn_id):
    forced = "?api_key=" + API
    url = base_plisio_url + "operations/" + txn_id + forced
    try:
        r = requests.get(url, headers=headers_json)
    except Exception as e:
        return "Error: " + str(e), "", False
    if r.status_code == 200:
        data = json.loads(r.text)
        if data['status'] == "success":
            data = data['data']
            return data['status'], data.get("tx_url", None), True
        else:
            return "Error: " + data['status'], "", False
    else:
        return "Error: " + str(r.status_code), "", False


def check_valid_perfect_money(account_id, passphrase):
    URL = f'https://perfectmoney.com/acct/balance.asp?AccountID={account_id}&PassPhrase={passphrase}&'
    try:
        text = ""
        r = requests.get(URL)
        if r.status_code == 200:
            html = HTMLParser(r.text)
            for data in html.css('input'):
                if data.attributes.get("name", None) is not None:
                    if "ERROR" == data.attributes['name']:
                        return False, "Error: " + data.attributes['value']
                    else:
                        text += f"{data.attributes['name']} | {data.attributes['value']}\n"
            return True, text
        else:
            return False, "Error: HTTP " + str(r.status_code)
    except Exception as e:
        return False, "Error: " + str(e)


def get_U_perfect_money(account_id, passphrase):
    URL = f'https://perfectmoney.com/acct/balance.asp?AccountID={account_id}&PassPhrase={passphrase}&'
    try:
        r = requests.get(URL)
        if r.status_code == 200:
            html = HTMLParser(r.text)
            for data in html.css('input'):
                if data.attributes.get("name", None) is not None:
                    if "ERROR" == data.attributes['name']:
                        return False, "Error: " + data.attributes['value']
                    elif "U" == data.attributes['name'][0]:
                        return True, data.attributes['name']
            return False, "Error: not found API error"
        else:
            return False, "Error: HTTP " + str(r.status_code)
    except Exception as e:
        return False, "Error: " + str(e)


def validate_perfect_money_voucher(account_id, passphrase, ev_number, ev_code):
    url = "https://perfectmoney.com/acct/ev_activate.asp"
    try:
        status, Payee_Account = get_U_perfect_money(account_id, passphrase)
        if status is True:
            data = {
                "AccountID": account_id,
                "PassPhrase": passphrase,
                "ev_number": ev_number,
                "ev_code": ev_code,
                "Payee_Account": Payee_Account
            }
            r = requests.post(url, data=data)
            html = HTMLParser(r.text)
            VOUCHER_NUM = None
            for data in html.css('input'):
                if data.attributes.get("name", None) is not None:
                    if "ERROR" == data.attributes['name']:
                        return False, "Error: " + data.attributes['value'], 0.0
                    elif "VOUCHER_NUM" == data.attributes['name']:
                        VOUCHER_NUM = data.attributes['value']
                    elif "VOUCHER_AMOUNT" == data.attributes['name']:
                        VOUCHER_AMOUNT = float(data.attributes['value'])
            if VOUCHER_NUM is not None:
                return True, VOUCHER_NUM, VOUCHER_AMOUNT
            else:
                return False, "Error: not found", 0.0
        else:
            return False, Payee_Account, 0.0
    except Exception as e:
        return False, "Error: " + str(e), 0.0


def check_valid_zarinpal(name):
    try:
        url = f"https://zarinp.al/api/v4/personalLink/{name}.json"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return True, "Good"
        else:
            return False, "Error: HTTP " + str(r.status_code)
    except Exception as e:
        return False, "Error: " + str(e)


def check_valid_idpay(name):
    try:
        url = "https://idpay.ir/" + name
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return True, "Good"
        else:
            return False, "Error: HTTP " + str(r.status_code)
    except Exception as e:
        return False, "Error: " + str(e)


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
            "user-agent": user_agent
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
