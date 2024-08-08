from flask import Blueprint, jsonify, request
import requests


auth_blueprint = Blueprint('auth_blueprint', __name__)

@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    token = request.json['token']

    url = 'https://api.datawrapper.de/v3/charts'
    headers = {
        'accept': '*/*',
        'Authorization': 'Bearer {}'.format(token)
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        return jsonify({'message': 'Invalid authentication credentials'}), 401
    elif response.status_code == 200:
        res = jsonify({'message': 'Login successful'})
        return res