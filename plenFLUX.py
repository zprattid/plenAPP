import re
from openpyxl import load_workbook
import os
import datetime

class plenFLUX:
	def __init__(self):
		self.excelPATH = "\\\\192.168.102.5\\t. de noche\\EXCEL PLENOIL\\"
		self.excelNAME = "Flujo de clientes.xlsx"
		self.paths = []
		files = os.listdir(self.excelPATH)
		for i in files:
			if "INCIDENCIAS PLENOIL" in i:
				self.paths.append(i)
		#print(self.paths)
		self.ranges = 3 #leer columna c
	def _genGroup(self):
		groups = {"total": 0}
		for i in range(24):
			if i <10:
				groups["0"+str(i)] = []
			else:
				groups[str(i)] = []
		return groups
	def _reader(self,path,groups):
		#print(path)
		wb = load_workbook(filename = self.excelPATH+path)
		#print(wb.worksheets)
		for i in range(self.ranges):
			ws = wb.worksheets[i]
			#print(ws)
			#print(i)
			col = ws["C"]
			#print(len(col))
			for x in range(len(col)):
				#print(str(type(col[x].value))+"||"+str(col[x].value))
				if type(col[x].value) == str:
					hora = re.search(r'\d\d:\d\d',col[x].value)
					try:
						if hora.group():
							#print(hora.group().split(":"))
							groups["total"] = groups["total"] +1
							Shora = hora.group().split(":")[0]
							groups[Shora].append(hora.group())
					except:
						#print(str(type(col[x].value))+"||"+str(col[x].value))
						pass
				elif type(col[x].value) == datetime.time:
					groups["total"] = groups["total"] +1
					hora = col[x].value.hour
					if hora < 10:
						groups["0"+str(hora)].append("0"+str(hora)+":"+str(col[x].value.minute))
					else:
						groups[str(hora)].append(str(hora)+":"+str(col[x].value.minute))
	def _FULLreader(self,groups):
		for FILE in self.paths:
			self._reader(FILE,groups)
	def _Percentager(self,cant, tot):
		return round((cant/tot)*100,2)
	def _xlsWriter(self,path,dic):
		wb = load_workbook(self.excelPATH+self.excelNAME)
		#print(path == "INCIDENCIAS PLENOIL.xlsx")
		if path == "INCIDENCIAS PLENOIL.xlsx":
			month = datetime.datetime.now().month
			ws = wb.worksheets[month]
		elif path == 0:
			ws = wb.worksheets[0]
		elif "MARZO" in path:
			ws = wb.worksheets[3]
		elif "ABRIL" in path:
			ws = wb.worksheets[4]
		elif "MAYO" in path:
			ws = wb.worksheets[5]
		elif "JUNIO" in path:
			ws = wb.worksheets[6]
		elif "JULIO" in path:
			ws = wb.worksheets[7]
		elif "AGOSTO" in path:
			ws = wb.worksheets[8]
		elif "SEPTIEMBRE" in path:
			ws = wb.worksheets[9]
		elif "OCTUBRE" in path:
			ws = wb.worksheets[10]
		elif "NOVIEMBRE" in path:
			ws = wb.worksheets[11]
		elif "DICIEMBRE" in path:
			ws = wb.worksheets[12]
		for i in range(24):
			if i<10:
				ws["A"+str(i+2)] = "0"+str(i)
				ws["B"+str(i+2)] = len(dic["0"+str(i)])
				cant = len(dic["0"+str(i)])
			else:
				ws["A"+str(i+2)] = str(i) 
				ws["B"+str(i+2)] = len(dic[str(i)]) 
				cant = len(dic[str(i)])
			ws["C"+str(i+2)] = self._Percentager(cant,dic["total"])
		wb.save(self.excelPATH+self.excelNAME)
	def CompleteWrite(self):
		##Escritura de cada hoja mensual
		for FILE in self.paths:
			print("Procesando: "+FILE)
			g = self._genGroup()
			self._reader(FILE,g)
			self._xlsWriter(FILE,g)
		##Escritura de la hoja de totales
		print("Procesando: TOTALES")
		g = self._genGroup()
		self._FULLreader(g)
		self._xlsWriter(0,g)
	def CurrentWrite(self):
		g = self._genGroup()
		print("Procesando: INCIDENCIAS PLENOIL.xlsx")
		self._reader("INCIDENCIAS PLENOIL.xlsx", g)
		self._xlsWriter("INCIDENCIAS PLENOIL.xlsx",g)

def main():
	flux = plenFLUX()
	flux.CompleteWrite()	
	
if __name__ == "__main__":
	main()
