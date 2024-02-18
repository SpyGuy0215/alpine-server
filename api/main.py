from flask import Flask, request
from api.gds import getGrades
from api.proxy import refresh_proxies, get_random_proxies

app = Flask(__name__)


@app.route("/")
def index():
    # Return a 200 code to show all systems are operational
    return "Server is online"


@app.route("/gradebook")
async def gradebook():
    username = request.args.get("username")
    password = request.args.get("password")
    response = await getGrades(username, password)
    return response


@app.route("/refresh-proxy")
async def proxyTest():
    status = await refresh_proxies()
    return status

@app.route("/get-proxies")
async def getProxies():
    proxies = await get_random_proxies()
    return proxies


if __name__ == "__main__":
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
