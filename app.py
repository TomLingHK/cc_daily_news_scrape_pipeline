import os
import threading
import requests
from flask import Flask, jsonify, request

from return_news_config import return_news_config
from return_extract_prompt import return_extract_prompt
from update_csv import update_csv_sheet as update_csv
from check_added_url import check_added_url

import traceback

app = Flask(__name__)

SERVICE_NAME = "daily_news_scrape"
# BASE_PATH = "./daily_news_data/"
BASE_PATH = os.getenv("BASE_PATH") or "/nas_data/"

# if not (os.path.isdir(BASE_PATH) and os.access(BASE_PATH, os.R_OK)):
#     BASE_PATH = "/app/nas_data/"

print('BASE_PATH: ', BASE_PATH)

# prefix for txt file that stores daily added url
ADDED_URL_TXT_PREFIX = "added_url_"
# prefix for csv file that stores daily news details
DAILY_NEWS_CSV_PREFIX = "daily_news_"

# "/app/nas_data/pipeline_scrape_daily_news/",

APP_CONST = {
    'BASE_PATH': BASE_PATH,
    'ADDED_URL_TXT_PREFIX': ADDED_URL_TXT_PREFIX,
    'DAILY_NEWS_CSV_PREFIX': DAILY_NEWS_CSV_PREFIX,
}

# def run_pipeline_and_callback(callback_url, func, *func_args, **func_kwargs):
#     """
#     This function runs in the background thread.
#     It contains your complete task logic and sends a callback to Webhook Url when finished.
#     """
#     payload = {}

#     try:
#         result = func(*func_args, **func_kwargs)

#         # Organize your task's output result into the 'result' field
#         payload = {
#             "status": "success",
#             "service": SERVICE_NAME,
#             "result": result
#         }

#     except Exception as e:
#         tb = traceback.format_exc()
#         print(tb)
#         payload = {
#             "status": "failed",
#             "service": SERVICE_NAME,
#             "error": str(e)
#         }

#     finally:
#         if callback_url:
#             print('callback_url: ', callback_url)
#             try:
#                 print(f"Sending callback to {callback_url}")
#                 response = requests.post(callback_url, json=payload, timeout=(20, 60))
#                 # Raise for non-2xx status codes so we only print success when it's truly sent
#                 response.raise_for_status()
#                 print(f"Callback sent successfully. Status code: {response.status_code}")
#             except requests.exceptions.ConnectTimeout:
#                 print("Connection timed out!")
#             except requests.exceptions.Timeout:
#                 print("The request timed out")
#             except requests.exceptions.HTTPError as http_e:
#                 resp = getattr(http_e, 'response', None)
#                 status = getattr(resp, 'status_code', 'N/A')
#                 text = getattr(resp, 'text', '')
#                 print(f"Callback request failed with HTTP error: {http_e} - Status: {status} - Response: {text}")
#             except requests.RequestException as req_e:
#                 print(f"Failed to send callback: {req_e}")
#         else:
#             print("No callback_url provided. Skipping callback.")
    
@app.route('/check_added_url', methods=['POST'])
def trigger_check_added_url():
    """
    Check if url already existed in the txt file. Return url that are not existed in the txt file.
        date(string): "20250905"
        input(list): [{"article_url": "https://example.com/news1"}, {"article_url": "https://example.com/news2"}]
    """
    
    print(f"BACKGROUND TASK STARTED for endpoint: /check_added_url")
    data = request.get_json(silent=True) or {}
    # if 'callback_url' not in data:
    #     print(f"callback_url missing in request body, returning error response.")
    #     return jsonify({"error": "Missing 'callback_url' in request body"}), 400
    if 'date' not in data:
        print(f"date missing in request body, returning error response.")
        return jsonify({"error": "Missing 'date' in request body"}), 400
    
    # callback_url = data['callback_url']
    date = data['date']
    input_payload = data.get('input', [])
    lang = data.get('lang', "zh") # default to Chinese if not provided
    
    if (len(date)!=8) or (not date.isdigit()):
        print(f"Invalid date format in request body, returning error response.")
        return jsonify({"error": "Invalid 'date' format. Expected 'YYYYMMDD'."}), 400
    
    # thread = threading.Thread(
    #     target=run_pipeline_and_callback,
    #     args=(callback_url,
    #           check_added_url,
    #           APP_CONST,
    #           input_payload,
    #           date
    #           )
    # )
    # thread.daemon = True
    # thread.start()

    # response = {
    #     "message": "Task accepted and is running in the background.",
    #     "service": SERVICE_NAME
    # }
    # return jsonify(response), 202
    
    return jsonify(check_added_url(APP_CONST, input_payload, date, lang)), 200

@app.route('/run', methods=['POST'])
def trigger_run():
    """
    The entry point for the web service. It receives the launch request.
        date(string): "20250905"
        input(list): [{article_url: "xxx", ...}, {...}]
    """
    
    print(f"BACKGROUND TASK STARTED for endpoint: /run")
    data = request.get_json(silent=True) or {}
    # if 'callback_url' not in data:
    #     print(f"callback_url missing in request body, returning error response.")
    #     return jsonify({"error": "Missing 'callback_url' in request body"}), 400
    if 'date' not in data:
        print(f"date missing in request body, returning error response.")
        return jsonify({"error": "Missing 'date' in request body"}), 400
    
    # callback_url = data['callback_url']
    date = data['date']
    input_payload = data.get('input', [])
    lang = data.get('lang', "zh") # default to Chinese if not provided
    
    if (len(date)!=8) or (not date.isdigit()):
        print(f"Invalid date format in request body, returning error response.")
        return jsonify({"error": "Invalid 'date' format. Expected 'YYYYMMDD'."}), 400
    
    # thread = threading.Thread(
    #     target=run_pipeline_and_callback,
    #     args=(callback_url,
    #           update_csv,
    #           APP_CONST,
    #           input_payload,
    #           date
    #           )
    # )
    # thread.daemon = True
    # thread.start()

    # response = {
    #     "message": "Task accepted and is running in the background.",
    #     "service": SERVICE_NAME
    # }
    # return jsonify(response), 202
    
    return jsonify(update_csv(APP_CONST, input_payload, date, lang)), 200

@app.route('/news_config', methods=['GET'])
def trigger_get_news_config():
    """
    Return the news config base on the specified language. The config include source, url and prompt of different news source.
        lang(string): "en" or "zh"
    """
    
    print(f"BACKGROUND TASK STARTED for endpoint: /news_config")
    data = request.get_json(silent=True) or {}
    # if 'callback_url' not in data:
    #     print(f"callback_url missing in request body, returning error response.")
    #     return jsonify({"error": "Missing 'callback_url' in request body"}), 400
    
    # callback_url = data['callback_url']
    lang = data.get('lang', "zh") # default to Chinese if not provided
    
    # thread = threading.Thread(
    #     target=run_pipeline_and_callback,
    #     args=(callback_url,
    #           return_news_config,
    #           APP_CONST,
    #           lang
    #           )
    # )
    # thread.daemon = True
    # thread.start()

    # response = {
    #     "message": "Task accepted and is running in the background.",
    #     "service": SERVICE_NAME
    # }
    # return jsonify(response), 202
    
    return jsonify(return_news_config(APP_CONST, lang)), 200

# @app.route('/extract_prompt', methods=['GET'])
# def trigger_get_extract_prompt():
#     """
#     Returns the prompt for extracting prompt content and help categorizing the news.
#     """
    
#     print(f"BACKGROUND TASK STARTED for endpoint: /extract_prompt")
#     return jsonify(return_extract_prompt(APP_CONST)), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)