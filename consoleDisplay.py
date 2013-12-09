import csv
from pprint import pprint
import random
import sys
from engine import *

currentDir="c:\Users\Alan\Desktop\RobotEmpire\\"


#
# Console version of the Display class
# Holds lists of cards and displays them all
# Uses a layout file passed in
#
class DisplayConsole(object):

    def __init__(self,diplayLayout):
        self.lists=[]
        self.on=False
        self.phase=""

        self.layout=[]
        with open(diplayLayout, 'rb') as layoutFile:
            layoutReader = csv.reader(layoutFile, delimiter=',', quotechar='|')
            for row in layoutReader:
                self.layout.append(row)

        self.tableau=0

    def addList(self,newlist):
        self.lists.append(newlist)

    def turnOn(self,value=True):
        self.on=value

    def setup(self,numberPlayers,enemysuite,playersuites):
        self.numberPlayers=numberPlayers
        self.enemysuite=enemysuite
        self.playersuites=playersuites

    def updatePhase(self,oldphase,newphase):
        self.phase=newphase
        self.display()

    def updatePlayer(self,newplayerList,turn):
        self.playerList=newplayerList
        self.turn=turn
        self.display()
        charval = raw_input("NEXT PLAYER [enter]")
    
    def display(self):
        if self.on:
            print
            print("="*80)
            #for l in self.lists:
                #pprint(l)
            for [ltype,data] in self.layout:
                if ltype=="label":
                    if data=="enemy":
                        print('Enemy : {0}'.format(self.enemysuite))
                    elif data=="player":
                        print('Player {0}: {1}'.format(self.playerList.playerNumber,
                                                       self.playersuites[self.playerList.playerNumber-1]))
                    elif data=="turn":
                        print('Turn {0}'.format(self.turn))
                    elif data=="points":
                        print('Points {0}'.format(self.playerList.points))
                elif ltype=="text":
                    print(data)
                elif ltype=="list":
                    for l in self.lists:
                        if l.name==data:
                            if type(l)==CardList:
                                for card in l:
                                    print(card)
                            elif type(l)==CardPile:
                                sys.stdout.write("("+str(l.size())+")")
                                print(l.peek())
                            #pprint(l)
                            break
                elif ltype=="listsize":
                    for l in self.lists:
                        if l.name==data:
                            print("{0}:{1}".format(data,l.size()))
                            break
                elif ltype=="playerlist":
                    for l in self.lists:
                        if l.name==data and l.player==self.playerList.playerNumber:
                            if type(l)==CardList:
                                for card in l:
                                    print(card)
                            elif type(l)==CardPile:
                                sys.stdout.write("("+str(l.size())+")")
                                print(l.peek())
                            #pprint(l)
                            break
            print
            print(self.phase)
            print

##    def findList(self,listName):
##        for l in self.lists:
##            if l.name==listName:
##                if type(l)==CardList:
##                    for card in l:
##                        print(card)
##                elif type(l)==CardPile:
##                    sys.stdout.write("("+str(l.size())+")")
##                    print(l.peek())
##                #pprint(l)
##                break

    def userPickList(self,pickableFrom):
        pickedTuples=[]
        pickedCards=[]

        pickedCost=0
        while 1:

            picked=self.pickCard(pickableFrom,
                                 "Select multiple cards {0} to {1} or (c) to cancel",
                                 (ePlayable.single,),
                                 ("c","d"))

            if not picked:
                break
            
            if picked == "c":
                pickedCards=[]
                break

            if picked == "d":
                break

            print(picked)
            (cardList,card,index)=picked
            card.playable=ePlayable.none

            pickedTuples.append(picked)

            
        #reset all the playable-ness
        for (cardList,card,cardIndex) in pickableFrom:
            card.playable=ePlayable.none

        if len(pickedTuples)>0:
            return pickedTuples

        return False

    def userPickCost(self,pickableFrom,price):
        pickedTuples=[]
        pickedCards=[]

        pickedCost=0
        while pickedCost<price:
            str="Pay with {0} cards ".format(price-pickedCost)
            picked=self.pickCard(pickableFrom,
                                 str+"{0} to {1} or (c) to cancel",
                                 (ePlayable.cost,),
                                 ("c",))

            if picked == "c":
                pickedCards=[]
                break

            (cardList,card,index)=picked
            card.playable=ePlayable.none

            pickedCost=pickedCost+card.playableCost

            pickedTuples.append(picked)

            
        #reset all the playable-ness
        for (cardList,card,cardIndex) in pickableFrom:
            card.playable=ePlayable.none

        pickedTuples2=[]
        if pickedCost>=price:
            for (cardList,card,index) in pickedTuples:
                index=cardList.index(card)
                cardList.remove(card)
                pickedTuples2.append((cardList,card,index))
            return pickedTuples2

        return False
    

    def userPickSingle(self,pickableFrom):

        picked=self.pickCard(pickableFrom,
                             "Pick a card to play {0} to {1} or (d) for done",
                             (ePlayable.single,ePlayable.pfrom1,ePlayable.pfrom2),
                             ("d",))

        if picked == "d":
            #reset all the playable-ness
            for (cardList,card,cardIndex) in pickableFrom:
                card.playable=ePlayable.none
            return (ePlayable.none,False,False)
        
        (cardListPicked,cardPicked,indexPicked)=picked

        if cardPicked.playable==ePlayable.single:
            #reset all the playable-ness
            for (cardList,card,cardIndex) in pickableFrom:
                card.playable=ePlayable.none
            return (ePlayable.single,picked,False)

        cardListPicked.pop(indexPicked)
            
        pickedTo=self.pickCard(pickableFrom,
                               "Pick position to put {0} to {1} or (c) to cancel",
                               (cardPicked.playable+1,),
                               ("c",))

        retPlayable=cardPicked.playable

        #reset all the playable-ness
        for (cardList,card,cardIndex) in pickableFrom:
            card.playable=ePlayable.none

        if pickedTo == "c":
            #reinsert first card
            cardListPicked.insert(indexPicked,cardPicked)
            return (ePlayable.cancel,False,False)

        (cardListTo,cardTo,indexTo)=pickedTo

        if type(cardListTo) != CardPile:
            raise Exception("cardListTo must currently be a CardPile")

        #put first card ontop of it's new place
        cardListTo.append(cardPicked)

        return (retPlayable,picked,pickedTo)
        

    
    def pickCard(self,picklist,printString,playableStates,cancelChars):
        picked=()
        pickCount=[]

        if len(picklist)==0:
            return False
        
        pickCard=[]

        #Label all the pickable cards
        index=1
        for (cardList,card,cardIndex) in picklist:
            if card.playable in playableStates :
                card.playableValue=index
                index=index+1
                pickCount.append((cardList,card,cardIndex))
            else:
                card.playableValue=0
        self.display()

        if index>1:
            #Pick one
            valid=False
            while (valid is not True):
                charval = raw_input((printString+": ").format(1,index-1))
                for cancelChar in cancelChars:
                    if charval == cancelChar:
                        return cancelChar
                try:
                    val=int(charval)
                    if val>0 and val<index:
                        valid=True
                    
                except ValueError:
                    print("Oops!  That was not a valid number.  Try again...")

            picked=pickCount[val-1]
        
        return picked

        
    def moveCardTo(self,card,cardList):
        cardList.append(card)
        self.display()


    def dealCard(self,oldCardList,newCardList):
        newCardList.append(oldCardList.pop())
        self.display()

    def internalAttack(self,card1,card2):
        print(card1)
        print("attacks with {0} to".format(card1.attack))
        print(card2)
        if card1.attack >= card2.defense:
            print("The winner is:")
            print(card1)
            return(True,False)
        else:
            print("attack fails.")
            print(card2)
            print("attacks with {0} to".format(card1.attack))
            if card2.attack >= card1.defense:
                print("The winner is:")
                print(card2)
                return(False,True)
            else:
                print("Attack fails.")
                return(True,True)


    def attack(self,card1,card2):

        card1Survive = True            
        card2Survive = True            

        if card1.speed > card2.speed:
            (card1Survive,card2Survive)=self.internalAttack(card1,card2)
            
        elif card2.speed > card1.speed:
            (card2Survive,card1Survive)=self.internalAttack(card2,card1)

        else:
            print(card1)
            print("and")
            print(card2)
            print("attack each other.")
            if card2.attack >= card1.defense and card1.attack >= card2.defense:
                print("Both are destroyed.")
                card1Survive=False
                card2Survive=False
            if card1.attack >= card2.defense:
                print("The winner is:")
                print(card1)
                card2Survive=False
            elif card2.attack >= card1.defense:
                print("The winner is:")
                print(card2)
                card1Survive=False
            else:
                print("Attack fails.")

        charval = raw_input("[enter]")
        return (card1Survive,card2Survive)




display = DisplayConsole(currentDir+"consoleDisplay.txt")

CardList.setDisplay(display)
CardPile.setDisplay(display)

deck = Deck(currentDir+"classes.txt",currentDir+"soldiers.txt")

numberPlayers=1

tableau = Tableau(deck,numberPlayers,display)

display.tableau=tableau

engine = GameEngine(tableau)


while 1:
    engine.run()
    #print(engine.phase)




