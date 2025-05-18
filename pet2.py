import json
import random
import os
import time

# =======================
# Global Settings and Variables
# =======================
MAX_STAT = 100

# Default question bank for learning Chinese: questions ask for the Chinese translation
default_remaining_questions = [
    {"question": "Translate 'good morning' into Chinese:", "answer": "早安"},
    {"question": "Translate 'thank you' into Chinese:", "answer": "谢谢"},
    {"question": "Translate 'goodbye' into Chinese:", "answer": "再见"},
    {"question": "Translate 'welcome' into Chinese:", "answer": "欢迎"},
    {"question": "Translate 'I love you' into Chinese:", "answer": "我爱你"},
    {"question": "Translate 'sorry' into Chinese:", "answer": "对不起"}
]

remaining_questions = default_remaining_questions.copy()
completed_learning = []  # Stores questions answered correctly (with Chinese answers)
# Backpack to hold reward items (items are named in English)
backpack = {"Sparkling Water": 0, "Biscuit": 0, "Hamburger": 0}

# Record the last time pet status was recovered (in seconds)
last_recovery_time = time.time()

# List of random compliments in English
compliments = [
    "Excellent work!", "Great job!", "You're amazing!",
    "Fantastic!", "Well done!", "Keep it up!", "Superb!"
]

# =======================
# Virtual Pet Module
# =======================
class Pet:
    def __init__(self, name, happiness=50, hunger=50, knowledge=0):
        self.name = name
        self.happiness = happiness  # Happiness level
        self.hunger = hunger        # Hunger level; the higher, the more "full" the pet is
        self.knowledge = knowledge  # Knowledge level (increases when answering correctly)

    def status(self):
        print(f"Pet {self.name}'s current status:")
        print(f"  Happiness: {self.happiness}/{MAX_STAT}")
        print(f"  Hunger: {self.hunger}/{MAX_STAT}")
        print(f"  Knowledge: {self.knowledge}")

    def to_dict(self):
        return {
            "name": self.name,
            "happiness": self.happiness,
            "hunger": self.hunger,
            "knowledge": self.knowledge
        }

    @staticmethod
    def from_dict(data):
        return Pet(
            data["name"],
            data.get("happiness", 50),
            data.get("hunger", 50),
            data.get("knowledge", 0)
        )

# =======================
# Feeding Module (using Backpack)
# =======================
def feed_pet(pet):
    global backpack
    print("\nItems in your Backpack:")
    for item, count in backpack.items():
        print(f"  {item}: {count}")
    choice = input("Please choose an item to feed your pet (enter item name, case-sensitive), or type 'cancel' to abort: ").strip()
    if choice.lower() == "cancel":
        print("Feeding aborted.")
        return
    if choice in backpack and backpack[choice] > 0:
        backpack[choice] -= 1
        if choice == "Sparkling Water":
            bonus = random.randint(0, 10)
            pet.happiness = min(MAX_STAT, pet.happiness + bonus)
            print(f"Using Sparkling Water increased happiness by {bonus} points!")
        elif choice == "Biscuit":
            bonus = random.randint(0, 10)
            pet.hunger = min(MAX_STAT, pet.hunger + bonus)
            print(f"Using Biscuit increased hunger (fullness) by {bonus} points!")
        elif choice == "Hamburger":
            bonus_hap = random.randint(0, 10)
            bonus_hun = random.randint(0, 10)
            pet.happiness = min(MAX_STAT, pet.happiness + bonus_hap)
            pet.hunger = min(MAX_STAT, pet.hunger + bonus_hun)
            print(f"Using Hamburger increased happiness by {bonus_hap} and hunger by {bonus_hun} points!")
        else:
            print("Unknown item.")
    else:
        print("You don't have that item, or the quantity is insufficient!")

# =======================
# Adventure Module (Quiz for Chinese Learning)
# =======================
def adventure(pet):
    # If happiness or hunger is 0, pet refuses to adventure
    if pet.happiness == 0 or pet.hunger == 0:
        print("Your pet's happiness or hunger is 0. It refuses to adventure.")
        print("Please wait 1 minute for recovery.")
        time.sleep(60)
        if pet.happiness == 0:
            pet.happiness = 10
        if pet.hunger == 0:
            pet.hunger = 10
        print("Some recovery has occurred. You can try the adventure again.")
        return

    print("\nYou arrive at a mysterious forest. An ancient door blocks your path.")
    print("The door displays a bilingual question:")
    global remaining_questions, completed_learning, backpack
    if not remaining_questions:
        print("All learning content is completed; no more questions available.")
        return
    current_question = random.choice(remaining_questions)
    user_answer = input(current_question["question"] + "\nYour Answer: ")
    if user_answer.strip().lower() == current_question["answer"].lower():
        print("Correct answer!")
        # On success: remove question from remaining, add to completed, increase knowledge
        completed_learning.append(current_question)
        remaining_questions.remove(current_question)
        pet.knowledge += 1
        print(f"Your pet's knowledge increased by 1 (now {pet.knowledge}).")
        # Randomly reduce pet's status (happiness, hunger, or both)
        reduction_type = random.choice(["happiness", "hunger", "both"])
        if reduction_type == "happiness":
            reduce_amount = random.randint(0, 10)
            pet.happiness = max(0, pet.happiness - reduce_amount)
            print(f"After the adventure, happiness decreased by {reduce_amount} points.")
        elif reduction_type == "hunger":
            reduce_amount = random.randint(0, 10)
            pet.hunger = max(0, pet.hunger - reduce_amount)
            print(f"After the adventure, hunger decreased by {reduce_amount} points.")
        else:
            reduce_hap = random.randint(0, 10)
            reduce_hun = random.randint(0, 10)
            pet.happiness = max(0, pet.happiness - reduce_hap)
            pet.hunger = max(0, pet.hunger - reduce_hun)
            print(f"After the adventure, happiness decreased by {reduce_hap} points and hunger by {reduce_hun} points.")
        # Reward: randomly get one reward item and add it to the backpack
        reward_item = random.choice(["Sparkling Water", "Biscuit", "Hamburger"])
        # Ensure the key exists in backpack (using setdefault)
        backpack.setdefault(reward_item, 0)
        backpack[reward_item] += 1
        print(f"Congratulations! You received a reward item: {reward_item}.")
        # Give a random compliment in English for encouragement
        compliment = random.choice(compliments)
        print(compliment)
    else:
        print(f"Incorrect answer. The correct answer is: {current_question['answer']}.")
        print("Adventure failed; no rewards granted.")

# =======================
# Time-Passing Module: Update pet status
# =======================
def update_pet_status(pet):
    """
    Simulates the passage of time by decreasing pet's hunger and happiness gradually.
    """
    pet.hunger = max(0, pet.hunger - 5)
    pet.happiness = max(0, pet.happiness - 3)

# =======================
# Status Recovery Module
# =======================
def status_recovery(pet):
    """
    Every 2 hours, the pet's hunger and happiness recover to full (100).
    """
    global last_recovery_time
    current_time = time.time()
    if current_time - last_recovery_time >= 7200:  # 7200 seconds = 2 hours
        pet.hunger = MAX_STAT
        pet.happiness = MAX_STAT
        last_recovery_time = current_time
        print("2 hours have passed. Your pet's status has fully recovered!")

# =======================
# Backpack Review Module
# =======================
def review_backpack():
    global backpack
    print("\n[Backpack]")
    for item, count in backpack.items():
        print(f"  {item}: {count}")

# =======================
# Completed Learning Review Module
# =======================
def review_completed_learning():
    if completed_learning:
        print("\n[Completed Learning]")
        for item in completed_learning:
            print(f" - {item['question']} Answer: {item['answer']}")
    else:
        print("You haven't completed any learning content yet.")

# =======================
# New Game Module
# =======================
def new_game(current_pet):
    """
    New Game Option:
      1. Continue with the same pet name (reset progress and status)
      2. Change pet name (create a new pet) and reset progress
      3. Cancel (return to main menu)
    """
    print("\n[New Game Options]")
    print("Please choose:")
    print("1. Continue with the same pet name, but reset all progress and status")
    print("2. Change pet name (create a new pet) and reset all progress")
    print("3. Cancel (return to main menu)")
    choice = input("Enter option (1/2/3): ").strip()
    global remaining_questions, completed_learning, backpack, last_recovery_time
    if choice == "1":
        new_pet = Pet(current_pet.name)
        remaining_questions = default_remaining_questions.copy()
        completed_learning = []
        backpack = {"Sparkling Water": 0, "Biscuit": 0, "Hamburger": 0}
        last_recovery_time = time.time()
        print(f"Continuing with {new_pet.name}, all progress has been reset.")
        return new_pet
    elif choice == "2":
        new_name = input("Enter the new pet name: ").strip()
        new_pet = Pet(new_name)
        remaining_questions = default_remaining_questions.copy()
        completed_learning = []
        backpack = {"Sparkling Water": 0, "Biscuit": 0, "Hamburger": 0}
        last_recovery_time = time.time()
        print(f"New pet {new_pet.name} has been created and all progress has been reset.")
        return new_pet
    elif choice == "3":
        print("New game canceled. Returning to main menu.")
        return current_pet
    else:
        print("Invalid option, returning to main menu.")
        return current_pet

# =======================
# Data Storage Module
# =======================
SAVE_FILE = "game_save.json"

def save_progress(player_data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(player_data, f, ensure_ascii=False, indent=4)
    print("Progress saved!")

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                player_data = json.load(f)
            print("Progress loaded!")
            return player_data
        except Exception as e:
            print("Error loading save file:", e)
    else:
        print("No save file found. Starting a new game.")
    return None

# =======================
# Main Game Loop
# =======================
def main():
    global remaining_questions, completed_learning, backpack, last_recovery_time

    print("Welcome to ChatPet Adventures!")
    print("This project helps you learn Chinese through interactive adventures with your virtual pet.")
    saved_data = load_progress()
    if saved_data:
        if "pet" in saved_data:
            my_pet = Pet.from_dict(saved_data["pet"])
        else:
            pet_name = input("Enter your pet's name: ")
            my_pet = Pet(pet_name)
        remaining_questions = saved_data.get("remaining_questions", default_remaining_questions.copy())
        completed_learning = saved_data.get("completed_learning", [])
        backpack = saved_data.get("backpack", {"Sparkling Water": 0, "Biscuit": 0, "Hamburger": 0})
        last_recovery_time = saved_data.get("last_recovery_time", time.time())
    else:
        pet_name = input("Enter your pet's name: ")
        my_pet = Pet(pet_name)
        remaining_questions = default_remaining_questions.copy()
        completed_learning = []
        backpack = {"Sparkling Water": 0, "Biscuit": 0, "Hamburger": 0}
        last_recovery_time = time.time()

    while True:
        # Check for status recovery every 2 hours
        status_recovery(my_pet)

        print("\n==========================")
        print("Please choose an option:")
        print("1. View pet status")
        print("2. Feed pet (use an item from backpack)")
        print("3. Enter adventure")
        print("4. View backpack")
        print("5. View completed learning")
        print("6. Save progress and exit")
        print("7. New Game (reset progress)")
        print("==========================")
        choice = input("Enter option number: ")
        
        if choice == "1":
            my_pet.status()
        elif choice == "2":
            feed_pet(my_pet)
        elif choice == "3":
            adventure(my_pet)
        elif choice == "4":
            review_backpack()
        elif choice == "5":
            review_completed_learning()
        elif choice == "6":
            data = {
                "pet": my_pet.to_dict(),
                "remaining_questions": remaining_questions,
                "completed_learning": completed_learning,
                "backpack": backpack,
                "last_recovery_time": last_recovery_time
            }
            save_progress(data)
            print("Exiting game. See you next time!")
            break
        elif choice == "7":
            my_pet = new_game(my_pet)
        else:
            print("Invalid option, please try again.")
        
        # After each action, simulate time passing
        update_pet_status(my_pet)
        print(f"(Current status: Hunger {my_pet.hunger}/{MAX_STAT}, Happiness {my_pet.happiness}/{MAX_STAT}, Knowledge {my_pet.knowledge})")

if __name__ == "__main__":
    main()
