from flask import Blueprint, render_template,request, url_for, redirect, flash
from models.user import User
from flask_login import login_required, login_user, current_user

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/', methods=['POST'])
def create():
    params = request.form
    new_user = User(username=params.get("username"), email= params.get("email"), password = params.get("password"))
    if new_user.save():
        flash ("Successfully Sign Up!", "success")
        login_user(new_user)
        return redirect(url_for("users.show", username=new_user.username))
    else:
        for err in new_user.errors:
            flash (err, "danger")
        return redirect(url_for("users.new"))

@users_blueprint.route('/<username>', methods=["GET"])
@login_required
def show(username):
    user = User.get_or_none (User.username == username)
    if user:
        return render_template("users/show.html",user=user)
    else:
        flash(f"No {username} user found.", "danger" )
        return redirect(url_for('home'))
        

@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"
    
@users_blueprint.route('/<id>/edit', methods=['GET'])
@login_required
def edit(id):
    user = User.get_or_none(User.id==id)
    if user:
        if current_user.id == int(id):
            return render_template("users/edit.html", user=user)
        else:
            flash ("You are not authorized to edit users other than yourself!", "danger")
            return redirect(url_for("users.show", username = user.username))
    else:
        flash ("No such user!")
        return redirect(url_for("home"))        

@users_blueprint.route('/<id>', methods=['POST'])
@login_required
def update(id):
    user = User.get_or_none(User.id==id)
    if user:
        if current_user.id == int(id):
            params = request.form

            user.username = params.get("username")
            user.email = params.get("email")
            password = params.get("password")
        
            if len(password) > 0:
                user.password = password
            
            if user.save():
                flash ("Profile Updated Successfully", "primary")
                return redirect(url_for("users.show", username = user.username))
            else:
                flash ("Unable to. Please try again!")
                for err in user.errors:
                    flash (err)
                return redirect(url_for("users.edit", id=user.id))
                
        else:
            flash ("You are not authorized to edit users other than yourself!", "danger")
            return redirect(url_for("users.show", username = user.username))   

    else:
        flash ("No such user!")
        return redirect(url_for("home"))        
