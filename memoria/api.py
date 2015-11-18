# coding=utf-8
import json
import hashlib

import content
from bottle import Bottle, response, request

api = Bottle(autojson=False)


def json_response(callback):
    def wrapper(*args, **kwargs):
        response.headers['Content-Type'] = 'application/json; charset=utf-8'

        try:
            result = callback(*args, **kwargs)
        except Exception, e:
            response.status = 500
            result = {
                'error': str(e)
            }

        return json.dumps(result, encoding='utf-8', ensure_ascii=False, indent=True)

    return wrapper


def cached_response(callback):
    def wrapper(*args, **kwargs):
        result = callback(*args, **kwargs)

        etag = '"%s"' % hashlib.md5(result.encode('utf-8')).hexdigest()
        response.set_header('ETag', etag)

        if request.get_header('If-None-Match') == etag:
            response.status = 304
            result = ''

        return result

    return wrapper


DEBUG = True


@api.get('/exercises', apply=[cached_response, json_response])
def get_exercises():
    columns = [
        'id',
        'created_time',
        'updated_time',
        'scope',
        'scope_letters',
        'definition',
        'notes',
        'rating',
        'practice_time',
        'disabled',
    ]

    result = []

    cursor = content.open_connection()
    for row in cursor.execute('SELECT %s FROM exercises' % ', '.join(columns)):
        row = list(row)
        row[-1] = row[-1] != 0
        result.append(dict(zip(columns, row)))

    return result


@api.post('/exercises', apply=[json_response])
def add_exercise():
    exercise = request.json

    columns = []
    placeholders = []
    params = []
    for column, value in exercise.items():
        columns.append(column)
        placeholders.append('?')
        params.append(value)

    connection = content.open_connection()
    cursor = connection.cursor()
    cursor.execute(
        ''.join(['INSERT INTO exercises (', ', '.join(columns), ') VALUES (', ', '.join(placeholders), ')']),
        params
    )

    return {
        'id': cursor.lastrowid
    }


@api.route('/exercises/<exercise_id:int>', method='PATCH', apply=[json_response])
def update_exercise(exercise_id):
    exercise = request.json

    setters = []
    params = []
    for column, value in exercise.items():
        setters.append('%s = ?' % column)
        params.append(value)

    params.append(exercise_id)
    params.append(exercise['updated_time'])

    connection = content.open_connection()
    cursor = connection.cursor()
    cursor.execute(
        ''.join(['UPDATE exercises SET ', ', '.join(setters), ' WHERE id = ? AND updated_time < CAST(? AS INTEGER)']),
        params
    )

    return {
        'updated': cursor.rowcount
    }
