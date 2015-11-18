# coding=utf-8
import json
import sqlite3

from os import path

DATABASE = path.sep.join(('databases', 'content.db'))
VERSION = 1


class transaction(object):
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.connection.execute('BEGIN')
        return self.connection.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            self.connection.execute('COMMIT')
        else:
            self.connection.execute('ROLLBACK')


def open_connection():
    connection = sqlite3.connect(DATABASE, isolation_level=None)

    current_version = connection.execute('PRAGMA user_version').fetchone()[0]

    if current_version < VERSION:
        with transaction(connection) as cursor:
            if current_version == 0:
                __create_database(cursor)

            cursor.execute('PRAGMA user_version = %d' % VERSION)

    return connection


def __create_database(cursor):
    cursor.execute('''
        CREATE TABLE exercises (
            id INTEGER PRIMARY KEY,
            created_time INTEGER NOT NULL,
            updated_time INTEGER NOT NULL,
            scope TEXT NOT NULL,
            scope_letters TEXT NOT NULL UNIQUE,
            definition TEXT NOT NULL,
            notes TEXT,
            rating INTEGER NOT NULL,
            practice_time INTEGER NOT NULL,
            disabled INTEGER NOT NULL DEFAULT 0
        )
    ''')

    try:
        with open('exercises.json', 'r') as f:
            exercises = json.loads(f.read())

            for exercise in exercises:
                cursor.execute('''
                    INSERT INTO exercises
                        (created_time, updated_time, scope, scope_letters, definition, notes, rating, practice_time)
                        VALUES
                        (?, ?, ?, ?, ?, ?, ?, ?)
                ''', [
                    exercise['createdTime'],
                    exercise['updatedTime'],
                    exercise['scope'],
                    exercise['scopeLetters'],
                    exercise['definition'],
                    exercise['notes'],
                    exercise['rating'],
                    exercise['practiceTime'],
                ])
    except IOError:
        pass
