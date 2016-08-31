#!/usr/bin/python
import os
import sys
import logging
# append current dir to module path
cwd = os.getcwd()
install_root = os.path.join(cwd, 'geo_poetry_server')
sys.path.append(install_root)
# assuming this module is in the same dir as passenger_wsgi, this now works!
from geo_poetry_server import app

# create a logfile in the current directory
logfilename = os.path.join(install_root, 'logs', 'passenger_wsgi.log')
# configure the logging
logging.basicConfig(filename=logfilename, level=logging.INFO)
logging.info("Running %s", sys.executable)

def application(environ, start_response):
    logging.info("Application called:")
    logging.info("environ: %s", str(environ))
    results = []
    try:
        results = app(environ, start_response)
        logging.info("App executed successfully")
    except Exception, inst:
        logging.exception("Error: %s", str(type(inst)))
    logging.info("Application call done")
    return results