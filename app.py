from flask import Flask, flash, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from flask_wtf import CSRFProtect
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
# from models import User
from forms import RegistrationForm

app = Flask(__name__)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# SQLAlchemy Configuration
engine = create_engine('sqlite:///my_chat_app.db')
Base = declarative_base()
class User(Base, UserMixin):  # Add UserMixin to your User class
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password = Column(String(255))

    def is_active(self):
        return True  # Change this logic based on your application's requirements

    # Other User class methods (if any)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

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

if __name__ == '__main__':
    socketio.run(app, debug=True)
