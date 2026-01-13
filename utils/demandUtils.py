from models.Facility import Facility
from models.Demand import Demand
from typing import List, Set, Tuple

def waitingDems(allocations:List[Demand],waitingFlag:int) -> Set[Tuple[int,int,int]]:
    """
    Recebe a lista de demandas iniciais e retorna um conjunto com todas as demandas que
    estão no raio de cobertura de, ao menos, uma facilidade.
    """
    return set([tuple(allocations[i]) for i in range(len(allocations)) if allocations[i][0] == waitingFlag])

def allocate(coverageMatrix:List[List[int]], facility:Facility, iFacility:int, demands:List[Demand],totDemandServed:int, minDemand:int,waitingFlag:int,unservedDemands:Set[Tuple[int,int,int]]) -> None :
    """
    Aloca demandas ainda não atendidas para as facilidades da solução inicial. O processo
    termina assim que a demanda mínima é atendida. A lista de alocações (que nesse contexto
    é referida por "demands") é atualizada por referência, assim como os atributos do objeto
    "facility". Ao final, é retornado a quantidade total de demandas atendidas e um conjunto
    com as demandas recém-atendidas.
    """
    capacity = facility.capacity
    newServedDemands:Set[Tuple[int,int,int]] = set()

    for unservedDemand in unservedDemands:
        if (capacity == facility.served or minDemand <= totDemandServed):
            break
        i = unservedDemand[2]
        demandValue = demands[i][1]
        if ((coverageMatrix[i][iFacility]) and (demandValue+facility.served <= capacity)):
            demands[i][0] = iFacility
            facility.served += demandValue
            totDemandServed += demandValue
            newServedDemands.add(unservedDemand)
    return (totDemandServed, newServedDemands)