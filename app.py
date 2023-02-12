from bs4 import BeautifulSoup
import lxml,json,requests
from flask import *
import random
import string
import asSQL
from asSQL import Client
from flask import Flask, request, jsonify
users_db = Client("users")
users_table = users_db['users']
users_table.create_table()

bots_db = Client("bots")
bots_table = bots_db['bots']
bots_table.create_table()
app = Flask(__name__)
@app.route('/create_bot', methods=['POST'])
def create_bot():
    bot_username = request.json.get('bot_username')
    bot_name = request.json.get('bot_name')
    user_id = request.json.get('user_id')

    if bots_table.key_exists(bot_username):
        return jsonify({"result": "Username already taken"}), 400
    
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
    bot_info = {"bot_name": bot_name, "bot_username": bot_username, "token": token}

    bots_table.set(token, bot_info)
    if users_table.key_exists(user_id):
        users_table.push(user_id, bot_info)
    else:
        users_table.set(user_id, [bot_info])
    return jsonify({"result": bot_info}), 200

@app.route('/bot<token>/getme', methods=['GET'])
def getme(token):
    
    if not bots_table.key_exists(token):
        return jsonify({"result": "Unauthorized"}), 401
    
    bot_info = bots_table.get(token)
    return jsonify({"result": bot_info}), 200

@app.route("/data/")
def info():
    userid = request.args.get("id")
    URL = f"https://i.instagram.com/api/v1/users/{userid}/info"
    headers = {'User-Agent':'Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)'} 
    response = requests.get(URL, headers=headers)
    return (response.json()["user"])
@app.route('/teleinfo/',methods=['GET'])
def telegraminfograber_page():

    search_query = str(request.args.get('url'))
    try:
        url = f'{search_query}?embed=1'
        views_table = []
        date_table = []
        title_table = []

        result = requests.get(f"{url}")
        src = result.content

        soup = BeautifulSoup(src, "lxml")

        views = soup.find_all("span", {"class": "tgme_widget_message_views"})
        g = str(views[0]).replace('</span>','').replace('<span class="tgme_widget_message_views">','')

        title = soup.find_all("div", {"class": "tgme_widget_message_text js-message_text"})
        for i in range(len(title)):
            title_table.append(title[i].text)

        date = soup.find_all("time")
        for i in range(len(date)):
            date_table.append(date[i].text)

        data_set = {'date': f'{date_table[0]}', 'msg': f'{title_table[0]}', 'views': f'{g}', 'stats': f'Loaded'}
        json_string = json.dumps(data_set, ensure_ascii=False)
        response = Response(json_string, content_type="application/json; charset=utf-8")
        return response
    except:
        data_set = {'stats': f'Error!'}
        return data_set
    
if __name__ == "__main__":
    app.run()
