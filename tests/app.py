from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

app = Flask(__name__)
app.secret_key = 'secret_key'

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    weight = StringField('Weight', validators=[DataRequired()])
    height = StringField('Height', validators=[DataRequired()])
    goal = StringField('Goal', validators=[DataRequired()])
    target_weight = StringField('Target Weight', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Handle form submission (save data to database, etc.)
        pass
    return render_template('register.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)
