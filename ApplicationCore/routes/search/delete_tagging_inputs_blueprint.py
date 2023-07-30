
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from Utils.json_encoder import GenericJsonEncoder

delete_tagging_inputs_blueprint = Blueprint('delete_tagging_inputs_blueprint', __name__)

@delete_tagging_inputs_blueprint.route('/api/delete-tagging-inputs', methods=['POST'])
def delete_tagging_inputs():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    delete_tagging_input_sp = 'CALL search_schema.delete_tagging_input(:user_id)'

    db.session.execute(text(delete_tagging_input_sp), {'user_id': user_id[0][0]})

    db.session.commit()

    operation_response = {
        "operation_success": True,
        "responsePayload": {
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
