from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from datetime import datetime
from pygal.style import BlueStyle
from peewee import *
import requests
import json
import pygal
import coffee

app = Flask(__name__)

bootstrap = Bootstrap(app)

db= SqliteDatabase('coffee.db')

last_brewed=None

 

class BaseModel(Model):
    class Meta:
        database=db

class Pot(BaseModel):
    time = DateTimeField()

class Stats(BaseModel):
    coffeeC = FloatField()
    coffeeF = FloatField()
    heaterC = FloatField()
    heaterF = FloatField()

@app.before_first_request
def first():
    if not Pot.table_exists():
        db.create_tables([Pot])
    if not Stats.table_exists():
        db.create_tables([Stats])
    coffee.setupPin()
    global last_brewed
    last_brewed = Pot.select().order_by(Pot.id.desc()).get().time 

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
    coffee.coffeeOn()
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
    coffee.coffeeOn()
    return render_template("index.html",last=last_brewed)


@app.route('/stop_brew_button')
def stop_brew_button():    
    #do stuff
    coffee.coffeeOff()
    return render_template("index.html",last=last_brewed)

@app.route('/analytics')
def analytics():
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
        if (cur_day !=day or cur_month!=month or cur_hour!=hour):
            dates.append(datetime(2017,month,day,hour))
            frequency.append(1)
            if cur_day!=None:
                idx=idx+1
        else:
            frequency[idx]=frequency[idx]+1
        cur_day=day
        cur_month=month
        cur_hour=hour

    coffeeCArray = []
    coffeeFArray = []
    heaterCArray = []
    heaterFArray = []
    for temp in Stats.select():
        coffeeCArray.append(temp.coffeeC)
        coffeeFArray.append(temp.coffeeF)
        heaterCArray.append(temp.heaterC)
        heaterFArray.append(temp.heaterF)

    date_chart = pygal.Line()
    date_chart.title = "Number of Pots Brewed Per Hour"
    date_chart.x_labels = map(lambda d: d.strftime('%Y-%m-%d %H:00'), dates)
    date_chart.add("Brews",frequency)
    date_chart=date_chart.render_data_uri()

    water_level_chart = pygal.Bar(width=200, style=BlueStyle, range=(0.0,100.0))
    water_level_chart.title = "Current Water Level"
    water_level_chart.x_labels = ["Level"]
    water_level_chart.add("",((9-(coffee.pingWater()))/5.75)*100)
    water_level_chart=water_level_chart.render_data_uri()

    line_chart = pygal.Line()
    line_chart.title = 'Temp Of Coffee and Heater (Degrees)'
    line_chart.x_labels = ["Coffee (C)", "Coffee (F)", "Heater (C)", "Heater (F)"]
    line_chart.add('Coffee (C)',  coffeeCArray)
    line_chart.add('Coffee (F)',  coffeeFArray)
    line_chart.add('Heater (C)',  heaterCArray)
    line_chart.add('Heater (F)',  heaterFArray)
    line_chart=line_chart.render_data_uri()

    return render_template("analytics.html",last=last_brewed, date_chart=date_chart, water_level_chart=water_level_chart, temp_chart=line_chart)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
