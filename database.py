import os
from sqlalchemy import Column, String, Integer, Boolean,create_engine,Numeric,DateTime
from flask_sqlalchemy import SQLAlchemy
import json

from config import database

database_path = database["path"] 
database_path = database_path.replace("postgres://","postgresql://")

db = SQLAlchemy()

"""
#########################################################
DB Setup
#########################################################
"""
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


"""
#########################################################
CLASSES / ENTITIES
#########################################################
"""
class Session(db.Model):  
  __tablename__ = 'sessions'
  id = Column(Integer, primary_key=True)
  category_id = Column(Integer,db.ForeignKey("categories.id"),nullable=False)
  timestamp = Column(DateTime,nullable = False)
  num_questions = Column(Integer,nullable=True)

  def __init__(self, timestamp,category_id,num_questions):
    self.timestamp = timestamp
    self.category_id = category_id
    self.num_questions = num_questions

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      "timestamp":self.timestamp
    }


class Quiz(db.Model):  
  __tablename__ = 'quizzes'

  id = Column(Integer, primary_key=True)
  question_id = Column(Integer,db.ForeignKey("questions.id"),nullable=False)
  session_id = Column(Integer,db.ForeignKey("sessions.id"),nullable=False)
  category_id = Column(Integer,db.ForeignKey("categories.id"),nullable=False)
  answer = Column(Numeric,nullable=False)
  num_question = Column(Integer,nullable=False)
  predict_proba = Column(Numeric,nullable=False)
  #user_feedback = db.relationship("ToolFeedback",backref = "Quiz",lazy=True)

  def __init__(self, question_id,session_id,answer,category_id,num_question,predict_proba):
    self.question_id = question_id
    self.session_id = session_id
    self.answer = answer
    self.category_id = category_id
    self.predict_proba = predict_proba
    self.num_question = num_question

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      "session_id":self.session_id,
      "question_id":self.question_id,
      "answer":self.answer,
      "category_id":self.category_id
    }

class Category(db.Model):  
  __tablename__ = 'categories'

  id = Column(Integer, primary_key=True)
  category = Column(String,nullable=False)

  def __init__(self, category):
    self.category = category

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      "category":self.category
    }

class Question(db.Model):  
  __tablename__ = 'questions'

  id = Column(Integer, primary_key=True)
  question = Column(String,nullable=False)
  Type = Column(String,nullable=False)
  category_id = Column(Integer,db.ForeignKey("categories.id"),nullable=False)
  category = db.relationship("Category",backref = "Question",lazy=True)

  def __init__(self, question,category_id,Type):
    self.question = question
    self.category_id = category_id
    self.Type = Type

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'question': self.question,
      "category":self.category.format(),
      "Type":self.Type
    }

class Movie(db.Model):  
  __tablename__ = 'movies'

  id = Column(Integer, primary_key=True)
  title = Column(String,nullable=False)
  description = Column(String)
  category_id = Column(Integer,db.ForeignKey("categories.id"),nullable=False)
  category = db.relationship("Category",backref = "Movie",lazy=True)

  def __init__(self, title,description,category_id):
    self.title = title
    self.description = description
    self.category_id = category_id

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'title': self.title,
      "description":self.description,
      "category_id":self.category_id,
      "category":self.category.format()
    }

class QuestionMovie(db.Model):  
  __tablename__ = 'QuestionMovie'

  id = Column(Integer, primary_key=True)
  question_id = Column(Integer,db.ForeignKey("questions.id"),nullable=False)
  movie_id = Column(Integer,db.ForeignKey("movies.id"),nullable=False)
  answer = Column(Numeric,nullable=False)
  movie = db.relationship("Movie",backref = "QuestionMovie",lazy=True)
  question = db.relationship("Question",backref = "QuestionMovie",lazy=True)

  def __init__(self, question_id,movie_id,answer):
    self.question_id = question_id
    self.movie_id = movie_id
    self.answer = answer

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      "movie_id":self.movie_id,
      "question_id":self.question_id,
      'answer': self.answer
    }
