from webapp import create_app
from flask_mysqldb import MySQL

app = create_app()
mysql = MySQL(app)

from api.account import account_bp
app.register_blueprint(account_bp)

from api.collection import collection_bp
app.register_blueprint(collection_bp)


if __name__ == '__main__':
    app.run(host="localhost", port=3333)
