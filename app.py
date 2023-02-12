from bs4 import BeautifulSoup
import lxml,json,requests
from flask import *
import random
import string
import asSQL
from asSQL import Client
from flask import Flask, request, jsonify


from flask import Flask, request
import asSQL
from asSQL import Client
import random
import string

app = Flask(__name__)
users_table = Client("users")["users_table"]
bots_table = Client("bots")["bots_table"]
users_table.create_table()
bots_table.create_table()
@app.route('/create_bot', methods=['POST'])
def create_bot():
    bot_name = request.form.get('bot_name')
    bot_username = request.form.get('bot_username')
    user_id = request.form.get('user_id')
    
    if not all([bot_name, bot_username, user_id]):
        return {"result": "Error: Missing params"}
    if not bot_username.endswith("bot"):
        return {"result": "Error: Bot username should end with 'bot'"}
    if bots_table.key_exists(bot_username):
        return {"result": "Error: Bot username already exists"}
    else:
        token = ''.join(random.choices(string.digits + string.ascii_letters, k=30))
        bot_info = {"username": bot_username, "name": bot_name, "token": token}
        bots_table.set(bot_username, bot_info)
        
        if users_table.key_exists(user_id):
            users_bots = users_table.get(user_id)
            users_bots.append(bot_info)
            users_table.set(user_id, users_bots)
        else:
            users_table.set(user_id, [bot_info])
        
        return {"result": bot_info}

@app.route('/getme', methods=['POST'])
def getme():
    token = request.form.get('token')
    if not token:
        return {"result": "Error: Missing params"}
    for key, value in bots_table.get_all().items():
        if value['token'] == token:
            return {"result": value}
    return {"result": "Unauthorized"}

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
