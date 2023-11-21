from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Integer, String, ForeignKey
from sqlalchemy.orm import validates, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)



class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'
    serialize_rules = ('-signups.activity', )

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)
    difficulty = mapped_column(Integer)

    signups = relationship ('Signup',
                               back_populates = 'activity',
                               cascade = 'all, delete-orphan')
    signup_camper = association_proxy('signups', 'camper')
    
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}, {self.difficulty}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'
    serialize_rules=('-signups.camper', )

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    age = mapped_column(Integer)

    signups = relationship(
        'Signup',
        back_populates = 'camper',
        cascade = 'all, delete-orphan'
    )
    activities = association_proxy('signups', 'activity')
    
    @validates('name')
    def validate_name(self, key, new_name):
        if not new_name:
            raise ValueError ("Must have a name")
        return new_name
    
    @validates('age')
    def validate_ag(self, key, new_age):
        if not (new_age >=8 and new_age <= 18):
            raise ValueError ("Must be between 8 and 18")
        return new_age

    def __repr__(self):
        return f'<Camper {self.id}, {self.name}, {self.age}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'
    serialize_rules = ('-activity.signups',
                       '-camper.signups',
                       '-activity.id',
                       '-camper.id')

    id = mapped_column(Integer, primary_key=True)
    time = mapped_column(Integer)
    activity_id  = mapped_column(Integer, ForeignKey('activities.id'))
    camper_id = mapped_column(Integer, ForeignKey('campers.id'))
    
    activity = relationship('Activity', back_populates = 'signups')
    camper = relationship('Camper', back_populates = 'signups')
    
    @validates('time')
    def validate_ag(self, key, new_time):
        if not (new_time >=0 and new_time <= 23):
            raise ValueError ("Must be between 0 and 23")
        return new_time
    
    def __repr__(self):
        return f'<Signup {self.id}, {self.time}, {self.activity_id}, {self.camper_id}>'
   
# add any models you may need.
