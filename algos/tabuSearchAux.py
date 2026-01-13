from typing import List, Tuple
from models.Solution import Sol
import copy as cp

def doOperation(s:Sol,sTabu:Sol,coverageMatrix:List[List[int]],tabu:List[int],i:int,pIter:int,is2install:bool) -> Tuple[Sol,Sol,int]:
    sNeighbour:Sol = cp.deepcopy(s)
    sNeighbour.move(pIter,coverageMatrix,is2install=is2install)
    
    config:int = None
    if is2install:
        config = s.closeFacil[pIter][0]
        cost = s.facilities[config].cost
        sNeighbour.evaluate(cost,opened=True)
    else:
        config = s.openFacil[pIter][0]
        cost = s.facilities[config].cost
        sNeighbour.evaluate(cost,opened=False)

    if (tabu[config] >= i) and (sNeighbour < sTabu):
        sTabu = cp.deepcopy(sNeighbour) 

    return (sNeighbour,sTabu,config)

def install(s:Sol,sTabu:Sol,coverageMatrix:List[List[int]],tabu:List[int],i:int,pIter:int) -> Tuple[Sol,Sol,int]:
    return doOperation(s,sTabu,coverageMatrix,tabu,i,pIter,is2install=True)

def close(s:Sol,sTabu:Sol,coverageMatrix:List[List[int]],tabu:List[int],i:int,pIter:int) -> Tuple[Sol,Sol,int]:
    return doOperation(s,sTabu,coverageMatrix,tabu,i,pIter,is2install=False)