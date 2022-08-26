from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List
from random import randrange, shuffle

# TODO add option to be able to count cards (deck refilement)
# TODO add multiple players


class NotEnoughMoney(Exception):
    pass


def main() -> None:
    """Play the game"""
    player = Player()
    player.add_name()
    player.add_deposit()

    dealer = Player()
    dealer.add_name("Dealer")

    deck = Deck()

    while True:
        if player.get_total_money() == 0:
            print("The game is over, you don't have money anymore !")
            return

        player.cards = []
        dealer.cards = []

        deck.create()
        deck.shuffle()

        bet = player.bet()

        for _ in range(2):
            player.add_card(deck.deal_card())
            dealer.add_card(deck.deal_card())

        player.print_cards()

        while True:
            action = input("What do you want to do: new card (1), split (2), all good (3)? \n")
            # TODO refactor with a Enum class
            if action == "1":
                player.add_card(deck.deal_card())
                player.print_cards()
                player.hand_value()
            elif action == "2":
                if player.get_total_money() >= bet:
                    player.total_money -= bet
                    bet *= 2
                    player.add_card(deck.deal_card())
                    player.print_cards()
                    player.hand_value()
                    break
                else:
                    print(f"You don't have enough money, you need {bet} and you have {player.get_total_money()}")
                    continue
            elif action == "3":
                player.print_cards()
                player.hand_value()
                break
            else:
                print("This is not a valid action")

            if player.has_lost(bet):
                break

            if player.hand_value() == 21:
                print("You have a BlackJack!!!")
                break

        player_won = dealer.dealer_turn(deck, player.hand_value())

        if player_won == 1:
            player.add_money(bet * 2)
            print(f"You won: {bet * 2}")
            print(f"You now have: {player.get_total_money()}")
        elif player_won == 0:
            player.add_money(bet)
            print("It's a draw")
            print(f"You now have: {player.get_total_money()}")
        else:
            player.remove_money(bet)
            print(f"You lost: {bet}")
            print(f"You now have: {player.get_total_money()}")


class CardColor(Enum):
    DIAMOND = "diamond"
    HEART = "heart"
    CLUB = "club"
    SPADE = "spade"


class CardFigure(Enum):
    AS = "AS"
    KING = "KING"
    QUEEN = "QUEEN"
    JACK = "JACK"
    TEN = "TEN"
    NINE = "NINE"
    EIGHT = "EIGHT"
    SEVEN = "SEVEN"
    SIX = "SIX"
    FIVE = "FIVE"
    FOUR = "FOUR"
    THREE = "THREE"
    TWO = "TWO"


CARD_VALUES = {
    "AS": (1, 11),
    "KING": 10,
    "QUEEN": 10,
    "JACK": 10,
    "TEN": 10,
    "NINE": 9,
    "EIGHT": 8,
    "SEVEN": 7,
    "SIX": 6,
    "FIVE": 5,
    "FOUR": 4,
    "THREE": 3,
    "TWO": 2,
}


@dataclass
class Card:
    color: CardColor
    figure: CardFigure

    def __str__(self):
        return f"{self.color.value} of {self.figure.name.lower()}"


class Deck:
    deck: List[Card] = []

    def get(self) -> List[Card]:
        return self.deck

    def create(self) -> List[Card]:
        for color in CardColor:
            for figure in CardFigure:
                self.deck.append(Card(color, figure))

        return self.deck

    def shuffle(self) -> None:
        shuffle(self.deck)

    def deal_card(self) -> Card:
        index_card_to_pick = randrange(len(self.deck))
        return self.deck.pop(index_card_to_pick)

    def card_value(self, card_figure: str) -> Any:
        return CARD_VALUES[card_figure]

    def __str__(self) -> str:
        return str([
            f"{card.color.value} of {card.figure.name.lower()}"
            for card in self.deck]
        )


@dataclass
class Player:
    name: str = ""
    cards: List[Card] = field(default_factory=list)
    total_money: int = 0

    def add_name(self, name: str = ""):
        if not name:
            self.name = input("What is you name ?\n")
        else:
            self.name = name

    def add_deposit(self) -> None:
        amount = int(input("How much money do you want to depose ?\n"))
        self.add_money(amount)

    def add_money(self, amount) -> None:
        self.total_money += amount

    def remove_money(self, amount) -> None:
        self.total_money == amount

    def add_card(self, card):
        self.cards.append(card)

    def dealer_turn(self, deck: Deck, score_to_beat: int) -> int:
        if score_to_beat > 21:
            return -1

        while self.hand_value() < score_to_beat:
            self.add_card(deck.deal_card())

            if self.hand_value() > 21:
                print("The dealer had over 21.")
                self.print_cards()
                print(self.hand_value())
                return 1

        if self.hand_value == score_to_beat:
            print("You are equal")
            self.print_cards()
            print(self.hand_value())
            return 0

        print(f"The dealer beat you with a score of: {self.hand_value()}")
        self.print_cards()
        return -1

    def bet(self) -> int:
        amount = int(input("How much money do you want to bet this turn ?\n"))

        if self.total_money < amount:
            raise NotEnoughMoney()
        self.total_money -= amount

        return amount

    def hand_value(self):
        total_hand_value = 0
        number_aces = 0

        for card in self.cards:
            if isinstance(CARD_VALUES[card.figure.name], int):
                total_hand_value += CARD_VALUES[card.figure.name]
            else:
                number_aces += 1

        total_hand_value = self.add_aces(total_hand_value, number_aces)

        return total_hand_value

    def has_lost(self, bet: int) -> bool:
        if self.hand_value() > 21:
            return True
        return False

    def add_aces(self, total_value: int, number_of_aces: int) -> int:
        if number_of_aces <= 0:
            return total_value
        elif total_value + 11 + number_of_aces - 1 > 21:
            return total_value + number_of_aces
        else:
            return total_value + 11 + number_of_aces - 1

    def print_cards(self):
        for card in self.cards:
            print(card)
        print(self.hand_value())

    def get_total_money(self) -> int:
        return self.total_money

    def __str__(self) -> str:
        return f"{self.player_name} have {self.total_money} chips"


if __name__ == "__main__":
    main()
