from flask_sqlalchemy import SQLAlchemy
import requests
import time
from flask import Flask, render_template, request
from datetime import datetime
from multiprocessing import Process, Value

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new.db'
db = SQLAlchemy(app)	

moistURL = 'https://api.particle.io/v1/devices/350025000b47363339343638/moisturePercentage?access_token=1aa09ff2c1a069ca69c16e6822b0602412a8c1c4'
tempURL = 'https://api.particle.io/v1/devices/350025000b47363339343638/temperature?access_token=1aa09ff2c1a069ca69c16e6822b0602412a8c1c4'
humidURL = 'https://api.particle.io/v1/devices/350025000b47363339343638/humidity?access_token=1aa09ff2c1a069ca69c16e6822b0602412a8c1c4'

def getjson(url):
	r = requests.get(url)
	return r.json()['result']
	
class Plant(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.String, nullable=False, default = datetime.now().strftime("%A, %B %d, %I:%M %p"))
	moisture = db.Column(db.Integer)
	temperature = db.Column(db.Float)
	humidity = db.Column(db.Float)
def __repr__(self):
	return f"Plant('{self.time}','{self.moisture}','{self.temperature}','{self.humidity}')"
db.create_all()

xvalues = Plant.query.with_entities(Plant.time).all()
ytemperature = Plant.query.with_entities(Plant.temperature).all()
ymoisture = Plant.query.with_entities(Plant.moisture).all()
yhumidity = Plant.query.with_entities(Plant.humidity).all()
idvalues = Plant.query.with_entities(Plant.id).all()
reallyxvalues=['']
reallyidvalues=[]
reallytemperature=[]
reallyhumidity = []
reallymoisture = []
reallytimes = []
for i in range(10,(len(xvalues))):
	reallyxvalues.append(xvalues[i][0])
for i in range(1,(len(ytemperature))):
	reallytemperature.append(ytemperature[i][0])
for i in range(1,(len(yhumidity))):
	reallyhumidity.append(yhumidity[i][0])
for i in range(1,(len(ymoisture))):
	reallymoisture.append(ymoisture[i][0])
for i in range(1,(len(idvalues))):
	reallyidvalues.append(idvalues[i][0])
class values():
	globalmoist = reallymoisture[-1]
	globalhumid = reallyhumidity[-1]
	globaltemp = reallytemperature[-1]
v = values()
def record_loop(loop_on):
	try:
		while True:
			if loop_on.value == True:
				print("loop running")
				v.globalmoist = getjson(moistURL)
				time.sleep(3)
				v.globalhumid = getjson(humidURL)
				time.sleep(3)
				v.globaltemp = getjson(tempURL)
				time.sleep(3)
				newReading = Plant(moisture = v.globalmoist, temperature = v.globaltemp, humidity = v.globalhumid)
				db.session.add(newReading)
				Plant.query.filter(Plant.humidity >= 100).delete()
				db.session.commit()
				time.sleep(1)
	except KeyError:
		print('Box disconnected!')

allvalues= {'idvalues':reallyidvalues, 'xvalues':reallyxvalues,'ytemperature':reallytemperature,'ymoisture':reallymoisture,'yhumidity':reallyhumidity, 'currenttemperature':v.globaltemp, 'currenthumidity':v.globalhumid,'currentmoisture':v.globalmoist}

@app.route('/')
def index():
	return render_template("websiteinprogress.html", allvalues=allvalues)

if __name__ == "__main__":
	recording_on = Value('b', True)
	p = Process(target=record_loop, args=(recording_on,))
	p.start()  
	app.run(use_reloader=False)
	p.join()


