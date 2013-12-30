
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


ePlayable = enum("none","pfrom1","pto1","pfrom2","pto2","single","cost","cancel","done")

eOrder = enum("first","second","both","neither")

eCardTypes = enum("space","worker","soldier","facility","instant","cover","factory")

eSuiteNames = enum("Blank","Socialist Union Republic Army","Nuclear Bodgers","Insectoids","Void")

eCardState = enum("normal","dead","turned","good")


eEngineStages = enum("upkeepInit","upkeep","upkeepSetup","upkeepReturn","enemyDealInit","enemyDeal","enemyDealCheck",
                     "playerDealInit","playerDeal",
                     "buildInit","buildSetup","buildCost","buildFinal",
                     "attackInit","attackSetup","attack","attackAfter",
                     "collectInit","collectSetup",
                     "produceInit","produce","produceSell","produceSold","produceDeal",
                     "nextPlayer")

ePhases = enum("upkeep","build","attack","collect","produce")
