from flask import Flask, render_template, request, session, url_for, redirect
import hashlib
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'secret'


class User:
    def __init__(self, firstname, lastname, email, password):
        self.fisrtname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password


def checkMail(email):
    Mailregex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(Mailregex, email)):
        return True
    else:
        return False


@app.route('/adduser', methods=['POST'])
def adduser():
    UserToAdd = User(request.form['fn'], request.form['nm'],
                     request.form['email'], request.form['pwd'])
    if(checkMail(UserToAdd.email) == False):
        return redirect(url_for('signup'))
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email=?", (UserToAdd.email,))
    rows = cur.fetchall()
    print(rows)
    if rows:
        return 'Email no longer available'
    pwdhash = hashlib.md5(UserToAdd.password.encode())
    cur.execute(
        "INSERT INTO users (firstname,lastname,email,password) VALUES (?,?,?,?)", (UserToAdd.fisrtname, UserToAdd.lastname, UserToAdd.email, pwdhash.hexdigest()))
    con.commit()
    cur.close()
    return redirect(url_for('signin'))


@ app.route('/connectProcess',  methods=['POST'])
def connectProcess():
    UserToConnect = User(
        None, None, request.form['email'], request.form['pwd'])
    if(checkMail(UserToConnect.email) == False):
        return redirect(url_for('signup'))
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    pwdhash = hashlib.md5(UserToConnect.password.encode())
    cur.execute(
        "SELECT * FROM users WHERE email=? and password=?", (UserToConnect.email, pwdhash.hexdigest()))
    rows = cur.fetchall()
    if rows:
        session['status'] = True
        session['id'] = rows[0][0]
        session['firstname'] = rows[0][1]
        session['lastname'] = rows[0][2]
        session['email'] = UserToConnect.email
        return redirect(url_for('modify'))
    else:
        session['status'] = False
        return redirect(url_for('signup'))


@ app.route('/connect')
def connect():
    return render_template('connect.html')


@ app.route('/modifyProcess', methods=['POST'])
def modifyProcess():
    if not 'status' in session or session['status'] == False:
        return render_template('signup.html')
    UserToModify = User(None, None, request.form['email'], None)
    if(checkMail(UserToModify.email) == False):
        return redirect(url_for('modify'))
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET email=? WHERE id=?", (UserToModify.email,  session['id']))
    con.commit()
    cur.close()
    con.close()
    session['email'] = UserToModify.email
    return redirect(url_for('modify'))


@ app.route('/modify')
def modify():
    if not 'status' in session or session['status'] == False:
        return redirect(url_for('signup'))
    return render_template('modify.html')


@ app.route('/logout')
def logout():
    if not 'status' in session or session['status'] == False:
        return redirect(url_for('signup'))
    elif session['status'] == True:
        session['status'] = False
        del session['id']
        del session['firstname']
        del session['lastname']
        del session['email']
        return redirect(url_for('signup'))


@ app.route('/signup')
def signup():
    return render_template('signup.html')


@ app.route('/signin')
def signin():
    if not 'status' in session or session['status'] == False:
        return render_template('connect.html')
    elif session['status'] == True:
        return redirect(url_for('modify'))


@ app.route('/')
def home():
    if not 'status' in session or session['status'] == False:
        return redirect(url_for('signup'))
    elif session['status'] == True:
        return redirect(url_for('modify'))


if __name__ == '__main__':
    app.run()
