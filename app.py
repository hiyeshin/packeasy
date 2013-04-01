# -*- coding: utf-8 -*-
import os, datetime
import re
from unidecode import unidecode

from flask import Flask, session, request, url_for, escape, render_template, json, jsonify, flash, redirect, abort

# import all of mongoengine
from mongoengine import *
import models

from flask.ext.mongoengine import mongoengine

# for json needs
import json
from flask import jsonify

# below is for Flask-login

from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
import requests

from flaskext.bcrypt import Bcrypt

#custom user library - maps User object to User model
from libs.user import *

#################################################################
############ importing is over and now it's flask code ##########
#################################################################

app = Flask(__name__)   # create our flask app
app.config['CSRF_ENABLED'] = False

# --------- Database Connection ---------
# MongoDB connection to MongoLab's database
connect('mydata', host=os.environ.get('SECRET_KEY'))
flask_bcrypt = Bcrypt(app)

#mongolab connection
# uses .env file to get connection string
# using a remote db get connection string from heroku config
# 	using a local mongodb put this in .env
#   MONGOLAB_URI=mongodb://localhost:27017/dwdfall2012
mongoengine.connect('userdemo', host=os.environ.get('MONGOLAB_URI'))

# Login management defined
# reference http://packages.python.org/Flask-Login/#configuring-your-application
login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

# Flask-Login requires a 'user_loader' callback 
# This method will called with each Flask route request automatically
# When this callback runs, it will populate the User object, current_user
# reference http://packages.python.org/Flask-Login/#how-it-works
@login_manager.user_loader
def load_user(id):
	if id is None:
		redirect('/login')

	user = User()
	user.get_by_id(id)
	if user.is_active():
		return user
	else:
		return None

# connect the login manager to the main Flask app
login_manager.setup_app(app)



@app.route('/')
def index():
	# get requested user's content
	user_content = models.Content.objects

	# prepare the template data dictionary
	templateData = {
		'current_user' : current_user,
		'user_content'  : user_content,
		'users' : models.User.objects()
	}
	
	app.logger.debug(current_user)

	return render_template('home.html', **templateData)
	

# hardcoded categories for the checkboxes on the form
# categories = ['web','physical computing','software','video','music','installation','assistive technology','developing nations','business','social networks']
# --------- Routes ----------

# this is our main user page
@app.route('/users/<username>', method = ['GET', 'POST'])
def user(username):

	# Does requested username exists, 404 if not
	try:
		user = models.User.objects.get(username=username)

	except Exception:
		e = sys.exc_info()
		app.logger.error(e)
		abort(404)

	# get content that is linked to user, 
	user_content = models.Content.objects(user=user)

	# prepare the template data dictionary
	templateData = {
		'user' : user,
		'current_user' : current_user,
		'user_content'  : user_content,
		'users' : models.User.objects()
	}


	if request.method == "POST" && trip_form.validate():
		trip = models.Trip()
		trip.date = request.form.get('date','anonymous')
		trip.tripname = request.form.get('tripname','name your trip')
		trip.slug = slugify(trip.tripname + " " + trip.listname)
		trip.listname = request.form.get('listname','name your list')
		trip.item = request.form.get('item','shampoo')
		trip.quantity = request.form.get('quantity','3')
		trip.reminder = request.form.get('reminder','on')

		trip.save()

		return redirect('/%s' % idea.slug)

	else:
		templateData = {
			'trips': models.Idea.objects()
			'form' : trip_form
		}

		return render_template("home.html", **templateData)



	# return render_template('user_content.html', **templateData)


@app.route("/register", methods=['GET','POST'])
def register():
	
	# prepare registration form 
	registerForm = models.SignupForm(request.form)
	app.logger.info(request.form)

	if request.method == 'POST' and registerForm.validate():
		email = request.form['email']
		username = request.form['username']

		# generate password hash
		password_hash = flask_bcrypt.generate_password_hash(request.form['password'])
		
		# prepare User
		user = User(username=username, email=email, password=password_hash)
		
		# save new user, but there might be exceptions (uniqueness of email and/or username)
		try:
			user.save()	
			if login_user(user, remember="no"):
				flash("Logged in!")
				return redirect(request.args.get("next") or '/')
			else:
				flash("unable to log you in")

		# got an error, most likely a uniqueness error
		except mongoengine.queryset.NotUniqueError:
			e = sys.exc_info()
			exception, error, obj = e
			
			app.logger.error(e)
			app.logger.error(error)
			app.logger.error(type(error))

			# uniqueness error was raised. tell user (via flash messaging) which error they need to fix.
			if str(error).find("email") > -1:			
				flash("Email submitted is already registered.","register")
	
			elif str(error).find("username") > -1:
				flash("Username is already registered. Pick another.","register")

			app.logger.error(error)	

	# prepare registration form			
	templateData = {
		'form' : registerForm
	}
	
	return render_template("/auth/register.html", **templateData)

	
# Login route - will display login form and receive POST to authenicate a user
@app.route("/login", methods=["GET", "POST"])
def login():

	# get the login and registration forms
	loginForm = models.LoginForm(request.form)
	
	# is user trying to log in?
	# 
	if request.method == "POST" and 'email' in request.form:
		email = request.form["email"]

		user = User().get_by_email_w_password(email)
		
		# if user in database and password hash match then log in.
	  	if user and flask_bcrypt.check_password_hash(user.password,request.form["password"]) and user.is_active():
			remember = request.form.get("remember", "no") == "yes"

			if login_user(user, remember=remember):
				flash("Logged in!")
				return redirect(request.args.get("next") or '/admin')
			else:

				flash("unable to log you in","login")
	
		else:
			flash("Incorrect email and password submission","login")
			return redirect("/login")

	else:

		templateData = {
			'form' : loginForm
		}

		return render_template('/auth/login.html', **templateData)


# # Display all ideas for a specific category
# @app.route("/category/<cat_name>")
# def by_category(cat_name):

# 	# try and get ideas where cat_name is inside the categories list
# 	try:
# 		ideas = models.Idea.objects(categories=cat_name)

# 	# not found, abort w/ 404 page
# 	except:
# 		abort(404)

# 	# prepare data for template
# 	templateData = {
# 		'current_category' : {
# 			'slug' : cat_name,
# 			'name' : cat_name.replace('_',' ')
# 		},
# 		'ideas' : ideas,
# 		'categories' : categories
# 	}

# 	# render and return template
# 	return render_template('category_listing.html', **templateData)


# @app.route("/ideas/<idea_slug>")
# def idea_display(idea_slug):

# 	# get idea by idea_slug
# 	try:
# 		idea = models.Idea.objects.get(slug=idea_slug)
# 	except:
# 		abort(404)

# 	# prepare template data
# 	templateData = {
# 		'idea' : idea
# 	}

# 	# render and return the template
# 	return render_template('idea_entry.html', **templateData)

# @app.route("/ideas/<idea_slug>/edit", methods=['GET','POST'])
# def idea_edit(idea_slug):

	
# 	# try and get the Idea from the database / 404 if not found
# 	try:
# 		idea = models.Idea.objects.get(slug=idea_slug)
		
# 		# get Idea form from models.py
# 		# if http post, populate with user submitted form data
# 		# else, populate the form with the database record
# 		idea_form = models.IdeaForm(request.form, obj=idea)	
# 	except:
# 		abort(404)

# 	# was post received and was the form valid?
# 	if request.method == "POST" and idea_form.validate():
	
# 		# get form data - update a few fields
# 		# note we're skipping the update of slug (incase anyone has previously bookmarked)
# 		idea.creator = request.form.get('creator','anonymous')
# 		idea.title = request.form.get('title','no title')
# 		idea.idea = request.form.get('idea','')
# 		idea.categories = request.form.getlist('categories')

# 		idea.save() # save changes

# 		return redirect('/ideas/%s/edit' % idea.slug)

# 	else:

# 		# for form management, checkboxes are weird (in wtforms)
# 		# prepare checklist items for form
# 		# you'll need to take the form checkboxes submitted
# 		# and idea_form.categories list needs to be populated.
# 		if request.method=="POST" and request.form.getlist('categories'):
# 			for c in request.form.getlist('categories'):
# 				idea_form.categories.append_entry(c)

# 		templateData = {
# 			'categories' : categories,
# 			'form' : idea_form,
# 			'idea' : idea
# 		}

# 		return render_template("idea_edit.html", **templateData)


# @app.route("/ideas/<idea_id>/comment", methods=['POST'])
# def idea_comment(idea_id):

# 	name = request.form.get('name')
# 	comment = request.form.get('comment')

# 	if name == '' or comment == '':
# 		# no name or comment, return to page
# 		return redirect(request.referrer)


# 	#get the idea by id
# 	try:
# 		idea = models.Idea.objects.get(id=idea_id)
# 	except:
# 		# error, return to where you came from
# 		return redirect(request.referrer)


# 	# create comment
# 	comment = models.Comment()
# 	comment.name = request.form.get('name')
# 	comment.comment = request.form.get('comment')
	
# 	# append comment to idea
# 	idea.comments.append(comment)

# 	# save it
# 	idea.save()

# 	return redirect('/ideas/%s' % idea.slug)


# @app.route('/data/ideas')
# def data_ideas():
# 	ideas = models.Idea.objects().order_by('+timestamp').limit(10)

# 	if ideas:
# 		public_ideas = []

# 		#prep data for json
# 		for i in ideas:
			
# 			tmpIdea = {
# 				'creator' : i.creator,
# 				'title' : i.title,
# 				'idea' : i.idea,
# 				'timestamp' : str( i.timestamp )
# 			}

# 			# comments / our embedded documents

# 			tmpIdea['comments'] = [] # list - will hold all comment dictionaries
			
# 			# loop through idea comments
# 			for c in i.comments:
# 				comment_dict = {
# 					'name' : c.name,
# 					'comment' : c.comment,
# 					'timestamp' : str( c.timestamp )
# 				}

# 				# append comment_dict to ['comments']
# 				tmpIdea['comments'].append(comment_dict)

# 			public_ideas.append( tmpIdea )

# 		# prepare dictionary for JSON return
# 		data = {
# 			'status' : 'OK',
# 			'ideas' : public_ideas
# 		}

# 		# jsonify (imported from Flask above)
# 		# will convert 'data' dictionary and 
# 		return jsonify(data)

# 	else:
# 		error = {
# 			'status' : 'error',
# 			'msg' : 'unable to retrieve ideas'
# 		}
# 		return jsonify(error)

# @app.route('/getideas')
# def get_remote_ideas():

# 	# ideas available via json
# 	ideas_url = "http://itp-ideas-dwd.herokuapp.com/data/ideas"

# 	# make a GET request to the url
# 	idea_request = requests.get(ideas_url)

# 	# log out what we got
# 	app.logger.info(idea_request.json)

# 	# requests will automatically convert json for us.
# 	# .json will convert incoming json to Python dictionary for us
# 	ideas_data = idea_request.json

# 	# alternative way
# 	# ideas_data = json.loads( idea_request.text )

# 	# the returned json looks like
# 	# {
# 	# 	'status' : 'OK',
# 	# 	'ideas' : [
# 	# 		{
# 	# 		timestamp: "2012-10-02 09:16:54.086000",
# 	# 		title: "Immortality",
# 	# 		idea: "Immortality is the ability to live forever, or put another way, it is an immunity from death. It is unknown whether human physical (material) immortality is an achievable condition.",
# 	# 		comments: [ ],
# 	# 		creator: "John"
# 	# 		},
# 	# 		...
# 	# 	]
# 	# }

# 	if ideas_data.get('status') == "OK":
# 		templateData = {
# 			'ideas' : ideas_data.get('ideas') # get the ideas from the returned json
# 		}

# 		return render_template('remote_ideas.html', **templateData)

	
# 	else:
# 		return "uhoh something went wrong - status = %s" % ideas_data.get('status')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# slugify the title 
# via http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
	"""Generates an ASCII-only slug."""
	result = []
	for word in _punct_re.split(text.lower()):
		result.extend(unidecode(word).split())
	return unicode(delim.join(result))



# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)



	