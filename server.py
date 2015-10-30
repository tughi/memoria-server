from bottle import Bottle, run
from memoria.api import api
import os


# uWSGI support
os.chdir(os.path.dirname(__file__))

server = Bottle()
server.mount('/api/v1/', api)

# uWSGI support
application = server

if __name__ == '__main__':
    run(application, host='0.0.0.0', port=8000)
