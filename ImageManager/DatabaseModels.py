from datetime import datetime
import re
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from app import app
from utils import HTTPRequestError
from conf import CONFIG

app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG.get_db_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(app.config['SQLALCHEMY_DATABASE_URI'])

db = SQLAlchemy(app)


class ImageTemplate(db.Model):
    __tablename__ = 'templates'

    id = db.Column(db.Integer, db.Sequence('template_id'), primary_key=True)
    label = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.now)

    attrs = db.relationship("ImageAttr", back_populates="template", lazy='joined', cascade="delete")
    images = db.relationship("Image", secondary='image_template', back_populates="templates")

    def __repr__(self):
        return "<Template(label='%s')>" % self.label


class ImageAttr(db.Model):
    __tablename__ = 'attrs'

    id = db.Column(db.Integer, db.Sequence('attr_id'), primary_key=True)
    label = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.now)

    type = db.Column(db.String(32), nullable=False)
    value_type = db.Column(db.String(32), nullable=False)
    static_value = db.Column(db.String(128))

    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=False)
    template = db.relationship("ImageTemplate", back_populates="attrs")

    def __repr__(self):
        return "<Attr(label='%s', type='%s', value_type='%s')>" % (
            self.label, self.type, self.value_type)


class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.String(4), unique=True, nullable=False, primary_key=True)
    label = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.now)

    # template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=False)
    templates = db.relationship("ImageTemplate", secondary='image_template', back_populates="images")

    persistence = db.Column(db.String(128))

    def __repr__(self):
        return "<Image(label='%s')>" % self.label


class ImageTemplateMap(db.Model):
    __tablename__ = 'image_template'
    image_id = db.Column(db.String(4), db.ForeignKey('images.id'), primary_key=True, index=True)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), primary_key=True, index=True)


def assert_image_exists(image_id):
    try:
        return Image.query.filter_by(id=image_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise HTTPRequestError(404, "No such image: %s" % image_id)


def assert_template_exists(template_id):
    try:
        return ImageTemplate.query.filter_by(id=template_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise HTTPRequestError(404, "No such template: %s" % template_id)


def assert_image_relation_exists(image_id, template_id):
    try:
        return ImageTemplateMap.query.filter_by(image_id=image_id, template_id=template_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise HTTPRequestError(404, "Image %s is not associated with template %s" % (image_id, template_id))


def handle_consistency_exception(error):
    # message = error.message.replace('\n','')
    message = re.sub(r"(^\(.*?\))|\n", "", error.message)
    raise HTTPRequestError(400, message)
