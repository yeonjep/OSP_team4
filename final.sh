#!/bin/bash

#install "Chrome"

unzip final_team.zip


wget https://dl.google.com/linux/direct/google-chromestable_current_amd64.deb

sudo dpkg -i google-chrome-stable_current_amd64.deb

#install "chromedriver"

sudo apt-get install chromium-chromedriver

#other program install

python3 -m pip install --upgrade pip
pip install xlrd
apt-get install xvfb -y
pip install pyvirtualdisplay
pip install selenium
sudo apt-get install python3-pandas

cd final_team

chmod 755 app.py
./app.py
