import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from database import setup_db, db_drop_and_create_all, Question, Movie, QuestionMovie, Category, Quiz,Session
from config import bearer_tokens,database

class MovieTestCase(unittest.TestCase):
    """This class represents the movies test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = database["path"]
        self.database_path = self.database_path.replace("postgres://","postgresql://")
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # set tokens
        self.simpletoken = bearer_tokens["inspector"]
        self.admintoken = bearer_tokens["admin"]

        #Initialize
        try:
            #Clear the database
            self.client().get("/deleteall",headers={'Authorization': f"Bearer {self.admintoken}"})
            #add initial data
            self.client().get("/bulk",headers={'Authorization': f"Bearer {self.admintoken}"})
           
        except:
            print("The test script could not be initialised.")

        #Test data
        self.new_question = {
            "question": "Does the movie have a lot of romance?",
            "category_id":1,
            "Type":"Generic"
        }
        self.new_movie = {
            "title": "Casino Royale",
            "category_id":1,
            "description":"After receiving a license to kill, British Secret Service agent James Bond (Daniel Craig) heads to Madagascar, where he uncovers a link to Le Chiffre (Mads Mikkelsen), a man who finances terrorist organizations. Learning that Le Chiffre plans to raise money in a high-stakes poker game, MI6 sends Bond to play against him, gambling that their newest operative will topple the man's organization."
        }
        self.new_category = {
            "category": "Some new category"
        }
        self.new_answer = {
            "answer":0.5
        }

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Test definitions
    """
    def test_index(self):
        res = self.client().get("/")
        self.assertEqual(res.status_code,200)

    def test_422_index(self):
        res = self.client().get("/?question=1&answer=wronginput")
        self.assertEqual(res.status_code,422)

    def test_get_questions_by_category(self):
        res = self.client().get("/questions/categories/1",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(len(data["data"]))

    def test_404_get_questions_by_category(self):
        res = self.client().get("/questions/categories/100",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"Resource not found")

    def test_get_single_question(self):
        res = self.client().get("/questions/1",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
        selection = Question.query.get(1)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(selection.Type, data["Type"])

    def test_404_get_single_question(self):
        res = self.client().get("/questions/100000",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)

    def test_add_question(self):
        res = self.client().post("/questions",json=self.new_question,headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
        question = Question.query.filter(Question.id==data["added_question_id"]).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(question.format()["question"],self.new_question["question"])

    def test_422_add_question(self):
        res = self.client().post("/questions",json={"some_key":"Some value"},headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data["success"],False)
       
    
    # Continue with movies
    def test_get_movies_by_category(self):
        res = self.client().get("/movies/categories/1",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(len(data["data"]))

    def test_404_get_movies_by_category(self):
        res = self.client().get("/movies/categories/100",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"Resource not found")

    def test_get_single_movie(self):
        res = self.client().get("/movies/1",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
        selection = Movie.query.get(1)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(selection.title, data["title"])

    def test_404_get_single_movie(self):
        res = self.client().get("/movies/100000",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)

    def test_patch_movie(self):
        res = self.client().patch("/movies/3",json = {"title":"Star Wars: Episode 1"},headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
        selection = Movie.query.get(3)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(selection.title, "Star Wars: Episode 1")

    def test_404_patch_movie(self):
        res = self.client().patch("/movies/3",json = {"nothing":"nothing"},headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)

    def test_add_movie(self):
        res = self.client().post("/movies",json=self.new_movie,headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
        movie = Movie.query.filter(Movie.id==data["added_movie_id"]).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(movie.format()["title"],self.new_movie["title"])

    def test_422_add_movie(self):
        res = self.client().post("/movies",json={"some_key":"Some value"},headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data["success"],False)

    # Continue with categories
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(len(data["data"]))

    def test_add_category(self):
        res = self.client().post("/categories",json=self.new_category,headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
        cat = Category.query.filter(Category.id==data["added_category_id"]).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(cat.format()["category"],self.new_category["category"])

    def test_422_add_category(self):
        res = self.client().post("/categories",json={"some_key":"Some value"},headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data["success"],False)

    # Continue with answers
    def test_get_answers_by_category(self):
        res = self.client().get("/movieData/categories/1",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(len(data["data"]))

    def test_404_get_answers_by_category(self):
        res = self.client().get("/movieData/categories/100",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"Resource not found")


    def test_get_single_answer(self):
        res = self.client().get("/movieData/1/question/1",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
        selection = QuestionMovie.query.filter(QuestionMovie.question_id==1, QuestionMovie.movie_id==1 ).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(selection.answer, data["data"]["answer"])

    def test_404_get_single_answer(self):
        res = self.client().get("/movieData/1/question/10000",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)

    def test_delete_single_answer(self):
        res = self.client().delete("/movieData/1/question/1",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
        selection = QuestionMovie.query.filter(QuestionMovie.question_id==1, QuestionMovie.movie_id==1 ).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(selection, None)

    def test_404_delete_single_answer(self):
        res = self.client().delete("/movieData/1/question/10000",headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)

    def test_add_answer(self):
        # First delete answer
        res = self.client().delete("/movieData/1/question/1",headers={'Authorization': f"Bearer {self.admintoken}"})
        # Add answer again
        res = self.client().post("/movieData/1/question/1",json=self.new_answer,headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)
        selection = QuestionMovie.query.filter(QuestionMovie.question_id==1, QuestionMovie.movie_id==1 ).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(selection.format()["answer"],self.new_answer["answer"])

    def test_422_add_answer(self):
        res = self.client().post("/movieData/1/question/1",json={"some_key":"Some value"},headers={'Authorization': f"Bearer {self.admintoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data["success"],False)

    #At least two tests of RBAC for each role
    def test_admin_access(self):
        # Try access admin endpoint with simple user role
        res = self.client().delete("/movieData/1/question/1",headers={'Authorization': f"Bearer {self.admintoken}"})

        self.assertEqual(res.status_code,200)

    def test_401_admin_access(self):
        # Try access admin endpoint with simple user role
        res = self.client().delete("/movieData/1/question/1",headers={'Authorization': f"Bearer sometoken"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,500)
       

    def test_simple_user_access(self):
        # Try access admin endpoint with simple user role
        res = self.client().get("/questions/1",headers={'Authorization': f"Bearer {self.simpletoken}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)

    def test_401_simple_user_access(self):
        # Try access admin endpoint with simple user role
        res = self.client().get("/questions/1",headers={'Authorization': f"Bearer sometoken"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,500)
     

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()