from urllib import request
from bs4 import BeautifulSoup
import time
import pandas as pd

love_all = []
love_fifteen = []
love_thirty = []
love_forty = []
fifteen_love = []
fifteen_all = []
fifteen_thirty = []
fifteen_forty = []
thirty_love = []
thirty_fifteen = []
thirty_all = []
thirty_forty = []
forty_love = []
forty_fifteen = []
forty_thirty = []
deuce = []
def game_result_checker():
    if game_result[- 1] == ["AD", "40"]:
        game_result.append("W")
    elif game_result[- 1] == ["40", "AD"]:
        game_result.append("L")
    elif game_result[- 1][0] == "40":
        game_result.append("W")
    else:
        game_result.append("L")

def score_checker():
    result = game_result[- 1]
    if ["0", "0"] in game_result:
        love_all.append(result)
    if ["0", "15"] in game_result:
        love_fifteen.append(result)
    if ["0", "30"] in game_result:
        love_thirty.append(result)
    if ["0", "40"] in game_result:
        love_forty.append(result)
    if ["15", "0"] in game_result:
        fifteen_love.append(result)
    if ["15", "15"] in game_result:
        fifteen_all.append(result)
    if ["15", "30"] in game_result:
        fifteen_thirty.append(result)
    if ["15", "40"] in game_result:
        fifteen_forty.append(result)
    if ["30", "0"] in game_result:
        thirty_love.append(result)
    if ["30", "15"] in game_result:
        thirty_fifteen.append(result)
    if ["30", "30"] in game_result:
        thirty_all.append(result)
    if ["30", "40"] in game_result:
        thirty_forty.append(result)
    if ["40", "0"] in game_result:
        forty_love.append(result)
    if ["40", "15"] in game_result:
        forty_fifteen.append(result)
    if ["40", "30"] in game_result:
        forty_thirty.append(result)
    if ["40", "40"] in game_result:
        deuce.append(result)

urls = [
    "https://sportsnavi.ht.kyodo-d.jp/tennis/match/21184993/live/",
    "https://sportsnavi.ht.kyodo-d.jp/tennis/match/21160667/live/",
    "https://sportsnavi.ht.kyodo-d.jp/tennis/match/21145121/live/",
    "https://sportsnavi.ht.kyodo-d.jp/tennis/match/21119685/live/",
    "https://sportsnavi.ht.kyodo-d.jp/tennis/match/21120987/live/",
    "https://sportsnavi.ht.kyodo-d.jp/tennis/match/21106045/live/",
    "https://sportsnavi.ht.kyodo-d.jp/tennis/match/21105351/live/"
]

for url in urls:
    #Webページからのスクレイピング
    html = request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")

    #セット数の取得
    set_html = soup.find(id="period_link")
    set_sum = len(set_html.find_all("a"))

    #選手名の取得
    name = soup.find_all(class_="ht-gameHeadScore__playerName")
    player = {}
    player["home"] = name[0].text
    player["away"] = name[1].text

    for i in range(1, set_sum + 1):
        link_html = request.urlopen(url + "?period={}".format(i)).read()
        link_soup = BeautifulSoup(link_html, "html.parser")

        #サーバーの確認
        server_html = link_soup.find(id="game_1").find(class_="ht-style--flex")
        server = server_html.find(class_="ht-timeline__itemStatus").text

        if player["home"] in server:
            serve_flog = False
        else:
            serve_flog = True

        #各ゲームのスコアの取得
        game_result = []
        home_score = link_soup.find_all(class_="ht-timeline__statusScoreHome")
        away_score = link_soup.find_all(class_="ht-timeline__statusScoreAway")

        home_score.reverse()
        away_score.reverse()

        for h, a in zip(home_score, away_score):
            if serve_flog:
                score = [a.text, h.text]
            else:
                score = [h.text, a.text]

            if score == ["0", "0"] and len(game_result) > 0:
                game_result_checker()
                score_checker()
                serve_flog = not bool(serve_flog)
                game_result.clear()
            if score == ["0", "1"] or score == ["1", "0"]:
                game_result.clear()
                break
            game_result.append(score)
        if len(game_result) > 0:
            game_result_checker()
            score_checker()
            game_result.clear()
        time.sleep(1)


love_lists = [
    love_all.count("W") / len(love_all) * 100,
    fifteen_love.count("W") / len(fifteen_love) * 100,
    thirty_love.count("W") / len(thirty_love) * 100,
    forty_love.count("W") / len(forty_love) * 100
]

fifteen_lists = [
    love_fifteen.count("W") / len(love_fifteen) * 100,
    fifteen_all.count("W") / len(fifteen_all) * 100,
    thirty_fifteen.count("W") / len(thirty_fifteen) * 100,
    forty_fifteen.count("W") / len(forty_fifteen) * 100
]

thirty_lists = [
    love_thirty.count("W") / len(love_thirty) * 100,
    fifteen_thirty.count("W") / len(fifteen_thirty) * 100,
    thirty_all.count("W") / len(thirty_all) * 100,
    forty_thirty.count("W") / len(forty_thirty) * 100
]

forty_lists = [
    love_forty.count("W") / len(love_forty) * 100,
    fifteen_forty.count("W") / len(fifteen_forty) * 100,
    thirty_forty.count("W") / len(thirty_forty) * 100,
    deuce.count("W") / len(deuce) * 100
]

df = pd.DataFrame(love_lists, columns=["0"], index=["0", "15", "30", "40"])
df["15"] = fifteen_lists
df["30"] = thirty_lists
df["40"] = forty_lists

print(df)
