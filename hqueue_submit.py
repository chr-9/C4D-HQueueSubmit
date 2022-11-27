#hqueue_submit v1.1
#22/11/25 chi

import c4d
from c4d import gui
import subprocess
import os.path
import json
import socket
import xmlrpc.client
import math

pathProj = "";
jobname = "";
frameFrom = 0;
frameTo = 0;
takeName = "";
priority = 5;

# Local DriveLetter
fstr = "Z:/";
# NAS IP/Path
rstr = "\\\\192.168.0.3/Production/";

framesPerJob = 1;

#HQueue Server IP
hqueue_server = "192.168.0.2:5000";
hqueue_clientGroup = "C4D_RS";

#HQueue client Local bat
client_c4dloc = "C:/c4d.bat";

def Execute():
	global pathProj, jobname, frameFrom, frameTo, takeName, priority, fstr, rstr, hqueue_server, hqueue_clientGroup;
	
	# Create Job
	rd = doc.GetActiveRenderData();
	
	job_spec = { 
		"name": "C4D_" +jobname,
		"submittedBy": socket.gethostname(),
		"environment": { 
		},
		"command":  "",
		"maxHosts": 64,
		"minHosts": 1,
		"priority": priority,
		"children": []
	}
	
	#single frame
	if(framesPerJob == 1): 
		for i in range(frameFrom, frameTo+1): 
			cmd = client_c4dloc;
			if(rd[c4d.RDATA_FRAMESTEP]>1):
				cmd += " -render \"" + pathProj.replace(fstr, rstr) + "\" -frame " + str(i) + " " + str(i) +" " + rd[c4d.RDATA_FRAMESTEP];
			else:
				cmd += " -render \"" + pathProj.replace(fstr, rstr) + "\" -frame " + str(i);
			if(takeName != ""):
				cmd += " -take \"" + takeName + "\"";
			
			children = {
				"name": "Frame " + str(i),
				"priority": priority,
				"command": cmd,
				"tags": [ "single" ],
				"conditions": [
				{ 
					"type" : "client",
					"name": "group",
					"op": "==",
					"value": hqueue_clientGroup
				}
				]
			}
			job_spec["children"].append(children);
	
	#multiple frame
	if(framesPerJob > 1): 
		frameTotal = ( (frameTo+1) - frameFrom);
		job_count = math.floor(frameTotal / framesPerJob) + 1;
		if(job_count*framesPerJob == frameTotal): job_count -= 1;
		
		tmp_from = frameFrom;
		
		for i in range(0, job_count):
			if(tmp_from <= frameTo):
				cmd = client_c4dloc;
				tmp_to = tmp_from + (framesPerJob-1);
				if(tmp_to > frameTo): tmp_to = frameTo;
				
				if(rd[c4d.RDATA_FRAMESTEP]>1):
					cmd += " -render \"" + pathProj.replace(fstr, rstr) + "\" -frame " + str(tmp_from) + " " + str(tmp_to) + " " + rd[c4d.RDATA_FRAMESTEP];
				else:
					cmd += " -render \"" + pathProj.replace(fstr, rstr) + "\" -frame " + str(tmp_from) + " " + str(tmp_to);
				if(takeName != ""):
					cmd += " -take \"" + takeName + "\"";
				
				children = {
					"name": "Frame " + str(tmp_from) + "-" + str(tmp_to),
					"priority": priority,
					"command": cmd,
					"tags": [ "single" ],
					"conditions": [
					{ 
						"type" : "client",
						"name": "group",
						"op": "==",
						"value": hqueue_clientGroup
					}
					]
				}
				job_spec["children"].append(children);
				tmp_from += framesPerJob;
	
	#print(job_spec);
	
	hq = xmlrpc.client.ServerProxy("http://" + hqueue_server);
	try:
	    hq.ping();
	except ConnectionRefusedError:
	    print("Unable to connect to HQueue server.");
	    return;
	
	hq.newjob(job_spec);
	return

class settings(gui.GeDialog):
	res = False;
	def CreateLayout(self):
		self.SetTitle("HQueue Submit v1.1");
		
		self.GroupBegin(10000, c4d.BFH_LEFT, 2);
		self.AddStaticText(1000, c4d.BFH_LEFT, 0, 0, 'Project path', c4d.BORDER_NONE);
		self.AddEditText(1001, c4d.BFH_LEFT, 500, 0);
		self.AddStaticText(1002, c4d.BFH_LEFT, 0, 0, 'Job Name', c4d.BORDER_NONE);
		self.AddEditText(1003, c4d.BFH_LEFT, 500, 0);
		self.AddStaticText(1004, c4d.BFH_LEFT, 0, 0, 'Start Frame', c4d.BORDER_NONE);
		self.AddEditNumber(1005, c4d.BFH_LEFT, 200, 0);
		self.AddStaticText(1006, c4d.BFH_LEFT, 0, 0, 'End Frame', c4d.BORDER_NONE);
		self.AddEditNumber(1007, c4d.BFH_LEFT, 200, 0);
		self.AddStaticText(1008, c4d.BFH_LEFT, 0, 0, 'Take name', c4d.BORDER_NONE);
		self.AddEditText(1009, c4d.BFH_LEFT, 500, 0);
		self.AddStaticText(1010, c4d.BFH_LEFT, 0, 0, 'Priority', c4d.BORDER_NONE);
		self.AddEditNumberArrows(1011, c4d.BFH_LEFT, 200, 0);
		
		self.AddStaticText(2000, c4d.BFH_LEFT, 0, 0, '', c4d.BORDER_NONE);
		self.AddStaticText(2000, c4d.BFH_LEFT, 0, 0, '', c4d.BORDER_NONE);
		
		self.AddStaticText(1020, c4d.BFH_LEFT, 0, 0, 'Frames per job', c4d.BORDER_NONE);
		self.AddEditNumberArrows(1021, c4d.BFH_LEFT, 200, 0);
		
		self.AddStaticText(2000, c4d.BFH_LEFT, 0, 0, '', c4d.BORDER_NONE);
		self.AddStaticText(2000, c4d.BFH_LEFT, 0, 0, '', c4d.BORDER_NONE);
		
		self.AddStaticText(1012, c4d.BFH_LEFT, 0, 0, '[Local]Path Replace(from)', c4d.BORDER_NONE);
		self.AddEditText(1013, c4d.BFH_LEFT, 500, 0);
		self.AddStaticText(1014, c4d.BFH_LEFT, 0, 0, '[NAS]Path Replace(to)', c4d.BORDER_NONE);
		self.AddEditText(1015, c4d.BFH_LEFT, 500, 0);
		self.AddStaticText(1016, c4d.BFH_LEFT, 0, 0, 'HQueue Server IP:Port', c4d.BORDER_NONE);
		self.AddEditText(1017, c4d.BFH_LEFT, 500, 0);
		self.AddStaticText(1018, c4d.BFH_LEFT, 0, 0, 'HQueue Client Group', c4d.BORDER_NONE);
		self.AddEditText(1019, c4d.BFH_LEFT, 500, 0);
		
		self.GroupEnd();
		self.AddDlgGroup(c4d.DLG_OK|c4d.DLG_CANCEL);
		return False;
	
	def AskClose(self):
		global pathProj, jobname, frameFrom, frameTo, takeName, priority, framesPerJob, fstr, rstr, hqueue_server, hqueue_clientGroup;
		pathProj = self.GetString(1001).replace("/", os.sep).replace("\\", os.sep);
		jobname = self.GetString(1003);
		frameFrom = self.GetInt32(1005);
		frameTo = self.GetInt32(1007);
		takeName = self.GetString(1009);
		priority = self.GetInt32(1011);
		framesPerJob = self.GetInt32(1021);
		fstr = self.GetString(1013).replace("/", os.sep).replace("\\", os.sep);
		rstr = self.GetString(1015).replace("/", os.sep).replace("\\", os.sep);
		hqueue_server = self.GetString(1017);
		hqueue_clientGroup = self.GetString(1019);
		
		if(priority > 10):
			priority = 10;
		
		d = {
			"fstr": fstr,
			"rstr": rstr,
			"hqueue_server": hqueue_server,
			"hqueue_clientGroup": hqueue_clientGroup,
			"framesPerJob": framesPerJob,
		}
		
		jf = open(os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + os.sep + 'c4dhqueue.json', 'w');
		json.dump(d, jf);
		jf.close();
		
		return False;
	
	def InitValues(self):
		self.SetString(1001, pathProj);
		self.SetString(1003, jobname);
		self.SetLong(1005, frameFrom);
		self.SetLong(1007, frameTo);
		self.SetLong(1011, priority);
		self.SetLong(1021, framesPerJob)
		self.SetString(1013, fstr.replace("/", os.sep).replace("\\", os.sep));
		self.SetString(1015, rstr.replace("/", os.sep).replace("\\", os.sep));
		
		self.SetString(1017, hqueue_server);
		self.SetString(1019, hqueue_clientGroup);
		
		return True;
	
	def Command(self, id, msg):
		if id == 1:
			self.res = True;
		if id == 1 or id == 2:
			self.Close();
		return True;

class errordialog(gui.GeDialog):
	def CreateLayout(self):
		self.SetTitle('HQueue Submit');
		self.AddStaticText(1026, c4d.BFH_SCALEFIT,300, 10, 'Project is not saved');
		self.AddButton(20001, c4d.BFH_SCALE, name='OK');
		return True;
	
	def Command(self, id, msg):
		if id==20001:
		  self.Close();
		return True;
	
def main():
	global pathProj, jobname, frameFrom, frameTo, takeName, priority, framesPerJob, fstr, rstr, hqueue_server, hqueue_clientGroup;
	pathProj = doc.GetDocumentPath()+'/'+doc.GetDocumentName();
	if doc.GetDocumentPath()=='':
		dlg = errordialog();
		dlg.Open(c4d.DLG_TYPE_MODAL);
		return True;
	
	if os.path.exists(os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + os.sep + 'c4dhqueue.json'):
		f = open(os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + os.sep + 'c4dhqueue.json', 'r');
		s = json.load(f);
		f.close();
		
		fstr = s["fstr"];
		rstr = s["rstr"];
		hqueue_server = s["hqueue_server"];
		hqueue_clientGroup = s["hqueue_clientGroup"];
		try:
			framesPerJob = int(s.get("framesPerJob"));
		except:
			framesPerJob = 1;
	
	pathProj = pathProj.replace("/", os.sep).replace("\\", os.sep);
	
	jobname = doc.GetDocumentName().replace(".c4d", "");
	rd = doc.GetActiveRenderData();
	fps = doc.GetFps();
	frameFrom = (rd[c4d.RDATA_FRAMEFROM]).GetFrame(fps);
	frameTo = (rd[c4d.RDATA_FRAMETO]).GetFrame(fps);
	
	dlg = settings();
	dlg.Open(c4d.DLG_TYPE_MODAL);
	if dlg.res:
		c4d.StopAllThreads();
		Execute();
	
if __name__=='__main__':
	main();
	c4d.EventAdd();
