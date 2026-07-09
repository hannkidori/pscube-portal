import csv
import glob
import os
import datetime
import math
import re
from bs4 import BeautifulSoup

# 機種スペック（マイジャグラーV）
COIN_PER_GAME = 50 / 42.0
BIG_COINS = 240
REG_COINS = 96

# 設定確率 (設定1〜6)
SETTINGS = ["設定1", "設定2", "設定3", "設定4", "設定5", "設定6"]
PROB_BIG = [1/273.1, 1/270.8, 1/266.3, 1/254.0, 1/240.1, 1/229.1]
PROB_REG = [1/409.6, 1/385.5, 1/336.1, 1/290.0, 1/268.6, 1/229.1]

PRIOR_PROB = [0.45, 0.20, 0.15, 0.10, 0.05, 0.05]

def calculate_log_likelihood(n, k, p):
    if p <= 0 or p >= 1: return -float('inf')
    if k > n: return -float('inf')
    try: log_comb = math.log(math.comb(n, k))
    except ValueError: return -float('inf')
    return log_comb + k * math.log(p) + (n - k) * math.log(1 - p)

def bayesian_inference(games, big_count, reg_count):
    if games <= 0:
        return {s: 100.0/len(SETTINGS) for s in SETTINGS}, "不明"
        
    log_posteriors = []
    
    for i in range(len(SETTINGS)):
        ll_big = calculate_log_likelihood(games, big_count, PROB_BIG[i])
        ll_reg = calculate_log_likelihood(games, reg_count, PROB_REG[i])
        ll_prior = math.log(PRIOR_PROB[i])
        log_post = ll_big + ll_reg + ll_prior
        log_posteriors.append(log_post)
        
    max_log_post = max(log_posteriors)
    posteriors = [math.exp(lp - max_log_post) for lp in log_posteriors]
    
    sum_post = sum(posteriors)
    normalized = [p / sum_post * 100 for p in posteriors]
    
    result = {SETTINGS[i]: round(normalized[i], 1) for i in range(len(SETTINGS))}
    best_setting = SETTINGS[normalized.index(max(normalized))]
    
    return result, best_setting

html_files = glob.glob("*.html")
html_files = [f for f in html_files if f not in ["report.html", "page_after_captcha.html"]]

master_file = "master_data.csv"
existing_data = {}

if os.path.exists(master_file):
    with open(master_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['日付']}_{row['機種名']}_{row['台番']}"
            existing_data[key] = row

new_results = []

for target_file in html_files:
    try:
        mtime = os.path.getmtime(target_file)
        dt = datetime.datetime.fromtimestamp(mtime)
        if dt.hour < 9:
            reference_date = (dt - datetime.timedelta(days=1)).date()
        else:
            reference_date = dt.date()
            
        with open(target_file, "r", encoding="utf-8", errors="ignore") as file:
            soup = BeautifulSoup(file, "html.parser")
            
        title = soup.title.string if soup.title else "不明"
        machine_name = title.split("｜")[-1] if "｜" in title else "SマイジャグラーV"

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
            days_ago = int(re.sub(r'[^0-9]', '', active_tab_text)) if re.sub(r'[^0-9]', '', active_tab_text) else 1
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
                    coin_in = games * COIN_PER_GAME
                    coin_out = (big * BIG_COINS) + (reg * REG_COINS)
                    estimated_diff = int(coin_out - coin_in)
                    
                    total_bonus = big + reg
                    gassan = round(games / total_bonus, 1) if total_bonus > 0 else 0
                    reg_prob = round(games / reg, 1) if reg > 0 else 0
                else:
                    estimated_diff = 0
                    gassan = 0
                    reg_prob = 0
                
                bayes_probs, best_setting = bayesian_inference(games, big, reg)
                if games < 500:
                    best_setting = "判定不能(G不足)"

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
                    "設定1(%)": bayes_probs["設定1"],
                    "設定2(%)": bayes_probs["設定2"],
                    "設定3(%)": bayes_probs["設定3"],
                    "設定4(%)": bayes_probs["設定4"],
                    "設定5(%)": bayes_probs["設定5"],
                    "設定6(%)": bayes_probs["設定6"]
                }
                
                data_key = f"{date_str}_{machine_name}_{daiban}"
                existing_data[data_key] = row_dict
                
    except Exception as e:
        print(f"Error parsing {target_file}: {e}")

all_rows = list(existing_data.values())
all_rows.sort(key=lambda x: (x["日付"], x["台番"]), reverse=True)

with open(master_file, "w", encoding="utf-8-sig", newline="") as f:
    if len(all_rows) > 0:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)

print(f"Master Database updated! Total {len(all_rows)} records in {master_file}")
