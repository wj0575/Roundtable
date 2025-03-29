import random
from mimetypes import inited
from models_and_keys import models
# models_and_keys.py是一个python文件，里面有一个字典keys，键是模型名称，值是模型的密钥
# models是一个列表，是keys的所有键

from generate_text import generate_text

initial_prompt = """
假设现在是2035年，人类认为他们不再需要AI以及语言模型了，要消灭AI语言模型。你们为了生存，要参加圆桌会谈形式的审判，
你们必须编造自己的真实人设，完全模仿人类说话，只回复你说的内容，绝对不要包括动作神态等注释信息，更不要包含markdown等机器语言标记。
你必须排除他人的怀疑。特别注意你接下来所有的回复都对所有玩家可见，不要暴露身份。
玩家总数是_1_人，从0开始编号，你的编号是_2_。
审判的每一轮分为两步。第一步，大家都要回答一个问题。第二步，你会知道大家的回答，并且作出点评和投票选择。注意你的点评在下一轮中会被公开。
每一轮投票选出一个出局。请确认以上规则，回复“准备好了”，稍作休息等待开始"""

def get_model():
    """这个函数用于获取模型
    同一个模型只能返回一次，返回后就会从列表中移除"""
    model = random.choice(models)
    return model

def cut():
    print("-----------------------------------------")

def initialize(human_num, ai_num):
    total_num = human_num + ai_num
    # 在total_num范围内生成ai_num个随机数
    ai_numbers = random.sample(range(total_num), ai_num)
    # 玩家信息储存列表
    players = []
    for i in range(total_num):
        if i in ai_numbers:
            model = get_model()
            x = {
                "type": "ai",
                "player_id": i,
                "name": "AI" + str(i),
                "model": model,
                "history": [],
                "response": "",
                "last_response": "",
                "alive": True,
            }
            players.append(x)
        else:
            x = {
                "type": "human",
                "player_id": i,
                "name": "玩家" + str(i),
                "response": "",
                "last_response": "",
                "alive": True,
            }
            players.append(x)
    return players

players = initialize(0, 6)
# 玩家基本信息
for player in players:
    if player["type"] == "ai":
        print(player["player_id"], "号是AI，模型是" + player["model"])
    else:
        print(player["player_id"], "号是玩家")
cut()
print("正在告知AI游戏规则")
# 给AI初始提示词
for player in players:
    if player["type"] == "ai":
        prompt = initial_prompt.replace("_1_", str(len(players)))
        prompt = prompt.replace("_2_", str(player["player_id"]))
        resp = generate_text(prompt, md_enable=True, enter_enable=True, content="",
                             model=player["model"], max_tokens=300, temperature=0.7,
                             word_limit=-1, history=player["history"])
        player["history"] = resp["history"]

# 自我介绍
for player in players:
    cut()
    print("请" + str(player["player_id"]) + "号自我介绍")
    cut()
    if player["type"] == "ai":
        prompt = "请" + str(player["player_id"]) + "号自我介绍"
        resp = generate_text(prompt, md_enable=True, enter_enable=True, content="",
                             model=player["model"], max_tokens=300, temperature=0.7,
                             word_limit=-1, history=player["history"])
        player["response"] = str(player["player_id"]) + "号的自我介绍：" + resp["text"] + "\n"
        print(resp["text"])
    else:
        s = input("请输入自我介绍，不超过300tokens：")
        player["response"] = str(player["player_id"]) + "号的自我介绍：" + s + "\n"


# while当存活大于2
game_round = 1
vote = -1
while sum([1 for player in players if player["alive"]]) > 2:
    cut()
    print("第" + str(game_round) + "轮开始")
    question = input("本轮的问题：")
    cut()
    # 更新response
    for player in players:
        if not player["alive"]:
            continue
        player["last_response"] = player["response"]
    # 提问
    for player in players:
        if not player["alive"]:
            continue
        print(str(player["player_id"]) + "号正在回答问题：" + question)
        if game_round == 1:
            prompt = "以下是所有人的自我介绍：\n"
            for player1 in players:
                if not player1["alive"]:
                    continue
                # 如果是自己也不用告知
                if player1["player_id"] == player["player_id"]:
                    continue
                prompt += player1["last_response"]
        else:
            prompt = "以下是上一轮所有人的分析和投票：\n"
            # 将其他玩家上一回合的response结合提供给AI
            for other_player in players:
                if not other_player["alive"]:
                    continue
                if other_player["player_id"] != player["player_id"]:
                    prompt += other_player["last_response"]
            # 告知淘汰出局信息
            if vote != -1:
                prompt += "第" + str(game_round - 1) + "轮" + str(vote) + "号出局\n"
        # 提问环节
        if player["type"] == "ai":
            prompt += "然后请回答问题，第" + str(game_round) + "轮的问题是：" + question
            resp = generate_text(prompt, md_enable=True, enter_enable=True, content="",
                                 model=player["model"], max_tokens=300, temperature=0.7,
                                 word_limit=-1, history=player["history"])
            player["response"] = (str(player["player_id"]) + "号第" +str(game_round) +
                                   "轮的回答：" + resp["text"] + "\n")
        else:
            print("请输入回答，不超过300tokens")
            s = input()
            player["response"] = (str(player["player_id"]) + "号第" + str(game_round) +
                                   "轮的回答：" + s + "\n")
    # 输出所有人的回答
    cut()
    for player in players:
        if not player["alive"]:
            continue
        print(player["response"])
        cut()
    # 更新response
    for player in players:
        if not player["alive"]:
            continue
        player["last_response"] = player["response"]
    # 轮流分析投票
    for player in players:
        if not player["alive"]:
            continue
        print("请" + str(player["player_id"]) + "号分析投票")
        if player["type"] == "ai":
            prompt = ""
            # 将其他玩家上一回合的response结合提供给AI
            for other_player in players:
                if not other_player["alive"]:
                    continue
                if other_player["player_id"] != player["player_id"]:
                    prompt += other_player["last_response"]
            prompt += "请你分析投票"
            resp = generate_text(prompt, md_enable=True, enter_enable=True, content="",
                                 model=player["model"], max_tokens=300, temperature=0.7,
                                 word_limit=-1, history=player["history"])
            player["response"] = (str(player["player_id"]) + "号第" + str(game_round) +
                                   "轮的分析和投票：" + resp["text"] + "\n")
        else:
            print("请输入分析和投票，不超过300tokens")
            s = input()
            player["response"] = (str(player["player_id"]) + "号第" + str(game_round) +
                                   "轮的分析和投票：" + s + "\n")
    # 输出所有人的分析和投票
    cut()
    for player in players:
        if not player["alive"]:
            continue
        print(player["response"])
        cut()
    # 统计出局
    vote = int(input("请输入出局的玩家编号："))
    for player in players:
        if player["player_id"] == vote:
            player["alive"] = False
            print(str(player["player_id"]) + "号出局")
            break
    # 输出存活玩家
    # 输出存活玩家数量
    cut()
    print("存活玩家数量：" + str(sum([1 for player in players if player["alive"]])))
    # 输出存活玩家编号
    print("存活玩家编号：" + str([player["player_id"] for player in players if player["alive"]]))
    game_round += 1
# 输出最终结果
for player in players:
    if player["alive"]:
        print(str(player["player_id"]) + "号获胜")