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

########### user login form is over ############
## but what is content form then?

class Content(mongoengine.Document):
    user = mongoengine.ReferenceField('User', dbref=True) # ^^^ points to User model ^^^
    title = mongoengine.StringField(max_length="100",required=True)
    content = mongoengine.StringField(required=True)
    timestamp = mongoengine.DateTimeField(default=datetime.now())

    @mongoengine.queryset_manager
    def objects(doc_cls, queryset):
    	return queryset.order_by('-timestamp')

# content form
content_form = model_form(Content)


#############################################
# login info is done ########################
#############################################

# our demo model from week 5 in class
# class Log(Document):
# 	email = StringField()
# 	password = StringField()
# 	timestamp = DateTimeField(default=datetime.now())


# class Comment(EmbeddedDocument):
# 	name = StringField()
# 	comment = StringField()
# 	timestamp = DateTimeField(default=datetime.now())

	
class Trip(Document):
	startdate = StringField(max_length=120, required=True, verbose_name="start date")
	enddate = StringField(max_length=120, required=True, verbose_name="end date")	
	reminder = StringField(required = True)
	listname =  StringField(StringField(max_length=30))
	
	timestamp = DateTimeField(default=datetime.now())


# Create a Validation Form from the Idea model
TripForm = model_form(Trip)


class Items(Document):
	tripname = StringField(max_length=120, required=True)
	item = StringField(StringField(max_length=30))
	quantity = StringField(required=True)


ItemsForm = model_form(Items)