import os
import pandas as pd
import datetime
import json
import codecs

base_dir = os.path.dirname(os.path.abspath(__file__))
validations_dir = os.path.join(base_dir, "validations")
if not os.path.exists(validations_dir):
    os.makedirs(validations_dir)

stores = {
    "megaface_newking_scraper": {"name": "メガフェイス豊崎", "machine": "ニューキング", "store": "MEGAFACE"},
    "megaface_king_scraper": {"name": "メガフェイス豊崎", "machine": "キングハナハナ", "store": "MEGAFACE"},
    "megaface_myjuggler_scraper": {"name": "メガフェイス豊崎", "machine": "マイジャグラー", "store": "MEGAFACE"},
    "sunitoman_scraper": {"name": "サンシャイン糸満", "machine": "ドラゴンハナハナ", "store": "SUNITOMAN"},
    "sunitoman_newking_scraper": {"name": "サンシャイン糸満", "machine": "ニューキング", "store": "SUNITOMAN"},
    "sunitoman_myjuggler_scraper": {"name": "サンシャイン糸満", "machine": "マイジャグラー", "store": "SUNITOMAN"}
}

def generate_validation_html(t_date_str, t_minus_1_str, validation_results):
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>前日狙い目の結果検証 - {t_date_str}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #00d2d3;
            --secondary: #2f3542;
            --bg: #1e272e;
            --text: #f1f2f6;
            --card-bg: rgba(255, 255, 255, 0.05);
        }}
        body {{
            font-family: 'Inter', 'Noto Sans JP', sans-serif;
            background: linear-gradient(135deg, #1e272e 0%, #2f3542 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 2rem; }}
        h1 {{
            font-size: 2.2rem;
            background: linear-gradient(to right, #00d2d3, #0984e3);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        .back-btn {{
            display: inline-block;
            margin-bottom: 1.5rem;
            color: #a4b0be;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.3s;
        }}
        .back-btn:hover {{ color: #fff; }}
        
        .info-panel {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
            border: 1px solid rgba(0, 210, 211, 0.3);
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            border-top: 4px solid #747d8c;
            position: relative;
        }}
        
        .rank-badge {{
            position: absolute;
            top: -15px;
            left: -15px;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #f1c40f, #e67e22);
            color: #000;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 1.2rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}
        
        .machine-title {{
            font-size: 1.2rem;
            font-weight: 800;
            margin-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 5px;
        }}
        
        .prediction-box {{
            background: rgba(0,0,0,0.2);
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
            font-size: 0.9rem;
        }}
        
        .result-box {{
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .judgment {{
            font-size: 1.5rem;
            font-weight: 900;
        }}
        
        .diff-text {{
            font-size: 1.2rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../validation_calendar.html" class="back-btn">← カレンダーへ戻る</a>
        
        <header>
            <h1>🎯 前日の狙い目と結果の検証</h1>
            <p style="color: #a4b0be;">システムが弾き出した全体トップ10の狙い目が、実際に当たっていたかを検証します。</p>
        </header>
        
        <div class="info-panel">
            <h2 style="margin-bottom: 10px;">検証日: <strong>{t_date_str}</strong></h2>
            <p>使用データ: {t_minus_1_str} までのデータから算出された「{t_date_str}の狙い目」</p>
        </div>
        
        <div class="grid">
"""

    for res in validation_results:
        result_bg = f"rgba({int(res['color'][1:3], 16)}, {int(res['color'][3:5], 16)}, {int(res['color'][5:7], 16)}, 0.15)"
        diff_sign = "+" if res['実際_差枚'] > 0 else ""
        diff_color = "#2ecc71" if res['実際_差枚'] > 0 else "#e74c3c"
        store_color = "#ff6b81" if "メガフェイス" in res['店舗'] else "#ffa502" if "サンシャイン" in res['店舗'] else "#a4b0be"
        
        html += f"""
            <div class="card" style="border-top-color: {res['color']}">
                <div class="rank-badge">{res['順位']}</div>
                <div class="machine-title">
                    {res['台番']}番台 <span class="store-name" style="color: {store_color}; font-weight: bold; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; margin-left: 5px;">{res['店舗']}</span> <span style="font-size: 0.9rem; color: #a4b0be;">/ {res['機種名']}</span>
                </div>
                
                <div class="prediction-box">
                    <strong>予測スコア:</strong> {res['スコア']} pt<br>
                    <strong>選定理由:</strong> {res['予測理由']}
                </div>
                
                <div class="result-box" style="background: {result_bg}; border: 1px solid {res['color']}">
                    <div>
                        <div style="font-size: 0.8rem; color: #a4b0be;">実際の結果 (G: {res['実際_稼働']})</div>
                        <div class="diff-text" style="color: {diff_color}">{diff_sign}{res['実際_差枚']} 枚</div>
                        <div style="font-size: 0.8rem;">推測: {res['実際_設定']}</div>
                    </div>
                    <div class="judgment" style="color: {res['color']}">{res['判定']}</div>
                </div>
            </div>
"""

    html += """
        </div>
    </div>
</body>
</html>
"""
    file_path = os.path.join(validations_dir, f"{t_date_str}.html")
    with codecs.open(file_path, "w", "utf-8") as f:
        f.write(html)
    return file_path

def generate_calendar_html(dates_available):
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>検証レポート カレンダー</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #1e272e;
            --text: #f1f2f6;
            --card-bg: rgba(255, 255, 255, 0.05);
        }
        body {
            font-family: 'Inter', 'Noto Sans JP', sans-serif;
            background: linear-gradient(135deg, #1e272e 0%, #2f3542 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }
        .container { max-width: 900px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 2rem; }
        h1 {
            font-size: 2.2rem;
            background: linear-gradient(to right, #00d2d3, #0984e3);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .back-btn {
            display: inline-block;
            margin-bottom: 1.5rem;
            color: #a4b0be;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.3s;
        }
        .back-btn:hover { color: #fff; }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1.5rem;
        }
        
        .date-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            text-decoration: none;
            color: var(--text);
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }
        
        .date-card:hover {
            transform: translateY(-5px);
            border-color: #00d2d3;
            box-shadow: 0 10px 25px rgba(0, 210, 211, 0.2);
        }
        
        .date-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 4px;
            background: linear-gradient(to right, #00d2d3, #0984e3);
        }
        
        .date-icon { font-size: 2rem; margin-bottom: 10px; }
        .date-text { font-size: 1.2rem; font-weight: 800; letter-spacing: 1px; }
        .date-sub { font-size: 0.8rem; color: #a4b0be; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-btn">← ポータルへ戻る</a>
        
        <header>
            <h1>📅 過去の検証レポート一覧</h1>
            <p style="color: #a4b0be;">過去の狙い目がどれくらい当たっていたかを確認できます。</p>
        </header>
        
        <div class="calendar-grid">
"""

    dates_available.sort(reverse=True)
    for d in dates_available:
        html += f"""
            <a href="validations/{d}.html" class="date-card">
                <div class="date-icon">🎯</div>
                <div class="date-text">{d}</div>
                <div class="date-sub">結果検証を見る</div>
            </a>
"""

    html += """
        </div>
    </div>
</body>
</html>
"""
    with codecs.open(os.path.join(base_dir, "validation_calendar.html"), "w", "utf-8") as f:
        f.write(html)


def run_validation():
    all_data = []
    
    # 1. Load all data
    for folder, info in stores.items():
        csv_path = os.path.join(base_dir, folder, "master_data.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            df["店舗"] = info["name"]
            df["store_code"] = info["store"]
            all_data.append(df)
            
    if not all_data:
        print("No master_data.csv found.")
        return
        
    master_df = pd.concat(all_data, ignore_index=True)
    master_df["日付"] = pd.to_datetime(master_df["日付"])
    
    dates = master_df["日付"].sort_values().unique()
    if len(dates) < 2:
        print("Not enough dates to run validation.")
        return
        
    generated_dates = []
    
    print("Generating validation reports for all historical dates...")
    
    for i in range(1, len(dates)):
        T_date = dates[i]
        T_minus_1_date = dates[i - 1]
        
        t_date_str = pd.to_datetime(T_date).strftime('%Y-%m-%d')
        t_minus_1_str = pd.to_datetime(T_minus_1_date).strftime('%Y-%m-%d')
        
        # 3. Filter data for prediction
        pred_data = master_df[master_df["日付"] <= T_minus_1_date].copy()
        
        predictions = []
        
        # 4. Score all machines
        for (store_name, machine_name, daiban), group in pred_data.groupby(["店舗", "機種名", "台番"]):
            group = group.sort_values("日付")
            if group.empty:
                continue
                
            latest_data = group.iloc[-1]
            
            date_7_days_ago = T_minus_1_date - pd.Timedelta(days=7)
            recent_7days = group[group["日付"] > date_7_days_ago]
            
            diff_7days = recent_7days["推測差枚"].sum() if not recent_7days.empty else 0
            games_7days = recent_7days["累計ゲーム数"].sum() if not recent_7days.empty else 0
            
            score = 0
            tags = []
            
            if latest_data["最有力設定"] in ["設定V", "設定4", "設定6", "設定5"]:
                score -= 100
                tags.append("前日高設定(下げ確実)")
                
            has_recent_high = any((r["最有力設定"] in ["設定V", "設定4", "設定6", "設定5"]) or (r["推測差枚"] >= 2000) for _, r in recent_7days.iterrows())
            if has_recent_high:
                score -= 50
                tags.append("1週間内に高設定/出玉あり(見送り)")
            else:
                if diff_7days <= -4000:
                    score += 80
                    tags.append("完全放置・大凹み上げ狙い")
                elif diff_7days <= -2000:
                    score += 50
                    tags.append("完全放置・凹み上げ狙い")
                    
                if diff_7days < 0 and games_7days > 0:
                    game_bonus = int(games_7days / 1000) * 3
                    score += game_bonus
                    if game_bonus >= 30:
                        tags.append("高稼働マイナス台(店側のお詫び期待)")
                        
            if not tags:
                tags.append("特筆なし")
                
            predictions.append({
                "店舗": store_name,
                "機種名": machine_name,
                "台番": daiban,
                "スコア": score,
                "タグ": " / ".join(tags)
            })
            
        if not predictions:
            continue
            
        predictions_df = pd.DataFrame(predictions)
        predictions_df = predictions_df.sort_values("スコア", ascending=False)
        
        top_10 = predictions_df.head(10).to_dict('records')
        
        # 5. Check actual results on T_date
        actual_data = master_df[master_df["日付"] == T_date].copy()
        
        validation_results = []
        
        for rank, p in enumerate(top_10, 1):
            actual_row = actual_data[(actual_data["店舗"] == p["店舗"]) & (actual_data["機種名"] == p["機種名"]) & (actual_data["台番"] == p["台番"])]
            
            res = {
                "順位": rank,
                "店舗": p["店舗"],
                "機種名": p["機種名"],
                "台番": p["台番"],
                "スコア": p["スコア"],
                "予測理由": p["タグ"],
                "実際_稼働": 0,
                "実際_差枚": 0,
                "実際_設定": "データなし",
                "判定": "不発 ❌",
                "color": "#e74c3c"
            }
            
            if not actual_row.empty:
                row = actual_row.iloc[0]
                diff = int(row["推測差枚"])
                res["実際_稼働"] = int(row["累計ゲーム数"])
                res["実際_差枚"] = diff
                res["実際_設定"] = str(row["最有力設定"])
                
                if diff >= 2000:
                    res["判定"] = "大勝利 🎉"
                    res["color"] = "#f1c40f"
                elif diff > 0:
                    res["判定"] = "勝利 🎯"
                    res["color"] = "#2ecc71"
                elif res["実際_稼働"] < 500:
                    res["判定"] = "稼働不足 ⚠️"
                    res["color"] = "#95a5a6"
            else:
                res["判定"] = "データ未取得 ⚠️"
                res["color"] = "#95a5a6"
                
            validation_results.append(res)
            
        generate_validation_html(t_date_str, t_minus_1_str, validation_results)
        generated_dates.append(t_date_str)
        print(f"Generated validation HTML for {t_date_str}")
        
    generate_calendar_html(generated_dates)
    print("Generated validation_calendar.html with all dates.")

if __name__ == "__main__":
    run_validation()
