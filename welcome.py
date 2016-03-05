from flask import Flask, render_template, request, redirect, url_for, send_from_directory, current_app
application = app = Flask(__name__)
import random
import datetime
import os
from consts import *
from flask import session


counter = {}
app.secret_key = '4yt7573_secret!!!'

GOOD_ID = "1337"


def get_lang(pair, to_get):
    """get language from db"""
    try:
        lang = "unknown" if pair[to_get] == "" else pair[to_get]
    except:
        lang = "unknown"
    return lang


def new_pair(ip):
    print "new_pair"
    """generates new page with new pair of codes"""
    user = session.get('user', "USER")
    try:
        coun = COUNTER.find({"user": user})[0]["num"]
    except:
        coun = 0

    if not user == GOOD_ID and coun % 5 == 4:
        good_options = [e['Id'] for e in GOOD_PAIRS.find({})]
        r_num = int(good_options[random.randrange(len(good_options))])
    else:
        r_num = random.randrange(WEB_DB.count())
    print r_num
    if NEW_IDS_DB.find({"Id": str(r_num)}).count() == 0:
        print "dropped"
        new_pair(ip)
    try:
        pair = WEB_DB.find({"Id": r_num})[0]
    except:
        new_pair(ip)
    #remove from web, debugging stuff
    try:
        score = pair["similarity"]
    except:
        score = 1
    code1 = pair["code1"].strip().replace("<br/>\r\n", "").replace("<br/>\n", "")
    code2 = pair["code2"].strip().replace("<br/>\r\n", "").replace("<br/>\n", "")
    lang1 = get_lang(pair, "lang1")
    lang2 = get_lang(pair, "lang2")

    if type(ip) is list:
        ip = ip[0]

    return render_template("new_index.html",
                           code1=code1,
                           code2=code2,
                           pair_id=r_num,
                           #score=score,
                           lang1=lang1,
                           lang2=lang2,
                           counter=coun,
                           user=user)


@app.route("/about")
def about():
    """about page"""
    return render_template("new_about.html")


@app.route("/download", methods=['POST', 'GET'])
def download():
    """download page"""
    if request.method == 'GET':
        return render_template("new_download.html",
                               thanks="hidden",
                               text="Thank you!")
    else:
        try:
            """
            data = request.form
            mail = data["mail"]
            inst = data["inst"]
            uname = data["name"]
            for black_list_element in ["*", "drop"]:
                if black_list_element in mail.lower() or black_list_element in inst.lower() or black_list_element in uname.lower():
                    raise Exception
            if len(mail.strip()) == 0 or len(inst.strip()) == 0 or len(uname.strip()) == 0:
                raise Exception
            if not request.headers.getlist("X-Forwarded-For"):
                ip = request.remote_addr
            else:
                ip = request.headers.getlist("X-Forwarded-For")[0].split(",")[0]
            DOWNLOADS.insert({"mail": mail, "inst": inst, "userName": uname, "ip": ip})
            print "yyay!"
            """
            return download_file('ResearchData.zip')

        except Exception as e:
            print "oops", e
            return render_template("new_download.html",
                                   thanks="visible",
                                   text="Try again!")


@app.route('/uploads/<path:filename>')
def download_file(filename):
    uploads = os.path.join(current_app.root_path, "uploads/")
    return send_from_directory(uploads, filename, as_attachment=True)


@app.route("/", methods=['POST', 'GET'])
#@app.route("/index", methods=['POST', 'GET'])
def hello():
    global user_name
    print "hello", request.method
    """main function"""
    if not request.headers.getlist("X-Forwarded-For"):
        ip = request.remote_addr
    else:
        ip = request.headers.getlist("X-Forwarded-For")[0].split(",")[0]
    if request.method == 'GET':
        return new_pair(ip)
    else:
        try:
            req_val = request.form['btn']
            print "!", req_val
        except:
            if not request.form['user_name'] == "":
                session['user'] = request.form['user_name']
            return new_pair(ip)

        req_val = req_val.replace("\n", " ").replace("\t", "").replace("  ", " ").replace("  ", " ").replace("\r", "")
        if req_val == "About page":
            return about()
        if req_val == "Go back":
            return new_pair(ip)
        pair_id = request.form['pair_id']
        req_val = req_val.replace("\r\n", " ")
        if req_val == "I don't know":
            DONT_KNOW_DB.insert({"Id": pair_id, "Ip": ip, "Time": str(datetime.datetime.now())})
        elif req_val == "Report error":
            WEB_ERROR_DB.insert({"Id": pair_id, "Ip": ip, "Time": str(datetime.datetime.now())})
        else:
            print req_val
            save_res(pair_id, STRING_TO_GRADE[req_val], ip)
        #return redirect(url_for('hello'))
        return new_pair(ip)


def save_res(pair_id, grade, ip):
    """save the result to the db"""
    global counter
    user_name = session.get('user', "USER")
    WEB_RES_DB.insert({"Id": pair_id, "Grade": grade, "Ip": ip, "Time": str(datetime.datetime.now()), "user": user_name})
    if user_name == GOOD_ID:
        GOOD_PAIRS.insert({"Id": pair_id, "Grade": grade, "Ip": ip, "Time": str(datetime.datetime.now()), "user": user_name})
    num = 1
    if not user_name == "USER":
        try:
            num = COUNTER.find({'user': user_name})[0]["num"]
            COUNTER.update({"user": user_name}, {"$set": {"num": num + 1}})
            print "update"
        except:

            print COUNTER.insert({"user": user_name, "num": num})
            print "new"
        counter[ip] = counter.get(ip, 0) + 1
    print "SAVED: ", pair_id, grade, ip, user_name, num

port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))