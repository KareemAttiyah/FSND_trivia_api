import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    try:
      categories = Category.query.all()
      categories_list = {}

      for category in categories:
        categories_list[category.id] = category.type

      if len(categories_list) == 0 :
        abort(404)

      return jsonify({
        'success':True,
        'categories': categories_list
      }),200
    except BaseException: 
      abort(500)
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():

    categories = Category.query.all()
    categories_list = {}

    for category in categories:
      categories_list[category.id] = category.type

    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category': None,
      'categories': categories_list
    }),200

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    try:
      
      question = Question.query.get(question_id)
      # filter(Question.id == question_id).one_or_none()
      if question:
        question.delete()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.all()
        categories_list = {}
        for category in categories:
          categories_list[category.id] = category.type

        return jsonify({
          'success': True,
          'deleted': question_id,
          'questions': current_questions,
          'categories': categories_list,
          'total_questions': len(Question.query.all()),
          'current_category': None
        }) , 200
      else: 
        abort(404)
    except BaseException:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def add_questions():
    try:
      question = request.get_json()['question']
      answer = request.get_json()['answer']
      difficulty = request.get_json()['difficulty']
      category = request.get_json()['category']

      new_question = Question(question,answer,difficulty,category)
      new_question.insert()

      return jsonify({
        'success':True,
        'created_id': new_question.id,
        'total_questions': len(Question.query.all())
      }),200

    except BaseException:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search', methods=['POST'])
  def search_question():

    try:
      body = request.get_json()
      search =body.get('searchTerm',None)
      selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
      current_questions = paginate_questions(request,selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(current_questions),
        'current_category': None

      }),200 
    except BaseException:
      abort(422)
      
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_categories(category_id):
        
    categories_list = {}
    categories = Category.query.all()

    for c in categories:
      categories_list[c.id] = c.id

    if category_id not in categories_list:
      abort(404)      
    try:
      # category = category.type 
      # print (category_type)
      selection  = Question.query.order_by(Question.id).filter(Question.category == str(category_id)).all()
      current_questions = paginate_questions(request,selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        'current_category': category_id
      }),200
    except BaseException:
      
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
      
    data = request.get_json()
    previous_questions = data.get('previous_questions')
    quiz_category = data.get('quiz_category')

    if ((quiz_category is None) or (previous_questions is None)):
      abort(400)
      
    if ( quiz_category['id'] == 0):
      questions_query = Question.query.filter(Question.id.notin_(previous_questions)).all()
    else:
      questions_query = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_(previous_questions)).all()

    length_of_questions = len(questions_query)
    if length_of_questions > 0 :
      result = {
        "success": True,
        "question": Question.format(questions_query[random.randint(0, length_of_questions-1 ) ] )
      }
    else:
      result = {
        "success": True,
        "question": None
      }  
    return jsonify(result)  
        
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "Bad Request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422
  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "internal server error"
      }), 500


  return app

    