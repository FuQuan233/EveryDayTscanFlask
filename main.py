import flask
from flask import  Flask,request,render_template,session,redirect,Response
from flask_cors import CORS
import json,socket,re,time,datetime,threading,os
import pymysql
from codeScan import CodeScan
from flask_apscheduler import APScheduler
from gevent import pywsgi

app = Flask(__name__, static_url_path='')
CORS(app, resources=r'/*')
config = json.load(open('config.json','r',encoding="utf8"))
scheduler = APScheduler()
asdfasdf = 0

def dbquery(query,arg=()):
    db.ping(reconnect=True)
    cu = db.cursor()
    cu.execute(query,arg)
    ret = cu.fetchall()
    db.commit()
    cu.close()
    return ret

def row2dict(row):
    return {
        'id': row[0],
        'level': row[1],
        'owner': row[2],
        'file': row[3],
        'line': row[4],
        'date': row[5].strftime('%Y-%m-%d'),  # 格式化日期
        'errortype': row[6],
        'errorinfo': row[7],
        'msg': row[8],
        'content': row[9]
    }

scantime = config['scan_time'].split(':')
@scheduler.task('cron', id='run_code_scan', day='*', hour=scantime[0], minute=scantime[1], second='0')
def run_code_scan():
    global asdfasdf
    asdfasdf+=1
    scanner = CodeScan(app.logger, db, config)
    scanner.startScan()

@app.route('/api/setowner',methods=['POST'])
def setowner():
    id = int(request.form.get('id'))
    owner = request.form.get('owner')
    sql = "UPDATE `result_list` SET `owner` = %s WHERE `id` = %s"
    print((owner,id))
    dbquery(sql,(owner,id))
    resp = Response()
    resp.content_type='application/json'
    resp.set_data('{"isok":1}')
    return resp

@app.route('/api/getresults',methods=['GET'])
def getresult():
    date = str(request.args.get("date"))
    sql = 'SELECT `id`,`level`,`owner`,`file`,`line`,`date`,`errortype`,`errorinfo`,`msg`,`content` FROM result_list WHERE `date` = %s'
    ret = dbquery(sql,(date))
    errorlist=[]
    for i in ret:
        errorlist.append(row2dict(i))

    retdata = {"errorlist":errorlist}
    resp = Response()
    resp.content_type='application/json'
    resp.set_data(json.dumps(retdata))
    return resp

@app.route('/api/getallresults',methods=['GET'])
def getallresult():
    date = str(datetime.datetime.now().date())
    sql = 'SELECT `id`,`level`,`owner`,`file`,`line`,`date`,`errortype`,`errorinfo`,`msg`,`content` FROM result_list WHERE `last_show` = %s'
    ret = dbquery(sql,(date))
    errorlist=[]
    for i in ret:
        errorlist.append(row2dict(i))

    retdata = {"errorlist":errorlist}
    resp = Response()
    resp.content_type='application/json'
    resp.set_data(json.dumps(retdata))
    return resp

@app.route('/api/getbaseinfo',methods=['GET'])
def getbaseinfo():
    info = dict()
    info['title'] = config['title']
    info['datelist'] = list()
    ret = dbquery('SELECT `date` FROM result_list GROUP BY `date`')
    for i in ret:
        info['datelist'].append(i[0].strftime('%Y-%m-%d'))

    resp = Response()
    resp.content_type='application/json'
    resp.set_data(json.dumps(info))
    return resp

#web controller
@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    db = pymysql.connect(host=config['mysql_host'],user=config['mysql_user'],passwd=config['mysql_password'],database=config['mysql_database'])
    scheduler.init_app(app)
    scheduler.start()
    # app.run(host="0.0.0.0", port=9101, debug=True)
    server = pywsgi.WSGIServer(('0.0.0.0', config['port']), app)
    server.serve_forever()

    
