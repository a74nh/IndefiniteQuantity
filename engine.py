from cards import enum
from cards import ePlayable
from cards import eOrder
from cards import eCardTypes
from cards import eSuiteNames
from cards import eCardState

eEngineStages = enum("upkeepInit","upkeep","enemyDealInit","enemyDeal","enemyDealCheck",
                     "playerDealInit","playerDeal",
                     "buildInit","buildSetup","buildCost","buildFinal",
                     "attackInit","attackSetup","attack","attackAfter",
                     "collectInit","collectSetup",
                     "produceInit","produce","produceSell","produceSold","produceDeal",
                     "nextPlayer")


class PlayerCardLists(object):
    def __init__(self,playerNumber,suite,CardPile,CardList,CardCounter):
        self.playerNumber=playerNumber
        self.suite=suite

        self.points=CardCounter("playerPoints", playerNumber, 0)
        
        self.hand=CardList("playerHand",playerNumber)
        self.spareWorkers=CardPile("playerSpareWorkers",playerNumber)
        self.scrap=CardList("playerScrap",playerNumber)
        self.workers=[]
        self.soldiers=[]
        self.base=[]
        for x in range(5):
            self.workers.append(CardPile("playerWorkers{0}".format(x),playerNumber))
            self.soldiers.append(CardPile("playerSoldiers{0}".format(x),playerNumber))
            self.base.append(CardPile("playerBase{0}".format(x),playerNumber)) #facilites
            



#
# Current layout of the game
# Holds the various lists of cards
#
class Tableau(object):
    
    def __init__(self,deck,numberPlayers,display,CardPile,CardList,CardCounter):
        self.deck=deck
        self.numberPlayers=numberPlayers
        self.display=display

        self.enemysuite=deck.suites[0]

        self.display.setup(self.numberPlayers,self.enemysuite,deck.suites[1:])
        
        workerBlanks= []
        baseBlanks= []
        soldierBlanks= []
        stockBlanks= []
        self.enemyStock= CardPile("enemyStock",0)
        self.playerStock= CardPile("playerStock",0)
        self.enemySoldiers=[]
        self.enemyDiscard=CardPile("enemyDiscard",0)
        self.__playerLists=[]
        for x in range(numberPlayers):
            self.__playerLists.append(PlayerCardLists(x+1,deck.suites[x+1],CardPile,CardList,CardCounter))
        self.playerDiscard=CardPile("playerDiscard",0)

        for card in deck.cards:
            if card.isBlank():
                if card.name=="worker":
                    workerBlanks.append(card)
                elif card.name=="base":
                    baseBlanks.append(card)
                elif card.name=="soldier":
                    soldierBlanks.append(card)
                elif card.name=="stock":
                    stockBlanks.append(card)
            elif card.suite.name == self.enemysuite.name:
                if card.ctype != eCardTypes.factory and card.ctype != eCardTypes.cover and card.ctype != eCardTypes.worker:
                    self.enemyStock.append(card)
                    card.setState(eCardState.turned)
            else:              
                if card.ctype == eCardTypes.worker:
                    for p in self.__playerLists:
                        if card.suite.name == p.suite.name:
                            p.spareWorkers.append(card)
                            break
                elif card.ctype != eCardTypes.factory and card.ctype != eCardTypes.cover:
                    self.playerStock.append(card)
                    card.setState(eCardState.turned)

        for p in range(numberPlayers):
            for q in range(5):
                self.__playerLists[p-1].workers[q].append(workerBlanks.pop())
                self.__playerLists[p-1].base[q].append(baseBlanks.pop())
                self.__playerLists[p-1].soldiers[q].append(soldierBlanks.pop())
        for q in range(5):
            pile = CardPile("enemySoldiers{0}".format(q),0)
            pile.append(soldierBlanks.pop())
            self.enemySoldiers.append(pile)
        self.enemyDiscard.append(stockBlanks.pop())
        self.playerDiscard.append(stockBlanks.pop())
        
        self.display.turnOn()
        self.__phase=-1
        self.__player=-1
        self.__engineStage=-1
        self.__nextEngineStage=0
        self.attackPhase=-1
        self.playerDealPhase=0
        self.__history=[]
        self.__turn=0

    def nextEngineStage(self):
        self.__engineStage=self.__nextEngineStage
        return self.__engineStage

    def getCurrentPlayerLists(self):
        return self.__playerLists[self.__player-1]

    def getTurn(self):
        return self.__turn
    
    def getPlayerLists(self,player):
        return self.__playerLists[player-1]
        
    #def dealEnemy(self,num):
    #    for x in range(num):
    #        self.enemyStock.moveI(0,self.enemySoldiers)

    def dealPlayer(self,player,num):
        for x in range(num):
            self.getPlayerLists(player).hand.append(self.playerStock.pop())


    def undoHistory(self):

        while self.__history:
            last=self.__history.pop()

            if last['action'] == "setStage":
                self.__nextEngineStage=last['arg1']
                break #end loop
                
            elif last['action'] == "setPhase":
                self.display.updatePhase(last['arg2'],last['arg1'])
                
            elif last['action'] == "setPlayer":
                #TODO: add turn inc
                self.display.updatePlayer(last['arg2'],last['arg1'])
            
            elif last['action'] == "moveO":
                #TODO: self.display fix
                last['arg4'].pop()
                last['arg3'].insert(last['arg2'],last['arg1'])
            
            elif last['action'] == "userPickSingle":
                last['arg3'].insert(last['arg2'],last['arg1'])

            elif last['action'] == "userPickSingleTo":
                last['arg3'][last['arg2']]=last['arg1']
            
            elif last['action'] == "userPickCost":
                last['arg3'].insert(last['arg2'],last['arg1'])
            
            elif last['action'] == "moveCardTo":
                last['arg2'].pop()

            elif last['action'] == "ToBlank":
                last['arg1'].append(last['arg3'][last['arg2']])
                last['arg3'][last['arg2']]=False

            #self.display.()    
            #print(self.__history)



    ##STAGE INCREASING FUNCTIONS
    ##Called by the engine
    ##After calling, the engine should return

    def __setStage(self,nextEngineStage):
        self.__nextEngineStage=nextEngineStage
        self.__history.append({'action': 'setStage', 'arg1': self.__engineStage, 'arg2': nextEngineStage})


    def null(self,nextEngineStage):
        self.__setStage(nextEngineStage)


    def setPhase(self,nextEngineStage,phase):
        self.__setStage(nextEngineStage)
        self.__history.append({'action': 'setPhase', 'arg1': self.__phase, 'arg2': phase})
        
        self.display.updatePhase(self.__phase,phase)
        self.__phase=phase


    def setPlayer(self,nextEngineStage,player):
        self.__setStage(nextEngineStage)
        self.__turn=self.__turn+1
        self.__history.append({'action': 'setPlayer', 'arg1': self.__player, 'arg2': player, 'arg3': self.__turn})

        self.display.updatePlayer(self.__playerLists[player-1],self.__turn)
        self.__player=player

        
##    def checkEnemy(self,nextEngineStage):
##        self.__setStage(nextEngineStage)
##        
##        found=True
##        while(found):
##            found=False
##            for x in self.enemySoldiers:
##                if x.ctype != eCardTypes.soldier:
##                    self.__history.append({'action': 'moveO', 'arg1': x,
##                                                              'arg2': self.enemySoldiers.index(x),
##                                                              'arg3': self.enemySoldiers,
##                                                              'arg4': self.enemyDiscard})
##                    
##                    self.enemySoldiers.moveFrom(self.enemySoldiers.index(x),self.enemyDiscard)
##                    #self.enemySoldiers.moveO(x,self.enemyDiscard)
##                    found=True


    def userPickSingle(self,nextEngineStage,pickableFrom):
        self.__setStage(nextEngineStage)
        
        self.picked=self.display.userPickSingle(pickableFrom)
        (pickedState,picked,pickedTo)=self.picked

        if picked:
            (cardList,card,index)=picked
            self.__history.append({'action': 'userPickSingle', 'arg1': card,
                                                               'arg2': index,
                                                               'arg3': cardList})
            if pickedTo:
                (cardListTo,cardTo,indexTo)=pickedTo
                self.__history.append({'action': 'userPickSingleTo', 'arg1': cardTo,
                                                                     'arg2': indexTo,
                                                                     'arg3': cardListTo})   

            

    def userPickCost(self,nextEngineStage,pickableFrom,price,moveTo):
        self.__setStage(nextEngineStage)

        self.pickedCostList=[]
        ret=self.display.userPickCost(pickableFrom,price,moveTo)

        if ret is False:
            self.pickedCost=False
        else:
            self.pickedCost=True 
            for item in ret:
                (cardList,card,index)=item
                self.pickedCostList.append(card)
                self.__history.append({'action': 'userPickCost', 'arg1': card,
                                                                 'arg2': index,
                                                                 'arg3': cardList})

    def userPickList(self,nextEngineStage,pickableFrom,moveTo):
        self.__setStage(nextEngineStage)

        self.pickedCostList=[]
        ret=self.display.userPickList(pickableFrom,moveTo)

        if ret is False:
            self.pickedCost=False
        else:
            self.pickedCost=True 
            for item in ret:
                (cardList,card,index)=item
                self.pickedCostList.append(card)
                self.__history.append({'action': 'userPickList', 'arg1': card,
                                                                 'arg2': index,
                                                                 'arg3': cardList})

    def moveCardTo(self,nextEngineStage,card,cardList):
        self.__setStage(nextEngineStage)
        self.__history.append({'action': 'moveCardTo', 'arg1': card,
                                                       'arg2': cardList})
        self.display.moveCardTo(card,cardList)

        
    def dealCard(self,oldCardList,newCardList,newState):
        self.__history.append({'action': 'dealCardToBlank', 'arg1': oldCardList,
                                                            'arg2': newCardList})
        oldCardList.dealCard(newCardList,newState)


    def attack(self,nextEngineStage,enemyCard,playerCard):
        self.__setStage(nextEngineStage)
        self.attacked=self.display.attack(enemyCard,playerCard)

        #TODO FIX
        self.__history.append({'action': 'attack', 'arg1': enemyCard,
                                                   'arg2': playerCard})

        
    



#
# Runs the game
#
class GameEngine(object):

    def __init__(self,tableau):
        self.tableau=tableau
        
        self.phase=0
        
        self.tableau.setPlayer(eEngineStages.upkeepInit,1)
        #self.display.turnOn()


    def run(self):
        phase=self.tableau.nextEngineStage()
        getattr(self, eEngineStages.reverse_mapping[phase])(self.tableau.getCurrentPlayerLists())


    def upkeepInit(self,playerLists):
        self.tableau.setPhase(eEngineStages.upkeep,"upkeep")


    def upkeep(self,playerLists):
        self.tableau.null(eEngineStages.enemyDeal)


    def enemyDeal(self,playerLists):

        maxDeal = self.tableau.getTurn() + 1
        if maxDeal > 5:
            maxDeal=5

        for i in range(5):
            card=self.tableau.enemySoldiers[i].peek()

            if maxDeal == 0:
                break

            if self.tableau.enemyStock.peek().isBlank():
                print("ENEMY EMPTY STOCK TO DO")
                ewfwef

            if card.isBlank():
                maxDeal = maxDeal - 1
                print "deal 1"
                self.tableau.dealCard(self.tableau.enemyStock,
                                      self.tableau.enemySoldiers[i],
                                      eCardState.normal)
                print "deal 2"
                card=self.tableau.enemySoldiers[i].peek()

                print "deal 3"
                if card.ctype != eCardTypes.soldier:
                    self.tableau.dealCard(self.tableau.enemySoldiers[i],
                                          self.tableau.enemyDiscard,
                                          eCardState.normal)

                print "deal 4"
        self.tableau.null(eEngineStages.playerDeal)


    def playerDeal(self,playerLists):

        maxDeal = 1 
        if self.tableau.getTurn() == 1:
            maxDeal=5

        for i in range(maxDeal):

            if self.tableau.playerStock.peek().isBlank():
                print("PLAYER EMPTY STOCK TO DO")
                etreterer
            print "player deal 1"    
            self.tableau.dealCard(self.tableau.playerStock,
                                  playerLists.hand,
                                  eCardState.normal)
            print "player deal 2"
        self.tableau.null(eEngineStages.buildInit)


    def buildInit(self,playerLists):
        self.tableau.setPhase(eEngineStages.buildSetup,"build")

    
    def buildSetup(self,playerLists):

        playableList=[]

        #get total playable cost
        cash = len(playerLists.hand)-1
        for card in playerLists.scrap:
            cash = cash + card.scrap
        
        for card in playerLists.hand:
            #TODO: Add in effects
            #TODO: Add in instants
            if card.cost<len(playerLists.hand):
                if card.ctype==eCardTypes.soldier:
                    card.playable=ePlayable.pfrom1
                    playableList.append((playerLists.hand,card,playerLists.hand.index(card)))
                elif card.ctype==eCardTypes.facility:
                    card.playable=ePlayable.pfrom2
                    playableList.append((playerLists.hand,card,playerLists.hand.index(card)))
                else:
                    card.playable=ePlayable.none
            else:
                card.playable=ePlayable.none

        workercost=1
        for cardPile in playerLists.workers:
            if not cardPile.peek().isBlank():
                workercost=workercost+1

        if len(playerLists.hand) >=workercost:
            for cardPile in playerLists.workers:
                card=cardPile.peek()
                if card.isBlank():
                    card.playable=ePlayable.single
                    playableList.append((cardPile,card,-1))
                else:
                    card.playable=ePlayable.none

        for cardPile in playerLists.soldiers:
            card=cardPile.peek()
            if card.isBlank():
                card.playable=ePlayable.pto1
                playableList.append((cardPile,card,-1))
            else:
                card.playable=ePlayable.none

        for cardPile in playerLists.base:
            card=cardPile.peek()
            if card.isBlank():
                card.playable=ePlayable.pto2
                playableList.append((cardPile,card,-1))
            else:
                card.playable=ePlayable.none
        
        self.tableau.userPickSingle(eEngineStages.buildCost,playableList)


    def buildCost(self,playerLists):
        (pickedState,picked,pickedTo)=self.tableau.picked
        
        if picked and pickedTo:

            #Card and it's destination picked. Now pay for it
            
            (cardListPicked,cardPicked,indexPicked)=picked
            (cardListPickedTo,cardPickedTo,indexPickedTo)=pickedTo
            
            if cardPicked.isBlank():
                self.tableau.null(eEngineStages.attackInit)
                return
            
            playableList=[]
            for card in playerLists.hand:
                #TODO: Add in effects
                card.playable=ePlayable.cost
                card.playableCost=1
                playableList.append((playerLists.hand,card,playerLists.hand.index(card)))

            for card in playerLists.scrap:
                card.playable=ePlayable.cost
                card.playableCost=card.scrap
                playableList.append((playerLists.scrap,card,playerLists.scrap.index(card)))
                
            self.tableau.userPickCost(eEngineStages.buildFinal,
                                      playableList,
                                      cardPicked.cost,
                                      self.tableau.playerDiscard)

        elif picked:

            #Just a single card picked. Do the action for that card
            
            (cardListPicked,cardPicked,indexPicked)=picked
           
            if cardPicked.name == "worker":
                workercost=1
                for cardPile in playerLists.workers:
                    if not cardPile.peek().isBlank():
                        workercost=workercost+1

                if len(playerLists.hand)<workercost:
                    self.tableau.undoHistory()
                    return

                playerLists.spareWorkers.dealCard(cardListPicked,eCardState.normal)
                
                playableList=[]
                for card in playerLists.hand:
                    #TODO: Add in effects
                    card.playable=ePlayable.cost
                    card.playableCost=1
                    playableList.append((playerLists.hand,card,playerLists.hand.index(card)))

                for card in playerLists.scrap:
                    card.playable=ePlayable.cost
                    card.playableCost=card.scrap
                    playableList.append((playerLists.scrap,card,playerLists.scrap.index(card)))
                    
                self.tableau.userPickCost(eEngineStages.buildFinal,
                                          playableList,
                                          workercost,
                                          self.tableau.playerDiscard)


        elif pickedState == ePlayable.cancel:
            self.tableau.undoHistory()
            
        else:
            self.tableau.undoHistory()
            self.tableau.null(eEngineStages.attackInit)


    def buildFinal(self,playerLists):
        pickedList=self.tableau.pickedCostList

        if self.tableau.pickedCost:
            self.tableau.null(eEngineStages.attackInit)

        else:
            self.tableau.undoHistory()
            self.tableau.undoHistory()


    def attackInit(self,playerLists):
        self.tableau.attackPhase=-1
        self.tableau.setPhase(eEngineStages.attackSetup,"attack")
        

    def attackSetup(self,playerLists):
        self.tableau.attackPhase=self.tableau.attackPhase+1
        
        if self.tableau.attackPhase>=5:
            self.tableau.null(eEngineStages.collectInit)
            return
        
        enemyCard=self.tableau.enemySoldiers[self.tableau.attackPhase].peek()
        playerCard=playerLists.soldiers[self.tableau.attackPhase].peek()

        if not enemyCard.isBlank() and not playerCard.isBlank():
            #TODO Add in effects
            enemyCard.actualAttack = enemyCard.attack
            enemyCard.actualDefense = enemyCard.defense
            enemyCard.actualSpeed = enemyCard.speed
            playerCard.actualAttack = playerCard.attack
            playerCard.actualDefense = playerCard.defense
            playerCard.actualSpeed = playerCard.speed
            
            self.tableau.attack(eEngineStages.attackSetup,
                                self.tableau.enemySoldiers[self.tableau.attackPhase],
                                playerLists.soldiers[self.tableau.attackPhase])
            return
    
        self.tableau.null(eEngineStages.attackSetup)


    def collectInit(self,playerLists):
        self.tableau.lootPhase=-1
        self.tableau.setPhase(eEngineStages.collectSetup,"collect")


    def collectSetup(self,playerLists):
        self.tableau.lootPhase=self.tableau.lootPhase+1
        
        if self.tableau.lootPhase>=5:
            self.tableau.null(eEngineStages.produceInit)
            return

        playerSoldierPile=playerLists.soldiers[self.tableau.lootPhase]
        playerSoldier=playerSoldierPile.peek()
        playerWorker=playerLists.workers[self.tableau.lootPhase].peek()
        enemySoldierPile=self.tableau.enemySoldiers[self.tableau.lootPhase]
        enemySoldier=enemySoldierPile.peek()
        
        if not playerSoldier.isBlank() and playerSoldier.state==eCardState.dead:
            print("move dead card to discard")
            
        playerSoldier=playerLists.soldiers[self.tableau.lootPhase].peek()

        if ( playerSoldier.isBlank() and not playerWorker.isBlank()
                                   and not enemySoldier.isBlank()
                                   and not enemySoldier.state==eCardState.dead ):
            print("move worker to discard")
            playerLists.workers[self.tableau.lootPhase].dealCard(self.tableau.playerDiscard,eCardState.normal)
            
        if not enemySoldier.isBlank() and enemySoldier.state==eCardState.dead:

            if not playerSoldier.isBlank():
                print("collect scrap")
                enemySoldierPile.dealCard(playerLists.scrap,eCardState.normal)
            else:
                print("move dead card to discard")
                enemySoldierPile.dealCard(self.tableau.enemyDiscard,eCardState.normal)
                
        print(playerLists.scrap)
        self.tableau.null(eEngineStages.collectSetup)


    def produceInit(self,playerLists):
        self.tableau.lootPhase=-1
        self.tableau.setPhase(eEngineStages.produce,"produce")


    def produce(self,playerLists):
        
        for workerPile in playerLists.workers:
            if not workerPile.peek().isBlank():
                
                self.tableau.dealCard(self.tableau.playerStock,
                                      workerPile,
                                      eCardState.good)
        
        self.tableau.null(eEngineStages.produceSell)


    def produceSell(self,playerLists):

        playableList=[]
        
        for cardPile in playerLists.workers:
            card=cardPile.peek()
            if card.state==eCardState.good:
                card.playable=ePlayable.single
                playableList.append((cardPile,card,-1))
            else:
                card.playable=ePlayable.none

        if len(playableList)>0:
            self.tableau.userPickList(eEngineStages.produceSold,playableList,self.tableau.playerDiscard)
        else:
            self.tableau.null(eEngineStages.nextPlayer)

    def produceSold(self,playerLists):
        pickedList=self.tableau.pickedCostList

        if self.tableau.pickedCost:
            for card in pickedList:
                playerLists.points.incValue(1)

        self.tableau.null(eEngineStages.produceDeal)

    def produceDeal(self,playerLists):
        for cardPile in playerLists.workers:
            card=cardPile.peek()
            if card.state==eCardState.good:
                #card.state=eCardState.normal
                self.tableau.dealCard(cardPile,
                                      playerLists.hand,
                                      eCardState.normal)

        self.tableau.null(eEngineStages.nextPlayer)
        
    def nextPlayer(self,playerLists):

        #while 1:
        #    self.tableau.undoHistory()
        
        player=playerLists.playerNumber+1
        if player>self.tableau.numberPlayers:
            player=1
        self.tableau.setPlayer(eEngineStages.upkeepInit,player)




