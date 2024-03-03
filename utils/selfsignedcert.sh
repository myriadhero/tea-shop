#! /usr/bin/bash
sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout nginxcert.key -out nginxcert.crt