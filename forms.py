from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class ChatRoomForm(FlaskForm):
    room_name = StringField('Room Name', validators=[DataRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')], validators=[DataRequired()])
    submit = SubmitField('Create Chat Room')
