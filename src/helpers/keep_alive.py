from logging import Logger
import os
from flask import Flask
from threading import Thread

from helpers.validate import is_development

app = Flask("")


@app.route("/")
def home():
    Logger.info("pinged")
    return "Pong"


if is_development():

    def run():
        app.run(host="0.0.0.0", port=8080)

else:

    def run():
        from waitress import serve

        port = int(os.environ.get("PORT", 8080))
        serve(app, host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()
