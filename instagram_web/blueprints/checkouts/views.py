from flask import Blueprint, render_template,request, url_for, redirect, flash
from flask_login import login_required, login_user, current_user
import braintree
from models.checkout import Checkout
from models.user import User
from instagram_web.util.helpers import generate_client_token, transact
import requests

checkouts_blueprint = Blueprint('checkouts',
                            __name__,
                            template_folder='templates')

@checkouts_blueprint.route('/new', methods=['GET'])
@login_required
def new(image_id):
    client_token = generate_client_token()
    return render_template('checkouts/new.html', client_token=client_token, image_id=image_id)

@checkouts_blueprint.route('/', methods=['POST'])
@login_required
def create(image_id):
    amount= request.form["amount"]
    result = transact({
        "amount": request.form['amount'],
        "payment_method_nonce": request.form['payment_method_nonce'],
        "options": {
        "submit_for_settlement": True
        }
    })

    if result.is_success or result.transaction:
        checkout = Checkout(sender=User.get_by_id(current_user.id), image_id=image_id, amount=amount)
        checkout.save()

        # from app import app
        # mailgun_domain = app.config.get("MAILGUN_DOMAIN")
        # mailgun_recipient = app.config.get("MAILGUN_RECIPIENT")
        # result = requests.post(f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
        # auth=("api", app.config.get("MAILGUN_API_KEY")),
        # data={"from": f"Excited User <mailgun@{mailgun_domain}>",
        # "to": [ f"{mailgun_recipient}" ],
        # "subject": "Hello Peeps",
        # "text": "Thank you for your lovely DONATION~ Testing some Mailgun awesomness!"})

        flash("Thank you for your support!", "primary")
        return redirect(url_for("images.show",id= image_id))
    else:
        flash("Sorry, fail to donate. Please try again!", "danger")
        return redirect(url_for('checkouts.new', image_id=image_id))

