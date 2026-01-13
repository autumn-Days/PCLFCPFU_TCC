from models.Facility import Facility
from models.Demand import Demand
import utils.facilityUtils as facUtils 
import utils.demandUtils as demUtils
from typing import Tuple,List

def greedyHeuristic(facilities:List[Facility],
    allocations:List[Demand],
    coverageMatrix:List[List[int]],
    minDemand:int) -> int:
    totDemandServed:int =  0
    waitingFlag:int = len(facilities)+1
    quocients:List[float] = facUtils.calcQuocients(facilities)
    
    unservedDemands:Set = demUtils.waitingDems(allocations,waitingFlag)
    indexFacilities:List = [i for i in range(len(facilities))]

    combined:List[Tuple[int,float]] = list(zip(indexFacilities,quocients))
    combined.sort(key = lambda elem : elem[1], reverse=True)
    indexFacilities,_ = zip(*combined)
            
    j:int = 0
    while ((j != len(indexFacilities)) and
    (unservedDemands) and
    (totDemandServed < minDemand)):
        iFacility = indexFacilities[j] 
        facility = facilities[iFacility]
        if (facility.coverage > 0):
            capacity:int = facility.capacity
            newServedDemands:Set = None
            totDemandServed, newServedDemands = demUtils.allocate(coverageMatrix,facility,iFacility,allocations,totDemandServed,minDemand,waitingFlag,unservedDemands)
            if (newServedDemands):
                facility.open()
                unservedDemands -= newServedDemands
        j += 1
    return totDemandServed