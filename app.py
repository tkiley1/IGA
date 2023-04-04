from operator import methodcaller
from pickle import GET
from flask import Flask, render_template, redirect, send_file, flash, session, request
from flask_cors import CORS, cross_origin
from forms import *
from login_functions import *
import hashlib
import json
import ssl


app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['SECRET_KEY'] = "IGA"
#context = ssl.SSLContext()
#context.load_cert_chain("/home/solringonturnone/cert.pem","/home/solringonturnone/key.pem")

@app.route('/')
@app.route('/index', methods=['GET','POST'])
@cross_origin(supports_credentials = True)
def hello():
    if "user" not in session:
        return redirect('login')
    #TODO: Build home page
    return render_template('home.html')

#TODO: use this as a download for the rulebook
@app.route("/sample.txt")
def sample_download():
    if "user" not in session:
        return "Not Authorized."
    return send_file("templates/sample.txt")

@app.route("/confirm/<confirm_string>")
def confirm_user(confirm_string):
    message = confirm_user_account(confirm_string)
    return message
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    message = ''
    if form.validate_on_submit():
        message = user_login(form.user_name.data, hashlib.md5(form.password.data.encode()).hexdigest())
        if message == 'SUCCESS':
            session['user'] = form.user_name.data
            flash("Login Successful")
            return redirect('index')
    
    return render_template('login.html', form=form, message=message)

@app.route('/pwrecover', methods=['GET','POST'])
def pwrecover():
    form = PasswordRecovery()
    message = ''

    if form.validate_on_submit():
        message = pw_recover(form.email.data)
        if message == 'SUCCESS':
            return redirect('login')

    return render_template('pwrecover.html', form=form, message=message)

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = SignupForm()
    message = ''
    if form.validate_on_submit():
        #open database
        #check for user entry
        #create user entry
        #hash password
        #commit & close DB
        if hashlib.md5(form.password.data.encode()).hexdigest() == hashlib.md5(form.vpassword.data.encode()).hexdigest():
            message = new_user_reg(form.user_name.data, hashlib.md5(form.password.data.encode()).hexdigest(), form.email.data)
            if message=='SUCCESS':
                session['user'] = form.user_name.data
                flash("Welcome!")
                return redirect('/login')
        else:
            message = "Passwords do not match."
        
    return render_template('signup.html', form=form, message=message)

@app.route('/pwreset', methods=['GET','POST'])
def pwreset():

    if "user" not in session:
        return redirect('login')
    form = PasswordResetForm()
    message = ''

    #validate old password to ensure security
    if form.validate_on_submit():
        message = user_login(session['user'], hashlib.md5(form.current_password.data.encode()).hexdigest())

        if message != 'SUCCESS':
            return render_template('pwreset.html', form=form, message=message)

        if hashlib.md5(form.new_password.data.encode()).hexdigest() == hashlib.md5(form.confirm_new_password.data.encode()).hexdigest():
            message = password_reset(session['user'], hashlib.md5(form.new_password.data.encode()).hexdigest())
            if message == 'SUCCESS':
                return render_template('pwreset.html', form=PasswordResetForm(), message=message)

    return render_template('pwreset.html', form=form, message=message)




@app.route('/logout', methods={'GET'})
def logout():
    session.pop("user", None)
    return redirect('login')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="80")
    #app.run(host="0.0.0.0", port="443", ssl_context=context)