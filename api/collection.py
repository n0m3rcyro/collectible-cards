from flask import Blueprint, session, redirect, render_template, jsonify, request
import MySQLdb
import time
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

collection_bp = Blueprint('collection_bp', __name__)


@collection_bp.route("/")
@collection_bp.route("/collection")
def index():
    if not session.get("name"):
        return redirect("/login")
    return render_template("index.html")


@collection_bp.route("/api/collection", methods=["POST"])
def my_collection_data():
    if not session.get("name"):
        return redirect("/login")
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT cards.*, " \
          "IF(market.card_id IS NOT NULL, 'yes', 'no') AS on_market, " \
          "IF(market.asking_price IS NOT NULL, market.asking_price, 0) AS asking_price " \
          "FROM collections " \
          "INNER JOIN cards ON cards.id = collections.card_id " \
          "LEFT JOIN market ON market.card_id = collections.card_id " \
          "WHERE collections.user_id = %s"
    cursor.execute(sql, (session.get("id"),))
    collection = cursor.fetchall()
    return jsonify(collection)


@collection_bp.route("/api/addtomarket", methods=["POST"])
def add_to_market():
    if not session.get("name"):
        return redirect("/login")
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT COUNT(*) AS nb FROM collections WHERE user_id = %s AND card_id = %s"
    cursor.execute(sql, (session.get("id"), request.form.get("card_id")))
    result = cursor.fetchone()
    if result["nb"] == 1:
        sql = "INSERT INTO market (card_id, asking_price) VALUES (%s, %s)"
        cursor.execute(sql, (request.form.get("card_id"), request.form.get("asking_price")))
        return jsonify({"message": "success", "card_id": request.form.get("card_id"),
                        "asking_price": request.form.get("asking_price")})
    else:
        return jsonify({"message": "unsuccessful"})


@collection_bp.route("/api/removefrommarket", methods=["POST"])
def remove_from_market():
    if not session.get("name"):
        return redirect("/login")
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT COUNT(*) AS nb FROM market " \
          "INNER JOIN collections ON market.card_id = collections.card_id " \
          "WHERE collections.user_id = %s AND market.card_id = %s"
    cursor.execute(sql, (session.get("id"), request.form.get("card_id")))
    result = cursor.fetchone()
    if result["nb"] == 1:
        sql = "DELETE FROM market WHERE card_id = %s"
        cursor.execute(sql, (request.form.get("card_id"),))
        return jsonify({"message": "success", "card_id": request.form.get("card_id")})
    else:
        return jsonify({"message": "unsuccessful"})


@collection_bp.route("/marketplace")
def market():
    return render_template("marketplace.html")


@collection_bp.route("/api/marketplace", methods=["POST"])
def get_market_data():
    if not session.get("name"):
        return redirect("/login")
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT " \
          "market.card_id, cards.name, cards.current_skill, cards.potential_skill, cards.age, " \
          "cards.market_value, market.asking_price, " \
          "IF(collections.user_id = %s, 'invalid', 'valid') AS validity " \
          "FROM market " \
          "INNER JOIN cards ON cards.id = market.card_id " \
          "INNER JOIN collections ON collections.card_id = market.card_id"
    cursor.execute(sql, (session.get("id"),))
    results = cursor.fetchall()
    return jsonify(results)


@collection_bp.route("/api/buyfrommarket", methods=["POST"])
def buy_from_market():
    if not session.get("name"):
        return redirect("/login")
    from main import mysql
    user_id = session.get("id")
    card_id = request.form.get("card_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("LOCK TABLES users WRITE, market WRITE, collections WRITE, transactions WRITE")
    cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
    wallet = cursor.fetchone()["wallet"]
    # time.sleep(10)
    cursor.execute("SELECT asking_price FROM market WHERE card_id = %s", (card_id,))
    price = cursor.fetchone()["asking_price"]
    if wallet >= price:
        cursor.execute("UPDATE users SET wallet = wallet - %s WHERE id = %s", (price, user_id))
        cursor.execute("SELECT user_id FROM collections WHERE card_id = %s", (card_id,))
        seller_id = cursor.fetchone()["user_id"]
        cursor.execute("UPDATE collections SET user_id = %s WHERE card_id = %s", (user_id, card_id))
        cursor.execute("DELETE FROM market WHERE card_id = %s", (card_id,))
        cursor.execute("UPDATE users SET wallet = wallet + %s WHERE id = %s", (price, seller_id))
        cursor.execute("INSERT INTO transactions (seller_id, buyer_id, card_id, price) VALUES (%s, %s, %s, %s)",
                       (seller_id, user_id, card_id, price))
        cursor.execute("UNLOCK TABLES")
        update_market_value(card_id)
        return jsonify({"message": "success", "card_id": card_id})
    else:
        cursor.execute("UNLOCK TABLES")
        return jsonify({"message": "unsuccessful", "card_id": card_id, "reason": "insufficient credits"})


def update_market_value(card_id):
    from main import mysql
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT cards.age, cards.current_skill, cards.potential_skill, transactions.price " \
          "FROM transactions INNER JOIN cards " \
          "ON cards.id = transactions.card_id "
    cursor.execute(sql)
    results = cursor.fetchall()
    df = pd.DataFrame(results)
    x = np.asarray(df[['age', 'current_skill', 'potential_skill']])
    y = np.asarray(df['price'])
    line_reg = LinearRegression()
    line_reg.fit(x, y)
    sql = "SELECT age, current_skill, potential_skill FROM cards WHERE id = %s"
    cursor.execute(sql, (card_id,))
    row = cursor.fetchone()
    market_value = int(line_reg.predict([[row["age"], row["current_skill"], row["potential_skill"]]]))
    cursor.execute("UPDATE cards SET market_value = %s WHERE id = %s", (market_value, card_id))
