# -*- coding: utf-8 -*-
#! /usr/bin/python
#WEATHERUPLOADER.py
import httplib
import xdrlib

AUTH_SERVER = "sensorcloud.microstrain.com"

def authenticate_key(device_id, key):
	conn = httplib.HTTPSConnection(AUTH_SERVER)
	headers = {"Accept": "application/xdr"}
	url = "/SensorCloud/devices/%s/authenticate/?version=1&key=%s"%(device_id, key)
	
	print "Authenticating..."
	conn.request('GET', url=url, headers=headers)
	response =conn.getresponse()
	print response.status, response.reason
	
	#if response is 200 ok then we can parse the response to get the auth token and server
	if response.status is httplib.OK: 
		print "Credential are correct"
		data = response.read()
		unpacker = xdrlib.Unpacker(data)
		auth_token = unpacker.unpack_string()
		server = unpacker.unpack_string()
		print "unpacked xdr.  server:%s  token:%s"%(server, auth_token)
		return server, auth_token
	else: 
		print "Authentication Failure. Check Credentials and retry."

def GetSensors(server, auth_token, device_id):
	"""
	Download the Sensors and Channel information for the Device.
	Packs into a dict for easy parsing
	"""
	conn = httplib.HTTPSConnection(server)
	
	url = "/SensorCloud/devices/%s/sensors/?version=1&auth_token=%s" % (device_id, auth_token)
	headers = {"Accept":"application/xdr"}
	conn.request("GET", url=url, headers=headers)
	sensors = {}
	response = conn.getresponse()
	if response.status is httplib.OK:
		print "Data Retrieved"
		unpacker = xdrlib.Unpacker(response.read())
		#unpack version, always first
		unpacker.unpack_int()
		#sensor info is an array of sensor structs.  In XDR, first you read an int, and that's the number of items in the array.  You can then loop over the number of elements in the array
		numSensors = unpacker.unpack_int()
		for i in xrange(numSensors):
			sensorName = unpacker.unpack_string()
			sensorType = unpacker.unpack_string()
			sensorLabel = unpacker.unpack_string()
			sensorDescription = unpacker.unpack_string()
			#using sensorName as a key, add info to sensor dict
			sensors[sensorName] = {"name":sensorName, "type":sensorType, "label":sensorLabel, "description":sensorDescription, "channels":{}}
			#channels for each sensor is an array of channelInfo structs.  Read array length as int, then loop through the items
			numChannels = unpacker.unpack_int()
			for j in xrange(numChannels):
				channelName = unpacker.unpack_string()
				channelLabel = unpacker.unpack_string()
				channelDescription = unpacker.unpack_string()
				#using channel name as a key, add info to sensor's channel dict
				sensors[sensorName]["channels"][channelName] = {"name":channelName, "label":channelLabel, "description":channelDescription, "streams":{}}
				#dataStreams for each channel is an array of streamInfo structs, Read array length as int, then loop through the items
				numStreams = unpacker.unpack_int()
				for k in xrange(numStreams):
					#streamInfo is a union, where the type indicates which stream struct to use.  Currently we only support timeseries version 1, so we'll just code for that
					streamType = unpacker.unpack_string()
					if streamType == "TS_V1":
						#TS_V1 means we have a timeseriesInfo struct
						#total bytes allows us to jump ahead in our buffer if we're uninterested in the units.  For verbosity, we will parse them.
						total_bytes = unpacker.unpack_int()
						#units for each data stream is an array of unit structs.  Read array length as int, then loop through the items
						numUnits = unpacker.unpack_int()
						#add TS_V1 to streams dict
						sensors[sensorName]["channels"][channelName]["streams"]["TS_V1"] = {"units":{}}
						for l in xrange(numUnits):
							storedUnit = unpacker.unpack_string()
							preferredUnit = unpacker.unpack_string()
							unitTimestamp = unpacker.unpack_uhyper()
							slope = unpacker.unpack_float()
							offset = unpacker.unpack_float()
							#using unitTimestamp as a key, add unit info to unit dict
							sensors[sensorName]["channels"][channelName]["streams"]["TS_V1"]["units"][str(unitTimestamp)] = {"stored":storedUnit, 
							"preferred":preferredUnit, "unitTimestamp":unitTimestamp, "slope":slope, "offset":offset}
	return sensors

def uploadData(server, auth_token, device_id, sensor_name, channel_name, datalist, frequency):
 	"""
 	Upload a timeseries array of data in the form [(UNIXtime1,DATA10,(UNIXtime2,DATA2),...,[UNIXtimeLAST,DATAlast])
 	"""
 	HERTZ=1
 	SECONDS=0
 	conn = httplib.HTTPSConnection(server)
	url="/SensorCloud/devices/%s/sensors/%s/channels/%s/streams/timeseries/data/?version=1&auth_token=%s"%(device_id, sensor_name, channel_name, auth_token)
	
	#we need to pack these strings into an xdr structure
	packer = xdrlib.Packer()
	packer.pack_int(1)  #version 1
	
	#Upload samplerate data:
	if hertz==True:
		packer.pack_enum(HERTZ)
		packer.pack_int(frequency)
	else:
		packer.pack_enum(SECONDS)
		packer.pack_int(frequency)

	#Total number of datapoints.   
	POINTS = len(datalist)
	packer.pack_int(POINTS)
	
	print "packing data now..."
	#now pack each datapoint, we'll use a sin wave function to generate fake data.  we'll use the current time as the starting point
	for i in range(0,len(datalist)):
		packer.pack_hyper(int(datalist[i][0]))
		packer.pack_float(float(datalist[i][1]))  #generate value as a function of time
	data = packer.get_buffer()
	print "adding data..."
	headers = {"Content-type" : "application/xdr"}
	conn.request('POST', url=url, body=data, headers=headers)
	response =conn.getresponse()
	print response.status , response.reason
	
	#if response is 201 created then we know the channel was added
	if response.status is httplib.CREATED: 
		print "data successfuly added"
	else:
		print "Error adding data.  Error:", str(response.read())

device_id = 'your-device-id-goes-here'
key = 'your-api-key-goes-here'

#Authenticate with SensorCloud Server using OpenAPI info above.
server, auth_token = authenticate_key( device_id, key)

#Collect data from local persistent storage file:
timeseries = []
with open('weather.txt','r') as infile:
	for line in infile.readlines():
		timeseries.append([line.split(',')[0],line.split(',')[1].strip()])
	infile.close
sensor_name = 'weather'
channel_name = 'TemperatureF'
datalist = timeseries
frequency = 600 #seconds per sample
upload_data(server, auth_token, device_id, sensor_name, channel_name, datalist, frequency, hertz=False)
