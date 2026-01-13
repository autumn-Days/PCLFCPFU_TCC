import numpy as np
from typing import List,Tuple
from math import sqrt,ceil
from models.Facility import Facility
from models.Demand import Demand


def calcEucDist(p1:Tuple["np.float32","np.float32"],p2:Tuple["np.float32","np.float32"]) -> "np.float32":
	return np.sqrt(np.pow((p1[0] - p2[0]),2) + np.pow((p1[1] - p2[1]),2))

def initColumn(coverageMatrix:List[List[int]],content:List[str],
	indexCoord:Tuple[int,Tuple["np.float32","np.float32"]],n:int,
	m:int,r:float,allocations:List[Demand])->int:
	"""
	Inicializa a matriz de cobertura coluna por coluna, além de inicializar
	a lista das alocações.
	-content: O conteúdo do arquivo com os dados da instância.
	-indexCoord: O índice da facilidade em "facilities" e suas coordenadas
	-r: o raio de cobertura da instância
	"""
	firstCall = False
	demCovered = 0
	initAllocation = -1
	offset = n+1 #A linha com os dados do primeiro cliente (soma-se 1 para compensar a primeira linha)
	waitingFlag = n+1

	if len(allocations) == 0:
		firstCall = True
	for i in range(offset, offset+m):
		_, iReal, x, y, demValue = tuple(content[i].split("\t"))
		if calcEucDist((np.float32(x),np.float32(y)),indexCoord[1]) <= np.float32(r) :
			coverageMatrix[int(iReal)][indexCoord[0]] = 1
			demCovered += int(demValue)
			initAllocation = waitingFlag
			if len(allocations) == m:
				allocations[int(iReal)][0] = waitingFlag
		if firstCall:
			allocations.append([initAllocation, int(demValue), int(iReal)])
		initAllocation = -1
	return demCovered

def initDSs(content: List[str], U:int, r:float,m:int,n:int=100) -> Tuple[List[Facility],List[Demand],List[List[int]]]:
	"""
	Responsável pela criação de "coverageMatrix", "facilities" e "allocations"
	com base nos dados das instâncias.
	"""
	facilities:List[Facility] = []
	allocations:List[Demand] = []
	coverageMatrix:List[List[int]] = [[0 for i in range(n)] for j in range(m)]
	
	j = 0
	for line in content:
		if line[0] == 'F' :
			"""
			Os dados acerca das facilidades são obtidos. Para obter a soma
			as demandas no seus raio de cobertura, o valor retornado por "popu
			lateColumn" é usado. Essa função é responsável por inicializar as
			as colunas da matriz de cobertura, inicializar a lista das alocações, 
			além de retornar o valor de 'coverage'.
			"""
			_,_,x,y,cost = tuple(line.split("\t"))
			facility = Facility(U,float(cost))
			coords = (np.float32(x),np.float32(y))
			coverage = initColumn(coverageMatrix,content,(j,coords),n,m,r,allocations)
			facility.coverage = coverage
			facilities.append(facility)
			j += 1
		elif len(line.split("\t")) == 3:
			"""
			Quando este é o caso, a primeira linha está sendo lida.
			Após o "split", sobram 3 elementos contanto com o '\n'
			do final da linha.
			"""
			continue
		else:
			"""
			Para a inicialização das estruturas de dados, só é necessário
			ler o conteúdo dos arquivos até os dados pertinentes às facili-
			dades.
			"""
			break
	return facilities,allocations,coverageMatrix

def extractN_and_M(content:List[str]) -> Tuple[str,str]:
	"""
	Acessa o conteúdo do arquivo com os dados das instâncias e
	obtém a quantidade de facilidades e de clientes usados
	na instância em questão.
	"""
	firstLine = content[0]
	n,m,_ = tuple(firstLine.split("\t"))
	return n,m

def calcTotalDemand(content:List[str]) -> int:
	"""
	Calcula a demanda total de uma certa instância.
	"""
	n,m = extractN_and_M(content)
	n = int(n)
	m = int(m)
	totalDemand = 0
	offset = n+1 #A linha com os dados do primeiro cliente (soma-se 1 para compensar a primeira linha)
	for i in range(offset,offset+m):
		_,_,_,_,demValue = tuple(content[i].split("\t"))
		totalDemand += int(demValue)
	return totalDemand