from typing import List, Tuple
from models.Facility import Facility
from models.Demand import Demand
from algos.greedySolution import greedyHeuristic 
import utils.facilityUtils as facUtils
import bisect
import operator

class Sol:
    def __init__(self, facilities:List[Facility]=[], allocations:List[Demand]=[],
                 minDemand:int=float("inf"), penalty:float=float("inf")):
        self.facilities = facilities
        self.allocations = allocations
        self.objValue:float = float("inf")
        self.totalCost = float("inf")
        self.minDemand = minDemand
        self.totalServed:int = 0
        self.openFacil = []
        self.closeFacil = []
        self.penalty = penalty
        self.waitingFlag = len(self.facilities)+1

    def calcGreedySol(self, coverageMatrix:List[List[int]]) -> None:
        """
        Obtém uma solução por meio da heurística gulosa e inicializa os atribu-
        tos pertinentes:
        - quantidade total de demandas atendidas
        - qualidade da solução inicial
        - inicialização das listas auxiliares "openFacil" e "closeFacil"
        """
        self.totalServed = greedyHeuristic(self.facilities,self.allocations,coverageMatrix,self.minDemand)
        self.__initAtributes()

    def isFeasible(self) -> bool:
        #retorna a factibilidade da solução inicial
        return self.totalServed >= self.minDemand
    
    def evaluate(self, cost:float=float("inf"), opened=True, batch=False) -> None:
        fine:float = max(0, self.minDemand - self.totalServed) * self.penalty
        totalCost:float = 0 
        if (batch):
            for i in range(len(self.openFacil)):
                totalCost += self.openFacil[i][1]
        else:
            op = operator.add if (opened) else operator.sub  
            totalCost = op(self.totalCost,cost)
        self.totalCost = totalCost
        self.objValue = self.totalCost + fine

    def move(self, pIter:int, coverageMatrix:List[List[int]],
             is2install=False) -> None:
        if (self.isFeasible()):
            if (is2install):
                facility:Tuple[int,int] = self.closeFacil.pop(pIter) #facility: (indice,custo)
                indexFacility:int = facility[0]
                self.__install(indexFacility, coverageMatrix)
                self.__updateAuxList(facility,openFacil=True)
            else:
                facility:Tuple[int,int] = self.openFacil.pop(pIter)
                indexFacility = facility[0]
                self.__close(indexFacility, coverageMatrix)
                self.__updateAuxList(facility,closeFacil=True)
        else:
            facility:Tuple[int,int] = self.closeFacil.pop(pIter)
            facilityIndex = facility[0]
            self.__install(facilityIndex,coverageMatrix)
            self.__updateAuxList(facility,openFacil=True)

    def __initAtributes(self):
        self.__createInstalledClosed()
        self.evaluate(batch=True)

    def __createInstalledClosed(self) -> None:
        """
        Inicializa as listas closeFacil e openFacil, respectivamente,
        em ordem decrescente de custo de abertura e em ordem crescente
        de custo de abertura.
        """
        for i in range(len(self.facilities)):
            cost:float = self.facilities[i].cost
            if (self.facilities[i].status):
                self.openFacil.append((i,cost))
            else:
                self.closeFacil.append((i,cost))

        self.openFacil.sort(key = lambda facil:facil[1], reverse=True)
        self.closeFacil.sort(key = lambda facil:facil[1])

    def __updateAuxList(self,facility:Tuple[int,int], openFacil=False, closeFacil=False):
        """
        Atualiza as listas auxiliares "openFacil" e "closeFacil" de modo que a sua ordena-
        ção continue sendo respeitada. A funcionalidade utilizada para a inserção ordenada
        foi feita por meio da biblioteca "bisect". Para que seja possível rodar esse método
        é necessário utilizar o Python 3.10 ou superior.
        """
        if (openFacil):
            bisect.insort(self.openFacil, facility, key=lambda elem:-elem[1])
        elif(closeFacil):
            bisect.insort(self.closeFacil, facility, key=lambda elem:elem[1])

    def __install(self, iFacility:int, coverageMatrix:List[List[int]]) -> None:
        """
        Responsável por abrir e alocar demandas para a facilidade de índice
        `iFacility`.
        """
        self.facilities[iFacility].open()
        self.__findAllocateWaiters(iFacility, coverageMatrix)    

    def __findAllocateWaiters(self, iFacility:int, coverageMatrix:List[List[int]]) -> None:
        """
        Responsável por encontrar e alocar as demandas que que ainda não foram
        atendidas e estão dentro do raio de cobertura de uma dada facilidade e
        O método também atualiza os atributos pertinentes.
        """
        capacity = self.facilities[iFacility].capacity
        amountClients:int = len(self.allocations)
        for i in range(amountClients):
            served:int = self.facilities[iFacility].served
            if served == capacity:
                break
            elif (coverageMatrix[i][iFacility] and
                  self.allocations[i][0] == self.waitingFlag and
                  served + self.allocations[i][1] <= capacity):
                    self.allocations[i][0] = iFacility
                    self.facilities[iFacility].served += self.allocations[i][1]
                    self.totalServed += self.allocations[i][1]

    def __close(self,iFacility:int, coverageMatrix:List[List[int]]) -> None:
        """
        Responsável por fechar uma certa facilidade e realocar suas demandas
        para as facilidades abertas.
        """
        self.totalServed -= self.facilities[iFacility].served
        self.facilities[iFacility].close()
        beggars:List[Demand] = self.__findBeggars(iFacility)
        amountFacilities:int = len(self.facilities)
        
        for beggar in beggars:
            for j in range(amountFacilities):
                if (j != iFacility and
                coverageMatrix[beggar[2]][j] and
                self.facilities[j].status and
                self.facilities[j].hasSpace4Dem(beggar)):
                    beggar[0] = j
                    self.facilities[j].served += beggar[1]
                    self.totalServed += beggar[1]
                    break #!
   
    def __findBeggars(self,iFacility:int) -> List[Demand]:
        """
        Responsável por encontrar todas as demandas que devem ser realocadas para
        outra facilidade em virtude do fechamento da facilidade de índice 
        `iFacility`.
        
        Em relação ao nome do método, "beggar" vem do inglês "mendigo". No contexto
        do método, ele denota que antes alguns clientes estavam sendo atendidos, mas agora
        não estão mais e, portanto, poderiam ser entendidos dessa forma.
        """
        beggars:List[Demand] = []
        for i in range(len(self.allocations)):
            if self.allocations[i][0] == iFacility:
                self.allocations[i][0] = self.waitingFlag
                beggars.append(self.allocations[i])
        return beggars

    def __lt__(self, otherSol:"Sol"):
        #sobrecarga do operador de '<' entre objetos "Sol"
        if isinstance(otherSol, Sol):
            return self.objValue < otherSol.objValue
        raise TypeError("Sobrecarga inválida!")