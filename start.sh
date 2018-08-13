#!/bin/bash
echo >>logs/server.log
echo >>logs/server.log
echo "-----------------------------------------------" >>logs/server.log
date >>logs/server.log
echo >>logs/server.log
export FLASK_APP=geo_poetry_server.py
flask run --host=0.0.0.0 &>>logs/server.log

