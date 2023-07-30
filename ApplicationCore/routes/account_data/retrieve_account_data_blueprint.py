
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

retrieve_account_data_blueprint = Blueprint('retrieve_account_data_blueprint', __name__)

@retrieve_account_data_blueprint.route('/api/retrieve_account_data', methods=['POST'])
def retrieve_account_data():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    get_user_account_data = 'SELECT user_schema.get_user_account_data(:user_id)'

    user_account_data = db.session.execute(text(get_user_account_data), {'user_id': user_id[0][0]}).fetchall()

    user_account_data_string = user_account_data[0][0]
    user_account_data_string = user_account_data_string[1:]
    user_account_data_string = user_account_data_string[:-1]
    user_account_data = user_account_data_string.split(",")

    # ('(118,potato@salad.com,Pass123@&,Potato,Salad,2000-01-01,potato@salad.com,"(202) 555-0162",1)',)
    operation_response = {
        "operation_success": True,
        "responsePayload": {
            "firstName": user_account_data[3],
            "lastName": user_account_data[4],
            "emailAddress": user_account_data[1],
            "dateBirth": user_account_data[5],
            "telephoneNumber": user_account_data[7],
            "telephoneAreaCode": user_account_data[8],
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
    