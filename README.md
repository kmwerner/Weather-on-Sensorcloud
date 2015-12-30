# Weather-on-Sensorcloud
The files in this repository represent a project to collect the temperature and upload it to a convenient data storage location. The files are designed to be run regularly as a cron job on a small ubuntu home server.

sensorcloud.py - contains the sensorcloud python example functions (see LORD Microstrain's Github page) as well as a custom function for uploading any arbitrary timeseries data.

weatherchecker.py - This file uses the Open Weather Map library (pyowm) to check the current weather. Returns the timestamp and temperature in degF as a timeseries tuple.

weatheruploader.py - calls the function within weatherchecker.py and adds the resulting timeseries tuple to a semipermanent list stored as a text file. In order to decrease transactions on the sensorcloud server, this file has a 'dump' variable. Once the list has reached this length, the weatheruploader file authenticates with sensorcloud, packs it in the specified XML format, and then uploads the data.

All data generated using this project will be uploaded and visible at the public sensorcloud link (data stored on the BurlingtonTempF channel):
https://sensorcloud.microstrain.com/SensorCloud/data/OAPI004GLT2MFWDG/


