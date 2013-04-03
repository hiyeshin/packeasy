# -*- coding: utf-8 -*-
from mongoengine import *
from flask.ext.mongoengine.wtf import model_form
from wtforms.fields import * # for our custom signup form
from flask.ext.mongoengine.wtf.orm import validators
from flask.ext.mongoengine import *
from datetime import datetime
import logging 

# below class is hash,
class User(mongoengine.Document):
	username = mongoengine.StringField(unique=True, max_length=30, required=True, verbose_name="Pick a Username")
	email = mongoengine.EmailField(unique=True, required=True, verbose_name="Email Address")
	password = mongoengine.StringField(default=True,required=True)
	active = mongoengine.BooleanField(default=True)
	isAdmin = mongoengine.BooleanField(default=False)
	timestamp = mongoengine.DateTimeField(default=datetime.now())

user_form = model_form(User, exclude=['password'])

# Signup Form created from user_form
class SignupForm(user_form):
	password = PasswordField('Password', validators=[validators.Required(), validators.EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')

# Login form will provide a Password field (WTForm form field)
# because User.password is
class LoginForm(user_form):
	password = PasswordField('Password',validators=[validators.Required()])

#############################################
# login info is done ########################
#############################################
	
class Trip(mongoengine.Document):
	user = mongoengine.ReferenceField('User', dbref = True)
	startdate = mongoengine.StringField(required=True, verbose_name="start date")
	enddate = mongoengine.StringField(required=True, verbose_name="end date")
	location = mongoengine.StringField(required = True)
	reminder = mongoengine.StringField(required = True)
	tripname = mongoengine.StringField(max_length=120, required=True)
	timestamp = mongoengine.StringField(default=datetime.now())
# Create a Validation Form from the Idea model
trip_form = model_form(Trip)


class Items(Document):
	listname = StringField(StringField(max_length=30))
	item = StringField(StringField(max_length=30))
	quantity = StringField(required=True)

items_form = model_form(Items)