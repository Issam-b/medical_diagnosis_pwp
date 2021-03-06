"""
Created on 26.01.2013
Modified on 11.04.2017
@author: yazan barhoush
"""
import unittest
import json

import flask
import medical_forum.resources as resources
import medical_forum.database_engine as database

# Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/medical_forum_data_test.db'
DEFAULT_SCHEMA = "db/medical_forum_data_schema.sql"
DEFAULT_DATA_DUMP = "db/medical_forum_data_dump.sql"

ENGINE = database.Engine(DEFAULT_DB_PATH)

MASONJSON = "application/vnd.mason+json"
JSON = "application/json"
HAL = "application/hal+json"

FORUM_DIAGNOSIS_PROFILE = "/profiles/diagnosis-profile/"
ATOM_THREAD_PROFILE = "https://tools.ietf.org/html/rfc4685"

# Tell Flask that I am running it in testing mode.
resources.APP.config["TESTING"] = True
# Necessary for correct translation in url_for
resources.APP.config["SERVER_NAME"] = "localhost:5000"

# Database Engine utilized in our testing
resources.APP.config.update({"Engine": ENGINE})

# Other database parameters.
INITIAL_DIAGNOSES = 10


# Copied Class ResourcesAPITestCase from Ex. 4
class ResourcesAPITestCase(unittest.TestCase):
    """API Resources test setup and teardown funcitons"""

    # INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        """ Creates the database structure. Removes first any preexisting
            database file
        """
        print("Testing ", cls.__name__)
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        """Remove the testing database"""
        print("Testing ENDED for ", cls.__name__)
        ENGINE.remove_database()

    def setUp(self):
        """
        Populates the database
        """
        # This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        # Activate app_context for using url_for
        self.app_context = resources.APP.app_context()
        self.app_context.push()
        # Create a test client
        self.client = resources.APP.test_client()

    def tearDown(self):
        """
        Remove all records from database
        """
        ENGINE.clear()
        self.app_context.pop()


class DiagnosesTestCase(ResourcesAPITestCase):
    """Diagnoses resources API tests"""

    url = "/medical_forum/api/diagnoses/"

    diagnosis_by_doctor = {
        "disease": "Soreness in the throat",
        "diagnosis_description": ("Hi, I have this soreness in my throat. "
                                  "It started just yesterday and its getting worse by"),
        "user_id": "4",
        "message_id": "1"
    }

    diagnosis_by_nonexisting_user = {
        "disease": "Soreness in the throat",
        "diagnosis_description": ("Hi, I have this soreness in my throat. "
                                  "It started just yesterday and its getting worse by"),
        "user_id": "154",
        "message_id": "1"
    }

    diagnosis_by_patient = {
        "disease": "Soreness in the throat",
        "diagnosis_description": ("Hi, I have this soreness in my throat. "
                                  "It started just yesterday and its getting worse by"),
        "user_id": "1",
        "message_id": "1"
    }

    diagnosis_missing_disease = {
        "diagnosis_description": ("Hi, I have this soreness in my throat. "
                                  "It started just yesterday and its getting worse by"),
        "user_id": "4",
        "message_id": "1"
    }

    diagnosis_missing_diagnosis = {
        "disease": "Soreness in the throat",
        "user_id": "4",
        "message_id": "1"
    }

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")",
              self.test_url.__doc__, end=' ')
        with resources.APP.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.APP.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Diagnoses)

    # TODO def test_get_diagnoses(self) -- not implemented in database_connection.py, --extra
    # TODO def test_get_diagnoses_mimetype(self) -- not implemented in database_connection.py, --extra

    def test_add_diagnosis(self):
        """
        Test adding diagnoses to the database.
        """
        print("(" + self.test_add_diagnosis.__name__ + ")",
              self.test_add_diagnosis.__doc__)

        resp = self.client.post(resources.API.url_for(resources.Diagnoses),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.diagnosis_by_doctor))
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get("Location")
        self.assertIsNotNone(url)
        resp = self.client.get(url)
        self.assertTrue(resp.status_code == 200)

    def test_add_diagnosis_nondoctor(self):
        """
        Test adding diagnoses to the database by a non doctor
        """
        print("(" + self.test_add_diagnosis_nondoctor.__name__ + ")",
              self.test_add_diagnosis_nondoctor.__doc__)

        resp = self.client.post(resources.API.url_for(resources.Diagnoses),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.diagnosis_by_patient))
        self.assertTrue(resp.status_code == 400)

    def test_add_diagnosis_nonexisting_user(self):
        """Test adding a message with non existing user"""
        print("(" + self.test_add_diagnosis_nonexisting_user.__name__ + ")",
              self.test_add_diagnosis_nonexisting_user.__doc__)

        resp = self.client.post(resources.API.url_for(resources.Messages),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.diagnosis_by_nonexisting_user))
        self.assertTrue(resp.status_code == 400)

    def test_add_diagnosis_wrong_media(self):
        """
        Test adding diagnoses with a media different than json
        """
        print("(" + self.test_add_diagnosis_wrong_media.__name__ + ")",
              self.test_add_diagnosis_wrong_media.__doc__)
        resp = self.client.post(resources.API.url_for(resources.Diagnoses),
                                headers={"Content-Type": "text"},
                                data=self.diagnosis_missing_disease.__str__())
        self.assertTrue(resp.status_code == 415)

    def test_add_diagnosis_bad_format(self):
        """
        Test that add diagnosis response correctly when sending erroneous diagnosis
        format.
        """
        print("(" + self.test_add_diagnosis_bad_format.__name__ + ")",
              self.test_add_diagnosis_bad_format.__doc__)
        resp = self.client.post(resources.API.url_for(resources.Diagnoses),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.diagnosis_missing_diagnosis))
        self.assertTrue(resp.status_code == 400)


class DiagnosisTestCase(ResourcesAPITestCase):
    """Diagnosis resources API tests"""
    diagnosis_req_1 = {
        "disease": "Soreness in the throat",
        "diagnosis": "Hi, I have this soreness in my throat. It started just "
        "yesterday and its getting worse by",
        "user_id": "1",
        "message_id": "1"
    }

    diagnosis_wrong_req_1 = {
        "disease": "Dizziness when running"
    }

    diagnosis_wrong_req_2 = {
        "diagnosis": "Tony bought new car. John is shopping. Anne bought new car. ",
    }

    # Modified from def setUp(self):
    def setUp(self):
        super(DiagnosisTestCase, self).setUp()
        self.url = resources.API.url_for(resources.Diagnosis,
                                         diagnosis_id="dgs-1",
                                         _external=False)
        self.url_wrong = resources.API.url_for(resources.Diagnosis,
                                               diagnosis_id="dgs-290",
                                               _external=False)

    # Modified from def setUp(self):
    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        _url = "/medical_forum/api/diagnoses/dgs-1/"
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        with resources.APP.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.APP.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Diagnosis)

    def test_wrong_url(self):
        """
        Checks that GET Diagnosis return correct status code if given a
        wrong diagnosis
        """
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)

    def test_get_diagnosis(self):
        """
        Checks that GET Message return correct status code and data format
        """
        print("(" + self.test_get_diagnosis.__name__ + ")",
              self.test_get_diagnosis.__doc__)
        with resources.APP.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            controls = data["@controls"]
            self.assertIn("self", controls)
            self.assertIn("profile", controls)
            self.assertIn("user_id", controls)
            self.assertIn("collection", controls)

            # ToDo reply control?
            # reply_ctrl = controls["medical_forum:reply"]
            # self.assertIn("title", reply_ctrl)
            # self.assertIn("href", reply_ctrl)
            # # self.assertEqual(reply_ctrl["href"], self.url)
            # self.assertIn("encoding", reply_ctrl)
            # self.assertEqual(reply_ctrl["encoding"], "json")
            # self.assertIn("method", reply_ctrl)
            # self.assertEqual(reply_ctrl["method"], "POST")
            # self.assertIn("schema", reply_ctrl)

            self.assertIn("href", controls["self"])
            self.assertEqual(controls["self"]["href"], self.url)

            self.assertIn("href", controls["profile"])
            self.assertEqual(controls["profile"]
                             ["href"], FORUM_DIAGNOSIS_PROFILE)
            # ToDo self.assertEqual(controls["user_id"])
            # self.assertIn("href", controls["user_id"])
            # self.assertEqual(controls["user_id"]["href"], resources.api.url_for(
            #     resources.User, user_id=4, _external=False
            # ))

            self.assertIn("href", controls["collection"])
            self.assertEqual(controls["collection"]["href"], resources.API.url_for(
                resources.Diagnoses, _external=False
            ))

            # self.assertIn("href", controls["atom-thread:in-reply-to"])
            # self.assertEqual(controls["atom-thread:in-reply-to"]["href"], None)

            # Check rest attributes
            self.assertIn("disease", data)
            self.assertIn("user_id", data)
            self.assertIn("diagnosis_description", data)
            self.assertIn("message_id", data)
            # self.assertIn("editor", data)

    def test_get_diagnosis_mimetype(self):
        """
        Checks that GET Diagnoses return correct status code and data format
        """
        print("(" + self.test_get_diagnosis_mimetype.__name__ + ")",
              self.test_get_diagnosis_mimetype.__doc__)

        # Check that I receive status code 200
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type", None),
                         "{};{}".format(MASONJSON, FORUM_DIAGNOSIS_PROFILE))


if __name__ == "__main__":
    print("Start running tests")
    unittest.main()
