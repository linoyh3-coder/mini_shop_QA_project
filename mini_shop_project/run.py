from flask import Flask, send_from_directory
from app.controllers.shop_controller import shop_blueprint
from app.db.database import init_db

app = Flask(__name__, static_folder='static')

# Registration of the API Blueprint
app.register_blueprint(shop_blueprint, url_prefix='/api')

# Route to serve the frontend homepage
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    init_db()  # Initialize the tables and initial products
    print("🚀 השרת רץ בהצלחה בכתובת: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
