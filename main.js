var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('content.db');

db.get('PRAGMA user_version', [], function (error, row) {
  switch (row.user_version) {
    case 0:
      db.serialize(function () {
        db.run('CREATE TABLE exercises (id INTEGER PRIMARY KEY, scope TEXT NOT NULL UNIQUE, definition TEXT NOT NULL, notes TEXT, rating INTEGER NOT NULL, updated_time INTEGER NOT NULL, practice_time INTEGER NOT NULL)');
        db.run('PRAGMA user_version = 1');
      });
  }

  console.log('Database initialized from version ' + row.user_version);
});


var express = require('express');
var bodyParser = require('body-parser');
var app = express();

app.use('/api', bodyParser.json());

app.get('/api/v1/exercises', function (request, response) {
  db.all('SELECT * FROM exercises ORDER BY id', function (error, rows) {
    response.json(rows);
  })
});

app.post('/api/v1/exercises', function (request, response) {
  var exercise = request.body;
  console.log(exercise);
  db.run(
    'INSERT INTO exercises (id, scope, definition, notes, rating, updated_time, practice_time) VALUES (?, ?, ?, ?, ?, ?, ?)',
    [exercise.id, exercise.scope, exercise.definition, exercise.notes, exercise.rating, exercise.updated_time, exercise.practice_time],
    function (error) {
      if (error != null) {
        response.status(500).json(error);
      } else {
        response.json({'lastID': this.lastID});
      }
    }
  );
});

app.put('/api/v1/exercises/:id', function (request, response) {
  var exercise = request.body;
  console.log(exercise);
  db.run(
    'UPDATE exercises SET scope = ?, definition = ?, notes = ?, rating = ?, updated_time = ?, practice_time = ? WHERE id = ?',
    [exercise.scope, exercise.definition, exercise.notes, exercise.rating, exercise.updated_time, exercise.practice_time, request.params.id],
    function (error) {
      debugger;
      if (error != null) {
        response.status(500).json(error);
      } else {
        response.json({'changes': this.changes});
      }
    }
  );
});

app.listen(8081);
