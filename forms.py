from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired


class AddressForm(FlaskForm):
	address = StringField("Enter a valid address", 
		validators=[InputRequired(message="Address field cannot be blank")])