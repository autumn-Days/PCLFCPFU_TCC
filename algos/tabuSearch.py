from typing import List, Tuple
from models.Solution import *
from models.Facility import Facility
from models.Demand import Demand
from algos.greedySolution import *
import algos.tabuSearchAux as ta
import copy as cp

def tabuSearch(facilities:List[Facility], allocations:List[Demand],
               coverageMatrix:List[List[int]], minDemand:int,
               maxIter:int, dur:int, penalty:float)-> Tuple[Sol,bool]:
    config:int = -1
    s:Sol = Sol(facilities, allocations, minDemand, penalty=penalty)
    s.calcGreedySol(coverageMatrix)
    sStar:Sol = cp.deepcopy(s)
    i:int = 0
    bestIter:int = 0
    tabu:List[int] = [-1 for i in range(len(facilities))]
    while (i - bestIter < maxIter):
        sTabu:Sol = Sol()
        sNeighbour:Sol = Sol()
        pIter:int = 0
        if (s.isFeasible()):
            if (s.openFacil):
                sNeighbour,sTabu,config = ta.close(s,sTabu,coverageMatrix,tabu,i,pIter)
                pIter +=1
            while (pIter < len(s.openFacil) and
            (not sNeighbour.isFeasible() or                 
            tabu[config] >= i)):  
                sNeighbour,sTabu,config = ta.close(s,sTabu,coverageMatrix,tabu,i,pIter)
                pIter +=1
            if (not sNeighbour.isFeasible()) or (tabu[config] >= i):
                pIter = 0
                if (s.closeFacil):
                    sNeighbour,sTabu,config = ta.install(s,sTabu,coverageMatrix,tabu,i,pIter)
                    pIter += 1
                while (pIter < len(s.closeFacil) and (tabu[config] >= i)):
                    sNeighbour,sTabu,config = ta.install(s,sTabu,coverageMatrix,tabu,i,pIter)
                    pIter +=1
        else:
            if (s.closeFacil): 
                sNeighbour,sTabu,config = ta.install(s,sTabu,coverageMatrix,tabu,i,pIter)
                pIter +=1
            while (pIter < len(s.closeFacil) and
            (not sNeighbour.isFeasible() or
            tabu[config] >= i)):    
                s_aux = cp.deepcopy(s)
                s_aux.move(pIter,coverageMatrix,is2install=True)
                iFac = s.closeFacil[pIter][0]
                cost = s.facilities[iFac].cost
                s_aux.evaluate(cost,opened=True)
                if (s_aux < sNeighbour):
                    config = iFac
                    sNeighbour = cp.deepcopy(s_aux)
                    if tabu[config] >= i and sNeighbour < sTabu:
                        sTabu = cp.deepcopy(sNeighbour)
                pIter += 1
        if (sTabu < sStar):
            s = cp.deepcopy(sTabu)
            sStar = cp.deepcopy(sTabu)
            bestIter = i
        else:
            if (tabu[config] >= i):
                return (sStar,False)
            tabu[config] = i + dur
            s = cp.deepcopy(sNeighbour)
            if (s < sStar):
                sStar = cp.deepcopy(s)
                bestIter = i
        i += 1
    return (sStar,True)