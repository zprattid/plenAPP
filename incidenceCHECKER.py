# -*- coding: utf-8 -*-

import os

incPATH = '\\\\192.168.102.5\\t. de noche\\PLENOIL INCIDENCIA'
files = os.listdir(incPATH)
cFiles = []
for i in files:
	#print(i[-4:])
	if i[-4:] == ".pdf":
		cFiles.append(i)
		print(i)
input()
