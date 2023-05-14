from replit import web,db
from flask import request
import requests,json,os,random

def username():
    return web.auth.name

def pro_pic():
    return request.headers["X-Replit-User-Profile-Image"]

def sets():
    id = request.headers["X-Replit-User-Id"]
    name = request.headers["X-Replit-User-Name"]
    url = "https://api.booogle.app/api/"+os.environ['key']+"/"+id+"/"+name
    r = requests.get(url)
    text = r.json()
    url_revise = "https://revise.booogle.app/api/"+text["token"]+"/"+id+"/"+name
    r_revise = requests.get(url_revise)
    sets = r_revise.json()
    return sets

def delete_set(set_name):
    id = request.headers["X-Replit-User-Id"]
    name = request.headers["X-Replit-User-Name"]
    url = "https://api.booogle.app/api/"+os.environ['key']+"/"+id+"/"+name
    r = requests.get(url)
    text = r.json()
    url_revise = "https://revise.booogle.app/api/delete/"+text["token"]+"/"+id+"/"+name+"/"+set_name
    requests.get(url_revise)

def revise_new(a,b,c):
    id = request.headers["X-Replit-User-Id"]
    name = request.headers["X-Replit-User-Name"]
    url = "https://api.booogle.app/api/"+os.environ['key']+"/"+id+"/"+name
    r = requests.get(url)
    text = r.json()
    url_revise = "https://revise.booogle.app/api/new/"+text["token"]+"/"+id+"/"+name+"/"+a+"/"+b+"/"+c
    r = requests.get(url_revise)

def revise_new_quest(q,a,set_name):
    id = request.headers["X-Replit-User-Id"]
    name = request.headers["X-Replit-User-Name"]
    url = "https://api.booogle.app/api/"+os.environ['key']+"/"+id+"/"+name
    r = requests.get(url)
    text = r.json()
    url_revise = "https://revise.booogle.app/api/new_quest/"+text["token"]+"/"+id+"/"+name+"/"+set_name+"/"+q+"/"+a
    r = requests.get(url_revise)

def id_gen():
    id = ""
    keys = "1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm"
    for i in range(15):
        letter = random.choice(keys)
        id += letter
    return id

def make_dict(dictionary):
    list = dict(dictionary)
    for i in list:
        list[i] = dict(dictionary[i])
    return list