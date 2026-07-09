import csv
import glob
import os
import datetime
import math
from bs4 import BeautifulSoup

# 設定の確率定義（ハナハナV-30）
SETTINGS = {
    "1": {"BIG": 1/299, "REG": 1/496},
    "2": {"BIG": 1/291, "REG": 1/471},
    "3": {"BIG": 1/281, "REG": 1/442},
    "4": {"BIG": 1/268, "REG": 1/409},
    "V": {"BIG": 1/253, "REG": 1/372},
}

def calculate_bayes_probabilities(games, big, reg):
    if games == 0:
        return {"1": 20.0, "2": 20.0, "3": 20.0, "4": 20.0, "V": 20.0}, "不明"
    
    log_likelihoods = {}
    for s_name, probs in SETTINGS.items():
        p_big = probs["BIG"]
        p_reg = probs["REG"]
        
        # 二項分布の対数尤度 (定数項の組み合わせ計算は全設定共通なので省略)
        # BIGの尤度
        ll_big = big * math.log(p_big) + (games - big) * math.log(1 - p_big)
        # REGの尤度
        ll_reg = reg * math.log(p_reg) + (games - reg) * math.log(1 - p_reg)
        
        log_likelihoods[s_name] = ll_big + ll_reg
        
    # Log-Sum-Expトリックで確率に戻す
    max_ll = max(log_likelihoods.values())
    sum_exp = 0
    probs = {}
    for s_name, ll in log_likelihoods.items():
        probs[s_name] = math.exp(ll - max_ll)
        sum_exp += probs[s_name]
        
    final_probs = {}
    best_setting = "1"
    best_prob = -1
    for s_name in log_likelihoods.keys():
        prob_percent = (probs[s_name] / sum_exp) * 100
        final_probs[s_name] = round(prob_percent, 1)
        if prob_percent > best_prob:
            best_prob = prob_percent
            best_setting = s_name
            
    return final_probs, best_setting

html_files = glob.glob("*.html")
html_files = [f for f in html_files if f not in ["report.html", "page_after_captcha.html", "P'sCUBE（ピーズキューブ）_メガフェイス豊崎本館.html", "P'sCUBE（ピーズキューブ）｜SBﾆｭｰｷﾝｸﾞﾊﾅﾊﾅV-30.html"]]

master_file = "master_data.csv"
existing_data = {}

# 既存データの読み込み (重複防止のため key: 機種名_台番_日付)
if os.path.exists(master_file):
    with open(master_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['日付']}_{row['機種名']}_{row['台番']}"
            existing_data[key] = row

new_results = []

for target_file in html_files:
    try:
        # ファイルの更新日時から基準となる「営業日」を算出
        # 深夜0時〜9時は前日の営業日とする
        mtime = os.path.getmtime(target_file)
        dt = datetime.datetime.fromtimestamp(mtime)
        if dt.hour < 9:
            reference_date = (dt - datetime.timedelta(days=1)).date()
        else:
            reference_date = dt.date()
            
        with open(target_file, "r", encoding="utf-8", errors="ignore") as file:
            soup = BeautifulSoup(file, "html.parser")
            
        title = soup.title.string if soup.title else "不明"
        machine_name = title.split("｜")[-1] if "｜" in title else "SBニューキングハナハナV-30"

        # アクティブなタブ（相対日付）から絶対日付を計算
        active_tab_text = "本日"
        active_tabs = soup.find_all(class_=lambda c: c and ('active' in c or 'selected' in c or 'current' in c))
        for tab in active_tabs:
            text = tab.get_text(strip=True).replace('{', '本日').replace('O', '日前')
            if '日前' in text or '本日' in text:
                active_tab_text = text
                break
                
        if active_tab_text == "本日":
            actual_date = reference_date
        else:
            days_ago = int(active_tab_text.replace("日前", ""))
            actual_date = reference_date - datetime.timedelta(days=days_ago)
            
        date_str = actual_date.strftime("%Y-%m-%d")

        tables = soup.find_all("table")
        for table in tables:
            parent = table.find_parent("li")
            if not parent:
                parent = table.find_parent("div", class_=lambda c: c and ('box' in c or 'item' in c or 'grid' in c or 'cell' in c))
                
            if parent:
                daiban = ""
                for tag in parent.find_all('div', class_='line'):
                    daiban = tag.get_text(strip=True)
                    break
                if not daiban:
                    continue
                    
                stats = {}
                rows = table.find_all("tr")
                for row in rows:
                    cells = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
                    if len(cells) == 2:
                        key = cells[0].replace('m', '確率').replace('݌vQ[', '累計ゲーム').replace('őo', '最大放出数')
                        val = cells[1]
                        stats[key] = val
                        
                big_str = stats.get('BIG', '0')
                reg_str = stats.get('REG', '0')
                games_str = stats.get('累計ゲーム', '0')
                max_payout_str = stats.get('最大放出数', '0')
                
                big = int(big_str) if big_str.isdigit() else 0
                reg = int(reg_str) if reg_str.isdigit() else 0
                games = int(games_str) if games_str.isdigit() else 0
                max_payout = int(max_payout_str) if max_payout_str.isdigit() else 0
                
                if games > 0:
                    coin_in = games * 1.4124
                    coin_out = (big * 312) + (reg * 130)
                    estimated_diff = int(coin_out - coin_in)
                    
                    total_bonus = big + reg
                    gassan = round(games / total_bonus, 1) if total_bonus > 0 else 0
                    reg_prob = round(games / reg, 1) if reg > 0 else 0
                else:
                    estimated_diff = 0
                    gassan = 0
                    reg_prob = 0
                
                # ベイズ推定による各設定の確率計算
                bayes_probs, best_setting = calculate_bayes_probabilities(games, big, reg)
                if games < 500:
                    best_setting = "判定不能(G不足)"
                else:
                    best_setting = f"設定{best_setting}"

                row_dict = {
                    "日付": date_str,
                    "機種名": machine_name,
                    "台番": daiban,
                    "累計ゲーム数": games,
                    "BIG回数": big,
                    "REG回数": reg,
                    "最大放出数": max_payout,
                    "推測差枚": estimated_diff,
                    "合算確率": gassan,
                    "REG確率": reg_prob,
                    "最有力設定": best_setting,
                    "設定1(%)": bayes_probs["1"],
                    "設定2(%)": bayes_probs["2"],
                    "設定3(%)": bayes_probs["3"],
                    "設定4(%)": bayes_probs["4"],
                    "設定V(%)": bayes_probs["V"]
                }
                
                data_key = f"{date_str}_{machine_name}_{daiban}"
                existing_data[data_key] = row_dict
                
    except Exception as e:
        print(f"Error parsing {target_file}: {e}")

# 辞書をリストに戻して日付順にソートして保存
all_rows = list(existing_data.values())
all_rows.sort(key=lambda x: (x["日付"], x["台番"]), reverse=True)

with open(master_file, "w", encoding="utf-8-sig", newline="") as f:
    if len(all_rows) > 0:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)

print(f"Master Database updated! Total {len(all_rows)} records in {master_file}")
