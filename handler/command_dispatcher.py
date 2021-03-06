# -*- coding:gbk -*-

import os
import logging
import utils.log
import re
import random
import handler.game_rec as rec
import json
import handler.lottery as lottery
import service.card_service as card_service
import service.draw_service as draw_service
import datetime


logger = logging.getLogger(utils.log.Logger.LOGGER_NAME)


def roll_dice(express):
    index_d = express.find('d')
    if index_d == -1:
        index_d = express.find('D')
    if index_d == -1:
        return ['固定{}'.format(express), int(express)]
    num_of_dice = 1
    if index_d != 0:
        num_of_dice = int(express[0:index_d])
    max_value_of_dice = int(express[index_d + 1:])
    array = []
    val = 0
    for i in range(num_of_dice):
        res = random.randint(1, max_value_of_dice)
        array.append(str(res))
        val = val + res
    result = ['[' + ','.join(array) + ']', val]
    return result


def covert_at(at_str):
    match = re.findall(r'\d{6,}', at_str)
    if len(match) > 0:
        return match[0]
    return ""


def check(player, item):
    if player.getSkill(item) < 0:
        res = player.getSkill(item)
        if res < 0:
            res = player.getSkill(item)
        return res
    else:
        return player.getSkill(item)


def touch(player, item):
    if player.getSkill(item) < 0:
        key = item
        res = player.getSkill(key)
        if res < 0:
            logger.info(2)
            key = item
            res = player.getSkill(key)
            if res < 0:
                return False
        return key
    else:
        return item


class CommandDispatcher(object):
    def __init__(self):
        random.seed()
        logger.info('dispatcher inited')
        self.games = {}
        self.user_chance = {}
        self.cmd_dict = {'r': RollDiceCommand(), 'coc7': RoleGenerateCommand(), 'c': CheckCommand(self.games),
                         'sc': SanCheckCommand(self.games), 'join': JoinCommand(self.games),
                         'startGame': StartGameCommand(self.games), 'exitGame': ExitGameCommand(self.games),
                         'v': ViewCommand(self.games), 'save': SaveGameCommand(self.games),
                         'load': LoadGameCommand(self.games), 'd': DamageCommand(self.games),
                         'luck': LuckCommand(), 'ping': PingCommand(),
                         'draw': DrawCardCommand(), 'show': ShowCollectCommand(),
                         'jrrp': JRRPCommand(), 'desc': DescriptionCollectCommand(),
                         'send': SendCardCommand(), 'adminjrrp': AdminJRRPCommand(),
                         'addcard': AddCardCommand(), "sell": SellCardCommand()}

        self.cmd_dict['help'] = HelpCommand(self.cmd_dict)

    def __del__(self):
        logger.info('dispatcher del')

    @staticmethod
    def is_command(msg):
        if type(msg) != str:
            return False
        if msg[0] == "/":
            return True
        return False

    def execute_cmd(self, msg, from_qq, from_group):
        end_cmd = msg.find(" ")
        if end_cmd == -1:
            end_cmd = len(msg)
        cmd = msg[1:end_cmd]
        try:
            handler = self.cmd_dict[cmd]
        except KeyError:
            return "命令不存在，请使用/help查看所有支持的指令"
        msg = re.sub(r'\s+', ' ', msg)
        args = msg.split(' ')[1:]
        # for i in range(len(args)):
        #    args[i] = args[i].decode('gbk')

        logger.info('entered{3},{0},{1},{2}'.format(args, from_qq, from_group, cmd))
        return handler.execute_cmd(args, str(from_qq), str(from_group))


class AbstractCommand(object):
    def execute_cmd(self, args, from_qq, from_group):
        raise NotImplementedError('abstract')

    def help(self):
        raise NotImplementedError('abstract')


class RollDiceCommand(AbstractCommand):
    def execute_cmd(self, args, from_qq, from_group):
        logger.info("进入掷骰子命令，args:" + str(args))
        is_private = False
        result = "格式错误"
        if len(args) == 0:
            result = '掷骰结果: ' + roll_dice('1D100')[0]
            return result
        for arg in args:
            if re.match('^h$', arg):
                is_private = True
                continue

            if re.search(r'\d*[dD]\d+', arg):
                match_arr = re.findall(r'\d*[dD]\d+', arg)
                dice_arr = []
                for express in match_arr:
                    dice = roll_dice(express)
                    dice_arr.append(dice[0])
                    arg = arg.replace(express, str(dice[1]))

                if len(dice_arr) > 1:
                    result = '掷骰结果: ' + arg
                else:
                    result = '掷骰结果: ' + dice_arr[0]

                result = result + ' , 共计:' + str(eval(arg))
        return [result, is_private, '暗骰结果已私聊发送']

    def help(self):
        return '/r[h] 骰子表达式\n  - 骰子形如 [数字n]d[数字m] 含义为投掷n个m面骰子\n  - h为暗骰'


class RoleGenerateCommand(AbstractCommand):
    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入随机调查员属性命令")
        if len(args) == 0:
            num = 1
        else:
            num = int(args[0])
            num = num if num <= 5 else 5

        status = {'力量': True, '体质': True, '体型': False, '敏捷': True, '外貌': True, '教育': False, '意志': True, '幸运': True}
        result = "您的随机属性如下：\n"
        array = []
        for i in range(num):
            array = []
            for key, value in status.items():
                if value:
                    dice = roll_dice('3d6')[1]
                else:
                    dice = (roll_dice('2d6')[1] + 6)
                array.append(key + ": " + str(dice * 5))
            result += ", ".join(array) + "\n"

        return result

    def help(self):
        return '/coc7 [个数] 随机调查员属性'


class CheckCommand(AbstractCommand):
    def __init__(self, gamesDict):
        self.gamesDict = gamesDict

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入检定命令")

        if from_group not in self.gamesDict:
            return "本群没有正在进行的游戏。"

        if len(args) == 0:
            return '请输入要检定的属性或技能'
        player = fromQQ
        logger.info(type(fromQQ))
        index = 0
        call = "您"
        if len(args) > 1:
            call = args[0]
            player = covert_at(args[0])
            index = 1

        player = self.gamesDict[from_group].getRole(player)
        if not player:
            return call + "没有参加游戏"

        needBelow = check(player, args[index])
        if not needBelow:
            return call + "没有该属性或技能。"

        result = ""
        dice = random.randint(1, 100)
        if dice > needBelow:
            result = "失败"
        else:
            result = "成功"
        if dice < needBelow / 2:
            result = "困难成功"
        if dice < needBelow / 5:
            result = "极难成功"
        if (needBelow > 50 and dice == 100) or (needBelow <= 50 and dice >= 96):
            result = "大失败"
        elif dice == 1:
            result = "大成功"

        result = "{4}的{0}为{1}, 投骰结果为{2}, 检定结果：{3}。".format(args[index], needBelow, dice, result, call)
        return result

    def help(self):
        return '/c [at需要检定的玩家] 需要检定的属性'


class SanCheckCommand(AbstractCommand):
    def __init__(self, gamesDict):
        self.gamesDict = gamesDict

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入sancheck检定命令")

        if from_group not in self.gamesDict:
            return "本群没有正在进行的游戏。"

        if len(args) == 0:
            return '请输入sc表达式'
        player = fromQQ
        index = 0
        call = "您"
        if len(args) > 1:
            call = args[0]
            player = covert_at(args[0])
            index = 1

        player = self.gamesDict[from_group].getRole(player)
        if not player:
            return call + "没有参加游戏"

        needBelow = check(player, 'san')
        if not needBelow:
            return call + "没有该属性或技能。"

        result = True
        dice = random.randint(1, 100)
        if dice > needBelow:
            result = False

        slashIndex = args[index].find('/')

        damage = args[index][0:slashIndex] if result else args[index][slashIndex + 1:]
        result = "成功" if result else "失败"
        diceValue = roll_dice(damage)
        trueDamage = diceValue[1]
        player.setSkill('san', needBelow - trueDamage)

        result = "{4}的{0}当前为{1}, 投骰结果为{2}, 检定结果：{3}。扣除san值{5}点，当前san值：{6}".format('san值', needBelow, dice, result, call,
                                                                                  trueDamage, needBelow - trueDamage)
        return result

    def help(self):
        return '/sc [at需要检定的玩家] [sc表达式]'


class StartGameCommand(AbstractCommand):
    def __init__(self, gamesDict):
        self.gamesDict = gamesDict

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("Q群" + str(from_group) + "使用开启游戏命令")

        if from_group in self.gamesDict:
            return "本群已经有开始的游戏啦，如需重新开始请使用/exitGame命令先退出。"

        self.gamesDict[from_group] = rec.Game()
        return "游戏开始啦。"

    def help(self):
        return '/startGame 开启一局游戏'


class ExitGameCommand(AbstractCommand):
    def __init__(self, gamesDict):
        self.gamesDict = gamesDict

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("Q群" + str(from_group) + "使用结束游戏命令")

        if from_group not in self.gamesDict:
            return "本群没有正在进行的游戏。"

        self.gamesDict.pop(from_group)
        return "游戏已退出。"

    def help(self):
        return '/exitGame 关闭正在进行的游戏'


class SaveGameCommand(AbstractCommand):
    def __init__(self, gamesDict):
        self.gamesDict = gamesDict

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("Q群" + str(from_group) + "使用储存游戏命令")

        if from_group not in self.gamesDict:
            return "本群没有正在进行的游戏。"

        name = str(from_group)
        if len(args) != 0:
            name = args[0]

        self.gamesDict[from_group].saveGame(name)
        return "游戏已储存。"

    def help(self):
        return '/save [存档名，默认为qq群号] 存档正在进行的游戏'


class LoadGameCommand(AbstractCommand):
    def __init__(self, gamesDict):
        self.gamesDict = gamesDict

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("Q群" + str(from_group) + "使用读取游戏命令")

        if from_group not in self.gamesDict:
            return "本群没有正在进行的游戏。"

        name = str(from_group)
        if len(args) != 0:
            name = args[0]

        self.gamesDict[from_group].loadGame(name)
        return "游戏已读取完毕。"

    def help(self):
        return '/load [存档名，默认为qq群号] 读取存档'


class JoinCommand(AbstractCommand):
    def __init__(self, gamesDict):
        self.gamesDict = gamesDict

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("Q群{0}用户{1}使用参加游戏命令".format(from_group, fromQQ))

        if from_group not in self.gamesDict:
            return "本群没有正在进行的游戏。"

        player = fromQQ
        roleStr = ""
        if args[0].find("CQ:at") != -1:
            player = covert_at(args[0])
            roleStr = " ".join(args[1:])
            logger.info(roleStr)
        else:
            roleStr = " ".join(args)
        self.gamesDict[from_group].addRole(player, roleStr)
        skills = self.gamesDict[from_group].getRole(player).getAll()
        arr = []
        for key, value in skills.items():
            arr.append("{0}: {1}".format(key, value))

        return "[CQ:at,qq={0}]已成功参加游戏，请核对您的属性：\n".format(player) + ", ".join(arr)

    def help(self):
        return '/join [完整的属性信息] 参与本群进行的游戏'


class ViewCommand(AbstractCommand):
    def __init__(self, gamesDict):
        self.gamesDict = gamesDict

    def execute_cmd(self, args, fromQQ, from_group):

        if from_group not in self.gamesDict:
            return "本群没有正在进行的游戏。"

        if len(args) == 0:
            return "请输入要查看的技能或属性"

        if len(args) == 1:
            player = self.gamesDict[from_group].getRole(fromQQ)
            if not player:
                return "您没有参加游戏"
            if args[0] != 'all':
                return "您的属性：" + args[0] + "为" + str(check(player, args[0]))
            elif args[0] == 'all':
                skills = player.getAll()
                arr = []
                for key, value in skills.items():
                    arr.append("{0}: {1}".format(key, value))
                return "您的属性：\n" + ", ".join(arr)

        if len(args) == 2:
            args[0] = covert_at(args[0])
            player = self.gamesDict[from_group].getRole(args[0])
            if not player:
                return "该玩家没有参加游戏"

            if args[1] != 'all':
                return "[CQ:at,qq={0}]的属性：{1} 为 {2}".format(args[0], args[1], str(check(player, args[1])))
            elif args[1] == 'all':
                skills = player.getAll()
                arr = []
                for key, value in skills.items():
                    arr.append("{0}: {1}".format(key, value))
                return "[CQ:at,qq={0}]".format(args[0]) + "的属性：\n" + ", ".join(arr)

    def help(self):
        return '/v [at要查看的玩家，否则是查看自己] 属性或技能 查看玩家的状态'


class DamageCommand(AbstractCommand):
    def __init__(self, gamesDict):
        self.gamesDict = gamesDict

    def execute_cmd(self, args, fromQQ, from_group):
        if from_group not in self.gamesDict:
            return '本群没有已经开始的游戏。'
        if len(args) < 2:
            return '请输入参数[属性][伤害表达式]'
        player = fromQQ
        call = '您'
        if len(args) == 3:
            call = args[0]
            player = covert_at(args[0])
            args.pop(0)

        player = self.gamesDict[from_group].getRole(player)
        if not player:
            return call + "没有在游戏中"

        key = touch(player, args[0])
        if not key:
            return call + "没有该属性"

        nowVal = player.getSkill(key)
        matchArr = re.findall('\d*[dD]\d+', args[1])
        diceArr = []
        for express in matchArr:
            dice = roll_dice(express)
            diceArr.append(dice[0])
            args[1] = args[1].replace(express, str(dice[1]))
        damage = eval(args[1])
        text = "损失"
        if damage < 0:
            text = "恢复"
        player.setSkill(key, nowVal - damage)
        nowVal = player.getSkill(key)
        return "{0}{1}了{2}点{3}, 当前值为{4}".format(call, text, abs(damage), args[0], nowVal)

    def help(self):
        return '/d [at玩家] 属性 伤害表达式  指定某属性受到多少点伤害或恢复'


class DrawCardCommand(AbstractCommand):
    def __init__(self):
        pass

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入drawCard命令")
        if len(args) == 0:
            return "您必须指定抽卡池，例如：/draw scp.\n目前有SCP和COC两个卡池。"
        card_type = args[0]
        times = 1 if len(args) == 1 else int(args[1])
        if times < 1:
            return "您必须指定大于1次的调查。"
        chance = draw_service.get_user_chance(fromQQ)
        if chance < times:
            return "行动否决。您没有足够的行动许可。\n您当前只有{}份许可。\n您可以使用/jrrp 命令获取每天的抽卡机会！"\
                .format(chance)
        result = draw_service.draw_card(user_id=fromQQ, type=card_type, times=times)
        remains = draw_service.modify_chance(user_id=fromQQ, times=0-times)
        return result + "\n 您还剩{}次调查机会。".format(remains)

    def help(self):
        return '===============\n收藏相关命令\n/draw 抽卡'


class JRRPCommand(AbstractCommand):
    def __init__(self):
        pass

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入JRRP命令")
        dice = random.randint(3, 10)

        if draw_service.has_user_rolled(fromQQ, set_flag=True):
            return "哦嚯，你今天已经用光补给份额了，您当前共有份{}行动许可，明天再来试试吧！"\
                .format(draw_service.get_user_chance(fromQQ))
        else:
            remains = draw_service.modify_chance(fromQQ, times=dice)

        return "您成功申请了{}份行动许可！\n当前剩余{}份行动许可。\n快使用/draw [卡池] [次数]命令来进行调查！".format(
            dice, remains)

    def help(self):
        return '/jrrp 申请今天的调查许可！'


class AdminJRRPCommand(AbstractCommand):
    def __init__(self):
        pass

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入JRRP命令")
        if fromQQ != "631061840":
            return "警告:严禁未经授权的人员进行访问\n肇事者将被监控，定位并处理."

        toQQ = covert_at(args[0])
        val = roll_dice(args[1])[1]

        remains = draw_service.modify_chance(toQQ, times=val)

        return "您成功为{}分配了{}份行动许可！\n当前{}剩余{}份行动许可。".format(
            args[0], val, args[0], remains)

    def help(self):
        return '/adminjrrp 申请今天的调查许可！'


class ShowCollectCommand(AbstractCommand):
    def __init__(self):
        pass

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入ShowCollect命令")
        return card_service.get_user_collect(user_id=fromQQ)

    def help(self):
        return '/show 查看自己的收藏库'


class AddCardCommand(AbstractCommand):
    def __init__(self):
        pass

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入AddCard命令")
        if len(args) < 3:
            return "您至少需要指定编号，名称和类型（卡池）！"
        card_id = args[0]
        name = args[1]
        type = args[2]
        rare = args[3] if len(args) >= 4 else "N"
        desc = args[4] if len(args) >= 5 else ""
        info = args[5] if len(args) >= 6 else None

        return card_service.add_card(card_id=card_id, name=name, type=type, rare=rare, desc=desc, info=info)

    def help(self):
        return '/addcard [编号] [名称] [类型] [稀有度] [描述] [信息] 其中前三项必填'


class DescriptionCollectCommand(AbstractCommand):
    def __init__(self):
        pass

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入DescriptionCollect命令")
        if len(args) != 1:
            return "请使用/desc [收藏品编号] 指定要查看的调查报告。"
        return card_service.get_card(card_id=args[0])

    def help(self):
        return '/desc [收藏品编号] 查看指定的调查报告'


class SellCardCommand(AbstractCommand):
    def __init__(self):
        pass

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("SellCard")
        if len(args) >= 1:
            rare = args[0]
        else:
            rare = "all"

        return card_service.sell_card(from_user=fromQQ, rare=rare)

    def help(self):
        return '/sell [稀有度] 售卖所有给定条件的多余收藏物，不指定条件默认出售全部'


class SendCardCommand(AbstractCommand):
    def __init__(self):
        pass

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入SendCard命令")

        if len(args) != 3:
            return "您必须按照/send [at要送的人] [收藏品编号] [数量]的格式来使用命令。"
        to_user = covert_at(args[0])
        card_id = args[1]
        num = int(args[2])

        return card_service.send_card(from_user=fromQQ, to_user=to_user, card_id=card_id, num=num)

    def help(self):
        return '/send [at要送的人] [收藏品编号] [数量] 将自己的藏品交换给他人。'


class LuckCommand(AbstractCommand):
    def __init__(self):
        self.lottery = lottery.Lottery()

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入luck命令")
        result = self.lottery.draw()

        return result

    def help(self):
        return '===============\n日常相关命令\n/luck 抽签'


class PingCommand(AbstractCommand):
    def __init__(self):
        pass

    def execute_cmd(self, args, fromQQ, from_group):
        return "实验"

    def help(self):
        return '/ping 看看是不是活着'


class HelpCommand(AbstractCommand):
    def __init__(self, cmdDict):
        self.cmdDict = cmdDict

    def execute_cmd(self, args, fromQQ, from_group):
        logger.info("进入帮助命令")
        result = ""
        for cmd, obj in self.cmdDict.items():
            result += obj.help() + "\n"

        return result

    def help(self):
        return '/help 查看命令帮助'



