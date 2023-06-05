from flask import Flask, jsonify, request
from gds import getGrades

app = Flask(__name__)

@app.route('/')
def index():
    # Return a 200 code to show all systems are operational
    return 'Server is online'

@app.route('/gradebook')
async def gradebook():
    username = request.args.get('username')
    password = request.args.get('password')
    response = await getGrades(username, password)
    return response

if __name__ == '__main__':
    app.run()





# app = Flask(__name__)

# @app.route('/')
# def index():
#     return 'Hello, world!'

# @app.route('/grade')
# def getGrade():
#     username = request.args.get('username')
#     password = request.args.get('password')
#     grades = getGrades(username, password)
#     return grades

# if __name__ == '__main__':
#     app.run()