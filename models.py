# -*- coding: utf-8 -*-
from mongoengine import *

from flask.ext.mongoengine.wtf import model_form
from datetime import datetime

import logging

# our demo model from week 5 in class
class Log(Document):
	text = StringField()
	timestamp = DateTimeField(default=datetime.now())

class Comment(EmbeddedDocument):
	name = StringField()
	comment = StringField()
	timestamp = DateTimeField(default=datetime.now())
	
class Idea(Document):

	creator = StringField(max_length=120, required=True, verbose_name="First name")
	title = StringField(max_length=120, required=True)
	slug = StringField()
	idea = StringField(required=True, verbose_name="What is your idea?")

	# Category is a list of Strings
	categories = ListField(StringField(max_length=30))

	# Comments is a list of Document type 'Comments' defined above
	comments = ListField( EmbeddedDocumentField(Comment) )

	# Timestamp will record the date and time idea was created.
	timestamp = DateTimeField(default=datetime.now())


# Create a Validation Form from the Idea model
IdeaForm = model_form(Idea)

