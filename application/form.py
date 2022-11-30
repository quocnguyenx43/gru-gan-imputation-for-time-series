from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class ChangeInputFeatureForm(FlaskForm):
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

class ChangeStrategyForm(FlaskForm):
    strategy = SelectField(
        'Strategy',
        validators=[DataRequired()],
        choices=[
            ('All', 'All'),
            ('gan', 'GAN'),
            ('knn', 'kNN'),
            ('random', 'Random (Từ Q1 đến Q3)')
        ]
    )
    submit = SubmitField("Nổ máy!!")