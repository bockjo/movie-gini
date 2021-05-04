# Movie Gini
This application will read your mind just like magic and tell you what movie you are thinking of, just by asking a few questions. Go to https://movie-gini.herokuapp.com/ answer the questions while thinking of one of the following movies:

Titanic
E.T. the Extra-Terrestrial
Star Wars
The Lord of the Rings: The Return of the King
Terminator
The Lion King
Jurassic Park
Harry Potter and the Sorcerer's Stone
Schindler's List
The Dark Knight
Pirates of the Caribbean: The Curse of the Black Pearl
Transformers
Saving Private Ryan
The Matrix
Gladiator
The Avengers

## Capstone Project for Udacity's Full Stack Developer Nanodegree
Heroku Link: https://movie-gini.herokuapp.com/
While running locally: http://127.0.0.1:5000/

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python).

#### Virtual Enviornment

Recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

## Running locally

Before running the application locally, adjust `config.py` file in root directory to your settings:
- Replace the following import statements
  ```
    database = {
    "path": os.environ["GINI_DATABASE_URI"]
            }
  ```
  with
  ```
    database = {
    "path": "<YOUR DATABASE PATH>"
            }
  ```

To run the server, execute:

```bash
export FLASK_APP=app.py
flask run --reload
```

Setting the `FLASK_APP` variable to `app.py` directs flask to use the `app.py` file to find the application. 

Using the `--reload` flag will detect file changes and restart the server automatically.

## Authentication
This application requires authentication to perform various actions. All the endpoints require various permissions, except the root endpoint, that are passed via the `Bearer` token.

The application has two different types of roles:
- Admin
  - can access all endpoints.
- Inspector
  - can only access the GET enpoints and has the following permissions:
  - `get:answersbycategory, get:bulk, get:deleteall, get:moviebycategory, get:questionbycategory, get:singleanswer, get:singlemovie, get:singlequestion`

If you only want to test the API (i.e. Project Reviewer), you can simply take the existing bearer tokens in `config.py`.

Of course you can set-up your own Authentication service as well. If you already know your way around `Auth0`, just insert your data 
into `config.py` => auth0_config.

## API Reference

## Getting Started
This application can be run locally. The hosted version is at `https://movie-gini.herokuapp.com/`.

## Error Handling
The API will return the following errors based on how the request fails:
 - 400: Bad Request
 - 401: Unauthorized
 - 403: Forbidden
 - 404: Not Found
 - 405: Method Not Allowed
 - 406: Missing parameters
 - 422: Unprocessable Entity
 - 500: Internal Server Error

## Endpoints

#### GET /
 - General
   - root endpoint
   - Will launch the quiz and load the html front end
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/`


#### GET /questions/categories/{category_id}
 - General
   - gets all questions from a certain category
   - requires `get:questionbycategory` permission
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/questions/categories/1`

<details>
<summary>Sample Response</summary>

```
{
  "data": [
    {
      "Type": "Specific",
      "category": {
        "category": "Generic",
        "id": 1
      },
      "id": 1,
      "question": "Is the movie about a couple who fall in love on a cruise ship?"
    },
    {
      "Type": "Specific",
      "category": {
        "category": "Generic",
        "id": 1
      },
      "id": 2,
      "question": "Is an alien the main character in the movie?"
    }
  ],
  "success": true
}

```
  
</details>

#### GET /questions/{question_id}
 - General
   - gets a specific question
   - requires `get:singlequestion` permission
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/questions/1`

<details>
<summary>Sample Response</summary>

```
{
  "Type": "Specific",
  "category": {
    "category": "Generic",
    "id": 1
  },
  "id": 1,
  "question": "Is the movie about a couple who fall in love on a cruise ship?",
  "success": true
}


```
  
</details>

#### POST /questions
 - General
   - creates a new question
   - requires `admin` role.
   - requires `post:question` permission
 
 - Request Body
   - question: string, required
   - category_id: integer, required
   - Type: string, required, values should be ['Generic', 'Specific']
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/questions/`
   - Request Body
     ```
        {
            "question": "Is there a lot of romance in the movie?",
            "category_id": 1,
            "Type": "Generic"
        }
     ```

<details>
<summary>Sample Response</summary>

```
{
  "Type": "Generic",
  "added_question": "Is there a lot of romance in the movie?",
  "added_question_id": 30,
  "category": {
    "category": "Generic",
    "id": 1
  },
  "success": true
}

```
  
</details>

#### GET /movies/categories/{category_id}
 - General
   - Get paginated movies by category id
   - requires `get:moviebycategory` permission
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/movies/categories/1`

<details>
<summary>Sample Response</summary>

```
{
  "data": [
    {
      "category": {
        "category": "Generic",
        "id": 1
      },
      "category_id": 1,
      "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
      "id": 1,
      "title": "Titanic"
    },
    {
      "category": {
        "category": "Generic",
        "id": 1
      },
      "category_id": 1,
      "description": "A troubled child summons the courage to help a friendly alien escape Earth and return to his home world.",
      "id": 2,
      "title": "E.T. the Extra-Terrestrial"
    }
  ],
  "success": true
}


```
  
</details>

#### GET /movies/{id}
 - General
   - Get single movie by id
   - requires `get:singlemovie` permission
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/movies/1`

<details>
<summary>Sample Response</summary>

```
{
  "category": {
    "category": "Generic",
    "id": 1
  },
  "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
  "id": 1,
  "success": true,
  "title": "Titanic"
}



```
</details>

#### PATCH /movies/{id}
 - General
   - change title of a movie
   - requires `admin` role.
   - requires `patch:movie` permission
 
 - Request Body
   - title: string, required
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/movies/1`
   - Request Body
     ```
        {
            "title": "Titanic movie",
        }
     ```

<details>
<summary>Sample Response</summary>

```
{
  "movies": {
    "category": {
      "category": "Generic",
      "id": 1
    },
    "category_id": 1,
    "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
    "id": 1,
    "title": "Titanic movie"
  },
  "success": true
}

```
  
</details>

#### POST /movies
 - General
   - Add a new movie
   - requires `admin` role.
   - requires `post:movie` permission
 
 - Request Body
   - title: string, required
   - category_id: integer, required
   - description: string, optional
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/movies`
   - Request Body
     ```
        {
            "title": "Casino Royale",
            "category_id":1,
            "description":"After receiving a license to kill, British Secret Service agent James Bond (Daniel Craig) heads to Madagascar, where he uncovers a link to Le Chiffre (Mads Mikkelsen), a man who finances terrorist organizations. Learning that Le Chiffre plans to raise money in a high-stakes poker game, MI6 sends Bond to play against him, gambling that their newest operative will topple the man's organization."
        }
     ```

<details>
<summary>Sample Response</summary>

```
{
  "added_movie": "Casino Royale",
  "added_movie_id": 17,
  "category": {
    "category": "Generic",
    "id": 1
  },
  "success": true
}

```
</details>


#### GET /categories
 - General
   - Get all categories
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/categories`

<details>
<summary>Sample Response</summary>

```
{
  "categories": [
    {
      "category": "Generic",
      "id": 1
    }
  ],
  "success": true
}

```
</details>

#### POST /categories
 - General
   - Add a new movie
   - requires `admin` role.
   - requires `post:category` permission
 
 - Request Body
   - category: string, required
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/categories`
   - Request Body
     ```
        {
            "category": "Action"
        }
     ```

<details>
<summary>Sample Response</summary>

```
{
  "added_category": "Action",
  "added_category_id": 2,
  "success": true
}


```
</details>


#### GET /movieData/categories/{category_id}
 - General
   - Get all paginated answers to movies by category_id
   - requires `get:answersbycategory` permission
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/movieData/categories/1`

<details>
<summary>Sample Response</summary>

```
{"success": true, "data": [{"id": 1, "movie_id": 1, "question_id": 1, "answer": 1.0}, {"id": 2, "movie_id": 1, "question_id": 2, "answer": 0.0}, {"id": 3, "movie_id": 1, "question_id": 3, "answer": 0.0}, {"id": 4, "movie_id": 1, "question_id": 4, "answer": 0.0}, {"id": 5, "movie_id": 1, "question_id": 5, "answer": 0.0}, {"id": 6, "movie_id": 1, "question_id": 6, "answer": 0.0}, {"id": 7, "movie_id": 1, "question_id": 7, "answer": 0.0}, {"id": 8, "movie_id": 1, "question_id": 8, "answer": 0.0}, {"id": 9, "movie_id": 1, "question_id": 9, "answer": 0.0}, {"id": 10, "movie_id": 1, "question_id": 10, "answer": 0.0}]}

```
</details>

#### GET /movieData/{movie_id}/question/{question_id}
 - General
   - Get a single answer for a specifc movie (movie_id) and question (question_id)
   - requires `get:singleanswer` permission
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/movieData/1/question/1`

<details>
<summary>Sample Response</summary>

```
{
  "data": {
    "answer": 1.0,
    "id": 1,
    "movie_id": 1,
    "question_id": 1
  },
  "success": true
}


```
</details>

#### DELETE /movieData/{movie_id}/question/{question_id}
 - General
   - Delete a single answer for a specifc movie (movie_id) and question (question_id)
   - requires `admin` role.
   - requires `delete:answer` permission
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/movieData/1/question/1`

<details>
<summary>Sample Response</summary>

```
{
  "deleted_answer": {
    "answer": 1.0,
    "id": 1,
    "movie_id": 1,
    "question_id": 1
  },
  "success": true
}

```
</details>


#### POST /movieData/{movie_id}/question/{question_id}
 - General
   - Add a new answer for a given movie (movie_id) and question (question_id)
   - requires `admin` role.
   - requires `post:answer` permission
 
 - Request Body
   - answer: numeric, required
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/movieData/1/question/1`
   - Request Body
     ```
        {
            "answer": 1.0
        }
     ```

<details>
<summary>Sample Response</summary>

```
{"success": true, "added_answer_id": 465, "added_answer": 1.0, "movie": "Titanic", "question": "Is the movie about a couple who fall in love on a cruise ship?"}

```
</details>

#### GET /deleteall
 - General
   - Erases all entries from the database
   - requires `admin` role.
   - requires `get:deleteall` permission
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/deleteall`

<details>
<summary>Sample Response</summary>

```
{
  "message": "all data has been erased from the databases",
  "success": true
}

```
</details>

#### GET /bulk
 - General
   - Bulk upload initial movies dataset
   - requires `admin` role.
   - requires `get:bulk` permission
 
 - Sample Request
   - `https://movie-gini.herokuapp.com/bulk`

<details>
<summary>Sample Response</summary>

```
{
  "success": true
}

```
</details>
