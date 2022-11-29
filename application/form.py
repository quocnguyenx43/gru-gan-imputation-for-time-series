from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class UserInputForm(FlaskForm):
    feature = SelectField(
        'Target feature',
        validators=[DataRequired()],
        choices=[
            ('Temperature', 'Temperature'),
            ('Relative_Humidity', 'Relative Humidity'),
            ('Specific_Humidity', 'Specific Humidity'),
            ('Precipitation', 'Precipitation'),
            ('Pressure', 'Pressure'),
            ('Wind_Speed', 'Wind Speed'),
            ('Wind_Direction', 'Wind Direction')
        ]
    )
    category = SelectField(
        'Category feature',
        validators=[DataRequired()],
        choices=[
            ('MO', 'Month'),
            ('YEAR', 'Year')
        ]
    )
    submit = SubmitField("Nổ máy!!")