from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = 'your_secret_key'  # Change this to a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

app.debug = True

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('my event')
def handle_my_event(data):
    # Handle the event from the client
    print(data)
    # Send a response back to the client (optional)
    socketio.emit('response', {'message': 'Received your message!'})

@app.route('/emit_event', methods=['POST'])
def emit_event():
    # Emit the event to the server using Flask-SocketIO
    socketio.emit('my event', {'data': 'I\'m connected!'})

    # Return a response to the client (optional)
    return jsonify({'message': 'Event emitted successfully!'})


if __name__ == '__main__':
    socketio.run(app)
