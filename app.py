from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from forms import RegistrationForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room
from  werkzeug.utils import secure_filename
from rtc_forms import SendMessageForm
from models import User, Message, ChatRoom, ChatRoomUser, Session
import os
# from models import User
# from routes import 
# import routes

app = Flask(__name__, static_url_path='/static')
uploads_dir = os.path.join(app.static_folder, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)
csrf = CSRFProtect(app)  # CSRF token
bcrypt = Bcrypt(app) # password encryption


app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    with Session() as session:
        return session.query(User).get(int(user_id))

@app.route('/')
@login_required
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

    # Forget anu user_id
    # session.clear()
    
    form = RegistrationForm(request.form)  # Create an instance of the RegistrationForm
    if request.method == 'POST':
        username = request.form.get('username')
        # Validate user login (you may need to modify this)
        if username:
            with Session() as session:
                user = session.query(User).filter_by(username=username).first()
                if user:
                    login_user(user)
                    return redirect(url_for('index'))
    return render_template('login.html', form=form)  # Pass the form to the template context

# Placeholder, not used for now
@socketio.on('message')
@login_required
def handle_message(data):
    emit('message', data, broadcast=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# RTC funcionality/routes
@app.route('/chat_rooms', methods=['GET', 'POST'])
@login_required
def chat_rooms():
    # Create or list chat rooms
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        if room_name:
            chat_room = ChatRoom(name=room_name)
            chat_room.users.append(current_user)
            with Session() as session:
                session.add(chat_room)
                session.commit()
    chat_rooms = current_user.chat_rooms
    return render_template('chat_rooms.html', chat_rooms=chat_rooms)

@app.route('/chat_rooms/<int:room_id>', methods=['GET', 'POST'])
@login_required
def chat_room(room_id):
    # Join a chat room and send messages
    chat_room = ChatRoom.query.get(room_id)
    if chat_room and current_user in chat_room.users:
        form = SendMessageForm()
        if form.validate_on_submit():
            content = form.content.data
            message = Message(content=content, sender=current_user, chat_room=chat_room)
            with Session() as session:
                session.add(message)
                session.commit()
            emit('message', {'user_id': current_user.id, 'content': content}, room=room_id)
        messages = chat_room.messages
        return render_template('chat_room.html', chat_room=chat_room, messages=messages, form=form)
    return redirect(url_for('chat_rooms'))

@app.route('/join_chat_room/<int:room_id>', methods=['POST'])
@login_required
def join_chat_room(room_id):
    # Join a chat room
    chat_room = ChatRoom.query.get(room_id)
    if chat_room and current_user not in chat_room.users:
        chat_room.users.append(current_user)
        with Session() as session:
            session.commit()
        join_room(room_id)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})


if __name__ == '__main__':
    socketio.run(app, debug=True)
