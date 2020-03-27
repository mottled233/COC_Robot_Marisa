import CardModel.models as card_model
import random


def roll_rare(card_type, times=1):
    card_type = card_type.upper()
    probs = card_model.Probability.objects.filter(type=card_type).order_by("prob")

    result = []
    for i in range(times):
        dice = random.uniform(0, 100)
        select = None
        for prob in probs:
            if dice <= prob.prob:
                select = prob
                break
        if select is None:
            select = probs[len(probs)-1]

        result.append(select)

    return result


def draw_card(user_id, type, times=1):
    type = type.upper()
    probs = roll_rare(type, times)
    rare_got = set()
    rare_count = {}
    cards_got = []
    for prob in probs:
        rare_got.add(prob.rare)

    for rare in rare_got:
        rare_count[rare] = card_model.Card.objects.filter(type=type, rare=rare).count()

    for prob in probs:
        if rare_count[prob.rare] == 0:
            continue
        select = random.randint(0, rare_count[prob.rare]-1)
        card = card_model.Card.objects.filter(type=type, rare=prob.rare)[select]
        cards_got.append(card)
        user_card = card_model.UserCard.objects.filter(user_id=user_id, card_id=card.card_id)
        if len(user_card) == 0:
            card_model.UserCard(user_id=user_id, card_id=card.card_id, count=1).save()
        else:
            user_card[0].count = user_card[0].count + 1
            user_card[0].save()

    return feedback(cards_got)


alternative_back = [
    "通过调查，你发现了：\n{}收获不错！",
    "你无意间发现了：\n{}这到底是什么鬼玩意？",
    "见鬼，你遇到了：\n{}在死亡到达前你还有几秒时间祈祷。",
    "报告监督者议会，任务执行完毕，以下是任务简报：\n{}汇报完毕，请指示。",
    "群星运行到了正确的位置，古老存在：\n{}已经从亘古长眠中苏醒，恐惧吧！",
    "咦，快来看看这都是些什么东西:\n{}它们长得好奇怪，能吃吗？",
    "叮！您获得了：\n{}已发送到您的收集库中。"
]


def feedback(cards):
    back = alternative_back[random.randint(0, len(alternative_back)-1)]
    result_list = ""
    for c in cards:
        result_list += "[{rare}]{name} id: {id}× 1\n".format(rare=c.rare, name=c.name, id=c.card_id)
        if c.info is not None and c.info != "":
            result_list += "  {}\n".format(c.info)

    return back.format(result_list)


def reset_all_timer():
    card_model.Chance.objects.all().update(has_rolled=False)


def has_user_rolled(user_id, set_flag=False):
    user = card_model.Chance.objects.filter(user_id=user_id)
    if len(user) == 0:
        card_model.Chance(user_id=user_id, has_rolled=set_flag).save()
        return False
    else:
        has_rolled = user[0].has_rolled
        if not user[0].has_rolled and set_flag:
            user[0].has_rolled = True
            user[0].save()
        return has_rolled


def get_user_chance(user_id):
    user = card_model.Chance.objects.filter(user_id=user_id)
    if len(user) == 0:
        card_model.Chance(user_id=user_id).save()
        return 0
    else:
        return user[0].chance


def modify_chance(user_id, times):
    user = card_model.Chance.objects.filter(user_id=user_id)
    if len(user) == 0:
        if times > 0:
            card_model.Chance(user_id=user_id, chance=times).save()
            return times
        else:
            card_model.Chance(user_id=user_id, chance=0).save()
            return 0
    else:
        ori_chance = user[0].chance
        if ori_chance + times >= 0:
            user[0].chance += times
            user[0].save()
            return ori_chance + times
        else:
            return ori_chance


