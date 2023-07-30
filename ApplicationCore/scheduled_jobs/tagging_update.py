from app_start_helper import scheduler
from app_start_helper import db
from sqlalchemy import text
from app_start_helper import app
import json
from models.tagging_input import TaggingInput
from datetime import datetime, timedelta, date
from operator import attrgetter
from gnews import GNews
from analysis.news_classifier import NewsClassifier
from app_start_helper import nn, model_max_characters_allowed, keyword_extractor_nn
from Utils.json_encoder import GenericJsonEncoder
from flask_mail import Mail, Message
from threading import Thread
from app_start_helper import mail
from Utils.emo_icons import emo_icons

# This for prod
number_of_seconds = 3600 * 24

# This for testing
# number_of_seconds = 60 * 5

def tagging_update():
    scheduler.add_job(func=tagging_periodic_update, trigger="interval", seconds=number_of_seconds)

def tagging_periodic_update():
    with app.app_context():
        try:
            all_tagging_input = TaggingInput.query.all()

            username = ''

            for i in range(len(all_tagging_input)):
                try:
                    user_id = all_tagging_input[i].user_id

                    get_username = 'SELECT user_schema.get_username(:user_id)'

                    username = db.session.execute(text(get_username), {'user_id': user_id}).fetchall()

                    search_inputs = json.loads(all_tagging_input[i].tagging_input_list)

                    attributes = ('year', 'month', 'day')

                    today = date.today()
                    yesterday = today - timedelta(days = 1)

                    search_end_date = today
                    search_start_date = yesterday

                    search_inputs[0]['searchDate'] = str(search_end_date)
                    search_inputs[0]['dayBeforeSearchDate'] = str(search_start_date)

                    tagging_input_list_json = json.dumps(search_inputs, indent=4, cls=GenericJsonEncoder)

                    update_tagging_input_sp = 'CALL search_schema.update_tagging_input(:user_id,:tagging_input_list)'

                    db.session.execute(text(update_tagging_input_sp), {'user_id': user_id, 'tagging_input_list': tagging_input_list_json})

                    db.session.commit()

                    # search_end_date = datetime.strptime(search_inputs[0]['searchDate'], '%Y-%m-%d')
                    # search_start_date = datetime.strptime(search_inputs[0]['dayBeforeSearchDate'], '%Y-%m-%d')
                    comparison_start_date = search_start_date - timedelta(days=1)

                    search_end_date = attrgetter(*attributes)(search_end_date)
                    search_start_date = attrgetter(*attributes)(search_start_date)
                    comparison_start_date = attrgetter(*attributes)(comparison_start_date)

                    google_news = GNews(language='en', country='US', start_date = search_start_date, end_date = search_end_date, max_results = 20)
                    comparison_google_news = GNews(language='en', country='US', start_date = comparison_start_date, end_date = search_start_date, max_results = 20)
                    results = google_news.get_news(search_inputs[0]['searchInput'])
                    comparison_results = comparison_google_news.get_news(search_inputs[0]['searchInput'])

                    news_classifier = NewsClassifier(nn, results, google_news, model_max_characters_allowed, keyword_extractor_nn, search_inputs[0]['searchInput'], \
                                                    search_start_date, search_end_date)
                    comparison_news_classifier = NewsClassifier(nn, comparison_results, google_news, model_max_characters_allowed, keyword_extractor_nn, search_inputs[0]['searchInput'], \
                                                    comparison_start_date, search_start_date)
                    emo_breakdown_result_metadata = news_classifier.get_emo_percentage_breakdown_with_leading_results()
                    comparison_emo_breakdown_result_metadata = comparison_news_classifier.get_emo_percentage_breakdown_with_leading_results()
                    emo_breakdown_result_metadata.previous_average_emo_breakdown = comparison_emo_breakdown_result_metadata.average_emo_breakdown

                    get_existing_tagging_query_id = 'SELECT search_schema.get_existing_tagging_query_id(:user_id,:tagging_query)'

                    existing_tagging_query_id = db.session.execute(text(get_existing_tagging_query_id), {'user_id': user_id, 'tagging_query': search_inputs[0]['searchInput']}).fetchall()

                    emo_breakdown_result_metadata_json_data = json.dumps(emo_breakdown_result_metadata, indent=4, cls=GenericJsonEncoder)

                    update_tagging_result_sp = 'CALL search_schema.update_tagging_result(:tagging_query_id,:tagging_result_json)'

                    db.session.execute(text(update_tagging_result_sp), {'tagging_query_id': existing_tagging_query_id[0][0], 'tagging_result_json': emo_breakdown_result_metadata_json_data})

                    db.session.commit()

                    average_emo_breakdown = emo_breakdown_result_metadata.average_emo_breakdown
                    previous_average_emo_breakdown = emo_breakdown_result_metadata.previous_average_emo_breakdown

                    average_emo_breakdown = [
                        {'percentage': {
                            'emo': 'anger_percentage',
                            'current_emo': emo_breakdown_result_metadata.average_emo_breakdown.anger_percentage,
                            'previous_emo': emo_breakdown_result_metadata.previous_average_emo_breakdown.anger_percentage,
                            'percentage_change': 0
                        }},
                        {'percentage': {
                            'emo': 'disgust_percentage',
                            'current_emo': emo_breakdown_result_metadata.average_emo_breakdown.disgust_percentage,
                            'previous_emo': emo_breakdown_result_metadata.previous_average_emo_breakdown.disgust_percentage,
                            'percentage_change': 0
                        }},
                        {'percentage': {
                            'emo': 'fear_percentage',
                            'current_emo': emo_breakdown_result_metadata.average_emo_breakdown.fear_percentage,
                            'previous_emo': emo_breakdown_result_metadata.previous_average_emo_breakdown.fear_percentage,
                            'percentage_change': 0
                        }},
                        {'percentage': {
                            'emo': 'joy_percentage',
                            'current_emo': emo_breakdown_result_metadata.average_emo_breakdown.joy_percentage,
                            'previous_emo': emo_breakdown_result_metadata.previous_average_emo_breakdown.joy_percentage,
                            'percentage_change': 0
                        }},
                        {'percentage': {
                            'emo': 'neutral_percentage',
                            'current_emo': emo_breakdown_result_metadata.average_emo_breakdown.neutral_percentage,
                            'previous_emo': emo_breakdown_result_metadata.previous_average_emo_breakdown.neutral_percentage,
                            'percentage_change': 0
                        }},
                        {'percentage': {
                            'emo': 'sadness_percentage',
                            'current_emo': emo_breakdown_result_metadata.average_emo_breakdown.sadness_percentage,
                            'previous_emo': emo_breakdown_result_metadata.previous_average_emo_breakdown.sadness_percentage,
                            'percentage_change': 0
                        }},
                        {'percentage': {
                            'emo': 'surprise_percentage',
                            'current_emo': emo_breakdown_result_metadata.average_emo_breakdown.surprise_percentage,
                            'previous_emo': emo_breakdown_result_metadata.previous_average_emo_breakdown.surprise_percentage,
                            'percentage_change': 0
                        }},
                    ]

                    for i in range(len(average_emo_breakdown)):
                        average_emo_breakdown[i]['percentage']['percentage_change'] = round(((average_emo_breakdown[i]['percentage']['current_emo'] - average_emo_breakdown[i]['percentage']['previous_emo']) / average_emo_breakdown[i]['percentage']['previous_emo']) * 100, 2)

                    average_emo_breakdown = sorted(average_emo_breakdown, key=lambda x: (x['percentage']['current_emo']), reverse=True)

                    email_string = 'Emotional engagement for the tag ' + '\"' + search_inputs[0]['searchInput'] + '\"' + ' has changed: '

                    emo_sign1 = ''
                    if average_emo_breakdown[0]['percentage']['percentage_change'] > 0:
                        emo_sign1 = '+'
                    email_string = email_string + emo_icons[average_emo_breakdown[0]['percentage']['emo']] + ' ' + emo_sign1 + str(average_emo_breakdown[0]['percentage']['percentage_change']) + '%' + ' '

                    emo_sign2 = ''
                    if average_emo_breakdown[1]['percentage']['percentage_change'] > 0:
                        emo_sign2 = '+'
                    email_string = email_string + emo_icons[average_emo_breakdown[1]['percentage']['emo']] + ' ' + emo_sign2 + str(average_emo_breakdown[1]['percentage']['percentage_change']) + '%' + ' '

                    emo_sign3 = ''
                    if average_emo_breakdown[2]['percentage']['percentage_change'] > 0:
                        emo_sign3 = '+'
                    email_string = email_string + emo_icons[average_emo_breakdown[2]['percentage']['emo']] + ' ' + emo_sign3 + str(average_emo_breakdown[2]['percentage']['percentage_change']) + '%' + ' '

                    emo_sign4 = ''
                    if average_emo_breakdown[3]['percentage']['percentage_change'] > 0:
                        emo_sign4 = '+'
                    email_string = email_string + emo_icons[average_emo_breakdown[3]['percentage']['emo']] + ' ' + emo_sign4 + str(average_emo_breakdown[3]['percentage']['percentage_change']) + '%' + ' '

                    emo_sign5 = ''
                    if average_emo_breakdown[4]['percentage']['percentage_change'] > 0:
                        emo_sign5 = '+'
                    email_string = email_string + emo_icons[average_emo_breakdown[4]['percentage']['emo']] + ' ' + emo_sign5 + str(average_emo_breakdown[4]['percentage']['percentage_change']) + '%' + ' '

                    emo_sign6 = ''
                    if average_emo_breakdown[5]['percentage']['percentage_change'] > 0:
                        emo_sign6 = '+'
                    email_string = email_string + emo_icons[average_emo_breakdown[5]['percentage']['emo']] + ' ' + emo_sign6 + str(average_emo_breakdown[5]['percentage']['percentage_change']) + '%' + ' '

                    emo_sign7 = ''
                    if average_emo_breakdown[6]['percentage']['percentage_change'] > 0:
                        emo_sign7 = '+'
                    email_string = email_string + emo_icons[average_emo_breakdown[6]['percentage']['emo']] + ' ' + emo_sign7 + str(average_emo_breakdown[6]['percentage']['percentage_change']) + '%' + '. '

                    email_string = email_string + 'Please login to your Emotional Machines account to check out the rest!'

                    msg = Message()
                    msg.subject = "Daily Tag Update for " + '\"' + search_inputs[0]['searchInput'] + '\"'
                    msg.recipients = [username[0][0]]
                    msg.sender = 'noreply@emomachines.xyz'
                    msg.body = email_string

                    Thread(target=mail.send(msg)).start()

                except Exception as e:
                    msg = Message()
                    msg.subject = "Tagging update error related to particular query"
                    msg.recipients = ['antoine186@hotmail.com']
                    msg.sender = 'noreply@emomachines.xyz'
                    msg.body = str(e)

                    Thread(target=mail.send(msg)).start()

                    msg2 = Message()
                    msg2.subject = "Daily Tag Update for " + '\"' + search_inputs[0]['searchInput'] + '\"'
                    msg2.recipients = [username[0][0]]
                    msg2.sender = 'noreply@emomachines.xyz'
                    msg2.body = 'Not enough results for the past day. Will resume notifications from tomorrow on.'

                    Thread(target=mail.send(msg2)).start()

        except Exception as e:
            
            msg = Message()
            msg.subject = 'Tagging update error unrelated to specific search'
            msg.recipients = ['antoine186@hotmail.com']
            msg.sender = 'noreply@emomachines.xyz'
            msg.body = str(e)

            Thread(target=mail.send(msg)).start()

            msg2 = Message()
            msg2.subject = "Daily Tag Update for " + '\"' + search_inputs[0]['searchInput'] + '\"'
            msg2.recipients = [username[0][0]]
            msg2.sender = 'noreply@emomachines.xyz'
            msg2.body = 'Something is wrong with our notification system. We will fix this as soon as humanly possible!'

            Thread(target=mail.send(msg2)).start()
