# coding=utf-8
import json

import content
from bottle import Bottle, response, request

api = Bottle(autojson=False)


class ApiException:
    def __init__(self, code, message):
        self.code = code
        self.message = message


class ApiPlugin(object):
    def apply(self, callback, route):
        def decorator(*args, **kwargs):
            response.headers['Content-Type'] = 'application/json; charset=utf-8'

            try:
                result = callback(*args, **kwargs)
            except ApiException, e:
                response.status = e.code
                result = {
                    'error': e.message
                }

            return json.dumps(result, encoding='utf-8', ensure_ascii=False, indent=True)

        return decorator


api.install(ApiPlugin())

DEBUG = True


@api.get('/exercises')
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
        'practice_time'
    ]

    result = []

    cursor = content.open_connection()
    for row in cursor.execute('SELECT %s FROM exercises' % ', '.join(columns)):
        result.append(dict(zip(columns, row)))

    return result


@api.post('/exercises')
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


@api.route('/exercises/<exercise_id:int>', method='PATCH')
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
