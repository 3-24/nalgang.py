from flask import Flask, request
from attendance import Member
app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Welcome to youngseok's server."


@app.route('/nalgang', methods=['GET'])
def nalgang_point():
    userID = request.args.get('id', type=int)
    userGuild = request.args.get('guild', type=int)
    m = Member(None)
    m.id = userID
    m.guild = userGuild
    return str(m.get_point())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='50000')
