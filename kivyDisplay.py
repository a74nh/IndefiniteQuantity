import sys
from threading import Thread
import threading
import math
from time import sleep

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
from kivy.config import Config
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.clock import Clock

#Config.set('graphics', 'width', '1920')
#Config.set('graphics', 'height', '1080')
#Config.set('graphics', 'fullscreen', 'auto')

currentDir=""
#c:\Users\Alan\Desktop\RobotEmpire\\"


#from kivy.config import Config
#Config.set('kivy', 'double_tap_timeout', '5') #< 500 ms between 2 touch ta

################################################################################
#
# DisplayLock
#
# Wrapper class for a lock. Passes a card in when unlocking
#
class DisplayLock(object):

    def __init__(self):
        self.card = False
        self._lock = threading.Lock()
        
    def acquire(self):
        self._lock.acquire()
        
    def release(self,card):
        self.card=card
        if self._lock.locked():
            self._lock.release()
        
    def __enter__(self):
        self.acquire()
        
    def __exit__(self, type, value, traceback):
        self.release()


################################################################################
#
# CardScatter
#
# Wrapper class for a scatter to capture input presses
#
class CardScatter(ScatterLayout):

    #KivyCard binds this so that kivyCard.clicked() is called
    pressed = ListProperty([0, 0])

    clickable = False

##    lock = threading.Lock()
##    timerValid = False
##
##    def my_callback(self,dt):
##        self.lock.acquire(True)
##        if self.timerValid:
##            print "SINGLE", dt
##        self.timerValid=False
##        self.lock.release()
##        
##    def on_touch_down(self, touch):
##
##        if (not self.collide_point(*touch.pos)) or (not self.clickable):
##            return False
##
##        self.lock.acquire(True)
##
##        if touch.double_tap_time > 0 and touch.double_tap_time < 1:
##            print "DOUBLE"
##            self.timerValid=False
##            self.lock.release()
##            #set click
##        
##        elif not self.timerValid:
##            self.timerValid=True
##            Clock.schedule_once(self.my_callback, 1)
##            self.lock.release()
##
##        else:
##            self.lock.release()
##
##        return super(CardScatter, self).on_touch_down(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if looking or self.clickable:
                self.pressed = touch.pos
                # we consumed the touch. return False here to propagate
                # the touch further to the children.
                return True
        return super(CardScatter, self).on_touch_down(touch)


################################################################################
#
# KivyButton
#
# Wrapper class for a button
#
class KivyButton(Scatter):

    #pressed = ListProperty([0, 0])

    clickable = False

    def __init__(self,name,layout,clickaction,**kwargs):
        super(KivyButton,self).__init__(**kwargs)
        self.name=name
        self.layout=layout
        self.clickaction=clickaction
        imagename=currentDir+name+".png"
        self.image = Image(source=imagename, allow_stretch=True, keep_ratio=True)
        self.image.size= (Window.height*self.image.image_ratio, Window.height)

        self.size=self.image.size
        self.size_hint= (None, None)
        self.scale = 0.2
        
        self.add_widget(self.image)

    def enable(self, state, clickable):
        if state:
            self.layout.add_widget(self)
        else:
            self.layout.remove_widget(self)
        self.clickable=clickable
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.clickable:
            #self.pressed = touch.pos

            #Always consume. Click action checks for looking status
            print ('Hit button {name} at {pos}'.format(name=self.name, pos=touch.pos))
            return self.clickaction(self)

        return super(KivyButton, self).on_touch_down(touch)


################################################################################
#
# KivyCard
#
# Kivy extentions for a card
#    
class KivyCard(Card):
    def __init__(self,number,name,suite,ctype,cost,attack,defense,speed,scrap,upkeep,comments):
        super(KivyCard,self).__init__(number,name,suite,ctype,cost,attack,defense,speed,scrap,upkeep,comments)
        imagename=currentDir+"out/cards_{0:02}.png".format(self.number)
        self.image = Image(source=imagename, allow_stretch=True, keep_ratio=True)
        self.backImage = Image(source="back.png", allow_stretch=True, keep_ratio=True)
        self.image.size= (Window.height*self.image.image_ratio, Window.height)

        self.scatter = CardScatter()
        self.scatter.size=self.image.size
        self.scatter.size_hint= (None, None)
        self.scatter.scale = 0.2
        self.scatter.do_translation = False
        self.scatter.auto_bring_to_front = False
        
        self.scatter.bind(pressed=self.clicked)

        self.scatter.add_widget(self.image)

        self.has_dest=False
        self.cb=False
        if self.suite.name == eSuiteNames.Blank:
            self.image.opacity=0.5
            #with selfimage.canvas.before:
            #    Color(1, 0, 0, .5, mode='rgba')

        self.highlighted = Image(source=currentDir+'border.png', allow_stretch=True, keep_ratio=True)
        self.highlighted.size= self.image.size
        self.scatter.pos=(int(Window.width/2),int(-self.image.height))

        self.lock = threading.Lock()


    def highlight(self,highlighting):
        #WARNING: clears select state
        image=self.image
        if self.state==eCardState.turned or self.state==eCardState.good:
            image=self.backImage

        self.scatter.clickable=highlighting
        image.canvas.after.clear()
        
        if highlighting:
            with image.canvas.after:
                    bordersize=10
                    Color(1, 1, 1, 1, mode='rgba')
                    BorderImage(source=currentDir+'border.png',
                                border = (bordersize,bordersize,bordersize,bordersize),
                                size = (self.image.width+(bordersize*2), self.image.height+(bordersize*2)),
                                pos = (-bordersize,-bordersize))
            
    def select(self,selected):
        #WARNING: clears highlight state
        image=self.image
        if self.state==eCardState.turned or self.state==eCardState.good:
            image=self.backImage
            
        self.scatter.clickable=False
        image.canvas.after.clear()
        
        if selected:
            with image.canvas.after:
                    bordersize=10
                    Color(1, 0, 0, 1, mode='rgba')
                    BorderImage(source=currentDir+'border.png',
                                border = (bordersize,bordersize,bordersize,bordersize),
                                size = (self.image.width+(bordersize*2), self.image.height+(bordersize*2)),
                                pos = (-bordersize,-bordersize))


    def setState(self,state):
        if self.state==eCardState.turned or self.state==eCardState.good:
            #going from turned over, then restore image 
            self.scatter.clear_widgets()
            self.scatter.add_widget(self.image)
        super(KivyCard,self).setState(state)
        if state==eCardState.dead:
            self.scatter.rotation=90
        else:
            self.scatter.rotation=0
        if state==eCardState.turned or state==eCardState.good:
            self.scatter.clear_widgets()
            self.scatter.add_widget(self.backImage) 
        

    def setDest(self,x,y,scale,pile,wait):
        self.lock.acquire()
        displayLock = DisplayLock()
        self.dest=[x,y]
        self.destScale=scale
        self.destPile=pile
        #self.destLock=lock
        self.has_dest=True
        if self.destPile:
            self.destPile.layout.add_widget(self.scatter)
            #bring to the front:
            parent = self.destPile.layout.parent
            parent.remove_widget(self.destPile.layout)
            parent.add_widget(self.destPile.layout)

        increment = 2 #0.5

        xdist = abs(int(self.scatter.x-x))
        ydist = abs(int(self.scatter.y-y))

        if xdist == 0:  #avoid div by zero
            self.xmove=1
            self.ymove = increment * Window.height / 100
            print "XZERO y={0}/{1} {2}->{3}".format(self.ymove,ydist,self.scatter.y,y)
        elif ydist == 0:
            self.xmove= increment * Window.height / 100
            self.ymove = 1
            print "YZERO x={0}/{1} {2}->{3}".format(self.xmove,xdist,self.scatter.x,x)
        else:
            #print "DIST "+str(xdist)+" "+str(ydist)
            theta = math.atan2(ydist,xdist)
            self.xmove = increment * math.cos(theta) * Window.height / 100
            self.ymove = increment * math.sin(theta) * Window.height / 100
            print "DIST x={0}/{1} {2}->{3} y={4}/{5} {6}->{7}  theta={8} {9}".format(self.xmove,xdist,self.scatter.x,x,
                                                              self.ymove,ydist,self.scatter.y,y,
                                                              theta,math.degrees(theta))
        if not self.cb:
            with self.scatter.canvas:
                self.cb = Callback(self.destCallback)
        self.cb.ask_update()

        if wait:
            while self.has_dest:
                sleep(0)
        

    def destCallback(self, instr):
        if self.has_dest:

            posx=self.scatter.x
            posy=self.scatter.y
            if posx < self.dest[0]:
                posx = min(posx+self.xmove,self.dest[0])
            elif posx > self.dest[0]:
                posx = max(posx-self.xmove,self.dest[0])    
            if posy < self.dest[1]:
                posy = min(posy+self.ymove,self.dest[1])
            elif posy > self.dest[1]:
                posy = max(posy-self.ymove,self.dest[1])      
            self.scatter.pos=(posx,posy)

            if self.scatter.scale < self.destScale:
                self.scatter.scale = min(self.scatter.scale+0.004,self.destScale)
            elif self.scatter.scale > self.destScale:
                self.scatter.scale = max(self.scatter.scale-0.004,self.destScale)

            if int(posx) == int(self.dest[0]) and int(posy) == int(self.dest[1]):
                self.scatter.scale = self.destScale
                self.scatter.pos=(int(self.dest[0]),int(self.dest[1]))
                if self.destPile:
                    self.destPile.updateDisplay()
                #DO THESE LAST...
                self.has_dest=False
                self.lock.release()
            ##TODO REMOVE CALLBACL WHEN REACHED!!!!
            #print "callback"


    def clicked(self, instance, pos):
        global looking
        global lookingCard
        if looking:
            if not self.isBlank():
                if lookingCard == False:
                    self.pile.bringToFront()
                    lookingCard = self
                    dest=0
                    if self.scatter.x < Window.width/2:
                        dest=Window.width/2
                    self.setDest(dest,0,1,False,False)
                else:
                    lookingCard = False
                    self.pile.updateDisplay()
                print "looking"
        else:
            print ('Card selected: printed from root widget: {pos}'.format(pos=pos))
            displayLock.release(self)


################################################################################
#
# KivyCardCounter
#
# Kivy extentions for a CardCounter
#   
class KivyCardCounter(CardCounter):

    def __init__(self, name, player, value, *args):
        super(KivyCardCounter,self).__init__(name, player, value, *args)
        self.displayed=False

    def initDisplay(self,xpos,ypos,fontsize,parentlayout):
        self.displayed=True
        self.xpos=xpos
        self.ypos=ypos
        self.label= Label(text="{0}".format(self.value()), font_size=fontsize)
        self.label.pos=(xpos,ypos)
        parentlayout.add_widget(self.label)

    def incValue(self,value):
        super(KivyCardCounter,self).incValue(value)
        self.label.text="{0}".format(self.value())


################################################################################
#
# KivyCardList
#
# Kivy extentions for a CardList
#  
class KivyCardList(CardList):

    def __init__(self, name, player):
        super(KivyCardList,self).__init__(name, player)
        self.displayed=False
        self.lock = threading.Lock()

    def initDisplay(self,xpos,ypos,scale,parentlayout):
        self.displayed=True
        self.xpos=xpos
        self.ypos=ypos
        self.scale=scale
        self.layout= RelativeLayout()
        parentlayout.add_widget(self.layout)
        #self.ipos=(card.image.width*card.scatter.scale)
        self.updateDisplay()

    def updateDisplay(self):
        self.layout.clear_widgets()
        offset=0
        for card in self:
            card.scatter.scale=self.scale
            card.scatter.pos=(self.xpos+offset,self.ypos)
            self.layout.add_widget(card.scatter)
            offset=offset+int(card.image.width*card.scatter.scale*0.6)

    def moveFrom(self,index,newCardList,newState):
        if self.displayed:
            card=self[index]
            self.layout.remove_widget(card.scatter)
        super(KivyCardList,self).moveFrom(index,newCardList,newState)
        if self.displayed:
            #update remaining cards
            offset=0
            for card in self:
                card.scatter.pos=(self.xpos+offset,self.ypos)
                offset=offset+int(card.image.width*card.scatter.scale*0.6)

    def append(self,card):
        #self.lock.acquire()
        print card
        super(KivyCardList,self).append(card)
        if self.displayed:
            offset=(len(self)-1)*int(card.image.width*self.scale*0.6)
            card.setDest(self.xpos+offset,self.ypos,self.scale,self,True)

    def bringToFront(self):
        parent = self.layout.parent
        parent.remove_widget(self.layout)
        parent.add_widget(self.layout)
            

################################################################################
#
# KivyCardPile
#
# Kivy extentions for a CardPile
#  
class KivyCardPile(CardPile):

    def __init__(self, name, player):
        super(KivyCardPile,self).__init__(name, player)
        self.displayed=False
        self.lock = threading.Lock()
        
    def initDisplay(self,xpos,ypos,scale,parentlayout):
        self.displayed=True
        self.xpos=int(xpos)
        self.ypos=int(ypos)
        self.scale=scale
        self.layout= RelativeLayout()
        parentlayout.add_widget(self.layout)
        self.updateDisplay()

    def updateDisplay(self):
        self.layout.clear_widgets()
        card=self.peek()
        offset=0
        if card.state == eCardState.good:
            offset=10
            card2=self.peekpeek()
            card2.scatter.scale=self.scale
            card2.scatter.pos=(self.xpos,self.ypos)
            self.layout.add_widget(card2.scatter)
            
        card.scatter.scale=self.scale
        card.scatter.pos=(int(self.xpos+offset),int(self.ypos-offset))
        self.layout.add_widget(card.scatter)

    def dealCard(self,newCardList,newState):
        if self.displayed:
            #Display the card underneath (the next top one)
            self.layout.clear_widgets()
            card=self.peekpeek()
            card.scatter.scale=self.scale
            card.scatter.pos=(self.xpos,self.ypos)
            self.layout.add_widget(card.scatter)
        super(KivyCardPile,self).dealCard(newCardList,newState)

    def append(self,card):
        #self.lock.acquire()
        print card
        super(KivyCardPile,self).append(card)
        offset=0
        if card.state == eCardState.good:
            offset=10
        if self.displayed:
            card.setDest(self.xpos+offset,self.ypos-offset,self.scale,self,True)

    def bringToFront(self):
        parent = self.layout.parent
        parent.remove_widget(self.layout)
        parent.add_widget(self.layout)
            

################################################################################
#
# EngineThread
#
# Main thread, just calls into the engine
#  
class EngineThread(Thread):

    def __init__(self,engine):
        Thread.__init__(self)
        self.engine=engine
        
    def run(self):
        while 1:
            self.engine.run()


################################################################################
#
# MyApp
#
# Main app class. Acts as a Display class
# 
class MyApp(App):

    def build(self):

        #Window.size = (1920,1080)
        #Window.size = (1200,900)
        self.lists={}
        self.counters={}
        self.buttons={}
        self.labels={}
        self.on=False
        self.phase=""
        diplayLayout=currentDir+"kivyDisplay.txt"

        global displayLock
        displayLock = DisplayLock()
        
        self.layout=[]
        with open(diplayLayout, 'rb') as layoutFile:
            #layoutReader = csv.reader(layoutFile, delimiter=',', quotechar='|')
            for row in layoutFile:
                i=row.rstrip('\n')
                j=i.rstrip('\r')
                k=j.split(",")
                if len(k)==6:
                    self.layout.append(j.split(","))
                else:
                    print "INVALID LAYOUT LINE:",k


        self.relativeLayout = RelativeLayout()
        self.relativeLayout.size_hint=(None, None)
        #self.relativeLayout.pos_hint={'x':0,'y':0}

        background = Image(source="background.jpg", allow_stretch=True, keep_ratio=True)
        background.size= (Window.height*background.image_ratio, Window.height)
        self.relativeLayout.add_widget(background)
        
        self.tableau=0
        
        CardList.setDisplay(self)
        CardPile.setDisplay(self)
        CardCounter.setDisplay(self)
        
        deck = Deck(currentDir+"classes.txt",currentDir+"soldiers.txt",KivyCard)


        numberPlayers=1

        self.tableau = Tableau(deck,numberPlayers,self,KivyCardPile,KivyCardList,KivyCardCounter)

        engine = GameEngine(self.tableau)

        
        
        self.initDisplay()

        global looking
        global lookingCard
        looking = False
        lookingCard = False
        self.buttons["look"].enable(True,True)
        
        engineThread=EngineThread(engine)
        engineThread.start()
        
        return self.relativeLayout


    def addList(self,newlist):
        self.lists[newlist.name+str(newlist.player)]=newlist

    def addCounter(self,newcounter):
        self.counters[newcounter.name+str(newcounter.player)]=newcounter
        
    def turnOn(self,value=True):
        self.on=value

    def setup(self,numberPlayers,enemysuite,playersuites):
        self.numberPlayers=numberPlayers
        self.enemysuite=enemysuite
        self.playersuites=playersuites

    def updatePhase(self,oldphase,newphase):
        self.phase=newphase
        if oldphase != -1:
            self.buttons[ePhases.reverse_mapping[oldphase]+"_phase"].enable(False,False)
        self.buttons[ePhases.reverse_mapping[newphase]+"_phase"].enable(True,False)

    def updatePlayer(self,newplayerList,turn):
        self.playerList=newplayerList
        self.turn=turn
        #self.display()
        #charval = raw_input("NEXT PLAYER [enter]")
    
    def initDisplay(self):
        if self.on:
            #print self.layout
            for [ltype,data,xpos,ypos,scale,clickaction] in self.layout:

                if ltype=="list":
                    l=self.lists[data+str(0)]
                    l.initDisplay(int(Window.width*float(xpos)/100),
                                  int(Window.height*float(ypos)/100),
                                  float(scale),
                                  self.relativeLayout)
                            
                elif ltype=="playerlist":
                    l=self.lists[data+str(self.playerList.playerNumber)]
                    l.initDisplay(int(Window.width*float(xpos)/100),
                                  int(Window.height*float(ypos)/100),
                                  float(scale),
                                  self.relativeLayout)
                        
                elif ltype=="button":
                    button = KivyButton(data,self.relativeLayout,getattr(self,clickaction))
                    button.scale = float(scale)
                    button.pos=(Window.width*float(xpos)/100,
                                Window.height*float(ypos)/100)
                    self.buttons[data]=button

                elif ltype=="playerlabel":
                    l=self.counters[data+str(self.playerList.playerNumber)]
                    l.initDisplay(int(Window.width*float(xpos)/100),
                                  int(Window.height*float(ypos)/100),
                                  scale,
                                  self.relativeLayout)
                    
    def display(self):
        pass
##            print
##            print(self.phase)
##            print


    def userPickList(self,pickableFrom,moveTo):
        pickedTuples=[]

        pickedCost=0
        while 1:

            picked=self.pickCard(pickableFrom,
                                 "Select multiple cards {0} to {1} or (c) to cancel",
                                 (ePlayable.single,),
                                 True,True)

            if not picked:
                break

            if picked == ePlayable.cancel:
                pickedTuples=[]
                break

            if picked == ePlayable.done:
                break

            (cardList,card,index)=picked
            card.playable=ePlayable.none
            card.select(True)

            pickedTuples.append(picked)

            
        #reset all the playable-ness
        for (cardList,card,cardIndex) in pickableFrom:
            card.playable=ePlayable.none
            card.highlight(False)

        if len(pickedTuples)>0:
            pickedTuples2=[]

            for (cardList,card,index) in pickedTuples:
                
                if type(cardList) != KivyCardPile:
                    raise Exception("cardListPicked {0} must currently be a KivyCardPile".format(type(cardList)))

                if type(moveTo) != KivyCardPile:
                    raise Exception("cardList {0} must currently be a KivyCardPile".format(type(moveTo)))

                cardList.dealCard(moveTo,eCardState.normal)

                pickedTuples2.append((cardList,card,-1))
            return pickedTuples2
            
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
                                 False,True)

            if picked == ePlayable.cancel or picked == ePlayable.none:
                #Full selection could not be chosen, so clear everything chosen so far
                pickedCards=[]
                break
            
            (cardList,card,index)=picked
            card.playable=ePlayable.none
            card.select(True)

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
                    raise Exception("cardList {0} must currently be a KivyCardPile".format(type(moveTo)))

                index=cardList.index(card)

                cardList.moveFrom(index,moveTo,eCardState.normal)

                pickedTuples2.append((cardList,card,index))
            return pickedTuples2

        return False
    

    def userPickSingle(self,pickableFrom):

        picked=self.pickCard(pickableFrom,
                             "Pick a single card to play {0} to {1} or (d) for done",
                             (ePlayable.single,ePlayable.pfrom1,ePlayable.pfrom2),
                             True,False)

        if picked == ePlayable.done:
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
            #if card != cardPicked:
            card.highlight(False)
            #card.playable=ePlayable.none

        cardPicked.select(True)
            
        pickedTo=self.pickCard(pickableFrom,
                               "Pick position to put {0} to {1} or (c) to cancel",
                               (cardPicked.playable+1,),
                               False,True)

        retPlayable=cardPicked.playable

        #reset all the playable-ness
        for (cardList,card,cardIndex) in pickableFrom:
            card.playable=ePlayable.none
            card.highlight(False)
        cardPicked.select(False)

        if pickedTo == ePlayable.cancel:
            return (ePlayable.cancel,False,False)

        (cardListTo,cardTo,indexTo)=pickedTo

        if type(cardListTo) != KivyCardPile:
            raise Exception("cardListTo {0} must currently be a KivyCardPile".format(type(cardListTo)))

        if type(cardListPicked) != KivyCardList:
            raise Exception("cardList {0} must currently be a KivyCardList".format(type(cardList)))

        #put first card ontop of it's new place
        cardListPicked.moveFrom(indexPicked,cardListTo,eCardState.normal)

        return (retPlayable,picked,pickedTo)
        

    
    def pickCard(self,picklist,printString,playableStates,allowDone,allowCancel):
        picked=()
        pickCount=[]

        if len(picklist)==0:
            return ePlayable.none
        
        pickCard=[]

        displayLock.acquire()
        
        #Label all the pickable cards
        index=1
        for (cardList,card,cardIndex) in picklist:
            if card.playable in playableStates :
                card.highlight(True)
                index=index+1
                pickCount.append((cardList,card,cardIndex))

        if allowDone:
            self.buttons["done"].enable(True,True)

        if allowCancel:
            self.buttons["cancel"].enable(True,True)
            
        while [ 1 ]:
            print (printString+": ").format(1,index-1)

            returnValue=False
            displayLock.acquire()

            if type(displayLock.card) == KivyCard:
                for pick in picklist:
                    (cardList,card,cardIndex) = pick
                    if card == displayLock.card :
                        returnValue = pick
                        break
            elif type(displayLock.card) == KivyButton:
                if displayLock.card.name == "done" and allowDone:
                    returnValue = ePlayable.done
                elif displayLock.card.name == "cancel" and allowCancel:
                    returnValue = ePlayable.cancel

            if returnValue != False:
                displayLock.release(False)
                self.buttons["done"].enable(False,False)
                self.buttons["cancel"].enable(False,False)
                return returnValue
                
        
    def moveCardTo(self,card,cardList):
        cardList.append(card)
        #self.display()


    def attack(self,pile1,pile2):

        card1=pile1.peek()
        card2=pile2.peek()
        
        print "Enemy  {0} -> {1}/{2}".format(card1.actualSpeed,card1.actualAttack,card1.actualDefense)
        print "Player {0} -> {1}/{2}".format(card2.actualSpeed,card2.actualAttack,card2.actualDefense)
        #charval = raw_input("ATTACK [enter]")

        displayLock.acquire()
        self.buttons["attack"].enable(True,True)
        displayLock.acquire()
        self.buttons["attack"].enable(False,False)
        displayLock.release(False)

        card1Survive = True            
        card2Survive = True            

        if card1.actualSpeed > card2.actualSpeed:
            
            card1.setDest(card1.scatter.pos[0],card1.scatter.pos[1]-100,card1.scatter.scale,False,True)
            
            if card1.actualAttack >= card2.actualDefense:
                card2.setState(eCardState.dead)
                card2Survive=False

            elif card2.actualAttack >= card1.actualDefense:
                card1.setState(eCardState.dead)
                card1Survive=False

            card1.setDest(card1.scatter.pos[0],card1.scatter.pos[1]+100,card1.scatter.scale,False,True)
                
        elif card2.actualSpeed > card1.actualSpeed:

            card2.setDest(card2.scatter.pos[0],card2.scatter.pos[1]+100,card2.scatter.scale,False,True)

            if card2.actualAttack >= card1.actualDefense:
                card1.setState(eCardState.dead)
                card1Survive=False
                
            elif card1.actualAttack >= card2.actualDefense:
                card2.setState(eCardState.dead)
                card2Survive=False

            card2.setDest(card2.scatter.pos[0],card2.scatter.pos[1]-100,card2.scatter.scale,False,True)

        else:
            
            card1.setDest(card1.scatter.pos[0],card1.scatter.pos[1]-50,card1.scatter.scale,False,False)
            card2.setDest(card2.scatter.pos[0],card2.scatter.pos[1]+50,card2.scatter.scale,False,True)
            while card1.has_dest or card2.has_dest:
                sleep(0)
            
            if card1.actualAttack >= card2.actualDefense:
                card2.setState(eCardState.dead)
                card2Survive=False

            if card2.actualAttack >= card1.actualDefense:
                card1.setState(eCardState.dead)
                card1Survive=False

            card1.setDest(card1.scatter.pos[0],card1.scatter.pos[1]+50,card1.scatter.scale,False,False)
            card2.setDest(card2.scatter.pos[0],card2.scatter.pos[1]-50,card2.scatter.scale,False,True)
            while card1.has_dest or card2.has_dest:
                sleep(0)

        print "Enemy  survives={0}".format(card1Survive)
        print "Player survives={0}".format(card2Survive)

        #charval = raw_input("ATTACK END [enter]")

        return (card1Survive,card2Survive)


    def invade(self,invaderPile,victimPile,moveTo):

        invader = invaderPile.peek()
        victim = victimPile.peek()

        oldx=invader.scatter.x
        oldy=invader.scatter.y
        
        invader.setDest(victim.scatter.pos[0],victim.scatter.pos[1],victim.scatter.scale,False,True)

        if not victim.isBlank(): 
            victim.setState(eCardState.dead)

        invader.setDest(oldx,oldy,invader.scatter.scale,False,True)

        if not victim.isBlank(): 
            victimPile.dealCard(moveTo,eCardState.normal)
        

    def actionbutton(self,button):
        if looking:
            return False
        displayLock.release(button)
        return True
        
    def lookbutton(self,button):
        global looking
        global lookingCard
        if lookingCard == False:
            if button.name == "look":
                looking=True
                self.buttons["look"].enable(False,False)
                self.buttons["play"].enable(True,True)
            if button.name == "play":
                looking=False
                self.buttons["play"].enable(False,False)
                self.buttons["look"].enable(True,True)
        return True

################################################################################
#
# Main script
# 
if __name__ == '__main__': 

    MyApp().run()





