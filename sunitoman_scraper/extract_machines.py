import os
import glob
import email
from bs4 import BeautifulSoup
import math
import csv
import datetime

# 機種スペック（ドラゴンハナハナ-閃光-SP-30）
COIN_PER_GAME = 50 / 39.0  # ベース約39.0G = 約1.2820枚/G
BIG_COINS = 252
REG_COINS = 96

# 設定確率 (設定1〜6)
SETTINGS = ["設定1", "設定2", "設定3", "設定4", "設定5", "設定6"]
PROB_BIG = [1/256, 1/246, 1/235, 1/224, 1/212, 1/199]
PROB_REG = [1/642, 1/585, 1/537, 1/489, 1/442, 1/399]

PRIOR_PROB = [0.45, 0.20, 0.15, 0.10, 0.05, 0.05] # ホール側の設定配分（仮定）

def calculate_log_likelihood(n, k, p):
    if p <= 0 or p >= 1:
        return -float('inf')
    # 二項分布の対数尤度 (定数項 log(nCk) は設定比較では相殺されるので省略可能だが、一応計算)
    # math.comb は n < k のとき 0 になる
    if k > n:
        return -float('inf')
    
    # 尤度計算のオーバーフローを防ぐために対数で計算
    # log(P(X=k)) = log(nCk) + k*log(p) + (n-k)*log(1-p)
    try:
        log_comb = math.log(math.comb(n, k))
    except ValueError:
        return -float('inf')
        
    return log_comb + k * math.log(p) + (n - k) * math.log(1 - p)

def bayesian_inference(games, big_count, reg_count):
    if games <= 0:
        return {s: 100.0/len(SETTINGS) for s in SETTINGS}, "設定?"
        
    log_posteriors = []
    
    for i in range(len(SETTINGS)):
        ll_big = calculate_log_likelihood(games, big_count, PROB_BIG[i])
        ll_reg = calculate_log_likelihood(games, reg_count, PROB_REG[i])
        
        # 事前確率の対数
        ll_prior = math.log(PRIOR_PROB[i])
        
        log_post = ll_big + ll_reg + ll_prior
        log_posteriors.append(log_post)
        
    # 対数尤度から確率に戻す（オーバーフロー対策で最大値を引く）
    max_log_post = max(log_posteriors)
    posteriors = [math.exp(lp - max_log_post) for lp in log_posteriors]
    
    # 正規化
    sum_post = sum(posteriors)
    normalized = [p / sum_post * 100 for p in posteriors]
    
    result = {SETTINGS[i]: normalized[i] for i in range(len(SETTINGS))}
    best_setting = SETTINGS[normalized.index(max(normalized))]
    
    return result, best_setting

def process_file(filepath):
    print(f"Processing: {filepath}")
    
    # MHTMLの解析
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        msg = email.message_from_file(f)
        
    html_content = ""
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            break
            
    if not html_content:
        # MHTMLではなく純粋なHTMLファイルの場合
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 日付の決定
    now = datetime.datetime.now()
    if now.hour < 9:
        now = now - datetime.timedelta(days=1)
    
    date_offset = 0
    active_tabs = soup.find_all(class_='is-active')
    if active_tabs:
        date_text = active_tabs[-1].get_text(strip=True)
        # Handle literal unicode escapes if they exist in the HTML string
        if r'\u' in date_text:
            date_text = date_text.encode('utf-8', errors='ignore').decode('unicode_escape', errors='ignore')
            
        if '昨日' in date_text:
            date_offset = 1
        elif '日前' in date_text:
            try:
                date_offset = int(date_text.replace('日前', ''))
            except:
                pass
    
    target_date = (now - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")
    
    # テーブル行の取得
    rows = soup.find_all('tr')
    
    results = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 11:
            try:
                daiban = cols[0].get_text(strip=True)
                big_cnt = int(cols[1].get_text(strip=True))
                reg_cnt = int(cols[2].get_text(strip=True))
                games = int(cols[6].get_text(strip=True)) # 累計スタート
                
                # P-mobaはたまにデータがない台があるためスキップ
                if not daiban.isdigit(): continue
                
                # 差枚数推測
                diff_coins = (big_cnt * BIG_COINS) + (reg_cnt * REG_COINS) - (games * COIN_PER_GAME)
                
                # ベイズ推定
                probs, best = bayesian_inference(games, big_cnt, reg_cnt)
                
                results.append({
                    "日付": target_date,
                    "機種名": "Sドラゴンハナハナ-閃光-SP-30",
                    "台番": daiban,
                    "累計ゲーム数": games,
                    "BIG回数": big_cnt,
                    "REG回数": reg_cnt,
                    "推測差枚": int(diff_coins),
                    "REG確率": math.floor(games / reg_cnt) if reg_cnt > 0 else 0,
                    "最有力設定": best,
                    "設定1(%)": round(probs["設定1"], 1),
                    "設定2(%)": round(probs["設定2"], 1),
                    "設定3(%)": round(probs["設定3"], 1),
                    "設定4(%)": round(probs["設定4"], 1),
                    "設定5(%)": round(probs["設定5"], 1),
                    "設定6(%)": round(probs["設定6"], 1),
                })
            except Exception as e:
                pass # パース失敗行は無視
                
    return results

def main():
    target_dir = os.path.dirname(os.path.abspath(__file__))
    html_files = glob.glob(os.path.join(target_dir, "*.html")) + glob.glob(os.path.join(target_dir, "*.mht"))
    
    if not html_files:
        print("Error: No HTML files found in directory.")
        return
        
    all_data = []
    for f in html_files:
        if "report" not in f:
            all_data.extend(process_file(f))
            
    if not all_data:
        print("No valid data extracted.")
        return
        
    csv_file = os.path.join(target_dir, "master_data.csv")
    file_exists = os.path.exists(csv_file)
    
    # 重複排除のために既存のデータを読み込む
    existing_records = set()
    if file_exists:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_records.add((row["日付"], row["台番"]))
                
    # 追記
    fieldnames = ["日付", "機種名", "台番", "累計ゲーム数", "BIG回数", "REG回数", "推測差枚", "REG確率", "最有力設定", 
                  "設定1(%)", "設定2(%)", "設定3(%)", "設定4(%)", "設定5(%)", "設定6(%)"]
                  
    with open(csv_file, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            
        added = 0
        for data in all_data:
            if (data["日付"], data["台番"]) not in existing_records:
                writer.writerow(data)
                added += 1
                
    print(f"Extracted {len(all_data)} machines.")
    print(f"Added {added} NEW records to master_data.csv.")

if __name__ == "__main__":
    main()
