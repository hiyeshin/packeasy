# -*- coding: utf-8 -*-
import os, datetime
import re
from unidecode import unidecode

from flask import Flask, session, request, url_for, escape, render_template, json, jsonify, flash, redirect, abort
# session is just a dictionary and flask converts it to cookie

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

app = Flask(__name__)   # create our flask app
app.config['CSRF_ENABLED'] = False
app.secret_key = os.environ.get('SECRET_KEY')

flask_bcrypt = Bcrypt(app)

#   uses .env file to get connection string
#   using a remote db get connection string from heroku config
# 	using a local mongodb put this in .env
#   MONGOLAB_URI=mongodb://localhost:27017/dwdfall2012
mongoengine.connect('mydata', host=os.environ.get('MONGOLAB_URI'))

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

	# below is from the library not models module	
	user = User()
	user.get_by_id(id)
	if user.is_active():
		return user
	else:
		return None

# connect the login manager to the main Flask app
login_manager.setup_app(app)



@app.route('/') # this should be equal to login page
def index():
	# get requested user's content
	# then we don't need contents 
	# but trip info
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
@app.route('/users/<username>') # display all the post. we may not need it
def user(username):

	try:
		user = models.User.objects.get(username=username)

	except Exception:
		e = sys.exc_info()
		app.logger.error(e)
		abort(404)

	# get content that is linked to user, 
	user_content = models.Content.objects(user=user)
	#trip_form = models.TripForm(request.form)

	# prepare the template data dictionary
	templateData = {
		'user' : user,
		'current_user' : current_user,
		'user_content'  : user_content,
		'users' : models.User.objects()
	}

	return render_template("home.html", **templateData)

	# if request.method == "POST" and trip_form.validate():
	# 	trip = models.Trip()
	# 	trip.date = request.form.get('date','anonymous')
	# 	trip.tripname = request.form.get('tripname','name your trip')
	# 	trip.slug = slugify(trip.tripname + " " + trip.listname)
	# 	trip.listname = request.form.get('listname','name your list')
	# 	trip.item = request.form.get('item','shampoo')
	# 	trip.quantity = request.form.get('quantity','3')
	# 	trip.reminder = request.form.get('reminder','on')

	# 	trip.save()

		# return redirect('/%s' % idea.slug)

	



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


@app.route('/create', methods=['GET','POST'])
@login_required
def admin_main():

	contentForm = models.content_form(request.form)

	if request.method=="POST" and contentForm.validate():
		app.logger.debug(request.form)
		
		newContent = models.Content()
		newContent.title = request.form.get('title')
		newContent.content = request.form.get('content')

		#link to current user
		newContent.user = current_user.get()

		try:
			newContent.save()

		except:
			e = sys.exc_info()
			app.logger.error(e)
			
		return redirect('/create')

	else:
		templateData = {
			'allContent' : models.Content.objects(user=current_user.id),
			'current_user' : current_user,
			'form' : contentForm,
			'formType' : 'New'
		}
	

	return render_template('create.html', **templateData)
		
@app.route('/admin/<content_id>', methods=['GET','POST'])
@login_required
def admin_edit_post(content_id):

	# get the content requested
	contentData = models.Content.objects.get(id=content_id)

	# if contentData exists AND is owned by current_user then continue
	if contentData and contentData.user.id == current_user.id:

		# create the content form, populate with contentData
		contentForm = models.content_form(request.form, obj=contentData)

		if request.method=="POST" and contentForm.validate():
			app.logger.debug(request.form)
			
			contentData.title = request.form.get('title')
			contentData.content = request.form.get('content')

			
			try:
				contentData.save()

			except:
				e = sys.exc_info()
				app.logger.error(e)
			
			flash("Post was updated successfully.")
			return redirect('/admin/%s' % contentData.id)

		else:
			templateData = {
				'allContent' : models.Content.objects(user=current_user.id),
				'current_user' : current_user,
				'form' : contentForm,
				'formType' : 'Update'
			}
		
		return render_template('admin.html', **templateData)

	# current user does not own requested content
	elif contentData.user.id != current_user.id:
 
		flash("Log in to edit this content.","login")
		return redirect("/login")
	else:

		abort(404)
	

@app.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
        confirm_login()
        flash(u"Reauthenticated.")
        return redirect(request.args.get("next") or url_for("index"))
    
    templateData = {}
    return render_template("/auth/reauth.html", **templateData)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("home"))


def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)



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



	