import os
from flask import Flask, request, jsonify, abort, session, redirect, url_for,render_template
from sqlalchemy import exc,and_,or_
import json
from flask_cors import CORS
import pandas as pd
import simplejson
import pickle
from datetime import datetime
import numpy as np

from models.ml_models import trainer, finder
from config import pagination
from database import setup_db, db_drop_and_create_all, Question, Movie, QuestionMovie, Category, Quiz,Session #Add Tables
from auth import AuthError, requires_auth


"""
#########################################################
HELPERS
#########################################################
"""

def paginate(request,selection,items_per_page):
    page = request.args.get('page', 1, type=int)
    start = (page-1)*items_per_page
    end = start + items_per_page
    elements = [el.format() for el in selection]
    current_elements = elements[start:end]
    return(current_elements)

def exist(obj, item,column):
    if column == "title":
        selection = obj.query.filter(obj.title == item).one_or_none()
    elif column == "category":
        selection = obj.query.filter(obj.category == item).one_or_none()
    elif column == "question":
        selection = obj.query.filter(obj.question == item).one_or_none()
    else:
        selection = None

    if selection is None:
        return(False)
    else:
        return(True)

def create_app(test_config=None):
    """
    #########################################################
    Init FLASK
    #########################################################
    """

    app = Flask(__name__)
    setup_db(app)
    
    CORS(app)

    ITEMS_PER_PAGE = pagination["example"]
    

    """
    #########################################################
    CORS Headers 
    #########################################################
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,PATCH')
        return response

    """
    #########################################################
    ENDPOINTS
    #########################################################
    """
    @app.route("/login-results",methods = ["GET"])
    def hello():
        return(jsonify( {
            "success":True,
            "message": "You have been logged in. Save the access_token from the URL above."
        }))

    @app.route("/logout",methods = ["GET"])
    def bye():
        return(jsonify( {
            "success":True,
            "message": "You have been logged out."
        }))


    @app.route('/',methods = ["GET"])
    def play():
        category_id = 1
        cat = Category.query.get(category_id)
        # Get frontend data
        question_id = request.args.get('question',None)
        answer = request.args.get('answer',None)

        # Load model
        model = pickle.load(open(f"models/latest_model_{category_id}.pkl","rb"))

        if answer == None:
            # Initial question: Save a new session on start
            now = datetime.now()
            sess = Session(timestamp=now,category_id = category_id,num_questions=0)
            sess.insert()
            session_id = sess.id
            # Return random question
            responses_so_far = []
            session_finder= finder(model,use_model = "advanced",responses_so_far=responses_so_far)
            # Start with a random question
            next_q_id = np.random.choice(list(session_finder.feature_imp.keys()))
            # Get initial question
            q = Question.query.get(int(next_q_id))
            return render_template('index.html', question=next_q_id, question_text=q.question,session=session_id)

        # Run within the game
        #Get session_id from URL and load data
        try:    
            session_id = int(request.args.get('session',None))
        except:
            abort(422)
        sess = Session.query.get(int(session_id))

        # Get responses_so_far
        responses = Quiz.query.filter(Quiz.session_id==session_id).all()
        responses_so_far=[{e.question_id:float(e.answer)} for e in responses]
        
        # Launch finder
        session_finder= finder(model,use_model = "advanced",responses_so_far=responses_so_far)

        # Count questions
        num_questions = len(responses)+1
        # Update question count in session database
        sess.num_questions = num_questions
        sess.update()

        # Add current answer
        session_finder._add_answer(int(question_id),float(answer))
        # Predict
        result = session_finder._predict()
        
        #Save answer to db and best predict probability
        try:
            new = Quiz(question_id = int(question_id),answer=float(answer),session_id = session_id,category_id=category_id,
                        num_question = num_questions,predict_proba=result["best_item_prob"])
            new.insert()
        except:
            abort(422)
        

        # Stop if there is no more questions to ask or threshold has been reached
        if len(session_finder.available_questions)==0 or result["best_item_prob"]>0.3:
            best_idx = result['best_item_id']
            m = Movie.query.get(int(best_idx))
            return render_template('index.html', result=m.title,session=session_id)
         
        next_q_id = int(result["next_question_id"])
        next_question_text = result["next_question_text"]
        return render_template('index.html', question=next_q_id, question_text=next_question_text,session=session_id,prob = result["best_item_prob"])

  

    ############# Questions ####################
    @app.route('/questions/categories/<category_id>',methods = ["GET"])
    @requires_auth(permission='get:questionbycategory')
    def get_question_category(payload,category_id):
        data = Question.query.filter(Question.category_id==category_id).all()
        selection = paginate(request,data,ITEMS_PER_PAGE)
        if len(selection)==0:
            abort(404)
        
        return(jsonify({
            "success":True,
            "data": selection
        }))
    
    @app.route('/questions/<question_id>',methods = ["GET"])
    @requires_auth(permission='get:singlequestion')
    def get_question(payload,question_id):
        q = Question.query.get(int(question_id))
        if q==None:
            abort(404)
        
        return(jsonify({
            "success":True,
            "id":q.id,
            "question": q.question,
            "Type":q.Type,
            "category":q.category.format()
        }))

    @app.route('/questions',methods = ["POST"])
    @requires_auth(permission='post:question')
    def add_question(payload):
        body = request.get_json()
        try:
            question = body.get("question",None)
            category_id = body.get("category_id",None)
            Type = body.get("Type",None)

            if exist(Question,question,"question"):
                abort(422)
            else: 
                new_q = Question(question=question,category_id = category_id, Type = Type) 
                new_q.insert()
        except:
            abort(422)
    
        return(jsonify({
            "success":True,
            "added_question_id":new_q.id,
            "added_question":new_q.question,
            "Type":new_q.Type,
            "category":new_q.category.format()
        }))

    ############# Movies ####################
    @app.route('/movies/categories/<category_id>',methods = ["GET"])
    @requires_auth(permission='get:moviebycategory')
    def get_movie_category(payload,category_id):
        data = Movie.query.filter(Movie.category_id==category_id).all()
        selection = paginate(request,data,ITEMS_PER_PAGE)
        if len(selection)==0:
            abort(404)
        
        return(jsonify({
            "success":True,
            "data": selection
        }))

    @app.route('/movies/<movie_id>',methods = ["GET"])
    @requires_auth(permission='get:singlemovie')
    def get_movie(payload,movie_id):
        movie = Movie.query.get(int(movie_id))
        if movie == None:
            abort(404)
        
        return(jsonify({
            "success":True,
            "id":movie.id,
            "title": movie.title,
            "description":movie.description,
            "category":movie.category.format()
        }))

    @app.route('/movies/<movie_id>',methods = ["PATCH"])
    @requires_auth(permission='patch:movie')
    def update_movie(payload,movie_id):
        body = request.get_json()
        try:
            req_title = body.get("title")
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
            movie.title = req_title
            movie.update()
        except:
            abort(404)

        return(jsonify({
            "success":True,
            "movies": movie.format()
        }))
    

    @app.route('/movies',methods = ["POST"])
    @requires_auth(permission='post:movie')
    def add_movie(payload):
        body = request.get_json()
        try:
            title = body.get("title",None)
            description = body.get("description",None)
            category_id = body.get("category_id",None)

            if exist(Movie,title,"title"):
                abort(422)
            else: 
                new = Movie(title=title,description=description,category_id=category_id) 
                new.insert()
        except:
            abort(422)
    
        return(jsonify({
            "success":True,
            "added_movie_id":new.id,
            "added_movie":new.title,
            "category":new.category.format()
        }))

    ############# Category ####################

    @app.route('/categories',methods = ["GET"])
    def retrieve_categories():
        data = Category.query.order_by("id").all()
        selection = paginate(request,data,ITEMS_PER_PAGE)
        if len(selection)==0:
            abort(404)
        
        return(jsonify({
            "success":True,
            "data": selection
        }))

    @app.route('/categories',methods = ["POST"])
    @requires_auth(permission='post:category')
    def add_category(payload):
        body = request.get_json()
        try:
            category = body.get("category",None)

            if exist(Category,category,"category"):
                abort(422)
            else: 
                new = Category(category=category) 
                new.insert()
        except:
            abort(422)
    
        return(jsonify({
            "success":True,
            "added_category_id":new.id,
            "added_category":new.category
        }))

    ############# Question Movie Answers ####################
    @app.route('/movieData/categories/<category_id>',methods = ["GET"])
    @requires_auth(permission='get:answersbycategory')
    def get_answer_category(payload,category_id):
        data = QuestionMovie.query.filter(QuestionMovie.movie.has(category_id=category_id)).all()
        selection = paginate(request,data,ITEMS_PER_PAGE)
        if len(selection)==0:
            abort(404)
        
        return(simplejson.dumps({
            "success":True,
            "data": selection
        }))

    @app.route('/movieData/<movie_id>/question/<question_id>',methods = ["GET"])
    @requires_auth(permission='get:singleanswer')
    def get_answer(payload,movie_id,question_id):
        #try:
        selection = QuestionMovie.query.filter(and_(QuestionMovie.question_id==int(question_id), QuestionMovie.movie_id==int(movie_id))).one_or_none()
        if selection==None:
            abort(404)
        else:
            return(jsonify({
            "success":True,
            "data":selection.format()
        }))
        #except:
         #   abort(404)

    @app.route('/movieData/<movie_id>/question/<question_id>',methods = ["DELETE"])
    @requires_auth(permission='delete:answer')
    def delete_answer(payload,movie_id,question_id):
        selection = QuestionMovie.query.filter(and_(QuestionMovie.question_id==question_id, QuestionMovie.movie_id==movie_id)).one_or_none()
        if selection==None:
            abort(404)
        else:
            selection.delete()
            return(jsonify({
            "success":True,
            "deleted_answer":selection.format()
        }))


    @app.route('/movieData/<movie_id>/question/<question_id>',methods = ["POST"])
    @requires_auth(permission='post:answer')
    def add_answer(payload,movie_id,question_id):
        body = request.get_json()
        #Check if ids have been passed correctly and the resources exist
        movie = Movie.query.get(int(movie_id))
        question = Question.query.get(int(question_id))
        if (movie==None) or (question==None):
            abort(404)
        #Check if for this combination a data entry already exists
        selection = QuestionMovie.query.filter(and_(QuestionMovie.question_id==question_id, QuestionMovie.movie_id==movie_id)).one_or_none()
        if selection!=None:
            abort(422)
        #Add new data
        try:
            answer = float(body.get("answer",None)) 
            new = QuestionMovie(question_id=question_id,movie_id=movie_id,answer=answer) 
            new.insert()
        except:
            abort(422)
    
        return(simplejson.dumps({
            "success":True,
            "added_answer_id":new.id,
            "added_answer":new.answer,
            "movie":movie.title,
            "question":question.question
        }))

    ############# Other ####################
    @app.route("/deleteall",methods = ["GET"])
    @requires_auth(permission='get:deleteall')
    def delete_all(payload):
        db_drop_and_create_all()
        return(jsonify( {
            "success":True,
            "message": "all data has been erased from the databases"
        }))

    @app.route('/bulk',methods = ["GET"])
    @requires_auth(permission='get:bulk')
    def bulk_add_example_data(payload):
        categories = pd.read_csv("initialdata/categories.csv",sep=";")
        movies = pd.read_csv("initialdata/movies.csv",sep=";")
        questions = pd.read_csv("initialdata/questions.csv",sep=";")
        movie_answers = pd.read_csv("initialdata/question_movie_mapping.csv",sep=";",decimal=",")

        #Add example categories
        for i,row in categories.iterrows():
            new = Category(category=row["Category"]) 
            new.insert()
    
        #Add example movies
        for i,row in movies.iterrows():
            new = Movie(title=row["title"],description=row["description"],category_id=row["category_id"]) 
            new.insert()

        #Add example questions
        for i,row in questions.iterrows():
            new = Question(question=row["question"],category_id=row["category_id"],Type=row["Type"]) 
            new.insert()

        #Add Question Answers
        for i,row in movie_answers.iterrows():
            for question_id in movie_answers.columns[1:]:
                new = QuestionMovie(question_id=question_id,movie_id=row["movie_id"],answer=row[question_id]) 
                new.insert()
        
        return(jsonify({
        "success":True
        }))


    """
    #########################################################
    ERROR HANDLING
    #########################################################
    """
    @app.errorhandler(406)
    def missing_param(error):
        return jsonify({
                        "success": False, 
                        "error": 406,
                        "message": "Missing parameters"
                        }), 406

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                        "success": False, 
                        "error": 422,
                        "message": "unprocessable"
                        }), 422

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({
            "success": False, 
            "error": 404,
            "message": "Resource not found"
            }), 404)

    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({
            "success": False, 
            "error": 400,
            "message": "Bad request"
            }), 400)

    @app.errorhandler(500)
    def server_error(error):
        return (jsonify({
            "success": False, 
            "error": 500,
            "message": "Internal server error"
            }), 500)

    
    @app.errorhandler(AuthError)
    def auth_error(error):
        return (jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['message']
        }), error.status_code)

    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
