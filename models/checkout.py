import peewee as pw
from models.base_model import BaseModel
from models.user import User
from models.image import Image

class Checkout(BaseModel):
    amount = pw.DecimalField()
    image = pw.ForeignKeyField(Image, backref="checkouts")
    sender = pw.ForeignKeyField(User, backref="checkouts")