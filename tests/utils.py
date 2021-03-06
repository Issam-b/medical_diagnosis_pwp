"""
Helper functions for the test classes

Author: Issam
"""

import sqlite3
import pytest
from medical_forum import database_engine

# Define constants
FOREIGN_KEYS_ON = 'PRAGMA foreign_keys = ON'

# Tables content initial sizes
INITIAL_MESSAGES_COUNT = 19
INITIAL_USERS_COUNT = 25
INITIAL_USERS_PROFILE_COUNT = 25
INITIAL_DIAGNOSIS_COUNT = 10

# Tables names
USERS_TABLE = 'users'
USERS_PROFILE_TABLE = 'users_profile'
MESSAGES_TABLE = 'messages'
DIAGNOSIS_TABLE = 'diagnosis'


# Database file path to be used for testing only and create database instance
DB_PATH = 'db/medical_forum_data_test.db'
ENGINE = database_engine.Engine(DB_PATH)


@pytest.fixture
def execute_query(self, query, fetch_type):
    """
    This is a helper method to facilitate and be used by many methods.
    This method is used to handle the execution of queries and return the result of that query.
    :param self: to pass the context of the parent method.
    :param query: the query to execute.
    :param fetch_type: whether to return one or all results from the cursor instance
            after query execution.
    :return: Either one or all tuple of results.
    """
    # connection instance
    con = self.connection.con
    with con:
        # Cursor and row initialization
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # Provide support for foreign keys
        cur.execute(FOREIGN_KEYS_ON)
        # Execute main SQL Statement
        cur.execute(query)
        if fetch_type == 'one':
            return cur.fetchone()
        return cur.fetchall()


@pytest.fixture
def test_table_populated(self, table_name, element_count):
    """
    Check that the messages table has been populated with default data successfully.
    Calling sqlite directly (as stated in Exercise 1 docs)
    Exercise 1 has been used as a reference

    @:param: table_name: the name of the table to check.
    @:param: element_count: the count of elements (default) in the table.
     """
    # query to get list of messages table elements
    query = 'SELECT * FROM {}'.format(table_name)
    # Assert if count of messages doesn't equal the known initial value
    self.assertEqual(len(execute_query(self, query, 'all')), element_count)


@pytest.fixture
def test_table_schema(self, table_name, columns_names, columns_types, table_fk, fk_on):
    """
    General method to checks that the provided table has the right schema.
    Calling sqlite directly (as stated in Exercise 1 docs)
    Exercise 1 is used as reference and
    https://docs.python.org/3/library/unittest.html#re-using-old-test-code

    @:param table_name: the name of the table to check
    @:param columns_names: a tuple with the real/default column names
    @:param columns_types: a tuple with the real/default column types
    @:param table_fk: a tuple with the table's foreign keys
    @:param fk_on: whether the table has any foreign keys or not (True/False)
    """
    # connection instance
    con = self.connection.con
    with con:
        cursor = con.cursor()
        # collect column information in the query result
        # Every column will be represented by a tuple with the following attributes:
        # (id, name, type, not null, default_value, primary_key)
        cursor.execute('PRAGMA TABLE_INFO({})'.format(table_name))
        ti_result = cursor.fetchall()
        names = [tup[1] for tup in ti_result]
        types = [tup[2] for tup in ti_result]

        # Check and assert the names and their types with default ones
        self.assertEqual(names, columns_names)
        self.assertEqual(types, columns_types)

        if fk_on:
            # get the foreign key data using the the query below
            # the returned tuple has the following attributes
            # (id, seq, table, from, to, on_update, on_delete, match)
            # so we take elements (2, 3, 4) -> (table, from, to)
            # reference:
            # https://stackoverflow.com/questions/44424476/output-of-the-sqlites-foreign-key-list-pragma
            cursor.execute('PRAGMA FOREIGN_KEY_LIST({})'.format(table_name))
            fk_result = cursor.fetchall()
            # Check and assert that foreign keys are correctly set
            result_filtered = [(tup[2], tup[3], tup[4]) for tup in fk_result]
            for tup in result_filtered:
                # Test that each tup is included in the list of all default foreign keys
                self.assertIn(tup, table_fk)
