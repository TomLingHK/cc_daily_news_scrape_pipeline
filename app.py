import os
import threading
import requests
from flask import Flask, jsonify, request

from update_csv import update_csv_sheet as update_csv
from check_added_url import check_added_url

import traceback

app = Flask(__name__)

SERVICE_NAME = "daily_news_scrape"
# BASE_PATH = "./daily_news_data/"
BASE_PATH = os.getenv("BASE_PATH") or "/nas_data/"

if not (os.path.isdir(BASE_PATH) and os.access(BASE_PATH, os.R_OK)):
    BASE_PATH = "/app/nas_data/"

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

def run_pipeline_and_callback(callback_url, func, *func_args, **func_kwargs):
    """
    This function runs in the background thread.
    It contains your complete task logic and sends a callback to Webhook Url when finished.
    """
    payload = {}

    try:
        result = func(*func_args, **func_kwargs)

        # Organize your task's output result into the 'result' field
        payload = {
            "status": "success",
            "service": SERVICE_NAME,
            "result": result
        }

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        payload = {
            "status": "failed",
            "service": SERVICE_NAME,
            "error": str(e)
        }

    finally:
        if callback_url:
            try:
                requests.post(callback_url, json=payload, timeout=20)
                print("Callback sent successfully.")
            except requests.RequestException as req_e:
                print(f"Failed to send callback: {req_e}")
        else:
            print("No callback_url provided. Skipping callback.")
    
@app.route('/check_added_url', methods=['POST'])
def trigger_check_added_url():
    """
    Check if url already existed in the txt file. Return url that are not existed in the txt file.
    """
    data = request.get_json(silent=True) or {}
    if 'callback_url' not in data:
        return jsonify({"error": "Missing 'callback_url' in request body"}), 400
    if 'date' not in data:
        return jsonify({"error": "Missing 'date' in request body"}), 400
    
    callback_url = data['callback_url']
    date = data['date']
    input_payload = data.get('input', [])
    
    thread = threading.Thread(
        target=run_pipeline_and_callback,
        args=(callback_url,
              check_added_url,
              APP_CONST,
              input_payload,
              date
              )
    )
    thread.daemon = True
    thread.start()

    response = {
        "message": "Task accepted and is running in the background.",
        "service": SERVICE_NAME
    }
    return jsonify(response), 202

@app.route('/run', methods=['POST'])
def trigger_run():
    """
    The entry point for the web service. It receives the launch request.
    """
    data = request.get_json(silent=True) or {}
    if 'callback_url' not in data:
        return jsonify({"error": "Missing 'callback_url' in request body"}), 400
    if 'date' not in data:
        return jsonify({"error": "Missing 'date' in request body"}), 400
    
    callback_url = data['callback_url']
    date = data['date']
    input_payload = data.get('input', [])
    
    thread = threading.Thread(
        target=run_pipeline_and_callback,
        args=(callback_url,
              update_csv,
              APP_CONST,
              input_payload,
              date
              )
    )
    thread.daemon = True
    thread.start()

    response = {
        "message": "Task accepted and is running in the background.",
        "service": SERVICE_NAME
    }
    return jsonify(response), 202

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)