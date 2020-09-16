#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
'''

#SQL Lib
import pyodbc
##PDF gen
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
#Utilizado solo para mostrar los logos.
from PIL import Image, ImageTk


server = '192.168.102.202' 
database = '_Datos' 
username = 'david' 
password = 'dgc1991' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

class Incidencia:
    def __init__(self,data):
        self.abonado = data[1]
        self.recepcion = data[18]
        self.procesado = data[8]
        self.observaciones = data[10]


'''Obtener el listado de estaciones del servidor
arg curs: instancia de cursor SQL
return abonados: diccionario compuesto de listas.
    Clave: cue_iid (convertida a STR)
    Contenido = lista con todos los datos del abonado'''
def getEstaciones(curs):
    abonados = {}
    abCount = 0

    curs.execute("SELECT * FROM [m_cuentas] where cue_clinea = 'OIL'") 
    row = curs.fetchone() 
    while row:
        abonados[str(row[0])] = row 
        row = curs.fetchone()
        abCount = abCount +1
    print("Numero de cuentas OIL: "+str(abCount))
    return abonados

'''Obtiene TODOS los eventos XX2 y los cruza con una lista de abonados para excluir
los que no pertenezcan a Plenoil
arg curs: instancia de cursor SQL
arg abDict: diccionario generado por la funcion getEstaciones. Contiene el dealer OIL
return [incidencias, excluidos]: Lista compuesta de dos listas. Una de incidencias
pertenecientes a Plenoil y otra de eventos excluidos'''
def getEvents(curs,abDict):
    incidencias = []
    excluidos = []
    numEventos = 0 #Numero de eventos xx2
    numPlen = 0 #Eventos filtrados
    curs.execute("SELECT * FROM [p_recepcion] where rec_calarma = 'XX2'") 
    row = curs.fetchone() 
    while row: 
        #print(row[0])
        try:
            if abDict[str(row[1])]:
                incidencias.append(row)
                numPlen = numPlen + 1
        except KeyError:
            excluidos.append(row)
        row = cursor.fetchone()
        numEventos = numEventos + 1
    print("XX2 sin filtrar: "+ str(numEventos))
    print("XX2 filtrados por OIL: "+ str(numPlen))
    return [incidencias, excluidos]


def createIncidencias(inc):
    incInstancias = []
    for item in inc:
        i = Incidencia(item)
        incInstancias.append(i)
    return incInstancias

c = canvas.Canvas("hello.pdf",pagesize=landscape(A4))

def hello(c):
    c.drawString(0,0,"hello world")

hello(c)
c.showPage()
c.save()


'''abonados = getEstaciones(cursor)
filtrados = getEvents(cursor,abonados)[0]
instancias = createIncidencias(filtrados)
for item in instancias:
    print(item.abonado)
    print(item.observaciones)
'''