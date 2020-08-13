from flask import Blueprint, render_template,request, url_for, redirect, flash
from models.user import User
from flask_login import login_required, login_user, current_user
from instagram_web.util.helpers import upload_file_to_s3
from werkzeug import secure_filename

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
        flash("Successfully Sign Up!", "success")
        login_user(new_user)
        return redirect(url_for("users.show", username=new_user.username))
    else:
        for err in new_user.errors:
            flash(err, "danger")
        return redirect(url_for("users.new"))

@users_blueprint.route('/<username>', methods=["GET"])
@login_required
def show(username):
    user = User.get_or_none(User.username == username)
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
            flash("You are not authorized to edit users other than yourself!", "danger")
            return redirect(url_for("users.show", username = user.username))
    else:
        flash("No such user!")
        return redirect(url_for("home"))        

@users_blueprint.route('/<id>', methods=['POST'])
@login_required
def update(id):
    user = User.get_or_none(User.id==id)
    
    if user:
        if current_user.id == int(id):
            params = request.form

            user.is_private = True if params.get("private") == "on" else False

            user.username = params.get("username")
            user.email = params.get("email")

            is_private = params.get("is_private")
            if is_private == False:
                is_private == True

            else:
                is_private == False

            password = params.get("password")
            
        
            if len(password) > 0:
                user.password = password
            
            if user.save():
                flash("Profile Updated Successfully", "primary")
                return redirect(url_for("users.show", username=user.username))
            else:
                flash("Unable to edit. Please try again!")
                for err in user.errors:
                    flash(err)
                return redirect(url_for("users.edit", id=user.id))
                
        else:
            flash("You are not authorized to edit users other than yourself!", "danger")
            return redirect(url_for("users.show", username=user.username))   

    else:
        flash("No such user!")
        return redirect(url_for("home"))        

@users_blueprint.route('/<id>/upload', methods=['POST'])
@login_required
def upload(id):
    user = User.get_or_none(User.id==id)
    if user:
        if current_user.id == int(id): 
            if "profile_image" not in request.files:
                flash ("No profile image provided.")
                return redirect(url_for("users.edit", id=id))

            file = request.files["profile_image"]

            file.filename = secure_filename(file.filename)
        
            image_path = upload_file_to_s3(file,user.username )

            user.image_path = image_path
            if user.save():
                return redirect(url_for("users.show", username=user.username))
            else:
                flash("Unable to upload. Please try again later.", "danger")
                return redirect(url_for("users.edit", id=id))
        else:
            flash("You are not authorized to upload image from others account!")
            return redirect(url_for("users.show", username=user.username))   

    else:
        flash("No such user!")
        return redirect(url_for("home"))      


@users_blueprint.route('/<idol_id>/follow', methods=['POST'])
@login_required
def follow(idol_id):
    idol = User.get_by_id(idol_id)

    if current_user.follow(idol):
        if current_user.follow_status(idol).is_approved:
            flash(f"You have followed {idol.username}", "primary")
        else:
            flash(f"You have requested to follow {idol.username}","primary")
        return redirect(url_for("users.show",username=idol.username))
    else:
        flash("Unable to follow this user, try again", "danger")
        return redirect(url_for("users.show",username=idol.username))

@users_blueprint.route('/<idol_id>/unfollow', methods=['POST'])
@login_required
def unfollow(idol_id):
    idol = User.get_by_id(idol_id)

    if current_user.unfollow(idol):
        flash(f"You unfollowed {idol.username}", "primary")
        return redirect(url_for('users.show', username=idol.username))
    else:
        flash("Unable to unfollow this user, try again", "danger")
        return redirect(url_for("users.show",username=idol.username))

@users_blueprint.route('<username>/friend', methods=['GET'])
@login_required
def friend(username):
    user = User.get_or_none(User.username == username)
    if user:
        return render_template("users/friend.html",user=user)
    else:
        flash(f"No {username} user found.", "danger" )
        return redirect(url_for('home'))

@users_blueprint.route('/<fan_id>/approve', methods=['POST'])
@login_required
def approve(fan_id):
    fan = User.get_by_id(fan_id)

    if current_user.approve_request(fan):
        flash(f"You approve {fan.username}'s request", "primary")
        return redirect(url_for('users.show', username=current_user.username))
    else:
        flash(f"Unable to approve this user, try again", "danger")
        return redirect(url_for('users.show', username=current_user.username))

@users_blueprint.route('/<fan_id>/delete_request', methods=['POST'])
@login_required
def delete_request(fan_id):
    fan = User.get_by_id(fan_id)

    if fan.unfollow(User.get_by_id(current_user.id)):
        flash(f"You delete {fan.username}'s request", "primary")
        return redirect(url_for('users.show', username=current_user.username))
    else:
        flash(f"Unable to delete this user's request, try again", "danger")
        return redirect(url_for('users.show', username=current_user.username))