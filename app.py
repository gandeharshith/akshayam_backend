from flask import Flask
from routes.login import login_bp
from routes.signup import signup_bp
from routes.forgot_password import forgot_password_bp
from routes.add_category import add_category_bp
from routes.delete_category import delete_category_bp
from routes.add_item import add_item_bp
from routes.create_order import create_order_bp
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# Register blueprints
app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(forgot_password_bp)
app.register_blueprint(add_category_bp)
app.register_blueprint(delete_category_bp)
app.register_blueprint(add_item_bp)
app.register_blueprint(create_order_bp)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)
