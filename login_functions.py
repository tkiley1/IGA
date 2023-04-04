from distutils.util import execute
import sqlite3, smtplib, ssl, os, secrets
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import hashlib, datetime


KEY = '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'

'''
Function to register a new user

 username: string
 password: hashed string

 return: string error / success code

 The return value is passed back to the frontend, and displayed as the message element
'''
def new_user_reg(username, password, email):


    # Common code to open a connection to the database
    try:
        conn = sqlite3.connect('golf.db')
    except:
        return "Failed to connect to database - try again."

    # Code to ensure the accounts table exists, important for first deployment of the app
    c = conn.cursor()
    execute_string = "CREATE TABLE if not exists ACCOUNTS (UNAME STR, PASSWORD STR, EMAIL STR, DATE_CREATED STR, CONFIRMED STR, CONFIRMATION STR)"
    c.execute(execute_string)

    # On new user registration, we need to ensure that the username or email isn't already taken.
    execute_string = f"SELECT * FROM ACCOUNTS WHERE UNAME = '{username}'"
    c.execute(execute_string)

    un_collision = len(c.fetchall())

    execute_string = f"SELECT * FROM ACCOUNTS WHERE EMAIL = '{email}'"
    c.execute(execute_string)

    email_collision = len(c.fetchall())

    if un_collision + email_collision == 0:
        # If the username is free, insert the account username and password into the accounts table, and create a fresh entry into the playerstats table.
        confirm_string = secrets.token_urlsafe(16)
        send_welcome_email(email, username, confirm_string)
        user_date = datetime.date.today()
        
        entry_string = f"INSERT INTO ACCOUNTS (UNAME, PASSWORD, EMAIL, DATE_CREATED, CONFIRMED, CONFIRMATION) VALUES ('{username}','{password}', '{email}', '{user_date}', 'no', '{confirm_string}')"
        conn.execute(entry_string)
        conn.commit()
        conn.close()
        return 'SUCCESS'


    return "Username or email already taken - try a different one"

'''
Function to send a welcome email

email: string (email, validated on frontend)

user: string username

return: none

'''
def send_welcome_email(to_email, user, confirm_string):
    #TODO: update link once hosted
    message_content = f"""\
    <h1>Welcome to the Invaders Golf Association!</h1>
    <br><br>
    Hi {user}, thanks for signing up!<br>
    Please confirm your email by clicking here: http://127.0.0.1/confirm/{confirm_string}
    <br><br>
    Cheers,<br>
    The IGA Team

    """

    message = Mail(
    subject = "Welcome to IGA!",
    #TODO: make new email
    from_email = 'solringonturnone@gmail.com',
    to_emails = to_email,
    html_content = message_content)

    try:
        sg = SendGridAPIClient(KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


#Function to reset a user's password
#
# username: string
# password: hashed string
#
# return: string error / success code
#
# The return value is passed back to the frontend, and displayed as the message element
#
def password_reset(username, password):

    # Common code to open a connection to the database
    try:
        conn = sqlite3.connect('golf.db')
    except:
        return "Failed to connect to database - try again."

    #delete the user row, then reinsert with new password. (I haven't learned how to edit a row yet)
    c = conn.cursor()
    execute_string = f"delete from ACCOUNTS where UNAME='{username}'"
    c.execute(execute_string)
    conn.commit()

    execute_string = f"INSERT INTO ACCOUNTS (UNAME, PASSWORD) VALUES ('{username}','{password}')"
    c.execute(execute_string)

    conn.commit()
    conn.close()

    return "SUCCESS"

####
#Standard user login function
#
#username: string
#
#password: string(md5 hash)
#
#Return value: string (SUCCESS, Incorrect username or password)
#
#The return value is passed back to the frontend, and displayed as the message element
####
def user_login(username, password):

    # Common code to open a connection to the database
    try:
        conn = sqlite3.connect('golf.db')
    except:
        return "Failed to connect to database - try again."

    # Check to see if the username entered exists in the accounts table
    c = conn.cursor()

    execute_string = f"SELECT CONFIRMED FROM ACCOUNTS WHERE UNAME = '{username}'"
    try:
        c.execute(execute_string)
    except:
        return "Failed to connect to database - try again."
    data = c.fetchall()
    print(data)
    if data == [] or data[0][0] == 'no':
        return"Please confirm email before signing in."

    execute_string = f"SELECT * FROM ACCOUNTS WHERE UNAME = '{username}'"
    c.execute(execute_string)
    data = c.fetchall()
    if len(data) == 0:
        conn.close()
        return "Incorrect username or password."
    
    # Check to see if password and password confirmation match
    if str(password) == str(data[0][1]):

        conn.close()
        return "SUCCESS"

    # Close database connection
    conn.close()

    return "Incorrect username or password."

#Function to add a new deck for a user

# username: string
# deckname: string
# 
# Return value: string (SUCCESS, Incorrect username or password)
#
# The return value is passed back to the frontend, and displayed as the message element
#

def pw_recover(email):

    # Common code to open a connection to the database
    try:
        conn = sqlite3.connect('golf.db')
    except:
        return "Failed to connect to database - try again."

    c = conn.cursor()
    execute_string = f"SELECT * FROM ACCOUNTS WHERE EMAIL = '{email}'"
    c.execute(execute_string)
    data = c.fetchall()
    if len(data) == 0:
        conn.close()
        #returning success for everything as we do not want to give out information on registered emails
        return "SUCCESS"

    user = data[0][0]
    tmp_password = secrets.token_urlsafe(8)
    password_reset(user,hashlib.md5(tmp_password.encode()).hexdigest())
    message_content = f"""\
    <h1>EDH Tracker Temporary Password</h1>
    <br><br>
    Hi {user},<br><br> Try to remember your password next time!<br> Your temporary password is: {tmp_password}
    <br><br>
    Cheers,<br>
    The EDH Tracker Team

    """

    message = Mail(
    subject = "EDH Tracker Temporary Password",
    from_email = 'solringonturnone@gmail.com',
    to_emails = email,
    html_content = message_content)

    try:
        sg = SendGridAPIClient(KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


def confirm_user_account(confirm_string):
    # Common code to open a connection to the database
    try:
        conn = sqlite3.connect('golf.db')
    except:
        return "Failed to connect to database - try again."

    c = conn.cursor()
    execute_string = f"UPDATE ACCOUNTS SET CONFIRMED = 'yes' WHERE CONFIRMATION = '{confirm_string}'"
    c.execute(execute_string)
    conn.commit()
    conn.close()

    return "Account Validated!"