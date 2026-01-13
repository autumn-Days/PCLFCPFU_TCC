from models.Facility import Facility
from typing import List,Tuple

def calcQuocients(facilities:List[Facility]) -> List[float]:
    """
    Recebe uma lista de facilidades e retorna a lista de quocientes
    relacionados a cada facilidade. O quociente é dado pela quantidade
    prática de demandas que podem ser atendidas dividido pelo custo
    de instalação da facilidade. 
    """
    quocients:List[float] = []
    for i in range(len(facilities)):
        practCoverage:int = min(facilities[i].coverage,facilities[i].capacity)
        cost:float = facilities[i].cost
        quocients.append(practCoverage/cost)
    return quocients