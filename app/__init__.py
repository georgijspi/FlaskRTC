from flask import Flask
from flask_socketio import SocketIO

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize Flask-SocketIO
socketio = SocketIO(app)

# Import and register routes
from app import routes

if __name__ == "__main__":
    socketio.run(app, debug=True)
