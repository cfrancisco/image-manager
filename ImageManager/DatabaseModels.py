from datetime import datetime
import re
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from .app import app
from .utils import HTTPRequestError
from .conf import CONFIG
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from minio import Minio

app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG.get_db_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

minioClient = Minio(CONFIG.s3url, CONFIG.s3user, CONFIG.s3pass, secure=False)

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.String(36), unique=True, nullable=False, primary_key=True)
    label = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.now)
    fw_version = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    attrs = db.relationship("Attributes", cascade='all, delete-orphan')
    def __repr__(self):
        return "<Image(label={}, fw_version={})>".format(self.label, self.fw_version)

class Attributes(db.Model):
    __tablename__ = 'attributes'
    
    id = db.Column(db.String(36), unique=True, nullable=False, primary_key=True)
    label = db.Column(db.String(128), nullable=False)
    value = db.Column(db.String(128), nullable=True)
    image_id = db.Column(db.String(36), db.ForeignKey('images.id'))


def assert_image_exists(image_id):
    try:
        return Image.query.filter_by(id=image_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise HTTPRequestError(404, "No such image: %s" % image_id)


def get_all_images():
    return Image.query.all()


def get_all_images_filter(label):
    try:
        return Image.query.filter_by(**label).all()
    except InvalidRequestError:
        raise HTTPRequestError(400, 'Invalid query param supplied')


def handle_consistency_exception(error):
    # message = error.message.replace('\n','')
    message = re.sub(r"(^\(.*?\))|\n", "", error.message)
    raise HTTPRequestError(400, message)
