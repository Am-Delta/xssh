echo "Running ..."

sudo apt install python3
sudo apt install pip
sudo apt install git
pip install pyrogram
pip install random2
pip install qrcode
pip install cryptocompare
pip install tgcrypto
pip install selectolax
pip install bs4
pip install requests
pip install termcolor
pip install Unidecode
sudo apt install python3-random2
y
sudo apt install python3-qrcode
y
sudo apt install python3-bs4
y
sudo apt install python3-requests
y
sudo apt install python3-termcolor
y

mkdir /root/botCh

pkill -9 python3
pkill -9 python

mv /root/bot/Pannels.txt /root/botCh
mv /root/bot/backup /root/botCh
mv /root/bot/ssh /root/botCh
mv /root/bot/cache /root/botCh
mv /root/bot/logs.txt /root/botCh
mv /root/bot/All.txt /root/botCh
mv /root/bot/ssh.db /root/botCh
mv /root/bot/data.json /root/

rm -r /root/bot

#git clone "https://github.com/Am-Delta/bot.git" /root/bot/
git clone "https://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@github.com/Am-Delta/bot.git" /root/bot/

mv /root/botCh/Pannels.txt /root/bot
mv /root/botCh/backup /root/bot
mv /root/botCh/ssh /root/bot
mv /root/botCh/cache /root/bot
mv /root/botCh/logs.txt /root/bot
mv /root/botCh/All.txt /root/bot
mv /root/botCh/ssh.db /root/bot
mv /root/data.json /root/bot/

rm -r /root/botCh

cd /root/bot

clear

chmod 664 /root/bot/
chmod 664 /usr/local/lib/

python3 run.py

echo -ne '\n\n'
