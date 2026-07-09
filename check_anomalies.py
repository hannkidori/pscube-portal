import os
import pandas as pd
import json

base_dir = os.path.dirname(os.path.abspath(__file__))

targets = {
    "megaface_newking_scraper": "メガフェイス豊崎本館 (ニューキングハナハナ)",
    "megaface_king_scraper": "メガフェイス豊崎本館 (キングハナハナ)",
    "megaface_myjuggler_scraper": "メガフェイス豊崎本館 (マイジャグラー)",
    "sunitoman_scraper": "サンシャイン糸満店 (ドラゴンハナハナ)",
    "sunitoman_newking_scraper": "サンシャイン糸満店 (ニューキングハナハナ)",
    "sunitoman_myjuggler_scraper": "サンシャイン糸満店 (マイジャグラー)"
}

anomalies = []

for folder, store_name in targets.items():
    csv_file = os.path.join(base_dir, folder, "master_data.csv")
    if not os.path.exists(csv_file):
        continue
        
    try:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        for _, row in df.iterrows():
            try:
                date = str(row['日付'])
                daiban = str(row['台番'])
                games = int(row['累計ゲーム数'])
                big = int(row['BIG回数'])
                reg = int(row['REG回数'])
                diff = int(row['推測差枚'])
                
                anomaly_reasons = []
                
                # Rule 1: BIG 0 with games >= 2000
                if games >= 2000 and big == 0:
                    anomaly_reasons.append("BIGゼロ異常 (2000G以上)")
                    
                # Rule 2: REG 0 with games >= 2000
                if games >= 2000 and reg == 0:
                    anomaly_reasons.append("REGゼロ異常 (2000G以上)")
                    
                # Rule 3: BIG probability < 1/100 (games >= 1000)
                if games >= 1000 and big > 0:
                    prob = games / big
                    if prob < 100:
                        anomaly_reasons.append(f"BIG確率異常 (1/{int(prob)}で異常に良すぎる)")
                        
                # Rule 4: Extreme diffs
                if diff <= -8000:
                    anomaly_reasons.append(f"大ハマり異常 (差枚{diff}枚)")
                elif diff >= 15000:
                    anomaly_reasons.append(f"大爆発異常 (差枚{diff}枚)")
                    
                if anomaly_reasons:
                    anomalies.append({
                        "store": store_name,
                        "date": date,
                        "daiban": daiban,
                        "games": games,
                        "big": big,
                        "reg": reg,
                        "diff": diff,
                        "reasons": anomaly_reasons
                    })
                    
            except Exception as inner_e:
                continue
                
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")

# Save anomalies to json
output_file = os.path.join(base_dir, "anomalies.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(anomalies, f, ensure_ascii=False, indent=4)

print(f"Found {len(anomalies)} anomalies. Saved to anomalies.json.")
