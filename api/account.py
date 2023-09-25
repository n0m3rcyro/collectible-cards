from flask import Blueprint, request, session, redirect, render_template, jsonify
import re
import MySQLdb
import requests

account_bp = Blueprint('account_bp', __name__)


@account_bp.route("/login", methods=["POST", "GET"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        from main import mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, email, name, role FROM users WHERE email = %s AND password = %s", (email, password))
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session["email"] = account["email"]
            session["name"] = account["name"]
            session["id"] = account["id"]
            session["role"] = account["role"]
            return redirect("/")
        else:
            message = "Incorrect username/password!"
    return render_template("login.html", msg=message)


@account_bp.route("/logout")
def logout():
    session["loggedin"] = False
    session["email"] = None
    session["name"] = None
    session["id"] = None
    session["role"] = None
    return redirect("/login")


@account_bp.route("/register", methods=["POST", "GET"])
def register():
    msg = ''
    if request.method == "POST" and "name" in request.form and "password" in request.form \
            and "email" in request.form:
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        from main import mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email, ))
        account = cursor.fetchone()
        if account:
            msg = "Account already exists!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address!"
        elif not re.match(r"[A-Za-z0-9]+", name):
            msg = "Name must contain only characters and numbers!"
        elif not name or not password or not email:
            msg = "Please fill out the form!"
        else:
            cursor.execute("INSERT INTO users VALUES (NULL, %s, %s, %s, 'user', 500, 0)", (email, name, password))
            mysql.connection.commit()
            create_collection(cursor.lastrowid)
            return render_template("register-ok.html")
    elif request.method == "POST":
        msg = 'Please fill out the form!'
    return render_template("register.html", msg=msg)


def create_collection(user_id):
    url = 'http://localhost:3334/'
    response = requests.get(url)
    players = response.json()
    from main import mysql
    my_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "INSERT INTO cards (id, name, current_skill, potential_skill, age, market_value) " \
          "VALUES (%s, %s, %s, %s, %s, 100)"
    values = []
    ownership = []
    for player in players:
        values.append((player["id"], player["name"], player["current_skill"], player["potential_skill"], player["age"]))
        ownership.append((user_id, player["id"]))
    my_cursor.executemany(sql, values)
    mysql.connection.commit()
    sql = "INSERT INTO collections (user_id, card_id) VALUES (%s, %s)"
    my_cursor.executemany(sql, ownership)
    mysql.connection.commit()
    return user_id


@account_bp.route("/my-account")
def my_account():
    if not session.get("name"):
        return redirect("/login")
    return render_template("my-account.html")


@account_bp.route("/api/my-account", methods=["POST"])
def my_account_data():
    if not session.get("name"):
        return redirect("/login")
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT CONCAT(nb_cards, ' cards - ', total_market_value, '$ market value') AS c " \
          "FROM ( " \
          "SELECT COUNT(*) AS nb_cards, SUM(cards.market_value) AS total_market_value " \
          "FROM collections " \
          "INNER JOIN cards ON cards.id = collections.card_id " \
          "WHERE collections.user_id = %s ) AS tmp "
    cursor.execute(sql, (session.get("id"),))
    collection = cursor.fetchone()["c"]
    sql = "SELECT name AS country FROM countries WHERE id = (SELECT country FROM users WHERE id = %s)"
    cursor.execute(sql, (session.get("id"),))
    country = cursor.fetchone()["country"]
    return jsonify({"message": "success", "name": session.get("name"), "role": session.get("role"),
                    "collection": collection, "country": country})


@account_bp.route("/api/changename", methods=["POST"])
def change_name():
    if not session.get("name"):
        return redirect("/login")
    user_id = session.get("id")
    new_name = request.form["new_name"]
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
    session["name"] = new_name
    return jsonify({"message": "success", "new_name": new_name})


@account_bp.route("/api/changecountry", methods=["POST"])
def change_country():
    if not session.get("name"):
        return redirect("/login")
    user_id = session.get("id")
    if not 0 <= int(request.form["new_country_id"]) <= 219:
        return jsonify({"message": "unsuccessful", "reason": "invalid country id"})
    new_country_id = request.form["new_country_id"]
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE users SET country = %s WHERE id = %s", (new_country_id, user_id))
    cursor.execute("SELECT name FROM countries WHERE id = %s", (new_country_id,))
    new_country_name = cursor.fetchone()["name"]
    return jsonify({"message": "success", "new_country_id": new_country_id, "new_country_name": new_country_name})


@account_bp.route("/administration")
def administration():
    if not session.get("name"):
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("administration.html")


@account_bp.route("/api/getusers", methods=["POST"])
def get_users():
    if not session.get("name"):
        return redirect("/login")
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT users.id, email, users.name, role, countries.name AS country, wallet " \
          "FROM users " \
          "INNER JOIN countries ON countries.id = users.country " \
          "ORDER BY users.id"
    cursor.execute(sql)
    results = cursor.fetchall()
    return jsonify(results)


@account_bp.route("/api/changeusername", methods=["POST"])
def change_user_name():
    if not session.get("name"):
        return redirect("/login")
    if session.get("role") != "admin":
        return jsonify({"message": "unsuccessful", "reason": "insufficient privileges"})
    user_id = request.form["user_id"]
    new_name = request.form["new_name"]
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
    return jsonify({"message": "success", "new_name": new_name, "user_id": user_id})


@account_bp.route("/api/changeusercountry", methods=["POST"])
def change_user_country():
    if not session.get("name"):
        return redirect("/login")
    if session.get("role") != "admin":
        return jsonify({"message": "unsuccessful", "reason": "insufficient privileges"})
    user_id = request.form["user_id"]
    if not 0 <= int(request.form["new_country_id"]) <= 219:
        return jsonify({"message": "unsuccessful", "reason": "invalid country id"})
    new_country_id = request.form["new_country_id"]
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE users SET country = %s WHERE id = %s", (new_country_id, user_id))
    cursor.execute("SELECT name FROM countries WHERE id = %s", (new_country_id,))
    new_country_name = cursor.fetchone()["name"]
    return jsonify({"message": "success", "new_country_id": new_country_id, "new_country_name": new_country_name,
                    "user_id": user_id})


@account_bp.route("/api/changeuserrole", methods=["POST"])
def change_user_role():
    if not session.get("name"):
        return redirect("/login")
    if session.get("role") != "admin":
        return jsonify({"message": "unsuccessful", "reason": "insufficient privileges"})
    new_role = request.form["new_role"]
    if new_role not in ["admin", "user"]:
        return jsonify({"message": "unsuccessful", "reason": "incorrect role"})
    user_id = request.form["user_id"]
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
    return jsonify({"message": "success", "new_role": new_role, "user_id": user_id})


@account_bp.route("/api/getwallet", methods=["POST"])
def get_wallet():
    if not session.get("name"):
        return redirect("/login")
    user_id = session.get("id")
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
    wallet = cursor.fetchone()["wallet"]
    return jsonify({"message": "success", "wallet": wallet})
