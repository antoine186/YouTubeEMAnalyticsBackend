from flask import Blueprint, request, make_response
import json
from datetime import date
from operator import attrgetter
from app_start_helper import nn, model_max_characters_allowed, keyword_extractor_nn
from analysis.tweet_classifier import TweetClassifier
from Utils.json_encoder2 import GenericJsonEncoder2
from app_start_helper import db
from sqlalchemy import text
from flask_mail import Mail, Message
from threading import Thread
from app_start_helper import mail
from Utils.average_merger import average_merger

tweet_emo_mine_blueprint = Blueprint('tweet_emo_mine_blueprint', __name__)

@tweet_emo_mine_blueprint.route('/api/tweet_emo_mine', methods=['POST'])
def tweet_emo_mine():
    try:
        payload = request.data
        payload = json.loads(payload)

        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

        get_previous_twitter_result = 'SELECT search_schema.get_previous_twitter_result(:user_id)'

        previous_twitter_result = db.session.execute(text(get_previous_twitter_result), {'user_id': user_id[0][0]}).fetchall()

        get_previous_twitter_sample_size = 'SELECT search_schema.get_previous_twitter_sample_size(:user_id)'

        previous_sample_size = db.session.execute(text(get_previous_twitter_sample_size), {'user_id': user_id[0][0]}).fetchall()

        attributes = ('year', 'month', 'day')

        today = date.today()
        today = attrgetter(*attributes)(today)

        results = payload['rawTweets']

        tweet_classifier = TweetClassifier(nn, results, model_max_characters_allowed, keyword_extractor_nn, \
                                        today, payload['tweeter'], payload['urlLink'])
        
        emo_breakdown_result_metadata = tweet_classifier.get_emo_percentage_breakdown_with_leading_results()

        if previous_twitter_result[0][0] != None:
            # If there is a previous result to update
            previous_twitter_result = json.loads(previous_twitter_result[0][0])

            emo_breakdown_result_metadata = average_merger(emo_breakdown_result_metadata, previous_twitter_result, len(results), previous_sample_size[0][0])

            emo_breakdown_result_metadata_json_data = json.dumps(emo_breakdown_result_metadata, indent=4, cls=GenericJsonEncoder2)

            update_twitter_result_sp = 'CALL search_schema.update_twitter_result(:user_id,:previous_twitter_result,:sample_size)'

            db.session.execute(text(update_twitter_result_sp), {'user_id': user_id[0][0], 'previous_twitter_result': emo_breakdown_result_metadata_json_data,
                                                                'sample_size': previous_sample_size[0][0] + len(results)})

            db.session.commit()

            operation_response = {
                "operation_success": True,
                "responsePayload": {
                    "emo_breakdown_result_metadata_json_data": emo_breakdown_result_metadata_json_data
                },
                "error_message": ""
            }
            response = make_response(json.dumps(operation_response))
            return response
        else:
            # If this is the first result
            if emo_breakdown_result_metadata != None:
                emo_breakdown_result_metadata_json_data = json.dumps(emo_breakdown_result_metadata, indent=4, cls=GenericJsonEncoder2)
                #emo_breakdown_result_metadata_json_data = json.dumps(emo_breakdown_result_metadata)

                delete_twitter_result_sp = 'CALL search_schema.delete_twitter_result(:user_id)'

                db.session.execute(text(delete_twitter_result_sp), {'user_id': user_id[0][0]})

                db.session.commit()

                add_twitter_result_sp = 'CALL search_schema.add_twitter_result(:user_id,:previous_twitter_result,:sample_size)'

                db.session.execute(text(add_twitter_result_sp), {'user_id': user_id[0][0], 'previous_twitter_result': emo_breakdown_result_metadata_json_data, 'sample_size': len(results)})

                db.session.commit()

                operation_response = {
                    "operation_success": True,
                    "responsePayload": {
                        "emo_breakdown_result_metadata_json_data": emo_breakdown_result_metadata_json_data
                    },
                    "error_message": ""
                }
                response = make_response(json.dumps(operation_response))
                return response

            else:
                operation_response = {
                    "operation_success": False,
                    "responsePayload": {
                    },
                    "error_message": ""
                }
                response = make_response(json.dumps(operation_response))
                return response
    
    except Exception as e:
        msg = Message()
        msg.subject = 'Main emo search error'
        msg.recipients = ['antoine186@hotmail.com']
        msg.sender = 'noreply@emomachines.xyz'
        msg.body = str(e)

        Thread(target=mail.send(msg)).start()

        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
