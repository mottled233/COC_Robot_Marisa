# -*- coding:gbk -*-


import os
import logging
import utils.log
import re
import random
import json


logger = logging.getLogger(utils.log.Logger.LOGGER_NAME)


def parse(string, wanna, lens=2):
    indexD = string.find(wanna)
    margin = len(wanna)
    if indexD == -1:
        return -1
    else:
        try:
            value = int(string[indexD+margin+1:indexD+margin+1+lens])
            return value
        except Exception as e:
            logger.exception(e)
            return -1


class Game(object):
    def __init__(self):
        self.roles = {}

    def addRole(self, player, roleStr):
        self.roles[player] = Role(roleStr)

    def getRole(self, player):
        if player not in self.roles:
            return False
        return self.roles[player]

    def saveGame(self, filename):
        fd = open(filename, 'w')
        game = {}
        for key in self.roles.keys():
            game[key] = self.roles[key].toString()
        fd.write(json.dumps(game))
        fd.close()

    def loadGame(self, filename):
        fd = open(filename, 'r')
        fstr = ""
        for line in fd:
            fstr = fstr + line
        game = json.loads(fstr)
        self.roles = {}
        for key in game.keys():
            self.roles[key] = Role('', obj=json.loads(game[key]))
        fd.close()


class Role(object):
    def __init__(self, roleStr, obj=None):
        if obj is not None:
            self.roleStr = obj['roleStr']
            self.skill = obj['skill']
            self.statusList = obj['statusList']
            self.specialStatusList = obj['specialStatusList']
            self.proSkill = obj['proSkill']
        else:
            self.roleStr = roleStr
            initStr = ''
            with open('initProperties.txt', 'r') as f1:
                for l1 in f1:
                    initStr = initStr+l1
            self.roleStr = self.roleStr.replace(' Ω', '')
            self.roleStr = initStr + " " + self.roleStr
            logger.info(self.roleStr)
            self.skill = {}
            self.proSkill = {}

            self.statusList = ['力量', '体质', '体型', '敏捷', '外貌', '智力', '意志', '教育', '闪避', '斗殴']
            self.specialStatusList = ['MOV', '体格']

            rePattern = re.compile(r'([^\d\s]{1,10}:)?([^\d\s]{1,12})[\s:]{1,2}(\d{1,2})%?')
            skillArr = re.findall(rePattern, self.roleStr)
            logger.info(skillArr)
            for ma in skillArr:
                self.skill[ma[1]] = int(ma[2])
            self.skill['san'] = self.skill['San']
            self.skill.pop('San')

    def getSkill(self, skill):
        if skill not in self.skill:
            return -1
        return self.skill[skill]

    def setSkill(self, skill, value):
        self.skill[skill] = value

    def getAllVar(self):
        vars = {}
        for key in self.var.keys():
            vars[key] = self.skill[key]
        return vars

    def getAllStatus(self):
        status = {}
        for key in self.statusList:
            status[key] = self.skill[key]
        for key in self.specialStatusList:
            status[key] = self.skill[key]
        return status

    def getAll(self):
        return self.skill

    def getAllSkill(self):
        return self.proSkill

    def toString(self):
        role = {'roleStr': self.roleStr, 'skill': self.skill, 'statusList': self.statusList,
                'specialStatusList': self.specialStatusList, 'proSkill': self.proSkill}
        json_str = json.dumps(role, encoding='gbk')
        logger.info(json_str)
        return json_str
