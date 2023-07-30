from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

delete_tag_blueprint = Blueprint('delete_tag_blueprint', __name__)

@delete_tag_blueprint.route('/api/delete-tag', methods=['POST'])
def delete_tag():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    get_existing_tagging_query_id = 'SELECT search_schema.get_existing_tagging_query_id(:user_id,:tagging_query)'

    existing_tagging_query_id = db.session.execute(text(get_existing_tagging_query_id), {'user_id': user_id[0][0], 'tagging_query': payload['searchInput']}).fetchall()

    delete_tagging_result_sp = 'CALL search_schema.delete_tagging_result(:tagging_query_id)'

    db.session.execute(text(delete_tagging_result_sp), {'tagging_query_id': existing_tagging_query_id[0][0]})

    db.session.commit()

    delete_tagging_query_sp = 'CALL search_schema.delete_tagging_query(:user_id,:tagging_query)'

    db.session.execute(text(delete_tagging_query_sp), {'user_id': user_id[0][0], 'tagging_query': payload['searchInput']})

    db.session.commit()

    operation_response = {
        "operation_success": True,
        "responsePayload": {
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
