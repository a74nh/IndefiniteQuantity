#import csv
import random

from enums import *

#
#Represents a card suite
#
class Suite(object):
    def __init__(self, name, upkeep):
        self.name = name
        self.upkeep = upkeep
        
    def __str__(self):
        return ('<{0} upkeep:{1}>'.format(eSuiteNames.reverse_mapping[self.name],self.upkeep))

    def __repr__(self):
        return self.__str__()

#
#Represents a card
#    
class Card(object):
    def __init__(self,number,name,suite,ctype,cost,attack,defense,speed,scrap,upkeep,comments):
        self.number = number
        self.name = name
        self.suite = suite
        self.ctype = ctype
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.scrap = scrap
        self.upkeep = upkeep
        self.comments = comments
        self.playable = ePlayable.none
        self.playableValue = 0
        self.actualAttack = 0
        self.actualDefense = 0
        self.actualSpeed = 0
        self.state = eCardState.normal
        self.pile = False

    def isBlank(self):
        return self.suite.name == eSuiteNames.Blank
    
    def __str__(self):
        str="    "
        if self.playable and self.playableValue>0:
            str="{0:2}: ".format(self.playableValue)

        if self.isBlank():
            return str+"blank"
        
        if self.state == eCardState.good:
            return str+"PRODUCED GOOD"

        str=str+'{0} [{1}][{2}]'.format(self.name,
                                        eSuiteNames.reverse_mapping[self.suite.name],
                                        eCardTypes.reverse_mapping[self.ctype])
        if self.state == eCardState.dead:
            return str+" DEAD scrap:{0}".format(self.scrap)


        str=str+' c:{0}({1})'.format(self.cost,
                                     self.scrap)
        
        if self.ctype == eCardTypes.soldier:
            str=str+" Attack: {0}->{1}/{2}".format(self.speed,
                                                   self.attack,
                                                   self.defense)
        
        return str

    def __repr__(self):
        return self.__str__()


    def setState(self,state):
        self.state=state



class CardCounter(object):

    def __init__(self, name, player, value, *args):
        self.name=name
        self.player=player
        self.__value=value
        display.addCounter(self)

    @staticmethod
    def setDisplay(d):
        global display
        display = d

    def value(self):
        return self.__value

    def incValue(self,value):
        self.__value=self.__value+value


#
# Overrides list to provide display updates each time something changes.
# Class must be statically initialised with a display class
#
class CardList(list):
    
    def __init__(self, name, player, *args):
        list.__init__(self, *args)
        self.name=name
        self.player=player
        display.addList(self)

    @staticmethod
    def setDisplay(d):
        global display
        display = d

    def pop(self,index=-1):
         raise Exception("CardList pop")
    
##    def moveI(self,position,otherlist):
##        otherlist.append(list.pop(self,position))
##        display.display()
##
##    def moveO(self,entry,otherlist):
##        self.moveI(list.index(self,entry),otherlist)

    def __str__(self):
        return ('{0} : {1} {2}'.format(self.name,self.player,len(self)))

    def __repr__(self):
        return self.__str__()

    def size(self):
        return len(list)

    def moveFrom(self,index,newCardList,newState):
        card=list.pop(self,index)
        card.setState(newState)
        newCardList.append(card)

##    def append(self,card):
##        super(CardList,self).append(card)
##        card.pile=self

#
#
class CardPile(object):
    
    def __init__(self, name, player):
        self.__items = []
        self.name=name
        self.player=player
        display.addList(self)

    @staticmethod
    def setDisplay(d):
        global display
        display = d
        
    def isEmpty(self):
        return self.__items == []

    #WARNING: ignores index
    #TODO: REMOVE ME. Only used by undo
##    def insert(self,index,item):
##        #if index != -1:
##        #    raise Exception("CardPile can only pop last element")
##        self.__items.append(item)
##        display.display()

    def append(self, item):
        self.__items.append(item)
        item.pile=self
        display.display()

    #WARNING: ignores index
    #TODO: Internal only
##    def pop(self,index=-1):
##        #if index != -1:
##        #    raise Exception("CardPile can only pop last element")
##        ret=self.__items.pop()
##        display.display()
##        return ret

    def peek(self):
        return self.__items[-1]

    def peekpeek(self):
        return self.__items[-2]

    def size(self):
        return len(self.__items)

    def dealCard(self,newCardList,newState):
        card=self.__items.pop()
        card.setState(newState)
        newCardList.append(card)

        


#
# Loads in a full set of cards into a single list
#
class Deck(object):
    
    def __init__(self,suitesfilename,cardsfilename,CardType):
        self.suitesfilename = suitesfilename
        self.cardsfilename = cardsfilename
        
        with open(self.suitesfilename, 'rb') as suitesfile:
            with open(self.cardsfilename, 'rb') as cardsfile:
                next(suitesfile) # ignore header
                next(cardsfile) # ignore header
                #suitesreader = csv.reader(suitesfile, delimiter=',', quotechar='|')
                #cardreader = csv.reader(cardsfile, delimiter=',', quotechar='|')
                self.suites = []
                self.cards = []
                cardNum=1
                for suiteLine in suitesfile:
                    suiterow=suiteLine.split(",")
                    s_num,s_num2,s_name,_s_colour1,s_colour2,s_upkeep = suiterow
                    suite=Suite(getattr(eSuiteNames,s_name), s_upkeep.rstrip())
                    if suite.name == eSuiteNames.Blank:
                        self.blankSuite = suite
                    else:
                        self.suites.append(suite)
                    #print(suite)
                    count=0
                    for cardLine in cardsfile:
                        cardrow=cardLine.split(",")
                        if len(cardrow) != 12:
                            print "INVALID ROW {0} vs 12".format(len(cardrow))
                            print cardrow
                            continue
                        single,instances,name,ctype,cost,attack,defense,speed,aglity,scrap,upkeep,comments = cardrow
                        instances=int(instances)
                        count=count+instances
                        for x in range(instances):
                            card = CardType(cardNum,name,suite,getattr(eCardTypes,ctype),int(cost),int(attack),int(defense),int(speed),int(scrap),int(upkeep),comments)
                            self.cards.append(card)
                            #print(card)
                        cardNum=cardNum+1
                        if count >= int(s_num2):
                            break
                        
        random.shuffle(self.cards)
        random.shuffle(self.suites)


##    def randomSuite(self):
##        return random.choice([suite.name for suite in deck.suites])
##
##    def randomSuites(self):
##        #newlist=[suite.name for suite in deck.suites]
##        newlist=list(self.suites[1:])
##        random.shuffle(newlist)
##        return newlist
    
    def __str__(self):
        return 'myList(%s)' % self.cards

    def __repr__(self):
        return 'myList(%s)' % self.cards

