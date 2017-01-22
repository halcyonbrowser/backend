#!/bin/sh

: '
sed 's/main$/main universe/' -i /etc/apt/sources.list
apt-get update
apt-get upgrade -y

apt-get install -y build-essential xorg libssl-dev libxrender-dev wget gdebi openssl
wget http://download.gna.org/wkhtmltopdf/0.12/0.12.3/wkhtmltox-0.12.3_linux-generic-amd64.tar.xz
tar -xJf wkhtmltox-0.12.3_linux-generic-amd64.tar.xz
cd wkhtmltox
chown root:root bin/wkhtmltopdf
cp -r * /usr/
'
apt-get update && apt-get install -y wkhtmltopdf
