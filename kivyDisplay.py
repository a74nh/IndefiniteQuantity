import sys
from threading import Thread
from cards import *
from engine import *

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.graphics import BorderImage
from kivy.graphics import Callback
from time import sleep
from kivy.config import Config

#Config.set('graphics', 'width', '1920')
#Config.set('graphics', 'height', '1080')
#Config.set('graphics', 'fullscreen', 'auto')

currentDir=""
#c:\Users\Alan\Desktop\RobotEmpire\\"

##
##make a card/cardlist/cardpile file
##add subclasses here
##make engine be passed in the classes
##myclass = foo
##instance = myclass()
##
##instance.x()


#
#Represents a card
#    
class KivyCard(Card):
    def __init__(self,number,name,suite,ctype,cost,attack,defense,speed,scrap,upkeep,comments):
        super(KivyCard,self).__init__(number,name,suite,ctype,cost,attack,defense,speed,scrap,upkeep,comments)
        imagename=currentDir+"out/cards_{0:02}.png".format(self.number)
        self.image = Image(source=imagename, allow_stretch=True, keep_ratio=True)
        #self.image.size= (50/self.image.image_ratio,50/self.image.image_ratio)
        #self.image.size_hint= (0.5, 0.5)
        self.scatter = Scatter()
        #self.scatter.do_rotation=False
        #self.scatter.do_scale=False
        self.scatter.size=self.image.size
        self.scatter.size_hint=(None, None)
        self.scatter.add_widget(self.image)
        self.scatter.size=self.image.size
        self.has_dest=False

    def highlight(self,state):
        if state:
            with self.image.canvas.after:
                    bordersize=5
                    Color(1, 0, 0, .5, mode='rgba')
                    BorderImage(source=currentDir+'Conveyor Belt.jpg',
                                border = (bordersize,bordersize,bordersize,bordersize),
                                size = (self.image.width+(bordersize*2), self.image.height+(bordersize*2)),
                                pos = (-bordersize,-bordersize))

                    #Color(1, 0, 0, .5, mode='rgba')
                    #Rectangle(pos=card.scatter.pos, size=card.scatter.size)
                    #card.highlight = BorderImage(source=currentDir+'nuclear bomb.jpg',
                    #                                   border = (15, 16, 64, 16),
                    #                                   size = card.image.size)
        else:
            self.image.canvas.after.clear()

    def setState(self,state):
        super(KivyCard,self).setState(state)
        if state==eCardState.dead:
            self.scatter.rotation=90
        else:
            self.scatter.rotation=0
        

    def setDest(self,x,y,pile,wait):
        self.dest=[x,y]
        self.destPile=pile
        self.has_dest=True
        if self.destPile:
            self.destPile.layout.add_widget(self.scatter)
        
        with self.image.canvas:
            cb = Callback(self.callback)
        cb.ask_update()

        if wait:
            while self.has_dest:
                sleep(0)
        

    def callback(self, instr):
        if self.has_dest:
            posx=self.scatter.pos[0]
            posy=self.scatter.pos[1]
            if posx < self.dest[0]:
                posx = min(posx+10,self.dest[0])
            elif posx > self.dest[0]:
                posx = max(posx-10,self.dest[0])    
            if posy < self.dest[1]:
                posy = min(posy+10,self.dest[1])
            elif posy > self.dest[1]:
                posy = max(posy-10,self.dest[1])      
            self.scatter.pos=(posx,posy)
            if posx == self.dest[0] and posy == self.dest[1]:
                self.has_dest=False
                if self.destPile:
                    self.destPile.updateDisplay()
            ##TODO REMOVE CALLBACL WHEN REACHED!!!!
            #print "callback"


class KivyCardList(CardList):

    def __init__(self, name, player):
        super(KivyCardList,self).__init__(name, player)
        self.displayed=False

    def initDisplay(self,xpos,ypos,layout):
        self.displayed=True
        self.xpos=xpos
        self.ypos=ypos
        self.layout= RelativeLayout()
        layout.add_widget(self.layout)
        self.ipos=100
        self.updateDisplay()

    def updateDisplay(self):
        self.layout.clear_widgets()
        offset=0
        for card in self:
            card.scatter.pos=(self.xpos+offset,self.ypos)
            self.layout.add_widget(card.scatter)
            offset=offset+100
            
    def moveFrom(self,index,newCardList):
        if self.displayed:
            card=self[index]
            self.layout.remove_widget(card.scatter)
        super(KivyCardList,self).moveFrom(index,newCardList)
        if self.displayed:
            #update remaining cards
            offset=0
            for card in self:
                card.scatter.pos=(self.xpos+offset,self.ypos)
                offset=offset+100

    def append(self,card):
        super(KivyCardList,self).append(card)
        if self.displayed:
            offset=len(self)*100
            card.setDest(self.xpos+offset,self.ypos,self,True)


class KivyCardPile(CardPile):

    def __init__(self, name, player):
        super(KivyCardPile,self).__init__(name, player)
        self.displayed=False
        
    def initDisplay(self,xpos,ypos,layout):
        self.displayed=True
        self.xpos=xpos
        self.ypos=ypos
        self.layout= RelativeLayout()
        layout.add_widget(self.layout)
        self.updateDisplay()

    def updateDisplay(self):
        self.layout.clear_widgets()    
        card=self.peek()
        card.scatter.pos=(self.xpos,self.ypos)
        self.layout.add_widget(card.scatter)

    def dealCard(self,newCardList):
        if self.displayed:
            card=self.peek()
            self.layout.remove_widget(card.scatter)
        super(KivyCardPile,self).dealCard(newCardList)
        #if self.displayed:
        #    card=self.peek()
        #    card.scatter.pos=(self.xpos,self.ypos)
        #    self.layout.add_widget(card.scatter)

    def append(self,card):
##        if self.displayed:
##            if self.displayed:
##                pcard=self.peek()
##                self.layout.remove_widget(pcard.scatter)
        super(KivyCardPile,self).append(card)
        if self.displayed:
            pcard=self.peek()
            card.setDest(self.xpos,self.ypos,self,True)


class EngineThread(Thread):

    def __init__(self,engine):
        Thread.__init__(self)
        self.engine=engine
        
    def run(self):
        while 1:
            self.engine.run()
            print(self.engine.phase)


class MyApp(App):

    def build(self):

        self.lists=[]
        self.on=False
        self.phase=""
        diplayLayout=currentDir+"kivyDisplay.txt"
        
        self.layout=[]
        with open(diplayLayout, 'rb') as layoutFile:
            #layoutReader = csv.reader(layoutFile, delimiter=',', quotechar='|')
            for row in layoutFile:
                self.layout.append(row.split(","))


        self.relativeLayout = RelativeLayout()

        self.tableau=0
        
        CardList.setDisplay(self)
        CardPile.setDisplay(self)

        deck = Deck(currentDir+"classes.txt",currentDir+"soldiers.txt",KivyCard)

        numberPlayers=1

        self.tableau = Tableau(deck,numberPlayers,self,KivyCardPile,KivyCardList)

        engine = GameEngine(self.tableau)

        
        
        self.initDisplay()
        
        engineThread=EngineThread(engine)
        engineThread.start()
        
        return self.relativeLayout


    

            

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
        #self.display()

    def updatePlayer(self,newplayerList,turn):
        self.playerList=newplayerList
        self.turn=turn
        #self.display()
        #charval = raw_input("NEXT PLAYER [enter]")
    
    def initDisplay(self):
        if self.on:

            for [ltype,data,xpos,ypos] in self.layout:
    ##            if ltype=="label":
    ##                if data=="enemy":
    ##                    print('Enemy : {0}'.format(self.enemysuite))
    ##                elif data=="player":
    ##                    print('Player {0}: {1}'.format(self.playerList.playerNumber,
    ##                                                   self.playersuites[self.playerList.playerNumber-1]))
    ##                elif data=="turn":
    ##                    print('Turn {0}'.format(self.turn))
    ##                elif data=="points":
    ##                    print('Points {0}'.format(self.playerList.points))
    ##            elif ltype=="text":
    ##                print(data)
                if ltype=="list":
                    for l in self.lists:
                        if l.name==data:
                            l.initDisplay(float(xpos),float(ypos),self.relativeLayout)
                            break
    ##            elif ltype=="listsize":
    ##                for l in self.lists:
    ##                    if l.name==data:
    ##                        print("{0}:{1}".format(data,l.size()))
    ##                        break
                elif ltype=="playerlist":
                    for l in self.lists:
                        if l.name==data and l.player==self.playerList.playerNumber:
                            l.initDisplay(float(xpos),float(ypos),self.relativeLayout)
                            break


    def display(self):
            print
            print(self.phase)
            print


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

    def userPickCost(self,pickableFrom,price,moveTo):
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
            card.highlight(False)

            pickedCost=pickedCost+card.playableCost

            pickedTuples.append(picked)

        #reset all the playable-ness
        for (cardList,card,cardIndex) in pickableFrom:
            card.playable=ePlayable.none
            card.highlight(False)

        pickedTuples2=[]
        if pickedCost>=price:
            for (cardList,card,index) in pickedTuples:
                
                if type(cardList) != KivyCardList:
                    raise Exception("cardListPicked {0} must currently be a KivyCardList".format(type(cardList)))

                if type(moveTo) != KivyCardPile:
                    raise Exception("cardList {0} must currently be a KivyCardPile".format(type(cardList)))

                index=cardList.index(card)

                cardList.moveFrom(index,moveTo)

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
                card.highlight(False)
            return (ePlayable.none,False,False)
        
        (cardListPicked,cardPicked,indexPicked)=picked

        if cardPicked.playable==ePlayable.single:
            #reset all the playable-ness
            for (cardList,card,cardIndex) in pickableFrom:
                card.playable=ePlayable.none
                card.highlight(False)
            return (ePlayable.single,picked,False)


        for (cardList,card,cardIndex) in pickableFrom:
            if card != cardPicked:
                card.highlight(False)
            
        pickedTo=self.pickCard(pickableFrom,
                               "Pick position to put {0} to {1} or (c) to cancel",
                               (cardPicked.playable+1,),
                               ("c",))

        retPlayable=cardPicked.playable

        #reset all the playable-ness
        for (cardList,card,cardIndex) in pickableFrom:
            card.playable=ePlayable.none
            card.highlight(False)

        if pickedTo == "c":
            return (ePlayable.cancel,False,False)

        (cardListTo,cardTo,indexTo)=pickedTo

        if type(cardListTo) != KivyCardPile:
            raise Exception("cardListTo {0} must currently be a KivyCardPile".format(type(cardListTo)))

        if type(cardListPicked) != KivyCardList:
            raise Exception("cardList {0} must currently be a KivyCardList".format(type(cardList)))

        #put first card ontop of it's new place
        cardListPicked.moveFrom(indexPicked,cardListTo)

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
                card.highlight(True)
                card.playableValue=index
                index=index+1
                pickCount.append((cardList,card,cardIndex))
            else:
                card.playableValue=0
        #self.display()

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
        #self.display()


    def attack(self,pile1,pile2):

        card1=pile1.peek()
        card2=pile2.peek()
        
        print "{0} -> {1}/{2}".format(card1.actualSpeed,card1.actualAttack,card1.actualDefense)
        print "{0} -> {1}/{2}".format(card2.actualSpeed,card2.actualAttack,card2.actualDefense)
        charval = raw_input("ATTACK [enter]")
        
        card1Survive = True            
        card2Survive = True            

        if card1.actualSpeed > card2.actualSpeed:
            
            card1.setDest(card1.scatter.pos[0],card1.scatter.pos[1]-100,False,True)
            
            if card1.actualAttack >= card2.actualDefense:
                card2.setState(eCardState.dead)
                card2Survive=False

            elif card2.actualAttack >= card1.actualDefense:
                card1.setState(eCardState.dead)
                card1Survive=False

            card1.setDest(card1.scatter.pos[0],card1.scatter.pos[1]+100,False,True)
                
        elif card2.actualSpeed > card1.actualSpeed:

            card2.setDest(card2.scatter.pos[0],card2.scatter.pos[1]+100,False,True)

            if card2.actualAttack >= card1.actualDefense:
                card1.setState(eCardState.dead)
                card1Survive=False
                
            elif card1.actualAttack >= card2.actualDefense:
                card2.setState(eCardState.dead)
                card2Survive=False

            card2.setDest(card2.scatter.pos[0],card2.scatter.pos[1]-100,False,True)

        else:
            
            card1.setDest(card1.scatter.pos[0],card1.scatter.pos[1]-50,False,False)
            card2.setDest(card2.scatter.pos[0],card2.scatter.pos[1]+50,False,False)
            while card1.has_dest or card2.has_dest:
                sleep(0)
            
            if card1.actualAttack >= card2.actualDefense:
                card2.setState(eCardState.dead)
                card2Survive=False

            if card2.actualAttack >= card1.actualDefense:
                card1.setState(eCardState.dead)
                card1Survive=False

            card1.setDest(card1.scatter.pos[0],card1.scatter.pos[1]+50,False,False)
            card2.setDest(card2.scatter.pos[0],card2.scatter.pos[1]-50,False,False)
            while card1.has_dest or card2.has_dest:
                sleep(0)

        print "card1 survives={0}".format(card1Survive)
        print "card2 survives={0}".format(card2Survive)

        charval = raw_input("ATTACK END [enter]")

        return (card1Survive,card2Survive)




if __name__ == '__main__': 

    MyApp().run()

##
##    display = DisplayConsole(currentDir+"consoleDisplay.txt")
##
##    CardList.setDisplay(display)
##    CardPile.setDisplay(display)
##
##    deck = Deck(currentDir+"classes.txt",currentDir+"soldiers.txt")
##
##    numberPlayers=1
##
##    tableau = Tableau(deck,numberPlayers,display)
##
##    display.tableau=tableau
##
##    engine = GameEngine(tableau)
##
##
##    while 1:
##        engine.run()
##        #print(engine.phase)




