from random import shuffle
from Class_card import Card
class Deck:
    def __init__(self):#defines class
        self.deck_cards =[]#makes empty deck
    def create(self):

        for i in range(4):
            for x in range(1, 13 + 1):
                self.demoCard = Card(x, i)#makes 52 card 1 that is each values
                
                self.deck_cards.append(self.demoCard)#adds the card to deck
        return self.deck_cards       
                
    def deck_shuffle(self):
        return(shuffle(self.deck_cards))#puts the list in random order
        
    def deck_length(self):
        deck_length = len(self.deck_cards)#tells the length of the deck
        return(deck_length)
    def deck_draw(self):
        
        drawn_card = self.deck_cards.pop(0)#removes the top card of the deck and stores it
        #prints the card you remove
        return(drawn_card)
    
