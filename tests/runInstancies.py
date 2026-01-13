from algos.tabuSearch import tabuSearch
from tests.dataHandler import *
from tests.dsInitializer import *
import time
import numpy as np

def execute():
	MAX_ITER = 100
	DUR = 11
	PENALTY = 1000	
	
	instancies = [ "tests/instancies/GRID_PSCLP_n100_m1000_d1_100_f10_100_s1.dat",
		"tests/instancies/GRID_PSCLP_n100_m10000_d1_100_f10_100_s1.dat",
		"tests/instancies/GRID_PSCLP_n100_m50000_d1_100_f10_100_s1.dat"
	]
	instancies = makeParseable(instancies)
	
	amountClients = [1000,10000,50000]
	totalDemands = [calcTotalDemand(instance) for instance in instancies]
	clientsDems = dict(zip(amountClients,totalDemands))

	U = [0.05,0.02]
	D = [0.5,0.6,0.7]
	R = {
		0.5:[5.5,5.75,6.0,6.25],
		0.6:[4.0,4.25,4.5,4.75,5.0],
		0.7:[3.25,3.5,3.75,4.25]
	}
	instanceCounter = 1
	for u in U:
		for instance in instancies:
			for d in D :
				for r in R[d]:
					u = np.float32(u)
					d = np.float32(d)
					
					n,m = extractN_and_M(instance)

					n = int(n)
					m = int(m)
					
					totalDem:"np.int64" = np.int64(clientsDems[m])
					minDem:"np.float32" = totalDem*d #No trabalho base, o autor não tirou o ceil e nem o floor & usa um float
					capacity:float = float(minDem*u) #No trabalho base, o autor não tirou o ceil e nem o floor & usa um float

					totalDem= int(totalDem) #conversão de compatibilidade para a implementação da busca tabu
					minDem = float(minDem) #conversão de compatibilidade para a implementação da busca tabu

					params = (m,n,d,u,r,totalDem,minDem,capacity)
					facilities,allocations,coverageMatrix = initDSs(instance,capacity,r,m,n)
					
					print(f"Executando a {instanceCounter}° instância: m{m}_n{n}_r{r}_D{str(d)[:3]}_U{str(u)[:4]}")
					
					start = time.time()
					sStar,isAspCritBreaked = tabuSearch(facilities,allocations,coverageMatrix,minDem,MAX_ITER,DUR,PENALTY)
					timeTaken = time.time() - start
					
					saveData(params,sStar,isAspCritBreaked,timeTaken,coverageMatrix)
					
					del facilities
					del allocations
					del coverageMatrix
					del sStar
					
					instanceCounter +=1