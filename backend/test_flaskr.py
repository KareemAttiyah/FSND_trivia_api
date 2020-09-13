import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import unittest
import json

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format('hadeer','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'what is my name ?',
            'answer': 'trivia',
            'category': '5',
            'difficulty': 5}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_404_errorhandler_if_page_does_not_exist(self):
        res = self.client().get('/questions/?page=5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")
    def test_delete_questions(self):

        new_question = Question(question="what is my name ?",
                                answer="trivia",
                                category="5",
                                difficulty=5)

        new_question.insert()
        question_id = new_question.id

        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['deleted'], question_id )
        self.assertEqual(question, None)

    def test_delete_not_exist_question(self):
        res = self.client().delete('/questions/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "unprocessable")

    def test_add_question(self):
        res = self.client().post('/questions',json = self.new_question)
        data = json.loads(res.data)

        added_question = Question.query.filter(Question.question == "what is my name ?")

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['created_id'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(added_question)

    def test_failing_to_add_question(self):
        new_question = {
            'question': 'what is my name ?',
            'answer': 'trivia',
            'category': '1'
            }
        res = self.client().post('/questions',json = new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "unprocessable")

    def test_search_question(self):
        body = {
            "searchTerm": 'What'
        }
        res = self.client().post('/search', json = body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_search_failed(self):
        res = self.client().post('/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "unprocessable")


    def test_get_questions_by_categories(self): 

        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'],1)

    def test_get_questions_by_non_existant_category(self):

        res = self.client().get('/categories/11111/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")

    def test_get_question_for_quiz(self):
        body = {
            'previous_questions': [],
            'quiz_category': {
                    'type': 'Sports',
                    'id': '6'}}
        res = self.client().post('/quizzes',json= body )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_get_question_for_quiz_after_solving_all_questions(self):
        body = {
            'previous_questions': [10,11],
            'quiz_category': {
                    'type': 'Sports',
                    'id': '6'}}
        res = self.client().post('/quizzes',json= body )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)
   
    def test_quiz_bad_request(self):
        body = {
            'previous_questions': []
            }
        res = self.client().post('/quizzes',json= body )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], "Bad Request")

#Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()