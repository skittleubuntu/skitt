from pyexpat.errors import messages
from models import User
from flask import Flask, request, redirect, render_template, make_response, render_template_string, jsonify, url_for
from functions import *
app = Flask(__name__)

USERS_DB = "users/users.csv"
POSTS_DB = "posts/post.csv"
TEMP_DB = "users/temp.csv"
REPLYES_DB = "posts/replyes.csv"
HASH_DB = "users/hashkeys.csv"


@app.route("/api/posts")
def get_posts_api():
    offset = int(request.args.get("offset", 0) or 0)
    limit = int(request.args.get("limit", 10) or 10)

    posts = read_posts(POSTS_DB, offset=offset, limit=limit)

    post_dicts = [{
        "id": post.id,
        "author": post.author,
        "title": post.title,
        "content": post.text,
        "time": post.day
    } for post in posts]

    return jsonify(post_dicts)




@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route("/", methods=["POST", "GET"])
def index():

    user_id = request.cookies.get("user_id")
    hash = request.cookies.get("hash_key")
    if not user_id or not isinstance(user_id, str):
        print("No coockies")
        return redirect("/login")

    if check_hash(HASH_DB,user_id, hash):
        main_user = User(user_id, get_username(USERS_DB, user_id))
        posts = read_posts(POSTS_DB, offset=0, limit=10)

    else:
        print("No coockies")
        return redirect("/login")


    return render_template("index.html", main_user=main_user, posts=posts)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/post/<post_id>", methods=["POST", "GET"])
def post(post_id):
    user_id = request.cookies.get("user_id")
    main_user =  User(user_id, get_username(USERS_DB, user_id))
    post = get_post(POSTS_DB, post_id)
    replyes = read_replyes(REPLYES_DB, post_id)

    return render_template("post.html", post=post, main_user=main_user, replyes=replyes)

@app.route('/<username>', methods=["POST", "GET"])
def user_profile(username):
    user_id = request.cookies.get("user_id")
    owner = False
    main_user = User(user_id,get_username(USERS_DB, user_id))
    des = get_user_description(username)
    data = get_user_info(username)





    if not userIsExist(username, USERS_DB):
        return render_template("usernotexist.html")

    if user_id == get_id(USERS_DB, username):
        owner = True
        user = User(user_id, username)

    else:
        user = User(get_id(USERS_DB, username), username)
        data["follow"] = user_is_follower(main_user.name, username)

    if request.method == "POST" and owner:

        new_description = request.form.get("description", "").strip()
        if new_description:
            update_user_description(username, new_description)
            return redirect(url_for('user_profile', username=username))

    if request.method == "POST":

        if not user_is_follower(main_user.name, username):
            subscribe(USERS_DB,main_user.name,username)
            return redirect(url_for('user_profile', username=username))
        else:
            unsubscribe(main_user.name, username)
            return redirect(url_for('user_profile', username=username))




    posts = get_user_posts(POSTS_DB, username)

    return render_template("userpage.html", owner=owner, user=user, main_user=main_user,
                           posts=posts, des=des, data=data)



@app.route("/makepost/<page>/<userid>", methods=["POST"])
def makepost(page, userid):

    if request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("content")
        id = userid

        make_post(POSTS_DB, get_username(USERS_DB, id), text, title)



    if page == "index":
        return redirect("/")
    else:
        return redirect(f"/{page}")

@app.route('/reply/<post_id>/<user_id>', methods=['POST'])
def makereply(post_id, user_id):
    text = request.form['reply_text']
    author = get_username(USERS_DB, user_id)

    make_reply(REPLYES_DB, post_id, author, text)

    return redirect(url_for('post', post_id=post_id))


@app.route("/logout", methods=["POST"])
def logout():
    response = make_response(redirect("/login"))
    response.delete_cookie("user_id")
    response.delete_cookie("hash_key")
    return response



@app.route("/login", methods=["GET", "POST"])
def login():
    messages =""
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get('password')


        if check_password(USERS_DB, username, password):
            id = get_id(USERS_DB, username)
            response = make_response(redirect("/"))
            response.set_cookie("user_id", str(id))
            hash = get_hash(HASH_DB, id)
            response.set_cookie("hash_key", hash)
            return response

        else:
            messages = "Wrong password or username"




    return render_template("login.html",message= messages)


@app.route('/verify/<username>', methods=["POST","GET"])
def verify(username):
    message = ''
    email, password, code = tempdata_from_name(TEMP_DB, username)
    print(code)

    if request.method == "GET":
        # Надсилаємо код тільки при відкритті сторінки вперше
        spam(email, code)

    if request.method == "POST":
        writen_code = request.form.get("code")

        if writen_code == code:
            response = make_response(redirect("/"))
            id = add_user(USERS_DB, username, email, password)
            hash = generate_hash(HASH_DB, id)
            response.set_cookie("user_id", str(id))
            response.set_cookie("hash_key", hash)

            print(hash)
            return response
        else:
            message = "Wrong code"

    return render_template("verify.html", message=message, mail=email)



@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    data=''
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("mail")
        password = request.form.get("password")
        data = {"username":username, "email":email, "password":password}


        if not is_valid_email(email):
            message = "Your email is invalid"
        else:

            if strong_password(password) != True:
                message = strong_password(password)

            else:
                if not userIsExist(username, USERS_DB):
                    response = make_response(redirect(f"/verify/{username}"))
                    if temp_user_exist(TEMP_DB, username):
                        delete_temp_user(TEMP_DB, username)

                    temp_user(TEMP_DB, username, email, password)
                    #response.set_cookie("user_id", str(id))
                    return response
                else:
                    message = "User is exist, use another username"



    return render_template("register.html", message=message, data=data)

if __name__ == '__main__':
    app.run(debug=True)
