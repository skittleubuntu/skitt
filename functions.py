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

from static import USERS_DB, POSTS_DB, HASH_DB, CHATS_DB


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

def read_posts(file, offset=0, limit=10, stop_at_id=None):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)


    rows = rows[::-1]


    if stop_at_id is not None:
        for i, row in enumerate(rows):
            if row["id"] == str(stop_at_id):

                rows = rows[:i+1]
                break


    sliced_rows = rows[offset:offset + limit]

    posts = []
    for row in sliced_rows:
        posts.append(Post(
            int(row["id"]),
            row["author"],
            row["title"],
            row["text"],
            row["day"]
        ))

    return posts



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
    EMAIL_PASSWORD = "ylvxipafcsqcjgob"
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

def get_author_from_postid(file, postid):
    with open(file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["id"] == postid:
                return row["author"]


def make_reply(file, postid, author, text):

    user = get_author_from_postid(POSTS_DB, postid)

    text_notify = f"[user:{author}] comment your [post:{postid}]"
    make_notify(user, text_notify)


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

                print(row["id"], row["hash"])
                return row["hash"] == hash

def get_hash(file, id):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] == id:
                return row["hash"]


def get_users(file):
    with open(file, "r") as f:
        result = []
        reader = csv.DictReader(f)
        for row in reader:
            result.append(row["username"])

    return result

def get_users_by_name(file, username):
    with open(file, "r") as f:
        result = []
        reader = csv.DictReader(f)
        for row in reader:
            user = (row["username"])
            if user.lower().strip().startswith(username):
                result.append(User(get_id(file,user), user))

    return result




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


    text_notify = f"[user:{user}] start follow you!"
    make_notify(king, text_notify)

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

    notify_path = f"users/{king}/notify.txt"
    try:
        with open(notify_path, "r") as f:
            lines = f.readlines()

        with open(notify_path, "w") as f:
            for line in lines:
                if not line.startswith(f"[user:{user}] start follow"):
                    f.write(line)
    except FileNotFoundError:
        pass


def get_subscribes(username):
    subs = []
    with open(f"users/{username}/subscribes.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            subs.append(User(row["id"], row["username"]))
    return subs






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


def code_exist(code):
    users = get_users(USERS_DB)

    for user in users:
        with open(f"users/{user}/info.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["refcode"] == code:
                    return user
    return False

import csv

def do_verified_user(user, user_fornotify=''):
    filepath = f"users/{user}/info.csv"


    if user_fornotify != '':
        text_notify = f"[user:{user_fornotify}] write your referral code!"
        make_notify(user, text_notify)

    with open(filepath, newline='', mode='r') as csvfile:
        reader = list(csv.reader(csvfile))
        header = reader[0]
        data = reader[1]


    verified_idx = header.index("verified")
    activates_idx = header.index("activates")


    if data[verified_idx].lower() == "false":
        data[verified_idx] = "True"


    try:
        activates = int(data[activates_idx])
    except ValueError:
        activates = 0
    activates += 1
    data[activates_idx] = str(activates)

    with open(filepath, newline='', mode='w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerow(data)




def make_notify(user, info):



    now = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M")
    with open(f"users/{user}/notify.txt", "a") as f:
        f.write(f"{info}\t{now}\n")



def read_notify(user):
    notify = []

    with open(f"users/{user}/notify.txt") as f:
        for row in f:
            line = row.strip()


            time_match = re.search(r"\d{2}/\d{2}/\d{4} - \d{2}:\d{2}$", line)
            if time_match:
                time = time_match.group()
                line = line.replace(time, '').strip()
            else:
                time = ''

            tags = re.findall(r"\[([a-zA-Z0-9_]+):([^\]]+)\]", line)

            data = {}
            for key, value in tags:
                data[key] = value


            clean_text = re.sub(r"\[[a-zA-Z0-9_]+:[^\]]+\]", '', line).strip()

            data['text'] = clean_text
            data['time'] = time

            notify.append(data)


    return notify


def serverinfo_add(key, value:int):

    filename = "other/serverinfo.csv"

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    if rows:
        row = rows[0]
        row[key] = str(int(row[key]) + value)



    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['visited', 'users', 'posts', 'replies', 'verified_users']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow(row)


def get_serverinfo():

    filename = "other/serverinfo.csv"

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        return rows[0]

def userIsAdmin(user):
    with open(f"users/{user}/info.csv", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["admin"] != "False":
                return True
    return False


users = ["diego","cindy","anna","brian"]

for user in users:
    subscribe(USERS_DB,"skittleNotReal", user )



def chat_exist(file, user1,user2):
    with open(file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if (row["user1"] == user1 and row["user2"] == user2) or (row["user2"] == user1 and row["user1"] == user2):
                return True

    return False


def get_chat_id(file, user1,user2):
    with open(file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if (row["user1"] == user1 and row["user2"] == user2) or (row["user2"] == user1 and row["user1"] == user2):
                return row["chatid"]

    return False


def create_new_chat(file, user1, user2):
    max_chatid = 0

    with open(file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 3 and parts[2].isdigit():
                max_chatid = max(max_chatid, int(parts[2]))

    new_chatid = max_chatid + 1

    with open(file, 'a') as f:
        f.write(f"{user1},{user2},{new_chatid}\n")


    chat_filename = f"chats/{new_chatid}.csv"
    with open(chat_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["sender", "claimer", "text", "time"])

    return new_chatid


def write_messages(chatid, sender, claimer, text):
    with open(f"chats/{chatid}.csv", "a", newline='') as f:
        fieldnames = ["sender", "claimer", "text", "time"]
        time = datetime.datetime.now().strftime("%H:%M")

        writer = csv.DictWriter(f, fieldnames=fieldnames)



        writer.writerow({
            "sender": sender,
            "claimer": claimer,
            "text": text,
            "time": time
        })



def read_messages(chatid):

    result = []

    with open(f"chats/{chatid}.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            result.append({"sender_name":row["sender"], "content":row["text"], "time":row["time"]})

    return result
