from flask_wtf import FlaskForm
from wtforms import IntegerField, DecimalField, SubmitField
from wtforms.validators import NumberRange, InputRequired

class Form(FlaskForm):
    rating_A = DecimalField('Rating (%)', validators=[NumberRange(min=0,max=100,message='Must be a percentage (between 0 and 100)'), InputRequired()], default=75)
    num_reviews_A = IntegerField('Number of Reviews', validators=[InputRequired(), NumberRange(min=1, message='Must have 1 or more reviews')], default=20) #

    rating_B = DecimalField('Rating (%)', validators=[InputRequired(), NumberRange(min=0,max=100,message='Must be a percentage (between 0 and 100)')], default=80)
    num_reviews_B = IntegerField('Number of Reviews', validators=[InputRequired(), NumberRange(min=1, message='Must have 1 or more reviews')], default=5)

    submit = SubmitField('Compare Reviews')
