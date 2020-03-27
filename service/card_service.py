import CardModel.models as card_model


def get_card(card_id):
    card_id = card_id.upper()
    card = card_model.Card.objects.filter(card_id=card_id)
    if len(card) == 0:
        return "没有这个编号的调查报告，请检查编号是否正确"
    card = card[0]
    return format_card(card)


def add_card(card_id, type, name, rare="N", desc=None, info=None):
    if card_id is None or name is None or type is None or rare is None:
        return "编号，类型，名称，稀有度不能为空！"
    if card_model.Card.objects.filter(card_id=card_id).count() > 0:
        return "已有编号相同的收藏物！"
    card_model.Card(card_id=card_id, type=type, name=name, rare=rare, description=desc, info=info).save()
    return "卡牌已保存！"


def get_user_collect(user_id):
    ids = card_model.UserCard.objects.filter(user_id=user_id).values_list("card_id", flat=True)
    if len(ids) == 0:
        return "您的收容单元是空的，请先去调查吧！"
    cards = card_model.Card.objects.filter(card_id__in=ids)
    return format_card_list(cards, count=True, user_id=user_id)


def format_card_list(cards, count=False, user_id=None):
    type_list = cards.values('type').distinct()
    result = ""
    if user_id is not None:
        user_cards = card_model.UserCard.objects.filter(user_id=user_id)
    for card_type in type_list:
        card_in_type = cards.filter(type=card_type['type'])
        result += card_type['type']
        if count:
            now = card_in_type.count()
            max_count = card_model.Card.objects.filter(type=card_type['type']).count()
            result += "系列  {}/{}".format(now, max_count)
        result += "\n"
        rare_list = card_in_type.values('rare').distinct()

        for rare in rare_list:
            result += "|-- 稀有度:" + rare['rare']
            card_in_rare = card_in_type.filter(rare=rare['rare'])
            if count:
                now = card_in_rare.count()
                max_count = card_model.Card.objects.filter(type=card_type['type'], rare=rare['rare']).count()
                result += "  {}/{}".format(now, max_count)
            result += "\n"

            for card in card_in_rare:
                if user_id is not None:
                    count_num = user_cards.filter(card_id=card.card_id)
                    count_num = count_num[0].count if len(count_num) > 0 else 0
                    result += "|---- [{id}] {name} ×{num}\n".format(id=card.card_id,
                                                                    name=card.name, num=count_num)
                else:
                    result += "|---- [{id}] {name}\n".format(id=card.card_id, name=card.name)
    return result


def send_card(from_user, to_user, card_id, num):
    card_id = card_id.upper()
    from_user_card = card_model.UserCard.objects.filter(user_id=from_user, card_id=card_id)
    if len(from_user_card) == 0 or from_user_card[0].count < num:
        return "您家里也没有余粮啊。"
    to_user_card = card_model.UserCard.objects.filter(user_id=to_user, card_id=card_id)
    if len(to_user_card) == 0:
        to_user_card = card_model.UserCard(user_id=to_user, card_id=card_id, count=num)
    else:
        to_user_card = to_user_card[0]
        to_user_card.count += num

    from_user_card[0].count -= num
    to_user_card.save()
    from_user_card[0].save()
    return "达成交易！"


def sell_card(from_user, rare="all"):
    sell_price = dict()
    if rare == "all":
        user_cards = card_model.UserCard.objects.filter(user_id=from_user, count__gt=1)
        prices = card_model.SellPrice.objects.all()

    else:
        card_ids = card_model.Card.objects.filter(rare=rare).values_list("card_id", flat=True)
        user_cards = card_model.UserCard.objects.filter(user_id=from_user, count__gt=1, card_id__in=card_ids)
        prices = card_model.SellPrice.objects.filter(rare=rare)

    for price in prices:
        sell_price[price.type+"_"+price.rare] = price.price

    price_count = 0
    count = 0
    chance_rate = 5
    for card in user_cards:
        card_entity = card_model.Card.objects.get(card_id=card.card_id)
        price = sell_price.get(card_entity.type+"_"+card_entity.rare, 1)
        price_count += (card.count - 1) * price
        count += (card.count - 1)
        card.count = 1

    if rare == "all":
        card_model.UserCard.objects.filter(user_id=from_user, count__gt=1).update(count=1)
    else:
        card_ids = card_model.Card.objects.filter(rare=rare).values_list("card_id", flat=True)
        card_model.UserCard.objects.filter(user_id=from_user, count__gt=1, card_id__in=card_ids).update(count=1)

    user_chance = card_model.Chance.objects.get_or_create(user_id=from_user)[0]
    user_chance.chance += int(price_count/chance_rate)
    user_chance.save()

    return "您共出售了{}件藏品，共获得价值{}。\n已按照（{}/份）的汇率转换为行动许可{}份。\n您目前剩余{}份行动许可。"\
        .format(count, price_count, chance_rate, int(price_count/chance_rate), user_chance.chance)





def format_card(card):
    result = "[{name}]\n" \
             "编号：{id}\n" \
             "类型：{type}\n" \
             "稀有度：{rare}\n" \
             "描述：{description}"
    return result.format(name=card.name, id=card.card_id, type=card.type, rare=card.rare, description=card.description)
