from Class_card import Card
class Player:#define class of player
    def __init__(self, name):#gives player the starting things (name and empty hand)
        self.is_standing = False
        self.player_cards = []   
        self.player_name = name
        self.hand_value = 0
    def hand_size(self):
        return(len(self.player_cards))#tell how many cards in hand
        
    #def add_to_hand(self):
    #    draw = demo_deck.deck_draw()
    #   self.player_cards.append(draw)
    def play_card(self):
        if len(self.player_cards) == 0: print("you have no cards left in your deck")#if you have no cards left in the deck it doesn't run
        else:
            card_played = self.player_cards.pop(0)#plays the top card of the deck
            return(card_played)
    
    def insert_card(self, card):
        self.player_cards.append(card)
        self.player_card_value.append(card.VALUE)
    def stand(self):
        self.is_standing = True
    def hand_value(self, card_value): 
        for card in self.player_cards:
            self.hand_value += card.VALUE
    def reset(self):
         self.is_standing = False
         self.score = 0
         self.player_cards = []
    
    