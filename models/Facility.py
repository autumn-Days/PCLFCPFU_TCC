from models.Demand import Demand

class Facility:
    def __init__(self, capacity:int, cost:float, status:bool=False, coverage:int=0, served:int = 0) -> None:
        self.capacity = capacity
        self.cost = cost
        self.status = status 
        self.coverage = coverage
        self.served = served 
    
    def close(self) -> None:
        self.status = False
        self.served = 0
    
    def open(self) -> None:
        self.status = True

    def hasSpace4Dem(self,dem:Demand) ->bool:
        return (self.served+dem[1] <= self.capacity)