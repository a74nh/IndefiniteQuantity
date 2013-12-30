from enums import *

#TODO: Join with other suite specific actions. Split into a file per suite

class Upkeep(object):

    def __init__(self,tableau):
        self.tableau=tableau

    def upkeepNone(self,playerLists,cardPile):
        print "upkeep_None"
        pass

    def upkeepNoneReturn(self,playerLists,cardPile):
        print "upkeepNoneReturn"
        pass


    #Service
    #
    #Player must pay 1 for each soldier
    #
    
    def upkeepService(self,playerLists,cardPile):

        playableList=[]
        for c in playerLists.hand:
            #TODO: Add in effects
            c.playable=ePlayable.cost
            c.playableCost=1
            playableList.append((playerLists.hand,c,playerLists.hand.index(c)))

        for c in playerLists.scrap:
            c.playable=ePlayable.cost
            c.playableCost=c.scrap
            playableList.append((playerLists.scrap,c,playerLists.scrap.index(c)))


        self.tableau.pickedCost=False
        if playableList:
            self.tableau.userPickCost(eEngineStages.upkeepReturn,
                                      playableList,
                                      1,
                                      self.tableau.playerDiscard)
        else:
            self.tableau.null(eEngineStages.upkeepReturn)


    def upkeepServiceReturn(self,playerLists,cardPile):

        if not self.tableau.pickedCost:
            #player failed upkeep
            cardPile.dealCard(self.tableau.playerDiscard,eCardState.normal)

        self.tableau.null(eEngineStages.upkeepSetup)


    #Halflife
    #
    #Soldier expires after a certain time
    #
    
    def upkeepHalflife(self,playerLists,cardPile):
        print "upkeep_Halflife"
        pass

    def upkeepHalflifeReturn(self,playerLists,cardPile):
        print "upkeepHalflifeReturn"
        pass


    #Hunger
    #
    #Soldier consumes other soldiers
    #
    
    def upkeepHunger(self,playerLists,cardPile):
        print "upkeep_Hunger"
        pass

    def upkeepHungerReturn(self,playerLists,cardPile):
        print "upkeepHungerReturn"
        pass


    #Oldest
    #
    #Oldest Soldier is consumed
    #    

    def upkeepOldest(self,playerLists,cardPile):
        print "upkeep_Oldest"
        pass
    
    def upkeepOldestReturn(self,playerLists,cardPile):
        print "upkeepOldestReturn"
        pass
