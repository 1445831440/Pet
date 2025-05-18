import json
import random
import os
import time

# =======================
# 全局配置与变量
# =======================
MAX_STAT = 100

# 默认待学习题库（可扩展）
default_remaining_questions = [
    {"question": "Translate '早安' to English.", "answer": "good morning"},
    {"question": "Translate '谢谢' to English.", "answer": "thank you"},
    {"question": "Translate '再见' to English.", "answer": "goodbye"},
    {"question": "Translate '欢迎' to English.", "answer": "welcome"},
    {"question": "Translate '我爱你' to English.", "answer": "i love you"},
    {"question": "Translate '对不起' to English.", "answer": "sorry"}
]

# 全局变量（在新游戏和存档中会重置）
remaining_questions = default_remaining_questions.copy()
completed_learning = []  # 已完成学习记录（中英文对照）
# 背包：奖励道具初始均为0
backpack = {"气泡水": 0, "饼干": 0, "汉堡": 0}

# 定时恢复机制：记录上次恢复时间（秒）
last_recovery_time = time.time()

# 随机语言嘉奖列表
compliments = [
    "Excellent work!", "Great job!", "You're amazing!",
    "Fantastic!", "Well done!", "Keep it up!", "Superb!"
]

# =======================
# 虚拟宠物模块 (Pet Module)
# =======================
class Pet:
    def __init__(self, name, happiness=50, hunger=50, knowledge=0):
        self.name = name
        self.happiness = happiness  # 快乐值
        self.hunger = hunger        # 饱腹值
        self.knowledge = knowledge  # 学识

    def status(self):
        print(f"宠物 {self.name} 当前状态：")
        print(f"  快乐: {self.happiness}/{MAX_STAT}")
        print(f"  饱腹: {self.hunger}/{MAX_STAT}")
        print(f"  学识: {self.knowledge}")

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
# 喂宠物模块 (Feeding via Backpack)
# =======================
def feed_pet(pet):
    global backpack
    print("\n【背包中的道具】")
    for item, count in backpack.items():
        print(f"  {item}: {count}")
    choice = input("请选择要使用的道具进行喂养（输入名称，不区分大小写），或输入‘取消’返回：").strip()
    if choice.lower() == "取消":
        print("取消喂养。")
        return
    if choice in backpack and backpack[choice] > 0:
        backpack[choice] -= 1
        if choice == "气泡水":
            bonus = random.randint(0, 10)
            pet.happiness = min(MAX_STAT, pet.happiness + bonus)
            print(f"使用气泡水后，快乐增加了 {bonus} 点！")
        elif choice == "饼干":
            bonus = random.randint(0, 10)
            pet.hunger = min(MAX_STAT, pet.hunger + bonus)
            print(f"使用饼干后，饱腹增加了 {bonus} 点！")
        elif choice == "汉堡":
            bonus_hap = random.randint(0, 10)
            bonus_hun = random.randint(0, 10)
            pet.happiness = min(MAX_STAT, pet.happiness + bonus_hap)
            pet.hunger = min(MAX_STAT, pet.hunger + bonus_hun)
            print(f"使用汉堡后，快乐增加了 {bonus_hap} 点，饱腹增加了 {bonus_hun} 点！")
        else:
            print("未知的道具。")
    else:
        print("背包中没有该道具或数量不足！")

# =======================
# 冒险解谜模块 (Adventure Module)
# =======================
def adventure(pet):
    # 如果快乐或饱腹为0，则禁止闯关，并等待1分钟恢复
    if pet.happiness == 0 or pet.hunger == 0:
        print("宠物的快乐或饱腹为 0，不愿闯关。请等待 1 分钟以恢复状态。")
        time.sleep(60)
        if pet.happiness == 0:
            pet.happiness = 10
        if pet.hunger == 0:
            pet.hunger = 10
        print("状态恢复了一些，现在可以继续闯关。")
        return

    print("\n你来到神秘森林前，一扇古老的门挡住了去路。")
    print("门上刻着中英文题目：")
    global remaining_questions, completed_learning, backpack
    if not remaining_questions:
        print("所有学习内容已完成，无题目可答。")
        return
    current_question = random.choice(remaining_questions)
    user_answer = input(current_question["question"] + "\nYour Answer: ")
    if user_answer.strip().lower() == current_question["answer"].lower():
        print("答题正确！")
        # 答对后：移除该题目，记录到已完成，学识+1
        completed_learning.append(current_question)
        remaining_questions.remove(current_question)
        pet.knowledge += 1
        print(f"宠物学识增加了 1 点，现在学识: {pet.knowledge}")
        # 随机减少宠物状态
        reduction_type = random.choice(["happiness", "hunger", "both"])
        if reduction_type == "happiness":
            reduce_amount = random.randint(0, 10)
            pet.happiness = max(0, pet.happiness - reduce_amount)
            print(f"闯关后，快乐减少了 {reduce_amount} 点。")
        elif reduction_type == "hunger":
            reduce_amount = random.randint(0, 10)
            pet.hunger = max(0, pet.hunger - reduce_amount)
            print(f"闯关后，饱腹减少了 {reduce_amount} 点。")
        else:
            reduce_hap = random.randint(0, 10)
            reduce_hun = random.randint(0, 10)
            pet.happiness = max(0, pet.happiness - reduce_hap)
            pet.hunger = max(0, pet.hunger - reduce_hun)
            print(f"闯关后，快乐减少了 {reduce_hap} 点，饱腹减少了 {reduce_hun} 点。")
        # 奖励：随机获得一种奖励道具，存入背包
        reward_item = random.choice(["气泡水", "饼干", "汉堡"])
        backpack[reward_item] += 1
        print(f"恭喜，你获得了奖励道具：{reward_item}！")
        # 随机语言嘉奖
        compliment = random.choice(compliments)
        print(compliment)
    else:
        print(f"答题错误，正确答案是：{current_question['answer']}。闯关失败，无奖励。")


# =======================
# 定时恢复 (Status Recovery) 模块
# =======================
def status_recovery(pet):
    """
    每过 2 小时，宠物的饱腹和快乐恢复到满值 100
    """
    global last_recovery_time
    current_time = time.time()
    if current_time - last_recovery_time >= 7200:  # 7200秒=2小时
        pet.hunger = MAX_STAT
        pet.happiness = MAX_STAT
        last_recovery_time = current_time
        print("2小时已过，宠物状态恢复到满值！")

# =======================
# 查看背包 (Backpack) 模块
# =======================
def review_backpack():
    global backpack
    print("\n【背包】")
    for item, count in backpack.items():
        print(f"  {item}: {count}")

# =======================
# 查看已完成学习模块 (Review Completed Learning)
# =======================
def review_completed_learning():
    if completed_learning:
        print("\n【已完成的学习】")
        for item in completed_learning:
            print(f" - {item['question']}  答案: {item['answer']}")
    else:
        print("你还没有完成任何学习内容。")

# =======================
# 新开始模块 (New Game)
# =======================
def new_game(current_pet):
    """
    新开始选项
      1. 以原宠物名字继续游戏（重置闯关进度、属性、背包、学习记录）
      2. 更换宠物名称（创建新宠物，同时重置进度）
      3. 误触返回（取消操作，返回主菜单）
    """
    print("\n【新开始选项】")
    print("请选择:")
    print("1. 使用原宠物名称继续，但重置所有进度和属性")
    print("2. 更换宠物名称（创建新宠物）并重置所有进度")
    print("3. 取消（返回主菜单）")
    choice = input("输入选项（1/2/3）：").strip()
    global remaining_questions, completed_learning, backpack, last_recovery_time
    if choice == "1":
        # 以原宠物名称，重置属性与进度
        new_pet = Pet(current_pet.name)
        remaining_questions = default_remaining_questions.copy()
        completed_learning = []
        backpack = {"气泡水": 0, "饼干": 0, "汉堡": 0}
        last_recovery_time = time.time()
        print(f"已使用 {new_pet.name} 继续游戏，所有进度均已重置。")
        return new_pet
    elif choice == "2":
        new_name = input("请输入新的宠物名称：").strip()
        new_pet = Pet(new_name)
        remaining_questions = default_remaining_questions.copy()
        completed_learning = []
        backpack = {"气泡水": 0, "饼干": 0, "汉堡": 0}
        last_recovery_time = time.time()
        print(f"已创建新宠物 {new_pet.name} 并重置所有进度。")
        return new_pet
    elif choice == "3":
        print("取消新开始，返回主菜单。")
        return current_pet
    else:
        print("无效选项，返回主菜单。")
        return current_pet

# =======================
# 数据存储模块 (Storage Module)
# =======================
SAVE_FILE = "game_save.json"

def save_progress(player_data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(player_data, f, ensure_ascii=False, indent=4)
    print("进度已保存！")

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                player_data = json.load(f)
            print("进度加载成功！")
            return player_data
        except Exception as e:
            print("加载存档时出错：", e)
    else:
        print("未找到存档，将初始化新进度。")
    return None

# =======================
# 主程序入口 (Main Game Loop)
# =======================
def main():
    global remaining_questions, completed_learning, backpack, last_recovery_time

    print("欢迎来到聊宠历险记！")
    saved_data = load_progress()
    if saved_data:
        if "pet" in saved_data:
            my_pet = Pet.from_dict(saved_data["pet"])
        else:
            pet_name = input("请给你的宠物取一个名字：")
            my_pet = Pet(pet_name)
        remaining_questions = saved_data.get("remaining_questions", default_remaining_questions.copy())
        completed_learning = saved_data.get("completed_learning", [])
        backpack = saved_data.get("backpack", {"气泡水": 0, "饼干": 0, "汉堡": 0})
        last_recovery_time = saved_data.get("last_recovery_time", time.time())
    else:
        pet_name = input("请给你的宠物取一个名字：")
        my_pet = Pet(pet_name)
        remaining_questions = default_remaining_questions.copy()
        completed_learning = []
        backpack = {"气泡水": 0, "饼干": 0, "汉堡": 0}
        last_recovery_time = time.time()

    while True:
        # 检查2小时恢复状态
        status_recovery(my_pet)

        print("\n==========================")
        print("请选择操作：")
        print("1. 查看宠物状态")
        print("2. 喂宠物 (使用背包道具)")
        print("3. 进入冒险关卡")
        print("4. 查看背包")
        print("5. 查看已完成的学习")
        print("6. 保存进度并退出游戏")
        print("7. 新开始 (重新初始化进度)")
        print("==========================")
        choice = input("输入选项编号：")
        
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
            print("游戏结束，期待下次再见！")
            break
        elif choice == "7":
            my_pet = new_game(my_pet)
        else:
            print("无效选项，请重新选择。")
        

        print(f"(当前状态：饱腹 {my_pet.hunger}/{MAX_STAT}, 快乐 {my_pet.happiness}/{MAX_STAT}, 学识 {my_pet.knowledge})")

if __name__ == "__main__":
    main()
