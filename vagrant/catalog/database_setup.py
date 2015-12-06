from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

	@property
	def serialize(self):
		return {
			'name': self.name,
			'email': self.email,
			'picture': self.picture,
			'id': self.id,
		}

class Catalog(Base):
	__tablename__ = 'catalog'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User, backref='catalogs')

	@property
	def serialize(self):
		"""Retrun object data in easily serializeable format"""
		return {
			'id': self.id,
			'name': self.name,
			'user_name': self.user.name,
			'items': [i.serialize for i in self.items],
		}

class Item(Base):
	__tablename__ = 'item'

	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False)
	description = Column(String(250))
	catalog_id = Column(Integer, ForeignKey('catalog.id'))
	catalog = relationship(Catalog, backref='items')
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User, backref='items')
	last_update_time = Column(DateTime, default=func.now())

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'description': self.description,
			'catalog': self.catalog.name,
			'user_name': self.user.name,
		}

engine = create_engine('sqlite:///catalogitemwithuser.db')

Base.metadata.create_all(engine)

