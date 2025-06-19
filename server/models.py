from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_names)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Plant(db.Model, SerializerMixin):
    __tablename__ = 'plants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_in_stock = db.Column(db.Boolean, default=True)

    serialize_rules = ()

    def __repr__(self):
        return f'<Plant {self.id}: {self.name}>'
