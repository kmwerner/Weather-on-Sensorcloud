# Weather-on-Sensorcloud
The files in this repository represent a project to collect the temperature and upload it to a convenient data storage location. The files are designed to be run regularly as a cron job on a small ubuntu home server. Weatherchecker.py will be run every 10 minutes. Weatheruploader will be run every 6 hrs, uploading 36 new data points to the server. 

weatherchecker.py - This file uses the Open Weather Map library (pyowm) to check the current weather. Returns the timestamp and temperature in degF as a timeseries tuple. This data is written to a local .txt file that serves as local persistent data storage, thereby allowing batch uploads to the SensorCloud server. A limited number of upload/download transactions are allowed, so batching the uploads reduces the number of monthly transactions.

weatheruploader.py - Reads the persistent local file, munges the data into an acceptable timeseries format, and uses a custom "upload_data" function based on the SensorCloud API. Uses authorization function and 'get_sensors' functions from the SensorCloud API python example file available under LORD Microstrain's github page.

All data generated using this project will be uploaded and visible at the public sensorcloud link (data stored on the TemperatureF channel):
https://sensorcloud.microstrain.com/SensorCloud/data/OAPI004GLT2MFWDG/


