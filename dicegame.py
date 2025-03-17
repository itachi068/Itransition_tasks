import sys
import random
import hmac
import hashlib
import secrets

class FairRandom:
    """Handles provable fair random generation using HMAC and secure keys."""
    
    @staticmethod
    def generate_secure_random(limit):
        key = secrets.token_bytes(32)  # 256-bit secure key
        number = secrets.randbelow(limit)  # Random number within range
        hmac_hash = hmac.new(key, str(number).encode(), hashlib.sha3_256).hexdigest()
        return number, key.hex(), hmac_hash  # Return number, key, and hash

    @staticmethod
    def compute_modular_result(user_choice, computer_choice, limit):
        return (user_choice + computer_choice) % limit

class Dice:
    """Represents a single dice with custom face values."""
    
    def __init__(self, values):
        for value in values:
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"Invalid dice face value: {value}. Dice faces must be non-negative integers.")
        self.values = values
    
    def roll(self, face_index):
        return self.values[face_index]

class Player:
    """Handles player-specific logic and choices."""
    
    def __init__(self, name):
        self.name = name
        self.dice_choice = None

    def choose_dice(self, available_dice):
        """User selects a dice from available options."""
        print(f"{self.name}, choose your dice:")
        for idx, dice in enumerate(available_dice):
            print(f"{idx} - {dice.values}")

        choice = input("Your selection: ")
        if not choice.isdigit() or int(choice) not in range(len(available_dice)):
            print("Invalid selection. Try again.")
            return self.choose_dice(available_dice)
        
        self.dice_choice = int(choice)
        print(f"{self.name} chose dice: {available_dice[self.dice_choice].values}")

class DiceGame:
    """Main game logic for the non-transitive dice game."""
    
    def __init__(self, dice_sets):
        if len(dice_sets) < 3:
            print("Error: You must specify at least 3 dice configurations.")
            print("Example: python dicegame.py 2,2,4,4,9,9 6,8,1,1,8,6 7,5,3,7,5,3")
            sys.exit(1)

        try:
            self.dice = [Dice([int(x) for x in d.split(",")]) for d in dice_sets]
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        self.user = Player("User")
        self.computer = Player("Computer")

    def determine_first_turn(self):
        print("Let's determine who makes the first move.")
        comp_num, comp_key, comp_hmac = FairRandom.generate_secure_random(2)
        
        print(f"I selected a random value in the range 0..1 (HMAC={comp_hmac}).")
        print("Try to guess my selection.")
        
        print("0 - 0\n1 - 1\n2 - Exit\n3 - Help")
        
        user_guess = input("Your selection: ")
        
        if user_guess == "2":
            sys.exit(0)
        
        if not user_guess.isdigit() or int(user_guess) not in [0, 1]:
            print("Invalid input! Please enter 0 or 1.")
            return self.determine_first_turn()
        
        user_guess = int(user_guess)
        print(f"My selection: {comp_num} (KEY={comp_key}).")

        if user_guess == comp_num:
            print("You guessed correctly! You go first.")
            return self.user
        else:
            print("I go first.")
            return self.computer

    def roll_dice(self, player, modulo=6):
        """Handles rolling dice for a given player."""
        print(f"It's time for {player.name}'s throw.")
        face, key, hmac_value = FairRandom.generate_secure_random(modulo)
        print(f"I selected a random value in the range 0..{modulo - 1} (HMAC={hmac_value}).")
        
        print("Choose a number to add (modulo {modulo}):")
        for i in range(modulo):
            print(f"{i} - {i}")
        print(f"{modulo} - Exit")
        print(f"{modulo + 1} - Help")
        
        user_add = input("Your selection: ")
        
        if user_add == str(modulo):
            sys.exit(0)
        
        if not user_add.isdigit() or int(user_add) not in range(modulo):
            print("Invalid selection. Try again.")
            return self.roll_dice(player, modulo)
        
        user_add = int(user_add)
        final_index = FairRandom.compute_modular_result(user_add, face, modulo)
        print(f"My number is {face} (KEY={key}).")
        print(f"The result is {face} + {user_add} = {final_index} (mod {modulo}).")

        return self.dice[player.dice_choice].roll(final_index)

    def play_round(self):
        first_turn = self.determine_first_turn()

        if first_turn == self.computer:
            print("I make the first move and choose a dice.")
            available_dice = list(range(len(self.dice)))
            self.computer.dice_choice = random.choice(available_dice)
            available_dice.remove(self.computer.dice_choice)
            print(f"I choose dice: {self.dice[self.computer.dice_choice].values}")
            self.user.choose_dice([self.dice[idx] for idx in available_dice])
        else:
            self.user.choose_dice(self.dice)
            available_dice = [i for i in range(len(self.dice)) if i != self.user.dice_choice]
            self.computer.dice_choice = random.choice(available_dice)
            print(f"I choose dice: {self.dice[self.computer.dice_choice].values}")

        comp_roll = self.roll_dice(self.computer)
        user_roll = self.roll_dice(self.user)

        print(f"My throw is {comp_roll}.")
        print(f"Your throw is {user_roll}.")

        if user_roll > comp_roll:
            print("You win!")
        elif user_roll < comp_roll:
            print("I win!")
        else:
            print("It's a tie!")
 
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Error: You must specify at least 3 dice configurations.")
        print("Example: python dicegame.py 2,2,4,4,9,9 6,8,1,1,8,6 7,5,3,7,5,3")
        sys.exit(1)

    game = DiceGame(sys.argv[1:])
    game.play_round()
