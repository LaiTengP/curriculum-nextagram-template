from flask import Blueprint, render_template,request, url_for, redirect, flash, request, session
from models.user import User
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')

@sessions_blueprint.route('/new', methods = ['GET'])
def new():
    return render_template ('sessions/new.html')

@sessions_blueprint.route ('/', methods = ['POST'])
def create():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.get_or_none(User.username == username)
    # if got user then check password
    if user:
        result = check_password_hash(user.password_hash , password)
        # if password match then login
        if result:
            flash("Password matched", "primary")
            # save user id in browser session
            # session['user_id'] = user.id 
            login_user(user)
            return redirect(url_for('users.show', username=user.username))
        # else error message
        else:
            flash("Password Not matched","danger")
            return  render_template("sessions/new.html")

    # else error message
    else:
        flash("User not found.", "danger")
        return  render_template("sessions/new.html")

@sessions_blueprint.route('/delete', methods = ['POST'])
@login_required
def destroy():
    logout_user()
    flash("Logout success!", "primary")
    return redirect(url_for("sessions.new"))