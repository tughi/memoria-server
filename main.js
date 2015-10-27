var fs = require('fs');

var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('content.db');

db.get('PRAGMA user_version', [], function (error, row) {
  switch (row.user_version) {
    case 0:
      var exercises = JSON.parse(fs.readFileSync('memoria-exercises.json', 'utf8'));

      db.serialize(function () {
        db.run('CREATE TABLE exercises (id INTEGER PRIMARY KEY, created_time INTEGER NOT NULL, updated_time INTEGER NOT NULL, scope TEXT NOT NULL UNIQUE, definition TEXT NOT NULL, notes TEXT, rating INTEGER NOT NULL, practice_time INTEGER NOT NULL)');
        db.run('PRAGMA user_version = 1');

        var updatedTime = new Date().getTime();
        for (var index in exercises) {
          var exercise = exercises[index];
          console.log(exercise);
          db.run(
            'INSERT INTO exercises (scope, definition, notes, rating, practice_time, created_time, updated_time) VALUES (?, ?, ?, ?, ?, ?, ?)',
            [exercise.scope, exercise.definition, exercise.notes, exercise.rating, exercise.practiceTime * 1000, exercise.id, updatedTime]
          )
        }
      });
  }

  console.log('Database initialized from version ' + row.user_version);
});


var express = require('express');
var bodyParser = require('body-parser');
var app = express();

app.use('/api', bodyParser.json());

app.get('/api/v1/:table', function (request, response) {
  console.log('GET ' + request.path);
  db.all(['SELECT * FROM ', request.params['table'], ' ORDER BY id'].join(''), function (error, rows) {
    response.json(rows);
  })
});

app.post('/api/v1/:table', function (request, response) {
  console.log('POST ' + request.path);
  var row = request.body;

  var columns = [];
  var placeholders = [];
  var params = [];
  for (var column in row) {
    columns.push(column);
    placeholders.push('?');
    params.push(row[column]);
  }

  db.run(
    ['INSERT INTO ', request.params['table'], ' (', columns.join(', '), ') VALUES (', placeholders.join(', '), ')'].join(''),
    params,
    function (error) {
      if (error != null) {
        response.status(500).json(error);
      } else {
        response.json({'lastID': this.lastID});
      }
    }
  );
});

app.patch('/api/v1/:table/:id', function (request, response) {
  console.log('PATCH ' + request.path);
  var exercise = request.body;

  var setters = [];
  var params = [];
  for (var column in exercise) {
    setters.push(column + ' = ?');
    params.push(exercise[column]);
  }

  params.push(request.params['id']);

  var statement = ['UPDATE ', request.params['table'], ' SET ', setters.join(', '), ' WHERE id = ?'].join('');
  console.log(statement);
  console.log(params);
  db.run(
    statement,
    params,
    function (error) {
      debugger;
      if (error != null) {
        console.log(error);
        response.status(500).json(error);
      } else {
        response.json({'changes': this.changes});
      }
    }
  );
});

app.listen(8081);
