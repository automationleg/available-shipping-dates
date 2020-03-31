#!/bin/sh

docker run -it --rm --name selenium-docker -v "/etc/openhab2/html/sklepy_charmonogram":/ python check_apimarket.py
