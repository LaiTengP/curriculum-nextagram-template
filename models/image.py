import peewee as pw
from playhouse.hybrid import hybrid_property
from models.base_model import BaseModel
from models.user import User

class Image(BaseModel):
    user = pw.ForeignKeyField(User, backref="images", on_delete="CASCADE") #on_delete CASCADE means when delete certain user, auto delete related images
    image_url = pw.TextField(null=False)

    @hybrid_property
    def full_image_url(self):
        from app import app
        return app.config.get("S3_LOCATION") + self.image_url
