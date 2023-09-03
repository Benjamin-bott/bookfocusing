
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    student_id = StringField('studentID', validators=[DataRequired()])
    passWord = TextAreaField('PassWord', validators=[DataRequired()])
    Manager = SelectField('Manager', choices=[("False", "False"), ("True", "True")], validators=[DataRequired()])
    submit = SubmitField("Add todo")


