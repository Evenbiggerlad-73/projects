from Class_card import Card
from Player_Class import Player
from Deck_Class import Deck
from random import randint
class WarRules():

    
    def __init__(self):
        self.war_deck = Deck()#creates deck and shuffles it
        self.war_deck.create()
        self.war_deck.deck_shuffle()
        tie = False
        self.player1 = Player("Todd")#creates and names both people playing
        self.player2 = Player("Lou")
        print(f"your player names are {self.player1.player_name} and {self.player2.player_name}")

    def deal(self):
        
        for x in range(self.war_deck.deck_length() // 2):#deals deck and if odd num gives last card to 1st player
            self.player1.insert_card(self.war_deck.deck_draw())
            self.player2.insert_card(self.war_deck.deck_draw())
        if self.war_deck.deck_length() == 1:
            self.player1.insert_card(self.war_deck.deck_draw())

    def play_cards(self):
        inplay_cards = []
        
        inplay_cards.append(self.player1.play_card())#puts top card of each players deck into play
        inplay_cards.append(self.player2.play_card())
        card1 = inplay_cards[0]
        card2 = inplay_cards[1]
        if card2.VALUE == card1.VALUE: #determines who has higher card and if they are tied it randomly gives you a winner
            coin_flip = randint(0, 1)
            if coin_flip == 0:
                winner = self.player1.player_name
            else: winner = self.player2.player_name
            # card3 = card1
            # card4 = card2
            # tie = True
            # game.play_cards
        elif card1.VALUE == 1: #this makes the ace act as the highest card in the deck because its given rank is 1 but you want it to be 14
            winner = self.player1.player_name
        elif inplay_cards[1].VALUE == 1:
            winner = self.player2.player_name
        elif inplay_cards[0].VALUE > inplay_cards[1].VALUE:
            winner = self.player1.player_name
        else: winner = self.player2.player_name
        
        if winner == self.player1.player_name:#whoever the winner is it adds the cards in the inplay zone to their deck
            self.player1.insert_card(card1)
            self.player1.insert_card(card2)
            
        else: 
            self.player2.insert_card(card1)
            self.player2.insert_card(card2)
        print(f"\nround {num_of_rounds}")
        print(f"{self.player1.player_name} played {inplay_cards[0]} and {self.player2.player_name} played {inplay_cards[1]} the winner of this hand is {winner}")#declares who won the hand
        print(f"{self.player1.player_name} has {self.player1.hand_size()} cards and {self.player2.player_name} has {self.player2.hand_size()} cards")

max_rounds = 100
num_of_rounds = 1
game = WarRules()#makes the game
game.deal()#deals out the deck

while game.player1.hand_size() != 0 and game.player2.hand_size() != 0 and num_of_rounds != max_rounds + 1:#gives endgame condition num_of_rounds is to make it not go to long
    game.play_cards()
    num_of_rounds += 1 #counts rounds

     
else:
    if game.player1.hand_size() > game.player2.hand_size():#because the game can end early the winner is whoever has the bigger hand at the end of the game
        print(f"the winner is {game.player1.player_name}")
    else: print(f"the winner is {game.player2.player_name}")
   
    