#
#   CURRENTLY NOT IN USE
#


from flask import flash, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from app import app, socketio, login_manager, bcrypt
from models import User, Session
from forms import RegistrationForm


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

        with Session() as session:
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                flash('Username already exists', 'danger')
                return render_template('register.html', form=form)

            user = User(username=username, password=hashed_password)
            session.add(user)
            session.commit()

            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
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

@socketio.on('message')
@login_required
def handle_message(data):
    emit('message', data, broadcast=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
