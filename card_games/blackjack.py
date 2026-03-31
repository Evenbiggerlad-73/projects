from Class_card import Card
from Player_Class import Player
from Deck_Class import Deck
from random import randint
class blackjack():#creates the game class
    def __init__(self):
        self.blackjack_deck = Deck()
        self.blackjack_deck.create()
        self.blackjack_deck.deck_shuffle()
        self.player = Player(input("please enter your name:  "))#gets player name and names a player dealer for the dealer in the game
        self.dealer = Player("dealer")
        self.player_wins = 0
        self.dealer_wins = 0
        print(f"your name is {self.player.player_name}")
    def deal(self):
        self.player.insert_card(self.blackjack_deck.deck_draw())#deals 2 cards to player and 1 to dealer
        
        self.dealer.insert_card(self.blackjack_deck.deck_draw())
        self.player.insert_card(self.blackjack_deck.deck_draw())
    def calculate_hand_score(self, player_obj):
        total = 0
        for card in player_obj.player_cards:#calculates score but makes all face cards equal to 10 instead of their value and acees = 1
            if card.VALUE >= 11:
                total += 10
            elif card.VALUE == 1:
                total += 1
            else:
                total += card.VALUE
        return total
    def run(self):
        round_num = 1
        
        while self.player_wins < 3 and self.dealer_wins < 3:#continues playing as long as no one has 3 wins
            self.player.reset()
            self.dealer.reset()    
            self.deal()
            while not (self.player.is_standing and self.dealer.is_standing):#contines until both player and dealer stands
                player_score = self.calculate_hand_score(self.player)#calculates both player and dealer score so it can stop if they go over 21 and it decideds what the dealer is doing
                dealer_score = self.calculate_hand_score(self.dealer)
                
                print(f"\n{self.player.player_name}'s score: {player_score}")
                print(f"Dealer's score: {dealer_score}")

                if not self.player.is_standing:#loops until player stands
                    choice = input("Press 'h' to hit, 's' to stand: ").lower()
                    if choice == "h":
                        self.player.insert_card(self.blackjack_deck.deck_draw())
                        if self.calculate_hand_score(self.player) > 21:
                            print("You have more than 21 dealer wins")#if yo9u have more than 21 you lose the round
                            self.player.stand()
                    else:
                        self.player.stand()

                if not self.dealer.is_standing:
                    if self.calculate_hand_score(self.dealer) <= 16:#dealer always hits if they have less than 16 and more than 16 they stand
                        self.dealer.insert_card(self.blackjack_deck.deck_draw())
                    else:
                        self.dealer.stand()
            final_player = self.calculate_hand_score(self.player)
            final_dealer = self.calculate_hand_score(self.dealer)
            print(f"{self.player.player_name}: {final_player} | Dealer: {final_dealer}")#lists final score for round
            if final_player > 21:#decides who wins and gives them 1 point unless tie than no more point
                self.dealer_wins += 1
                print("you lose")
            elif final_dealer > 21:
                print(f"{self.player.player_name} wins")
                self.player_wins += 1
            elif final_player > final_dealer:
                print(f"{self.player.player_name} wins")
                self.player_wins += 1
            elif final_dealer > final_player:
                print("you lose")
                self.dealer_wins += 1
            else:
                print("tie")
        if self.player_wins == 3:#figures out who won 3 rounds and declars them champion.
            print(f"\n you win")
        else:
            print(f"\ndealer won")
game = blackjack()
game.run()



