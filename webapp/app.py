from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from datetime import datetime
from peewee import *
import requests
import json
import pygal

app = Flask(__name__)

bootstrap = Bootstrap(app)

db= SqliteDatabase('coffee.db')

last_brewed=None

 

class BaseModel(Model):
    class Meta:
        database=db

class Pot(BaseModel):
    time = DateTimeField()

@app.before_first_request
def first():
    if not Pot.table_exists():
        db.create_tables([Pot])

@app.route('/')
def landing():
    global last_brewed
    return render_template("index.html",last=last_brewed)

@app.route('/brew', methods=['POST','BREW'])
def brew():    
    now =datetime.now()
    global last_brewed
    last_brewed=now
    new=Pot(time=last_brewed)
    new.save()
    #do stuff
    #landing()
    #return render_template("index.html",last=last_brewed)
    return '200'


@app.route('/brew_button')
def brew_button():    
    now =datetime.now()
    global last_brewed
    last_brewed=now
    new=Pot(time=last_brewed)
    new.save()
    #do stuff
    landing()
    return render_template("index.html",last=last_brewed)


@app.route('/analytics')
def analytics():
    Pot.select()
    dates = []
    frequency = []
    idx=0
    count=0
    cur_month=None
    cur_day=None
    cur_hour=None
    for user in Pot.select():
        month=user.time.month
        day=user.time.day
        hour=user.time.hour
        print hour
        if (cur_day !=day or cur_month!=month or cur_hour!=hour):
            dates.append(datetime(2017,month,day,hour))
            frequency.append(1)
            if cur_day!=None:
                idx=idx+1
        else:
            print frequency
            print idx
            frequency[idx]=frequency[idx]+1
        cur_day=day
        cur_month=month
        cur_hour=hour

        print user.time
    print dates
    print frequency

    date_chart = pygal.Line()
    date_chart.x_labels = map(lambda d: d.strftime('%Y-%m-%d %H:00'), dates)
    date_chart.add("Brews",frequency)
    date_chart=date_chart.render_data_uri()

    return render_template("analytics.html",last=last_brewed, date_chart=date_chart)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')