import csv
import os
import datetime
from models import *
import string
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets


def userIsExist(user, file):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == user:
                return True

    return False

def generate_code():
    result = ""
    for i in range(6):
        number = random.randint(0,9)
        result += str(number)
    return result


def add_user(file, username, email, password):
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ids = [int(row["id"]) for row in reader]
        new_id = max(ids) + 1 if ids else 1

    with open(file, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "username", "email", "password"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow({
            "id": new_id,
            "username": username,
            "email": email,
            "password": password
        })

    os.mkdir(f"users/{username}")

    open(f"users/{username}/about.txt", "w")

    open(f"users/{username}/notify.txt", "w")
    with open(f"users/{username}/followers.csv", "w") as f:
        f.write("id,username\n")
    with open(f"users/{username}/info.csv", "w") as f:
        f.write("admin,verified,refcode,activates\n")
        f.write(f"False,False,{generate_code()},0")
    with open(f"users/{username}/subscribes.csv", "w") as f:
        f.write("id,username\n")

    return new_id
#
# add_user("users/users.csv", "iva", "bas", "dasd")

def check_password(file,user,password):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == user:
                if row["password"] == password:
                    return True
                else:
                    return False


def get_id(file, username):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return row["id"]

    return False

def get_username(file, id):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] == id:
                return row["username"]

    return False

def read_posts(file, offset=0, limit=10):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)


    start = max(total - offset - limit, 0)
    end = total - offset

    sliced_rows = rows[start:end]

    posts = []
    for row in sliced_rows:
        posts.append(Post(
            row["id"],
            row["author"],
            row["title"],
            row["text"],
            row["day"]
        ))


    return reversed(posts)


def get_user_posts(file, username):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)





        posts = []
        for row in rows:

            if row["author"] == username:
                posts.append(Post(
                    row["id"],
                    row["author"],
                    row["title"],
                    row["text"],
                    row["day"]
                ))


        return reversed(posts)

def make_post(file, author, text, title):

    with open(file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ids = [int(row["id"]) for row in reader]
        new_id = max(ids) + 1 if ids else 1

    with open(file, "a") as f:
        fieldnames = ["id", "author", "title","text", "day"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        today = datetime.datetime.today()

        day = today.day
        month = today.month
        year = today.year

        hour = today.hour
        minute = today.minute


        writer.writerow({
            "id": new_id,
            "author": author,
            "title":title,
            "text": text,
            "day": f"{day}/{month}/{year} - {hour}:{minute}",
        })




def strong_password(password):

    NOALLOWED = "{}[]().,/\\|"

    if len(password) < 8:
        return "Password must be longer than 8"

    if not any(char.isalpha() for char in password):
        return "Password must contain symbols"

    if not any(char.isdigit() for char in password):
        return "Password must contain digits"

    if any(char in NOALLOWED for char in password):
        return "Password cannot contain not allowed symbols"

    return True

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def delete_temp_user(file, username):
    with open(file, newline='', encoding='utf-8') as f:
        rows = [row for row in csv.reader(f) if row[0] != username]

    with open(file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def temp_user_exist(file, username):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return True
    return False


def temp_user(file, username, email,password):
    with open(file, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["username", "email", "password", "code"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow({
            "username": username,
            "email": email,
            "password": password,
            "code":generate_code()
        })

def tempdata_from_name(file, username):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return row["email"], row["password"], row["code"]




def spam(email, large_number):
    print("Start sending email...")

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    EMAIL_SENDER = "skitt.noreply@gmail.com"
    EMAIL_PASSWORD = "ylvxipadsacawdascasdassfcsqcjgobqesdw"
    EMAIL_RECEIVER = email
    SUBJECT = "Skitt registration"



 
    MESSAGE = f"""
        <html>
            <body>
                <p>Your code for registration on Skitt</p>
                <p style="font-size: 100px; font-weight: bold;">{large_number}</p>
            </body>
        </html>
    """


    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(MESSAGE, "html"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
            print("List send succssecfull!")

    except Exception as e:
        print(f"Error to sending: {e}")
        return "Помилка при надсиланні"

def get_post(file, post_id):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)


        for row in rows:
            if row["id"] == post_id:
                return Post(
                row["id"],
                row["author"],
                row["title"],
                row["text"],
                row["day"]
            )


        return reversed(posts)


def read_replyes(file, id):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        replyes = []
        for row in rows:
            if row['postid'] == id:
                replyes.append(Reply(
                    row["author"],
                    row["text"],
                    row["day"]
                ))


        return reversed(replyes)

def make_reply(file, postid, author, text):
    with open(file, "a") as f:
        fieldnames = ["postid", "author", "text", "day"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        today = datetime.datetime.today()

        day = today.day
        month = today.month
        year = today.year

        hour = today.hour
        minute = today.minute

        writer.writerow({
            "postid": postid,
            "author": author,
            "text": text,
            "day": f"{day}/{month}/{year} - {hour}:{minute}",
        })




def generate_hash(file, id):
    with open(file, "a") as f:
        fieldnames = ["id", "hash"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        hash_key = secrets.token_hex(32)
        writer.writerow({"id":id, "hash":hash_key})

        return hash_key



def check_hash(file, id, hash):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] == id:
                return row["hash"] == hash

def get_hash(file, id):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] == id:
                return row["hash"]


def update_user_description(username, des):
    with open(f"users/{username}/about.txt", "w") as f:
        f.write(des)

def get_user_description(username):
    with open(f"users/{username}/about.txt", "r") as f:
        return f.readline()

def get_user_info(username):
    with open(f"users/{username}/info.csv", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            return {"admin":row["admin"],"verified":row["verified"],"refcode":row["refcode"], "activates":row["activates"]}

def subscribe(file,user, king):
    with open(f"users/{user}/subscribes.csv", "a") as f:
        fieldnames = ["id","username"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writerow({"id":get_id(file, king), "username":king})

    with open(f"users/{king}/followers.csv", "a") as f:
        fieldnames = ["id", "username"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writerow({"id": get_id(file, user), "username": user})


def user_is_follower(user, king):
    with open(f"users/{king}/followers.csv", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["username"] == user:
                return True

    return False

def unsubscribe(user, king):

    subscribes_path = f"users/{user}/subscribes.csv"
    with open(subscribes_path, "r", newline='') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if row["username"] != king]

    with open(subscribes_path, "w", newline='') as f:
        fieldnames = ["id", "username"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


    followers_path = f"users/{king}/followers.csv"
    with open(followers_path, "r", newline='') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if row["username"] != user]

    with open(followers_path, "w", newline='') as f:
        fieldnames = ["id", "username"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_subscribes(username):
    subs = []
    with open(f"users/{username}/subscribes.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            subs.append(User(row["id"], row["username"]))
    return subs



print(get_subscribes("skittle"))


def get_followers(username):
    follow = []
    with open(f"users/{username}/followers.csv", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            follow.append(User(row["id"], row["username"]))
    return follow


def are_friends(user1, user2):

    user1_is_sub = False
    user2_is_sub = False

    with open(f"users/{user1}/followers.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == user2:
                user1_is_sub = True

    with open(f"users/{user2}/followers.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == user1:
                user2_is_sub = True

    return user1_is_sub and user2_is_sub
