from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import emit, join_room
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy

from werkzeug.utils import secure_filename
from sqlalchemy import create_engine  # Import create_engine

from forms import  RegistrationForm, ChatRoomForm
from models import User
from sqlalchemy.ext.declarative import declarative_base


import os
from sqlalchemy.orm import sessionmaker



# Define the engine
engine = create_engine('sqlite:///my_chat_app.db')


Base = declarative_base()


# Define the Session
Session = sessionmaker(bind=engine)

# Initialize the Flask application
app = Flask(__name__, static_url_path='/static')
uploads_dir = os.path.join(app.static_folder, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_chat_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

db = SQLAlchemy(app)  # Initialize SQLAlchemy

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    with Session() as session:
        return session.query(User).get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Ensure the "static/uploads" directory exists
        upload_folder = os.path.join(app.root_path, 'static/uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Handle profile picture upload
        profile_picture = request.files['profile_picture']
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture_path = f'static/uploads/{filename}'  # Define your desired storage path
            profile_picture.save(profile_picture_path)
        else:
            profile_picture_path = None

        with Session() as session:
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                flash('Username already exists', 'danger')
                return render_template('register.html', form=form)

            user = User(username=username, password=hashed_password, profile_picture=profile_picture_path)
            session.add(user)
            session.commit()

            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        username = request.form.get('username')
        # Validate user login (you may need to modify this)
        if username:
            with Session() as session:
                user = session.query(User).filter_by(username=username).first()
                if user:
                    login_user(user)
                    return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/chat_rooms', methods=['GET', 'POST'])
@login_required
def chat_rooms():
    form = ChatRoomForm()

    if form.validate_on_submit():
        # Handle chat room creation
        room_name = form.room_name.data
        visibility = form.visibility.data

        # Create a new chat room
        chat_room = ChatRoom(name=room_name, visibility=visibility)
        db.session.add(chat_room)
        chat_room.users.append(current_user)
        db.session.commit()

        flash('Chat room created successfully!', 'success')

    chat_rooms = ChatRoom.query.all()
    return render_template('chat_rooms.html', form=form, chat_rooms=chat_rooms)

@app.route('/join_chat_room/<int:room_id>', methods=['POST'])
@login_required
def join_chat_room(room_id):
    chat_room = ChatRoom.query.get(room_id)

    if chat_room:
        if current_user not in chat_room.users:
            chat_room.users.append(current_user)
            db.session.commit()
            join_room(str(room_id))
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'You are already in this chat room.'})
    else:
        return jsonify({'status': 'error', 'message': 'Chat room not found.'})

@app.route('/chat_room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def chat_room(room_id):
    chat_room = ChatRoom.query.get(room_id)
    if not chat_room:
        flash('Chat room not found', 'error')
        return redirect(url_for('chat_rooms'))

    form = SendMessageForm()
    messages = Message.query.filter_by(chat_room_id=room_id).all()

    if form.validate_on_submit():
        content = form.content.data
        message = Message(content=content, sender=current_user, chat_room=chat_room)
        db.session.add(message)
        db.session.commit()
        emit('message', {'user_id': current_user.id, 'content': content}, room=str(room_id))

    return render_template('chat_room.html', chat_room=chat_room, form=form, messages=messages)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


if __name__ == '__main__':
    socketio.run(app, debug=True)
