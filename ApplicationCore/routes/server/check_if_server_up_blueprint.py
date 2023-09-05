
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from Utils.json_encoder import GenericJsonEncoder

check_if_server_up_blueprint = Blueprint('check_if_server_up_blueprint', __name__)

@check_if_server_up_blueprint.route('/api/check-if-server-up', methods=['POST'])
def check_if_server_up():
    operation_response = {
        "operation_success": True,
        "responsePayload": {
        },
    }
    response = make_response(json.dumps(operation_response))

    return response
