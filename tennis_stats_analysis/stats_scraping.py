from urllib import request
from bs4 import BeautifulSoup
import re
import time
import csv

urls = [
    "https://sportsnavi.ht.kyodo-d.jp/tennis/match/21119685/stats/"
]

for url in urls:
    #Webページからのスクレイピング
    html = request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")

    #セット数の取得
    set_html = soup.find(id="selectPeriod")
    set_sum = len(set_html.find_all("option")) - 1

    for i in range(1, set_sum + 1):
        home_player = dict()
        away_player = dict()

        link_html = request.urlopen(url + "?period={}".format(i)).read()
        link_soup = BeautifulSoup(link_html, "html.parser")

        stats_html = link_soup.find(id="modTennisStats").find(type="text/javascript")

        stats_html = stats_html.encode('utf-8')
        f = stats_html.decode('utf-8')
        f = f.replace("1st", "")
        f = f.replace("2nd", "")
        regex = re.compile('\d+')
        result = regex.findall(f)

        home = result[::2]
        away = result[1::2]
        labels = ["1stserve_percentage", "1stserve_point", "2ndserve_point", "ace", "double_fault", "break"]

        for h, a, l in zip(home, away, labels):
            home_player[l] = int(h)
            away_player[l] = int(a)

        table_html = link_soup.find(class_="ht-table--comparison")
        h_table = table_html.find_all(class_="ht-table--comparison__itemScoreHome")
        a_table = table_html.find_all(class_="ht-table--comparison__itemScoreAway")
        labels = ["game", "point", "game_streak", "point_streak"]

        for h, a, l in zip(h_table, a_table, labels):
            home_player[l] = int(h.text)
            away_player[l] = int(a.text)

        hp_stats = []
        ap_stats = []
        if home_player["game"] == 7:
            home_player["game"] -= 1
        elif away_player["game"] == 7:
            away_player["game"] -= 1
        else:
            pass
        hp_serve_game_sum = home_player["game"] - home_player["break"] + away_player["break"]
        ap_serve_game_sum = away_player["game"] - away_player["break"] + home_player["break"]

        #1stサーブ成功率
        hp_stats.append(home_player["1stserve_percentage"])
        ap_stats.append(away_player["1stserve_percentage"])

        #1stサーブ時得点率
        hp_stats.append(home_player["1stserve_point"])
        ap_stats.append(away_player["1stserve_point"])

        #全サーブポイント中の1stサーブ得点率
        hp_stats.append(home_player["1stserve_percentage"] * home_player["1stserve_point"] / 100)
        ap_stats.append(away_player["1stserve_percentage"] * away_player["1stserve_point"] / 100)

        #1サーブゲームあたりのダブルフォルト数
        hp_stats.append(home_player["double_fault"] / hp_serve_game_sum)
        ap_stats.append(away_player["double_fault"] / ap_serve_game_sum)

        #サーブキープ率
        hp_stats.append((home_player["game"] - home_player["break"]) / hp_serve_game_sum * 100)
        ap_stats.append((away_player["game"] - away_player["break"]) / ap_serve_game_sum * 100)

        #エースでの得点率
        hp_stats.append(home_player["ace"] / home_player["point"] * 100)
        ap_stats.append(away_player["ace"] / away_player["point"] * 100)

        #得点率
        sum_point = home_player["point"] + away_player["point"]
        hp_stats.append(home_player["point"] / sum_point * 100)
        ap_stats.append(away_player["point"] / sum_point * 100)

        #セットの勝敗
        def hp_win():
            hp_stats.append(1)
            ap_stats.append(0)
        def ap_win():
            hp_stats.append(0)
            ap_stats.append(1)

        if home_player["game"] == 6:
            hp_win()
        elif away_player["game"] == 6:
            ap_win()
        else:
            pass

        with open("game_stats.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(hp_stats)
            writer.writerow(ap_stats)

        time.sleep(1)