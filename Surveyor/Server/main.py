#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request,redirect,url_for,send_from_directory
import json
import os
from werkzeug.utils import secure_filename

from mysqlhelper import UserModel
model=UserModel()
import install_database
def run_sql(content,t=None):
    res=model.run(content,t)
    return res
def check_install():
    res=run_sql('show databases')
    if "wifi_information" not in str(res):
        install_database.Install_database_configuration()

App = Flask(__name__) # create a Flask instance

#<string:content>定义输入的内容的类型及变量名，注意":"左右不能有空格，
@App.route("/log/",methods=['POST'])
def log():
    json_dict = request.get_json()
    content = json_dict["info"]
    print "LogInfo:",content
    return 1


@App.route('/down_database/',methods=['POST'])
def down_data():
#    path=os.getcwd()
    scene=request.form.get('scene')
    sql2='show columns from fingerprints'
    
    cols=run_sql(sql2,scene)
    rows=[]
    for row in cols:
        rows.append(row['Field'])
    rows=','.join(rows)
    path='/var/lib/mysql'
    path=os.path.join(path,scene)

    file_name=scene+'.csv'

    file_dir=os.path.join(path,file_name)
    if os.path.exists(file_dir):
        os.remove(file_dir)
    sql="select %s into outfile '%s' fields terminated by ',' lines terminated by '\n' from fingerprints;" % (rows,os.path.join(path,file_name))
    run_sql(sql,scene)
    # building=request.form.get('building')
    # floor=request.form.get('floor')
    # dest_path=os.path.join('data',scene)
    # dest_path=os.path.join(dest_path,building)

    return send_from_directory(path,file_name)

@App.route('/download/',methods=['POST'])
def downloads():
    scene=request.form.get('scene')
    building=request.form.get('building')
    floor=request.form.get('floor')
    basepath = os.path.dirname(__file__)
    dest_path=os.path.join(basepath,"map")
    dest_path=os.path.join(dest_path,scene)
    dest_path=os.path.join(dest_path,building)
    return send_from_directory(dest_path,floor)


@App.route('/upload/', methods=['POST'])
def upload():
    scene=request.form.get('scene')
    building=request.form.get('building')

    f = request.files["image"]
    basepath = os.path.dirname(__file__)
    dest_path=os.path.join(basepath,"map")
    dest_path=os.path.join(dest_path,scene)
    dest_path=os.path.join(dest_path,building)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    upload_path = os.path.join(dest_path,secure_filename(f.filename))
    f.save(upload_path)
    
@App.route("/install/", methods=["POST"]) # methods可以是多个
def Run_install():
    # 从request请求中提取json内容
    json_dict = request.get_json()
    _type = json_dict["type"]
    if _type=='scene':
        scene_name=json_dict["name"]
        result=install_database.Install_scene(scene_name)
        sql="insert into scenes(name) values ('%s')" % (str(scene_name))
        run_sql(sql,'wifi_information')
    elif _type=='ap':
        scene_name=json_dict['name']
        result=install_database.add_ap_used_to_scene(scene_name)
    data = {"result": result}
    return json.dumps(data) # 将data序列化为json类型的str


@App.route("/run/sql/", methods=["POST"]) # methods可以是多个
def RunSql():
    # 从request请求中提取json内容
    json_dict = request.get_json()
    content = json_dict["sql"]
    selected_database=json_dict['database']
    print "SQL:",content
    print "Database",selected_database
    #rules of communication

    # 运行业务逻辑
    result = run_sql(content,selected_database)
    
    if result!=None:
        # 将结果格式化为dict
        print "Reults:",result
        data = {"result": result}
        return json.dumps(data) # 将data序列化为json类型的str
    else:
        print "execute sql  wrong"
        return "0"
if __name__ == "__main__":
    check_install()
    App.run(debug=True,host='0.0.0.0',port=80)


