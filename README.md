IndefiniteQuantity
==================


History
=====

IndefiniteQuantity is the result of an idea I had for a card game. Blending (probably too many) concepts from other games, this blended standard attacking rules with production based mechanics. However, what I really wanted from it were two things:
1 - Ability to play single player
2 - The threat that at any time everything could collapse from under you. This was not to be a game where players got gradually more and more powerful. Loss and recovery from that loss would be a central mechanic.

I set about writing a set of rules and ideas for cards to go with them.

Nandeck seemed suitable enough for designing some cards ( http://www.nand.it/nandeck/ ) despite some strange language choices. A deck of cards, with artwork hastily pulled from image searches, materialised.

After attacking a pile of printouts with scissors a few run-throughs told me that there needed to be a lot of changes – mere balancing or rule rewrites I wasn't quite sure and that dealing and shuffling small badly cut pieces of paper was very tedious. The obvious solution was I needed to visualise this. 

I had wanted to try Python for a while and now had a reason too. A few searches and I had found Kivy, which would give me an easy UI and portability across Lin/Win/And. Python proved to be as simple as it's hyped to be – almost like pseudocode.

Ignoring the Kivy part for the moment, I designed an systems with engine and display threads, with the display thread using the console. Integral to this was the storing of all history in order to be able to rewind/replay the game from any point.

With this all in place and running, I switched to Kivy. I would just subclass my display class to console and Kivy flavours. As with anything it wasn't quite that simple (“you need three of something before you can call your interface generic”) and the console display and history rollback remain broken since – although I don't see reinstating them too big an issue.

I tweaked rules and designed new cards as I went, but I think there is still a lot to be done in getting the mechanics right, and that's probably the next big area to tackle.

Current running the game will start a single player game with random chosen player and enemy teams. Players can build, attack and produce. Instants are ignored, and facilities don't do anything once placed. Hit the “eye” to switch to/from look mode, where cards zoom as clicked.

Rules are ever changing so I'm not documenting that yet.


Running
=======
Run main.py via Kivy


Other things to look at
=======================
out/ contains a image for each card.

The two .nde files can be loaded into nandeck to produce the cards.

