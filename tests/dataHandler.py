import math
from pathlib import Path
from typing import List, Tuple,Any
from models.Demand import Demand
import numpy as np

def makeParseable(paths:List[str]) -> List[List[str]]:
	"""
	Recebe os caminhos para as instâncias de testes e
	retorna o conteúdo de cada uma delas dentro de uma lista.
	"""
	filesContent = []
	for path in paths:
		with open(path) as file:
			file = file.readlines()
			filesContent.append(file)
	return filesContent

def stringfyMatrixLikeStructures(matrixLike:List[Any],isAllocations:bool=False,coverageMatrix=None,s:"Sol"=None) -> Any:
	"""
	uma "matrix-like-structure" é uma estrutura de dados que age como uma matriz. Existem várias estruturas desse tipo
	no algoritmo, como a matriz de alocações, ou as listas auxiliares openFacil e closeFacil, que são lista de tuplas.
	
	Essa função salva os dados dessas estruturas de dados e caso, 'allocations' seja passada para ela, coverageMatrix 
	e facilities também são passadas para que haja a verificação da legalidade das alocações e de outras características
	da solução 'sStar'.
	"""

	content = ""
	if isAllocations:
		DEMANDS = set()
		waitingFlag = len(s.facilities)+1
		
		servedAgain = 0
		servedByFacilities:List[int] = [s.facilities[i].served for i in range(len(s.facilities))]
		verifyServedByFacilities:List[int] = [0 for i in range(len(s.facilities))]

		notEvenInCover:List[Demand] = []#as demandas que estão sendo "atendidas" por facilidades que não estão perto o suficiente delas (será que tem ?)

		for i in range(len(matrixLike)):
			content += f"{i}: {matrixLike[i]}\n\n"
			
			if matrixLike[i][0] != -1 and matrixLike[i][0] != waitingFlag:
				allocation = matrixLike[i][0]
				isCovered = coverageMatrix[i][allocation]
				if (not isCovered):
					notEvenInCover.append(matrixLike[i])
				
				servedAgain += matrixLike[i][1]
				verifyServedByFacilities[allocation] += matrixLike[i][1]

		if servedAgain != s.totalServed:
			print("analisando")

		isTotalServedIncorrect = True if (servedAgain != s.totalServed) else False #se a quantidade total de demandas atendidas foi contada incorretamente
		isMinDemandNotServed = True if (servedAgain < s.minDemand) else False #se a demanda mínima foi contada incorretamente
		areServedMismatch = True if (verifyServedByFacilities != servedByFacilities) else False #Em casos de comparação de listas de inteiros, o que se compara é o valor e não as referências para os locais da memória que os guardam
		return content,notEvenInCover,isTotalServedIncorrect,isMinDemandNotServed, areServedMismatch
	else:
		content =""
		for i in range(len(matrixLike)):
			content += f"{i}: {matrixLike[i]}\n\n"
		return content

def stringfyFacilitiesInfo(s):
	"""
	Retorna uma string com os dados pertinentes e a preservação da restrição da capacidade
	"""
	content = ""

	SET_OPEN_FACIL = set(s.openFacil)
	SET_CLOSE_FACIL = set(s.closeFacil)

	closeServing:List[int] = [] #fechado & servindo
	overServing:List[int] = []#atende mais do que deveria
	WrongPlaceOpenF:List[int] = []#Está fechada, mas está salva em openFacil
	wrongPlaceCloseF:List[int] = []#Está aberta, mas está salva em closeFacil
	indifferents:List[int] = []#Deveria estar ou em openFacil ou em closeFacil, mas não está em nenhuma lista auxiliar
	
	for i in range(len(s.facilities)):
		facility = s.facilities[i]
		content += f"""Facilidade {i}:
	-status:{facility.status}
	-cost:{facility.cost}
	-coverage:{facility.coverage}
	-capacity_served:{facility.capacity}/{facility.served}
"""
		facilEncoded = (i,facility.cost)
		if (not facility.status) and (facility.served):
			closeServing.append(i)
		if (facility.served > facility.capacity):
			overServing.append(i)
		if (not facility.status) and (facilEncoded in SET_OPEN_FACIL):
			wrongPlaceOpenF.append(i)
		elif (facility.status) and (facilEncoded in SET_CLOSE_FACIL):
			wrongPlaceCloseF.append(i)
		elif (facilEncoded not in SET_OPEN_FACIL) and (facilEncoded not in SET_CLOSE_FACIL):
			indifferents.append(i)

	return content,closeServing,overServing,WrongPlaceOpenF,wrongPlaceCloseF,indifferents


def saveData(params:Tuple,s:"Sol",isAspCritBreaked:bool,timeTaken:float,coverageMatrix:List[List[int]]) -> None:
	"""
	tableResults: 	n	m	r	D	U	objV	time	fact	breakedCrit		totalCost	totalDemand		minDemand	totalServed		capacity	totalDemand*d	totalDemand*d*u		minDemand*u //Esses 3 últimos só servem para verificar erros de arrendodamento
	tableAmountTransgressions: |closeServing|	|overServing|	|WrongPlaceOpenF|	|wrongPlaceCloseF|	|indifferents|	|uniqueSourceBreaker|	|notEvenInCover|	|isTotalServedIncorrect|	|isMinDemandNotServed|
	

	OBS.:Ao rodar a 'main.py' mais de uma vez, delete o arquivo 'tests/results/resultsTable.txt' para que somente os dados relativos
	a execução atual sejam salvos.
	"""
	
	tableResults = "tests/results/resultsTable.txt"
	tableAmountTransgressions = "tests/results/amountTrangressions.txt"
	#tableFacilTrangressors = "tests/results/facilTransgressors.txt" 
	#tableAllocationTransgressors = "tests/results/facilTransgressors.txt"


	m,n,d,u,r,totalDemand,minDemand,capacity = params
	contentResults = f"{n}\t{m}\t{r}\t{str(d)[:3]}\t{str(u)[:4]}\t{s.objValue}\t{round(timeTaken,6)}\t{int(s.isFeasible())}\t{int(isAspCritBreaked)}\t{s.totalCost}\t{totalDemand}\t{minDemand}\t{s.totalServed}\t{capacity}\t{np.int64(totalDemand)*d}\t{np.int64(totalDemand)*d*u}\n"
	with open(tableResults,"a") as table:
		table.write(contentResults)

	fileNameConfig = f"m{m}_n{n}_D{d}_U{u}_r{r}"
	path2folderConfig = f"tests/results/U{str(u)[:4]}/m{m}/D{str(d)[:3]}/{fileNameConfig}.txt"
	
	path2create = Path(path2folderConfig)
	path2create.parent.mkdir(parents=True,exist_ok=True)

	contentCoverageMatrix = stringfyMatrixLikeStructures(coverageMatrix)
	contentOpenFacil = stringfyMatrixLikeStructures(s.openFacil)
	contentCloseFacil = stringfyMatrixLikeStructures(s.closeFacil)
	contentAllocations,notEvenInCover,isTotalServedIncorrect,isMinDemandNotServed,areServedMismatch = stringfyMatrixLikeStructures(s.allocations,True,coverageMatrix,s)
	contentFacilities,closeServing,overServing,WrongPlaceOpenF,wrongPlaceCloseF,indifferents = stringfyFacilitiesInfo(s)

	contentTrangressions = f"{len(notEvenInCover)}\t{int(isTotalServedIncorrect)}\t{int(isMinDemandNotServed)}\t{int(areServedMismatch)}\t{len(closeServing)}\t{len(overServing)}\t{len(WrongPlaceOpenF)}\t{len(wrongPlaceCloseF)}\t{len(indifferents)}\n"
	with open(tableAmountTransgressions, "a") as tableT:
		tableT.write(contentTrangressions)

	configContent = f"""COVERAGE_MATRIX:
{contentCoverageMatrix}
-=-=-=-=-=-=-=
ALLOCATIONS:

{contentAllocations}
-=-=-=-=-=-=-=
OPEN FACIL:

{contentOpenFacil}
-=-=-=-=-=-=-=
CLOSE FACIL:

{contentCloseFacil}
-=-=-=-=-=-=-=
FACILITIES INFO:

{contentFacilities}
"""
	with open(path2folderConfig, "w") as fileConfig :
		fileConfig.write(configContent)