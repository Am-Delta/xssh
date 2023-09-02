echo "Running ..."

sudo apt install python3
sudo apt install pip
sudo apt install git
sudo apt-get install screen
pip install termcolor
pip install pyrogram
pip install bs4
pip install requests
pip install tgcrypto
pip install qrcode
pip install random2
pip install cryptocompare
pip install selectolax

mkdir /root/botCh

pkill python3

mv /root/bot/Pannels.txt /root/botCh
mv /root/bot/backup /root/botCh
mv /root/bot/ssh /root/botCh
mv /root/bot/cache /root/botCh
mv /root/bot/logs.txt /root/botCh
mv /root/bot/All.txt /root/botCh
mv /root/bot/irr.txt /root/botCh
mv /root/bot/ssh.db /root/botCh
mv /root/bot/data.json /root/botch

rm -r /root/bot

#git clone "https://github.com/Am-Delta/bot.git" /root/bot/
git clone "https://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@github.com/Am-Delta/bot.git" /root/bot/

mv /root/botCh/Pannels.txt /root/bot
mv /root/botCh/backup /root/bot
mv /root/botCh/ssh /root/bot
mv /root/botCh/cache /root/bot
mv /root/botCh/logs.txt /root/bot
mv /root/botCh/All.txt /root/bot
mv /root/botCh/irr.txt /root/bot
mv /root/botCh/ssh.db /root/bot
mv /root/botCh/data.json /root/bot


cd /root/bot

clear

python3 run.py
