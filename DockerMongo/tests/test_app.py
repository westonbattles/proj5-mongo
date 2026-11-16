"""Submit/Display tests using Flask's test client and a temporary MongoDB database."""

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4

from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as brevet_app


class BrevetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        client = MongoClient(
            os.environ['DB_PORT_27017_TCP_ADDR'], 27017,
            serverSelectionTimeoutMS=10000,
        )
        cls.addClassCleanup(client.close)
        client.admin.command('ping')
        # A unique test database keeps the application's tododb untouched.
        cls.db = client[f'brevet_tests_{uuid4().hex}']
        cls.addClassCleanup(client.drop_database, cls.db.name)
        db_patch = patch.object(brevet_app, 'db', cls.db)
        db_patch.start()
        cls.addClassCleanup(db_patch.stop)

    def setUp(self):
        self.db.tododb.delete_many({})
        self.client = brevet_app.app.test_client()
        self.form = {
            'distance': '200',
            'begin_date': '2017-01-01',
            'begin_time': '08:00',
            'miles': ['31.1', '62.1', ''],
            'km': ['50', '100', ''],
            'location': ['Cafe', '', ''],
        }

    def test_submit_saves_controls(self):
        response = self.client.post('/new', data=self.form)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.db.tododb.count_documents({}), 1)
        saved = self.db.tododb.find_one()
        self.assertEqual(saved['brevet_distance_km'], 200)
        self.assertEqual(saved['begin_date'], '2017-01-01')
        self.assertEqual(saved['begin_time'], '08:00')
        self.assertEqual(len(saved['controls']), 2)
        first, second = saved['controls']
        self.assertEqual(first['km'], 50)
        self.assertEqual(first['location'], 'Cafe')
        self.assertEqual(first['open'], '2017-01-01T09:28:00+00:00')
        self.assertEqual(first['close'], '2017-01-01T11:30:00+00:00')
        self.assertEqual(second['km'], 100)
        self.assertEqual(second['location'], '')
        self.assertEqual(second['open'], '2017-01-01T10:56:00+00:00')
        self.assertEqual(second['close'], '2017-01-01T14:40:00+00:00')

    def test_empty_submit_saves_nothing(self):
        for field in ('miles', 'km', 'location'):
            self.form[field] = ['', '', '']

        response = self.client.post('/new', data=self.form)

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Enter at least one control', response.data)
        self.assertEqual(self.db.tododb.count_documents({}), 0)

    def test_display_shows_saved_brevet(self):
        self.db.tododb.insert_one({
            'brevet_distance_km': 200,
            'begin_date': '2017-01-01',
            'begin_time': '08:00',
            'controls': [{
                'km': 50, 'location': 'Cafe',
                'open': '2017-01-01T09:28:00+00:00',
                'close': '2017-01-01T11:30:00+00:00',
            }],
        })

        response = self.client.get('/display')

        self.assertEqual(response.status_code, 200)
        for text in ('200 km', '2017-01-01', '08:00', 'Cafe',
                     'Sun 1/1 9:28', 'Sun 1/1 11:30'):
            self.assertIn(text, response.get_data(as_text=True))

    def test_empty_display(self):
        response = self.client.get('/display')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No saved brevets yet.', response.data)


if __name__ == '__main__':
    unittest.main()
