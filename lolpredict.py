from flask import Flask

import torch
import sys
from flask import Flask, render_template, redirect, request, url_for
from flask import Flask, jsonify
import requests
import urllib
import urllib.request
from urllib.parse import quote
import re
from bs4 import BeautifulSoup


app = Flask(__name__)
model = torch.load('C:\\Users\\USER\\Desktop\\hello.py')


@app.route('/number<num1>,'  ,methods=['GET'])
def predictNum(num1):
    model = torch.load('C:\\Users\\USER\\Desktop\\hello.py')

    numberData = num1.split(",")
    for i in range(0,len(numberData)-1):
        numberData[i] = float(numberData[i])
    a = [numberData]
    y = model.predict(a)[0]
    if(y == 1):
        return "승리"
    else:
        return "패배"


def getPositionNumber(nick):
    request_headers = {
    'User-Agent': ('User-Agent": "Mozilla/5.0')
    }


    resp = requests.get("https://api.kda.ai/kr/api/summoners/"+quote(nick)+"?matchCategory=SoloRank&lang=ko")
    data = resp.json()
    
    position = data['mostLanes'][0]['lane']
    positionNumber = 0
    if position == "Top":
        positionNumber = 0
    elif position == "Jug":
        positionNumber = 1
    elif position == "Mid":
        positionNumber = 2
    elif position == "Adc":
        positionNumber = 3
    else:
        positionNumber = 4
        
    return positionNumber

@app.route('/calculate<nick1>,<nick2>,<nick3>,<nick4>,<nick5>',methods=['GET'])
def sortArray(nick1,nick2,nick3,nick4,nick5):
    arr = [[getPositionNumber(nick1),nick1],[getPositionNumber(nick2),nick2],[getPositionNumber(nick3),nick3],[getPositionNumber(nick4),nick4],[getPositionNumber(nick5),nick5]]
    arr.sort()
    return arr[0][1]+","+arr[1][1]+","+arr[2][1]+","+arr[3][1]+","+arr[4][1]

@app.route('/<name1>',methods=['GET'])
def getData(name1):
    nick = name1
    nick = re.sub(r"\s+", '', nick)
    request_headers = {
    'User-Agent': ('User-Agent": "Mozilla/5.0')
    }


    r = urllib.request.Request("https://www.op.gg/summoner/userName="+quote(nick), headers=request_headers)
    c = urllib.request.urlopen(r).read()
    soup = BeautifulSoup(c, "html.parser")
    ## BeautifulSoup으로 html소스를 python객체로 변환하기
    ## 첫 인자는 html소스코드, 두 번째 인자는 어떤 parser를 이용할지 명시.
    ## 이 글에서는 Python 내장 html.parser를 이용했다.
    for i in range(1,21):
        gameId = soup.select_one('#SummonerLayoutContent > div.tabItem.Content.SummonerLayoutContent.summonerLayout-summary > div.RealContent > div > div.Content > div.GameItemList > div:nth-child('+str(i)+') > div').get('data-game-id')
        summonerId = soup.select_one('#SummonerLayoutContent > div.tabItem.Content.SummonerLayoutContent.summonerLayout-summary > div.RealContent > div > div.Content > div.GameItemList > div:nth-child('+str(i)+') > div').get('data-summoner-id')
        gameResult = soup.select_one('#SummonerLayoutContent > div.tabItem.Content.SummonerLayoutContent.summonerLayout-summary > div.RealContent > div > div.Content > div.GameItemList > div:nth-child('+str(i)+') > div').get('data-game-result')
    
        request_headers1 = {
            "Content-Type": "text/html; charset=UTF-8",
            "Authority": "www.op.gg"
        }

    
        r1 = urllib.request.Request('https://www.op.gg/summoner/matches/ajax/detail/gameId=' + gameId + '&summonerId=' + summonerId, headers=request_headers1)
        c1 = urllib.request.urlopen(r1).read()
        soup1= BeautifulSoup(c1, "html.parser")
        gameData = soup1.text
        temp = re.sub(r"\n+", '@', gameData)
        temp1 = re.sub(r"\t+", '@', temp)
        temp2 = re.sub(r"\s+", '', temp1)
        gameDataNoSpace = re.sub(r"@+", ' ', temp2)
        gameData = gameDataNoSpace.split()
    
        remove_set = {'Overview','Team', 'Analysis','Build', 'etc','Victory','(Red','Team)','Tier','OP'
                      ,'Score','KDA','Damage','Wards','CS', 'Item','TeamAnalysis', '(RedTeam)', 'OPScore','Defeat', '(BlueTeam)'}

        result = [i for i in gameData if i not in remove_set]
        del result[75:87]
        
        if len(result) == 150:
            myIndex = int((result.index(nick)-2)/15)
            enemyIndex = int((result.index(nick)-2+75)/15)
            csPerMinute = result[14]
            csPerMinute = re.sub(r"/m", '', csPerMinute)
            cs = result[13] 
            minute = round((float(cs) / float(csPerMinute)),1)
    
    
            death = round(4*int(result[7+15*myIndex].split("/")[1])/minute,4)
            temp = ''+(result[8+15*myIndex])
            num = re.compile(r'\d+')
            killCoop = "{:.4f}".format(float(num.findall(temp)[0])/100)
            myTempDamage = re.sub(r",", '',result[9+15*myIndex])
            enemyTempDamage = re.sub(r",", '',result[9+15*enemyIndex])
            myDamage = int(myTempDamage)
            enemyDamage = int(enemyTempDamage)
            relativeDamage = "{:.4f}".format((myDamage - enemyDamage)/(minute*500))
            myCs = float(re.sub(r"/m", '', (result[14+15*myIndex])))
            enemyCs = float(re.sub(r"/m", '', (result[14+15*enemyIndex])))
            relativeCs = "{:.4f}".format(myCs - enemyCs)
    
            controlWard = int(result[10+15*myIndex])
            ward = int(re.sub(r"/", '',result[11+15*myIndex]))
            wardKill = int(result[12+15*myIndex])
    
            totalWardScore = "{:.4f}".format((controlWard + ward + wardKill)/minute)
            return str(death) +"," + str(killCoop) + "," + str(relativeDamage) + "," + str(relativeCs) + "," + str(totalWardScore) + ","

#def sortArray(nick1,nick2,nick3,nick4,nick5):
 #   arr = [[getPositionNumber(nick1),nick1],[getPositionNumber(nick2),nick2],[getPositionNumber(nick3),nick3],[getPositionNumber(nick4),nick4],[getPositionNumber(nick5),nick5]]
  #  arr.sort()
   # return arr

    

    
if __name__ == '__main__':
    app.run(host = '192.168.0.103', port = 8000)

    

