class Card:
    '''
    Card class for card games
    param VALUE int
    param SUIT int
    '''
    SUITS = {0: "Diamonds", 1: "Clubs", 2: "Hearts", 3: "Spades"}#defines the suits

    VALUES = {1: "Ace", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "Jack", 12: "Queen", 13: "King"}#defines all possible values
    def __init__(self,VALUE,SUIT):
         
         self.VALUE = VALUE
         self.SUIT = SUIT
    def __str__(self):
         return f"{Card.VALUES[self.VALUE]} of {Card.SUITS[self.SUIT]}"#names cards