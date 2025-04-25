from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class CoinSelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    coin = db.Column(db.String(10))
    ref_price = db.Column(db.Float)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_usdt_pairs():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            usdt_pairs = [symbol['symbol'][:-4] for symbol in data['symbols']
                         if symbol['symbol'].endswith('USDT') and symbol['status'] == 'TRADING']
            return sorted(usdt_pairs)
        return []
    except:
        return []

def get_coin_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@app.route('/')
@login_required
def index():
    coins = get_usdt_pairs()
    return render_template('index.html', coins=coins)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            return "Username already exists"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/get_price/<symbol>')
def get_price(symbol):
    data = get_coin_price(symbol)
    if data:
        return jsonify({'symbol': f"{symbol}USDT", 'price': float(data['price'])})
    return jsonify({'error': 'Unable to fetch price'}), 500

@app.route('/save_coins', methods=['POST'])
@login_required
def save_coins():
    data = request.json
    CoinSelection.query.filter_by(user_id=current_user.id).delete()
    for item in data:
        coin = CoinSelection(user_id=current_user.id, coin=item['coin'], ref_price=item['refPrice'])
        db.session.add(coin)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/load_coins')
@login_required
def load_coins():
    coins = CoinSelection.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'coin': c.coin, 'refPrice': c.ref_price} for c in coins])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
