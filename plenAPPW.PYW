#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
plenAPP

Aplicación diseñada para hacer de interfaz entre las incidencias generadas
en SoftGuard para el cliente Plenoil. Automatiza tareas de escritura en 
excels de control y el envío de correo de las mencionadas incidencias a
los coordinadores correspondientes.

Esta aplicación está cedida temporalmente a DIAMOND SEGURIDAD S.L.
PROPIEDAD DE D.GOMEZ CALLES
Todos los derechos reservados.'''
#Librería de interfaz
from tkinter import *
from tkinter import filedialog
from tkinter.font import Font
from tkinter import messagebox
from tkinter import ttk

#Archivos de configuracion y modulos personalizados.
from configuraciones import *
#from configDEBUG import *
from plenFLUX import plenFLUX

#Utilizado solo para mostrar los logos.
from PIL import Image, ImageTk

#Utilizado para extraer fecha y hora automaticamente para las incidencias.
from datetime import datetime

#Librería para escribir en los excel.
from openpyxl import load_workbook

#Librería SMTP para el envio de los correos.
import smtplib
import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.encoders import encode_base64

##Librerías necesarias para extraer datos del PDF
from tika import parser
import re

class Aplicacion():
	''' Clase monolitica que encapsula la interfaz y las funciones necesarias para su
	correcto desarrollo.'''
	def __init__(self):
		''' Creación de la interfaz y todas sus variables asociadas'''
		self.raiz = Tk()
		self.raiz.geometry('') 		#La línea de geometría sin definir ningún tamaño hace que la interfaz sea autoadaptable.
		self.fontTITLE = Font(size = 30)
		self.font = Font(size = 16)
		buttStyle = ttk.Style()
		buttStyle.configure("size.TButton", font = ("Helvetica",16))
		self.raiz.configure(bg = 'white')
		self.raiz.title('Incidencias plenoil')
		self.status = None	#Esta variable sirve para determinar si se ha elegido SI o NO en llamada, para evitar que los operadores la lien.
		self.stationName = "" #Variable necesaria al automatizar la eleccion de estación.
		self.adjunto = None #Variable que almacena el archivo adjunto
		##################
		##LOGOS y TITULO##
		##################
		diamondLOGO = ImageTk.PhotoImage(Image.open("logodiamond.png").resize((120,120)))
		plenoilLOGO = ImageTk.PhotoImage(Image.open("logoplenoil.png").resize((120,120)))
		self.diamondLOGO = ttk.Label(self.raiz, image = diamondLOGO)
		self.diamondLOGO.grid(column=5, row = 0, columnspan = 2)
		self.plenoilLOGO = ttk.Label(self.raiz, image = plenoilLOGO)
		self.plenoilLOGO.grid(column=0, row = 0, columnspan = 2)
		self.titleLABEL = ttk.Label(self.raiz, text= "INCIDENCIAS PLENOIL", font = self.fontTITLE)
		self.titleLABEL.grid(column = 2, row = 0, columnspan = 3)
		##############################
		##BOTONES DE LLAMADA Y ENVIO##
		##############################
		self.callLABEL = ttk.Label(self.raiz, text= "¿HAY LLAMADA?", font = self.font)
		self.yesBUTTON = ttk.Button(self.raiz, text="SI",
									command=self.showCALL, style = "size.TButton")
		self.noBUTTON = ttk.Button(self.raiz, text="NO",
								   command=self.showNOCALL, style = "size.TButton")
		self.sendBUTTON = ttk.Button(self.raiz, text="ENVIAR",
										command=self.sendIncidencia, style = "size.TButton")
		self.adjBUTTON = ttk.Button(self.raiz, text="ADJUNTAR",
										command=self.adjuntar, style = "size.TButton")
		self.incNAME = ttk.Label(self.raiz, text="", font = self.font)
		########################
		##SECCION "LLAMADA DE"##
		########################
		self.DEllamadaLABEL = ttk.Label(self.raiz, text="LLAMADA DE", font = self.font)
		self.DEllamadaVAR = StringVar(self.raiz)
		self.DEllamadaVAR.set("cliente")
		self.DEllamadaMENU = OptionMenu(self.raiz, self.DEllamadaVAR, *llamadas)        
		self.DEllamadaMENU.config(font = self.font) 
		########################       
		##SECCCION "INCIDENCIA##
		########################
		self.incidenciaLABEL = ttk.Label(self.raiz, text="INCIDENCIA", font = self.font)
		self.incidenciaVAR = StringVar(self.raiz)
		self.incidenciaVAR.set("cheque")
		self.incidenciaMENU = OptionMenu(self.raiz, self.incidenciaVAR, *incidencias)
		self.incidenciaMENU.config(font = self.font)
		self.incidenciaOTRO = ttk.Entry(self.raiz)
		self.incidenciaVAR.trace("w", self.checkOTRO)
		########################
		##SECCION "RESOLUCION"##
		########################
		self.resolucionLABEL = ttk.Label(self.raiz, text="RESOLUCION", font = self.font)
		self.resolucionVAR = StringVar(self.raiz)
		self.resolucionVAR.set("apertura manual")
		self.resolucionMENU = OptionMenu(self.raiz, self.resolucionVAR, *resoluciones)
		self.resolucionMENU.config(font = self.font)
		self.resolucionOTRO = ttk.Entry(self.raiz)
		self.resolucionVAR.trace("w", self.checkOTRO)       
		#########################
		##SECCION "SOLUCIONADO"##
		#########################
		self.solucionLABEL = ttk.Label(self.raiz, text="SOLUCIONADO", font = self.font)
		self.solucionVAR = StringVar(self.raiz)
		self.solucionVAR.set("si")
		self.solucionMENU = OptionMenu(self.raiz, self.solucionVAR, *bools)       
		self.solucionMENU.config(font = self.font)      
		#################################
		##SECCION "TELEFONO DE GUARDIA"##
		#################################
		self.tlfLABEL = ttk.Label(self.raiz, text="TELEFONO GUARDIA", font = self.font)
		self.tlfVAR = StringVar(self.raiz)
		self.tlfVAR.set("no")
		self.tlfMENU = OptionMenu(self.raiz, self.tlfVAR, *bools) 
		self.tlfMENU.config(font = self.font)
		###########################
		##SECCION "OBSERVACIONES"##
		###########################
		self.obsLABEL = ttk.Label(self.raiz, text="OBSERVACIONES", font = self.font)
		self.obsVAR = ttk.Entry(self.raiz)
		##################################
		##SECCION "TIEMPO DE RESOLUCION"##
		##################################
		self.tiempoLABEL = ttk.Label(self.raiz, text="TIEMPO DE RESOLUCION", font = self.font)
		self.tiempoVAR = ttk.Entry(self.raiz)
		self.tiempoAPROX = ttk.Label(self.raiz, text="", font = self.font)
		####################################
		##DISPOSICION INTERFAZ BASICA FIJA##
		####################################
		self.callLABEL.grid(column = 2, row = 1, columnspan = 3)
		self.yesBUTTON.grid(column = 2, row = 2, pady = 20)
		self.noBUTTON.grid(column = 4, row = 2, pady = 20)
		self.adjBUTTON.grid(column=1, row = 11, columnspan = 3, pady = 20)
		self.sendBUTTON.grid(column=3, row = 11, columnspan = 3, pady = 20)
		self.incNAME.grid(column = 2, row = 12, columnspan = 3, pady = 20)
		########
		##MENU##
		########
		'''self.menu = Menu(self.raiz)
		self.raiz.config(menu=self.menu)
		self.admin = Menu(self.menu, tearoff=0)
		self.help = Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Administracion", menu=self.admin)
		self.menu.add_cascade(label="Ayuda", menu=self.help)
		self.admin.add_command(label="Estaciones", command=self.estacionesWindow)
		self.admin.add_command(label="Incidencias", command=self.incidenciasWindow)
		self.admin.add_command(label="Resoluciones", command=self.resolucionesWindow)
		self.admin.add_command(label="Poner en copia...", command=self.copiaWindow)
		self.help.add_command(label="Instrucciones de uso")
		self.help.add_command(label="Acerca de...")'''
		##INICIO DEL BUCLE PRINCIPAL##
		#configActions.checkCopyFECHA()
		self.raiz.mainloop()
	def showCALL(self):
		'''Esta función crea la interfaz necesaria para rellenar una incidencia en excel'''
		##DISPOSICION "LLAMADA DE"
		self.DEllamadaLABEL.grid(column = 2, row = 3, columnspan = 3, pady = 20)
		self.DEllamadaMENU.grid(column = 2, row = 4, columnspan = 3)
		##DISPOSICION "INCIDENCIA"
		self.incidenciaLABEL.grid(column = 0, row = 3, columnspan = 2, pady = 20)
		self.incidenciaMENU.grid(column = 0, row = 4, columnspan = 2)
		##DISPOSICION "RESOLUCION"
		self.resolucionLABEL.grid(column = 5, row = 3, columnspan = 2, pady = 20)
		self.resolucionMENU.grid(column = 5, row = 4, columnspan = 2)
		##DISPOSICION "SOLUCION"
		self.solucionLABEL.grid(column = 0, row = 6, columnspan = 2, pady = 20)
		self.solucionMENU.grid(column = 0, row = 7, columnspan = 2)
		##DISPOSICION "TELEFONO DE GUARDIA"
		self.tlfLABEL.grid(column = 5, row = 6, columnspan = 2, pady = 20)
		self.tlfMENU.grid(column = 5, row = 7, columnspan = 2)
		##DISPOSICION "OBSERVACIONES"
		self.obsLABEL.grid(column = 2, row = 6, columnspan = 3)
		self.obsVAR.grid(column = 2, row = 7, columnspan = 3 )
		##DISPOSICION "TIEMPO DE RESOLUCION"
		self.tiempoLABEL.grid(column = 2, row = 8, columnspan = 3)
		self.tiempoVAR.grid(column = 2, row = 10, columnspan = 3)
		self.tiempoAPROX.grid(column = 2, row = 9, columnspan = 3)
		##Determinación de la variable STATUS
		self.status = True
	def showNOCALL(self):
		'''Esta función elimina todos los elementos no necesarios al no haber
		llamada. Para no confundirse con la interfaz básica de inicio, también
		muestra un mensaje de información sobre lo que el operador tiene que hacer'''
		self.DEllamadaLABEL.grid_forget()
		self.DEllamadaMENU.grid_forget()
		self.incidenciaLABEL.grid_forget()
		self.incidenciaMENU.grid_forget()
		self.incidenciaOTRO.grid_forget()
		self.resolucionLABEL.grid_forget()
		self.resolucionMENU.grid_forget()
		self.resolucionOTRO.grid_forget()
		self.solucionLABEL.grid_forget()
		self.solucionMENU.grid_forget()
		self.tlfLABEL.grid_forget()
		self.tlfMENU.grid_forget()
		self.obsLABEL.grid_forget()
		self.obsVAR.grid_forget()
		self.tiempoLABEL.grid_forget()
		self.tiempoVAR.grid_forget()
		##IMPORTANTE, determinacion de la variable STATUS.
		self.status = False
		messagebox.showinfo("NO HAY LLAMADA","PULSA ADJUNTAR Y ENVIAR")
	def checkOTRO(self, *args):
		'''Función que muestra cuadros de texto cuando se selecciona "otro"
		en incidencias o resoluciones. Se hace para poder especificar incidencias
		fuera de las listas predefinidas.'''
		if args[0] == "PY_VAR1": ##Esto podría cambiar si se modifica la interfaz
			if self.incidenciaVAR.get() == "otra incidencia":
				self.incidenciaOTRO.grid(column = 0, row = 5, columnspan =2)
			else:
				self.incidenciaOTRO.grid_forget()
		elif args[0] == "PY_VAR2": ##Esto podria cambiar si se modifica la interfaz
			if self.resolucionVAR.get() == "otra resolucion":
				self.resolucionOTRO.grid(column = 5, row = 5, columnspan =2)
			else:
				self.resolucionOTRO.grid_forget()
	def checkEstacionNAME(self):
		'''Función de control. Extra el nombre del archivo adjunto y lo 
		compara con la lista de estaciones definida en "configuraciones.py".'''
		## Se localiza el nombre en la ruta del archivo
		indName = self.adjunto.name.split("PLENOIL ")
		realNAME = indName[-1][0:-4]
		self.stationName = realNAME.lower()
		print("Nombre extraido: "+realNAME)
		## Se comparan el nombre de la entrada y la incidencia.
		try:
			estaciones[realNAME.lower()]#Importante convertir a minusculas
			print("Estación en el listado")
			if self.stationName in copyTOestefania:
				print("Mensaje en copia a ESTEFANIA")
			elif self.stationName in copyTOalberto:
				print("Mensaje en copia a ALBERTO")
			elif self.stationName in copyTOjavier:
				print("Mensaje en copia a JAVIER")
			elif self.stationName in copyTOpatricia:
				print("Mensaje en copia a PATRICIA")
			else:
				print("Mensaje SIN copia")
			return True
		except KeyError:
			print("Estación no esta en el listado")
			return False
	def calculateTIME(self):
		file_data = parser.from_file(self.adjunto.name)
		text = file_data['content']
		tPrint = ""
		dPrint = ""
		datetimeArray = []
		for line in text.split("\n"):
			if line is not "":
				if tPrint == "":
					hora = re.search(r'\d\d:\d\d:\d\d',line)
					try:
						tPrint = hora.group()[:-3]
					except AttributeError:
						pass
				if dPrint == "":
					fecha = re.search(r'\d\d/\d\d/\d\d\d\d',line)
					try:
						dPrint = fecha.group()
					except AttributeError:
						pass
				if line[0] == "[":
					fecha = line[1:11].split("/")
					#print(fecha)
					hora = line[12:17].split(":")
					#print(hora)
					for i in range(len(fecha)):
						fecha[i] = int(fecha[i])
					for i in range(len(hora)):
						hora[i] = int(hora[i])
					dat = datetime(fecha[2],fecha[1],fecha[0],hora[0],hora[1])
					datetimeArray.append(dat)
		startD = dPrint.split("/")
		startT = tPrint.split(":")
		for i in range(len(startD)):
			startD[i] = int(startD[i])
		for i in range(len(startT)):
			startT[i] = int(startT[i])
		startDATE = datetime(startD[2],startD[1],startD[0],startT[0],startT[1])
		endDATE = datetimeArray[-1]
		elapsed = endDATE-startDATE
		return "Calculado: "+str(elapsed.seconds//60)
	def printIncidencia(self):
		'''Genera la cadena de incidencia que será impresa en el excel.
		Efectua esta operación leyendo el pdf y buscando la hora de creacion
		del evento.
		También coge los valores de las variables de interfaz y luego lo 
		ordena todo en el formato requerido por el excel.'''
		##Procesado de fecha y hora
		file_data = parser.from_file(self.adjunto.name)
		text = file_data['content']
		tPrint = ""
		dPrint = ""
		for line in text.split("\n"):
			if line is not "":
				if tPrint == "":
					hora = re.search(r'\d\d:\d\d:\d\d',line)
					try:
						tPrint = hora.group()[:-3]
					except AttributeError:
						pass
				if dPrint == "":
					fecha = re.search(r'\d\d/\d\d/\d\d\d\d',line)
					try:
						dPrint = fecha.group()
					except AttributeError:
						pass
		##Procesado de posibles incidencias y resoluciones OTRO
		inci = self.incidenciaVAR.get().upper()
		reso = self.resolucionVAR.get().upper()
		if self.incidenciaVAR.get() == "otra incidencia":
			inci = self.incidenciaOTRO.get()
		if self.resolucionVAR.get() == "otra resolucion":
			reso = self.resolucionOTRO.get()
		##Añadido de la parte cheque
		anulado = ""
		numCHEQUE = ""
		if reso.lower() == "apertura manual" and inci.lower() == "cheque no impreso":
			anulado = "NO"
			numCHEQUE = "-"
		##Devolucion de la incidencia
		return[self.stationName.upper(),dPrint,tPrint
			,self.DEllamadaVAR.get().upper(),inci, reso,self.solucionVAR.get().upper()
			,self.tlfVAR.get().upper(),self.obsVAR.get().upper(),anulado,numCHEQUE
			,self.tiempoVAR.get()]
	def sendMail(self):
		'''Proceso para enviar el correo con la incidencia a los coordinadores
		correspondientes. Genera el correo electrónico y adjunta el archivo
		elegido.'''
		nameIND = self.adjunto.name.rfind("/")
		name = self.adjunto.name[nameIND+1: -4]
		subject = name
		message = MIMEMultipart()

		message['Subject'] = name
		message['From'] = senderCONFIG["user"]
		message['Reply-to'] = senderCONFIG["user"]
		
		if self.stationName in copyTOestefania:
			message['To'] = correos[estaciones[self.stationName]]+","+correoMARCOS+","+correoSALA+","+correos["estefania"]
			print("Mensaje en copia a ESTEFANIA")
		elif self.stationName in copyTOalberto:
			message['To'] = correos[estaciones[self.stationName]]+","+correoMARCOS+","+correoSALA+","+correos["alberto"]
			print("Mensaje en copia a ESTEFANIA")
		elif self.stationName in copyTOjavier:
			message['To'] = correos[estaciones[self.stationName]]+","+correoMARCOS+","+correoSALA+","+correos["javier"]
			print("Mensaje en copia a ESTEFANIA")
		elif self.stationName in copyTOpatricia:
			message['To'] = correos[estaciones[self.stationName]]+","+correoMARCOS+","+correoSALA+","+correos["patricia"]
			print("Mensaje en copia a PATRICIA")
		else:
			message['To'] = correos[estaciones[self.stationName]]+","+correoMARCOS+","+correoSALA
			print("Mensaje SIN copia")

		text = MIMEText(name)
		
		with open(self.adjunto.name, "rb") as opened:
			openedfile = opened.read()
		attachedfile = MIMEApplication(openedfile, _subtype = "pdf", _encoder = encode_base64)
		attachedfile.add_header('content-disposition', 'attachment', filename = name)
		body = name
		message.attach(text)
		message.attach(attachedfile)
		try:
			server = smtplib.SMTP(senderCONFIG["server"], senderCONFIG["port"])
			print("Conexion con Servidor correcta")
			#server.ehlo()
			server.login(senderCONFIG["user"], senderCONFIG["pass"])
			print("Login en servidor correcto")
			if self.stationName in copyTOestefania:
				server.sendmail(message['From'], [message['To'],correoMARCOS,correoSALA,correos["estefania"]], message.as_string())
			elif self.stationName in copyTOalberto:
				server.sendmail(message['From'], [message['To'],correoMARCOS,correoSALA,correos["alberto"]], message.as_string())
			elif self.stationName in copyTOjavier:
				server.sendmail(message['From'], [message['To'],correoMARCOS,correoSALA,correos["javier"]], message.as_string())
			elif self.stationName in copyTOpatricia:
				server.sendmail(message['From'], [message['To'],correoMARCOS,correoSALA,correos["patricia"]], message.as_string())
			else:
				server.sendmail(message['From'], [message['To'],correoMARCOS,correoSALA], message.as_string())
			print('Email Enviado')			
			server.close()
			print("Conexion con Servidor cerrada")
		except:
			print('Algo ha ocurrido. EMAIL NO ENVIADO')
			messagebox.showerror("ERROR","NO SE HA ENVIADO EL EMAIL")
	def adjuntar(self):
		'''Proceso básico que une todas las funciones anteriores. Hace todas
		las comprobaciones necesarias para asegurar que la incidencia se
		escribe donde corresponde y se envia a quien corresponde.'''
		self.adjunto = filedialog.askopenfile(initialdir="\\\\192.168.102.5\\t. de noche", parent=self.raiz,mode='rb',title='Examinar...')
		self.incNAME["text"] = self.adjunto.name.split("/")[-1]
		self.tiempoAPROX["text"] = self.calculateTIME()
		self.checkEstacionNAME()
	def sendIncidencia(self):
		if self.adjunto == None:
			messagebox.showerror("ERROR","NO HAY INCIDENCIA ADJUNTA")
		else:
			#print(adjunto.name)
			if self.status == True:
				if self.checkEstacionNAME() == True:
					print(self.printIncidencia())
					print("Incidencia Coincide con Estaciones")
					row = self.printIncidencia()
					coord = estaciones[self.stationName]
					worksheet = excelSHEETS[coord]
					try:
						wb = load_workbook(excelNAME)
						ws = wb.worksheets[worksheet]
						ws.append(row)
						wb.save(excelNAME)
						self.sendMail()
						if self.stationName in copyTOestefania:
							messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
												+correos[coord]+ ",estefania.ruiz@plenoil.es, "+correoMARCOS+" Y "+correoSALA)
						elif self.stationName in copyTOalberto:
							messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
												+correos[coord]+ ",alberto.sanchez@plenoil.es, "+correoMARCOS+" Y "+correoSALA)
						elif self.stationName in copyTOjavier:
							messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
												+correos[coord]+ ",javier.garcia@plenoil.es, "+correoMARCOS+" Y "+correoSALA)
						elif self.stationName in copyTOpatricia:
							messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
												+correos[coord]+ ",patricia.ferreiro@plenoil.es, "+correoMARCOS+" Y "+correoSALA)
						else:
							messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
												+correos[coord]+", "+correoMARCOS+" Y "+correoSALA)
					except PermissionError:
						messagebox.showerror("ERROR","EXCEL ABIERTO. CIERRA EXCEL Y REINICIA LA APLICACION")
				else:
					messagebox.showerror("ERROR","NOMBRE DE LA ESTACION NO ESTA EN LISTA")
			elif self.status == False:
				if self.checkEstacionNAME() == True:
					self.sendMail()
					coord = estaciones[self.stationName]
					if self.stationName in copyTOestefania:
						messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
											+correos[coord]+ ",estefania.ruiz@plenoil.es, "+correoMARCOS+" Y "+correoSALA)
					elif self.stationName in copyTOalberto:
						messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
											+correos[coord]+ ",alberto.sanchez@plenoil.es, "+correoMARCOS+" Y "+correoSALA)
					elif self.stationName in copyTOjavier:
						messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
											+correos[coord]+ ",javier.garcia@plenoil.es, "+correoMARCOS+" Y "+correoSALA)
					elif self.stationName in copyTOpatricia:
						messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
											+correos[coord]+ ",patricia.ferreiro@plenoil.es, "+correoMARCOS+" Y "+correoSALA)
					else:
						messagebox.showinfo("INCIDENCIA CORRECTA","AÑADIDO AL REGISTRO. ENVIADO A "
											+correos[coord]+", "+correoMARCOS+" Y "+correoSALA)
				else:
					messagebox.showerror("ERROR","NOMBRE DE LA ESTACION NO ESTA EN LISTA")
	def showCopyTO(self):
		src = configActions.readConfig()
		for line in src:
			if "copyTOestefania" in line:
				#print(line)
				start = line.find("[")
				stations = line[start+1:-2].split(",")
				curedSTA = []
				for station in stations:
					curedSTA.append(station[1:-1])
				stationSTRING = ""
				for STA in curedSTA:
					if STA == curedSTA[-1]:
						stationSTRING = stationSTRING+STA
					else:
						stationSTRING = stationSTRING+STA+","
				self.estefVAR.insert(0,stationSTRING)
			elif "copyTOalberto" in line:
				#print(line)
				start = line.find("[")
				stations = line[start+1:-2].split(",")
				curedSTA = []
				for station in stations:
					curedSTA.append(station[1:-1])
				stationSTRING = ""
				for STA in curedSTA:
					stationSTRING = stationSTRING+STA+","
				self.alberVAR.insert(0,stationSTRING)
			elif "copyTOjavier" in line:
				#print(line)
				start = line.find("[")
				stations = line[start+1:-2].split(",")
				curedSTA = []
				for station in stations:
					curedSTA.append(station[1:-1])
				stationSTRING = ""
				for STA in curedSTA:
					stationSTRING = stationSTRING+STA+","
				self.javieVAR.insert(0,stationSTRING)
		self.EdiaVAR.set(copyFECHA.day)
		self.EmesVAR.set(copyFECHA.month)
	def saveCopyTO(self):
		copyDICT = {"copyTOestefania": None,
					"copyTOalberto": None,
					"copyTOjavier": None
					}
		for ind,val in enumerate(copyDICT):
			if val == "copyTOestefania":
				rawStr = self.estefVAR.get()
			elif val == "copyTOalberto":
				rawStr = self.alberVAR.get()
			elif val == "copyTOjavier":
				rawStr = self.javieVAR.get()
			splitStr = rawStr.split(",")
			commedARR = []
			for i in splitStr:
				commedARR.append('"'+i+'"')
			finalStr = val+"=["
			for i in commedARR:
				if i == commedARR[-1]:
					finalStr = finalStr+i+"]\n"
				else:
					finalStr = finalStr+i+","
			copyDICT[val] = finalStr
		configActions.writeCopyTO(copyDICT)
	def estacionesWindow(self):
		print("Abriendo Menu Estaciones")
		self.estSettings = Toplevel(self.raiz)
		self.estSettings.geometry('') #Autoajustable
		self.estSettings.title("Configuracion estaciones")
		##Lista de estaciones
		self.estacionLABEL = ttk.Label(self.estSettings, text="Estaciones", font = self.font)
		self.estacionVAR = StringVar(self.estSettings)
		self.estacionMENU = OptionMenu(self.estSettings, self.estacionVAR, *estaciones)        
		self.estacionMENU.config(font = self.font)
		self.deleteBUT =  ttk.Button(self.estSettings, text="ELIMINAR", style = "size.TButton")
		self.estacionLABEL.grid(column = 1, row = 1, columnspan = 3)
		self.estacionMENU.grid(column = 1, row = 2, columnspan = 3)
		self.deleteBUT.grid(column = 1, row = 3, columnspan = 3)
		##Añadir
		self.nameLABEL = ttk.Label(self.estSettings, text="NOMBRE", font = self.font)
		self.nameVAR = ttk.Entry(self.estSettings)
		self.respLABEL = ttk.Label(self.estSettings, text="RESPONSABLE", font = self.font)
		self.respVAR = ttk.Entry(self.estSettings)
		self.addBUT =  ttk.Button(self.estSettings, text="AÑADIR", style = "size.TButton")
		self.nameLABEL.grid(column = 4, row = 1, columnspan = 1)
		self.nameVAR.grid(column = 5, row = 1, columnspan = 2)
		self.respLABEL.grid(column = 4, row = 2, columnspan = 1)
		self.respVAR.grid(column = 5, row = 2, columnspan = 2)
		self.addBUT.grid(column = 4, row = 3, columnspan = 3)
	def incidenciasWindow(self):
		print("Abriendo Menu Incidencias")
		self.estSettings = Toplevel(self.raiz)
		self.estSettings.geometry('') #Autoajustable
		self.estSettings.title("Configuracion Incidencias")
		##Lista de estaciones
		self.estacionLABEL = ttk.Label(self.estSettings, text="INCIDENCIAS", font = self.font)
		self.estacionVAR = StringVar(self.estSettings)
		self.estacionMENU = OptionMenu(self.estSettings, self.estacionVAR, *incidencias)        
		self.estacionMENU.config(font = self.font)
		self.deleteBUT =  ttk.Button(self.estSettings, text="ELIMINAR", style = "size.TButton")
		self.estacionLABEL.grid(column = 1, row = 1, columnspan = 3)
		self.estacionMENU.grid(column = 1, row = 2, columnspan = 3)
		self.deleteBUT.grid(column = 1, row = 3, columnspan = 3)
		##Añadir
		self.nameLABEL = ttk.Label(self.estSettings, text="NOMBRE", font = self.font)
		self.nameVAR = ttk.Entry(self.estSettings)
		self.addBUT =  ttk.Button(self.estSettings, text="AÑADIR", style = "size.TButton")
		self.nameLABEL.grid(column = 4, row = 1, columnspan = 2)
		self.nameVAR.grid(column = 4, row = 2, columnspan = 2)
		self.addBUT.grid(column = 4, row = 3, columnspan = 3)
	def resolucionesWindow(self):
		print("Abriendo Menu Resoluciones")
		self.estSettings = Toplevel(self.raiz)
		self.estSettings.geometry('') #Autoajustable
		self.estSettings.title("Configuracion Resoluciones")
		##Lista de estaciones
		self.estacionLABEL = ttk.Label(self.estSettings, text="RESOLUCIONES", font = self.font)
		self.estacionVAR = StringVar(self.estSettings)
		self.estacionMENU = OptionMenu(self.estSettings, self.estacionVAR, *resoluciones)        
		self.estacionMENU.config(font = self.font)
		self.deleteBUT =  ttk.Button(self.estSettings, text="ELIMINAR", style = "size.TButton")
		self.estacionLABEL.grid(column = 1, row = 1, columnspan = 3)
		self.estacionMENU.grid(column = 1, row = 2, columnspan = 3)
		self.deleteBUT.grid(column = 1, row = 3, columnspan = 3)
		##Añadir
		self.nameLABEL = ttk.Label(self.estSettings, text="NOMBRE", font = self.font)
		self.nameVAR = ttk.Entry(self.estSettings)
		self.addBUT =  ttk.Button(self.estSettings, text="AÑADIR", style = "size.TButton")
		self.nameLABEL.grid(column = 4, row = 1, columnspan = 2)
		self.nameVAR.grid(column = 4, row = 2, columnspan = 2)
		self.addBUT.grid(column = 4, row = 3, columnspan = 3)
	def copiaWindow(self):
		print("Abriendo Menu Copia a...")
		self.estSettings = Toplevel(self.raiz)
		self.estSettings.geometry('') #Autoajustable
		self.estSettings.title("Configuracion Envio de copias")
		##Lista de estaciones
		self.estefLABEL = ttk.Label(self.estSettings, text="ESTEFANIA", font = self.font)
		self.estefVAR = ttk.Entry(self.estSettings, width = 50)
		self.alberLABEL = ttk.Label(self.estSettings, text="ALBERTO", font = self.font)
		self.alberVAR = ttk.Entry(self.estSettings, width = 50)
		self.javieLABEL = ttk.Label(self.estSettings, text="JAVIER", font = self.font)
		self.javieVAR = ttk.Entry(self.estSettings, width = 50)
		dia = []
		for i in range(31):
			dia.append(i+1)
		mes = []
		for i in range(12):
			mes.append(i+1)
		self.SLABEL = ttk.Label(self.estSettings, text="DESDE", font = self.font)
		self.SdiaVAR = StringVar(self.estSettings)
		self.SdiaMENU = OptionMenu(self.estSettings, self.SdiaVAR, *dia)        
		self.SdiaMENU.config(font = self.font)
		self.SmesVAR = StringVar(self.estSettings)
		self.SmesMENU = OptionMenu(self.estSettings, self.SmesVAR, *mes)        
		self.SmesMENU.config(font = self.font)
		self.ELABEL = ttk.Label(self.estSettings, text="HASTA", font = self.font)
		self.EdiaVAR = StringVar(self.estSettings)
		self.EdiaMENU = OptionMenu(self.estSettings, self.EdiaVAR, *dia)        
		self.EdiaMENU.config(font = self.font)
		self.EmesVAR = StringVar(self.estSettings)
		self.EmesMENU = OptionMenu(self.estSettings, self.EmesVAR, *mes)        
		self.EmesMENU.config(font = self.font)
		self.saveBUT =  ttk.Button(self.estSettings, text="GUARDAR", style = "size.TButton", command = self.saveCopyTO)
		self.showBUT =  ttk.Button(self.estSettings, text="MOSTRAR", style = "size.TButton", command=self.showCopyTO)
		self.estefLABEL.grid(column = 1, row = 1, columnspan = 1)
		self.alberLABEL.grid(column = 1, row = 2, columnspan = 1)
		self.javieLABEL.grid(column = 1, row = 3, columnspan = 1)
		self.estefVAR.grid(column = 2, row = 1, columnspan = 4)
		self.alberVAR.grid(column = 2, row = 2, columnspan = 4)
		self.javieVAR.grid(column = 2, row = 3, columnspan = 4)
		self.SLABEL.grid(column = 1, row = 4, columnspan = 1)
		self.SdiaMENU.grid(column = 2, row = 4, columnspan = 1)
		self.SmesMENU.grid(column = 3, row = 4, columnspan = 1)
		self.saveBUT.grid(column = 5, row = 4, columnspan = 1)
		self.ELABEL.grid(column = 1, row = 5, columnspan = 1)
		self.EdiaMENU.grid(column = 2, row = 5, columnspan = 1)
		self.EmesMENU.grid(column = 3, row = 5, columnspan = 1)
		self.showBUT.grid(column = 5, row = 5, columnspan = 1)
		
class configActions():
	def checkCopyFECHA():
		global copyFECHA, copyTOalberto,copyTOestefania, copyTOjavier
		if copyFECHA <= datetime.now():
			copyTOalberto = []
			copyTOestefania = []
			copyTOjavier = []
			copyTOpatricia = []
			copyFECHA = None
			print("Limpiando copias")
	def readConfig():
		confSRC = open("configuraciones.py")
		confCONT = []
		for line in confSRC.readlines():
			if line is not "/n":
				confCONT.append(line)
		confSRC.close()
		return confCONT
	def writeCopyTO(copyDICT):
		##VA FUNCIONANDO, HAY QUE PULIR
		src = configActions.readConfig()
		srcMOD = []
		for line in src:
			modLine = line
			for ind, val in enumerate(copyDICT):
				if val in line:
					modLine = copyDICT[val]
			srcMOD.append(modLine)
		conf = open("configuraciones.py","w")
		for line in srcMOD:
			conf.write(line)
			#print(line)
		conf.close()

def incidenceChecker():
	pass

def main():
	#flux = plenFLUX()
	#flux.CurrentWrite()
	configActions.checkCopyFECHA()
	mi_app = Aplicacion()
	return 0


if __name__ == '__main__':
	main()
