from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)

@app.route("/")
def login():
    return render_template("portal.html")

if __name__ == '__main__':
    app.run()
