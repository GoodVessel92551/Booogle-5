from flask import Flask, render_template,redirect,request,current_app,session
from replit import web,db
from better_profanity import profanity
import os,random
from fun import pro_pic,username,sets,delete_set,revise_new,revise_new_quest,id_gen,make_dict,revise_new_account

user = web.UserStore()

app = Flask(__name__)
app.secret_key = os.environ['secret_key']

@app.route("/")
@web.authenticated_template("login.html")
def home():
    if username() not in db["users"]:
        db["users"].append(username())
        db[username()] = {
            "tasks":{},
            "settings":{},
            "about":{}
        }
    return render_template("home.html",profile_pic=pro_pic(),name=username())

@app.route("/games")
@web.authenticated_template("login.html")
def games():
    return render_template("games.html",profile_pic=pro_pic(),name=username())

@app.route("/time")
@web.authenticated_template("login.html")
def time():
    return render_template("time.html",profile_pic=pro_pic(),name=username())

@app.route("/play/<game>")
@web.authenticated_template("login.html")
def play(game):
    return render_template("play/"+game.lower()+".html",profile_pic=pro_pic(),name=username())

@app.route("/revise")
@web.authenticated_template("login.html")
def revise():
    revise_sets = sets()
    if revise_sets == "No User":
        return redirect("/revise/account")
    return render_template("revise.html",profile_pic=pro_pic(),name=username,revise_sets=revise_sets)

@app.route("/revise/flashcards/<set>")
@web.authenticated_template("login.html")
def flashcards(set):
    return render_template("revise/flashcards.html",profile_pic=pro_pic(),name=username,set=sets()[set])

@app.route("/revise/fill/<set>")
@web.authenticated_template("login.html")
def fill(set):
    return render_template("revise/fill.html",profile_pic=pro_pic(),name=username,set=sets()[set])

@app.route("/revise/finish")
@web.authenticated_template("login.html")
def finish():
    return render_template("revise/finish.html",profile_pic=pro_pic(),name=username)

@app.route("/revise/delete/<name>")
@web.authenticated_template("login.html")
def delete(name):
    delete_set(name)
    return redirect("/revise")
    
@app.route("/revise/new",methods=["POST","GET"])
@web.authenticated_template("login.html")
def new():
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        cover = request.form["cover"]
        r = revise_new(title,desc,cover)
        if r == False:
            return redirect("/revise/new")
        return redirect("/revise/new/question/"+title)
    return render_template("revise/new.html",name=username(),profile_pic=pro_pic())

@app.route("/revise/new/question/<name>",methods=["POST","GET"])
@web.authenticated_template("login.html")
def new_quest(name):
    if request.method == "POST":
        quest = request.form["quest"]
        ans = request.form["ans1"]
        r = revise_new_quest(quest,ans,name)
        if r == False:
            return redirect("/")
        if request.form["button"] == "finish":
            return redirect("/revise")
    return render_template("/revise/new_quest.html",name=username(),profile_pic=pro_pic())

@app.route("/revise/questions/<name>",methods=["POST","GET"])
@web.authenticated_template("login.html")
def question(name):
    set = sets()[name]
    if request.method == "POST":
        current = session.get("current")
        if session.get("current")["current"] == len(session.get("current")["order"]):
            user.current["stats"]["total"]["sets"] += 1
            return render_template("finish.html",name=username(),profile_pic=pro_pic())
        if session.get("next") == "False":
            answer = request.form["button"]
            answers = []
            for i in set[current["order"][current["current"]]]["answers"]:
                answers.append(set[current["order"][current["current"]]]["answers"][i])
            answer1 = answers[0]
            for i in range(1,len(answers)):
                answer1 += ", "+i
            session["next"] = "True"
            session["current"] = {"current":current["current"]+1,"order":current["order"]}
            if answer in answers:
                return render_template("revise/correct.html",name=username(),profile_pic=pro_pic(),answer=answer1)
            else:
                return render_template("revise/wrong.html",name=username(),profile_pic=pro_pic(),answer=answer1)
        else:
            session["next"] = "False"
    else:
        if len(set) < 4:
            session["notifications"] = ["You Need More Questions"]
            return redirect("/")
        order = []
        for i in range(1,len(set)):
            order.append("Q"+str(i))
        random.shuffle(order)
        session["next"] = "False"
        session["current"] = {"current":0,"order":order}
    ans = []
    if session.get("current")["current"] == len(session.get("current")["order"]):
        user.current["stats"]["total"]["sets"] += 1
        return render_template("revise/finish.html",name=username(),profile_pic=pro_pic())
    current = session.get("current")
    question = set[current["order"][current["current"]]]["question"]
    amount_needed = 3-len(set[current["order"][session["current"]["current"]]]["answers"])
    ans.append(set[current["order"][session["current"]["current"]]]["answers"]["ans1"])
    temp = list(current["order"])
    temp.remove(current["order"][current["current"]])
    try:
        type = set[current["order"][current["current"]]]["type"]
    except:
        for i in range(amount_needed):
            quest = random.choice(temp)
            temp.remove(quest)
            ans.append(set[quest]["answers"][random.choice(list(set[quest]["answers"].keys()))])
        random.shuffle(ans)
    else:
        ans = []
        for i in temp:
            if set[i]["type"] == type:
                temp.remove(i)
                ans.append(set[i]["answers"]["ans1"])
        if len(ans) >= 3:
            random.shuffle(ans)
            ans = ans[:2]
            ans.append(set[current["order"][session["current"]["current"]]]["answers"]["ans1"])
        else:
            ans.append(set[current["order"][session["current"]["current"]]]["answers"]["ans1"])
        while len(ans) < 3:
            quest = random.choice(temp)
            temp.remove(quest)
            ans.append(set[quest]["answers"][random.choice(list(set[quest]["answers"].keys()))])
        random.shuffle(ans)
    return render_template("revise/quests.html",name=username(),profile_pic=pro_pic(),sets=set,ans=ans,question=question)

@app.route("/tasks")
@web.authenticated_template("login.html")
def tasks():
    return render_template("tasks.html",name=username(),profile_pic=pro_pic(),tasks=make_dict(db[username()]["tasks"]))

@app.route("/tasks/new",methods=["POST","GET"])
@web.authenticated_template("login.html")
def tasks_new():
    if request.method == "POST":
        title = request.form["title"]
        date = request.form["date"]
        desc = request.form["desc"]
        task = {
            "title":title,
            "desc":desc,
            "date":date
        }
        id = id_gen()
        db[username()]["tasks"][id] = task
        return redirect("/tasks")
    return render_template("new_task.html",name=username(),profile_pic=pro_pic())

@app.route("/tasks/delete/<id>")
@web.authenticated_template("login.html")
def delete_task(id):
    del db[username()]["tasks"][id]
    return redirect("/tasks")

@app.route("/tasks/done/<id>")
@web.authenticated_template("login.html")
def done_task(id):
    del db[username()]["tasks"][id]
    return redirect("/tasks")

@app.route("/tasks/edit/<id>",methods=["POST","GET"])
@web.authenticated_template("login.html")
def edit_task(id):
    task = db[username()]["tasks"][id]
    if request.method == "POST":
        title = request.form["title"]
        date = request.form["date"]
        desc = request.form["desc"]
        task = {
            "title":title,
            "desc":desc,
            "date":date
        }
        db[username()]["tasks"][id] = task
        return redirect("/tasks")
    return render_template("edit_task.html",name=username(),profile_pic=pro_pic(),date=task["date"],title=task["title"],desc=task["desc"])
    
@app.route("/sw.js", methods=["GET"])
def sw():
    return current_app.send_static_file("sw.js")

@app.route("/offline")
def offline():
    return render_template("offline.html")

@app.route("/calculator")
@web.authenticated_template("login.html")
def calculator():
    return render_template("calculator.html",name=username(),profile_pic=pro_pic())

@app.route("/random")
@web.authenticated_template("login.html")
def random_number():
    return render_template("random_number.html",name=username(),profile_pic=pro_pic())

@app.route("/revise/account")
@web.authenticated_template("login.html")
def revise_account():
    return render_template("revise_account.html",name=username(),profile_pic=pro_pic())

@app.route("/revise/account/new")
@web.authenticated_template("login.html")
def add_revise_account():
    print(revise_new_account())
    return redirect("/revise")

app.run(host="0.0.0.0",port=8080,debug=True)