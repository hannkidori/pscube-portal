import csv
import sys
import json
from collections import defaultdict
import datetime
import os
import chardet

csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "master_data.csv")
html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.html")

data = []
if os.path.exists(csv_file):
    import chardet
    with open(csv_file, 'rb') as f_raw:
        raw_bytes = f_raw.read()
        detected = chardet.detect(raw_bytes)
        enc = detected['encoding'] or 'utf-8'
    with open(csv_file, 'r', encoding=enc) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)


import sys
original_data = data.copy()
if len(sys.argv) > 1:
    target_date_str = sys.argv[1]
    data = [r for r in data if r["日付"] <= target_date_str]
    html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"report_{target_date_str}.html")
else:
    html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.html")

all_dates = sorted(list(set(r["日付"] for r in original_data)), reverse=True)

machine_history = defaultdict(list)
for row in data:
    machine_history[row["台番"]].append(row)

predictions = []

if data:
    last_date_str = sorted(list(set(r["日付"] for r in data)))[-1]
    last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d")
    tomorrow = last_date + datetime.timedelta(days=1)
    is_friday = tomorrow.weekday() == 4
    is_tokubi = tomorrow.day % 10 in [1, 6]

    tomorrow_tags = []
    if is_friday: tomorrow_tags.append("華金（金曜日）")
    if is_tokubi: tomorrow_tags.append("特日（1・6の付く日）")
    tomorrow_info = " / ".join(tomorrow_tags) if tomorrow_tags else "通常営業日"
else:
    tomorrow_info = "データなし"
    tomorrow = datetime.datetime.now()

for daiban, history in machine_history.items():
    history.sort(key=lambda x: x["日付"], reverse=True)
    if not history: continue

    latest_data = history[0]
    score = 0
    tags = []
    if 0 < 0:
        tags.append("ベース設定低め(基本回収)")
    
    recent_3days = history[:3]
    recent_7days = history[:7]
    recent_14days = history[:14]
    
    diff_3days = sum(int(r["推測差枚"]) for r in recent_3days)
    games_3days = sum(int(r["累計ゲーム数"]) for r in recent_3days)
    
    diff_7days = sum(int(r["推測差枚"]) for r in recent_7days)
    games_7days = sum(int(r["累計ゲーム数"]) for r in recent_7days)
    
    diff_14days = sum(int(r["推測差枚"]) for r in recent_14days)
    games_14days = sum(int(r["累計ゲーム数"]) for r in recent_14days)
    
    # 前日が高設定だった場合の差枚数に応じた段階的ペナルティ/ボーナス
    latest_diff = int(latest_data.get("推測差枚", 0))
    if latest_data["最有力設定"] in ["設定6", "設定5", "設定V", "設定4"]:
        if latest_diff >= 4000:
            score -= 80
            tags.append("前日大爆発(下げ濃厚)")
        elif latest_diff >= 2000:
            score -= 40
            tags.append("前日優秀台(下げ警戒)")
        elif latest_diff > 0:
            score -= 10
            tags.append("前日ちょい勝ち(据え置き期待)")
        else:
            score += 50
            tags.append("前日高設定の不発(据え置き大チャンス!)")
            
    # マイナスからの反発・凹み上げ狙い
    if diff_7days <= -4000:
        score += 80
        tags.append("完全放置・大凹み上げ狙い")
    elif diff_7days <= -2000:
        score += 50
        tags.append("完全放置・凹み上げ狙い")
        
    # 高稼働マイナス台への店側のお詫び期待
    if diff_7days < 0 and games_7days > 0:
        game_bonus = int(games_7days / 1000) * 3
        score += game_bonus
        if game_bonus >= 30: 
            tags.append("高稼働マイナス台(お詫び期待)")

    if not tags: tags.append("特筆なし")

    predictions.append({
        "台番": daiban,
        "スコア": score,
        "タグ": "/ ".join(tags),
        "前日差枚": latest_data["推測差枚"],
        "diff_3": diff_3days, "games_3": games_3days,
        "diff_7": diff_7days, "games_7": games_7days,
        "diff_14": diff_14days, "games_14": games_14days
    })

predictions.sort(key=lambda x: x["スコア"], reverse=True)
predictions = predictions[:6]

json_data = json.dumps(data, ensure_ascii=False)
json_predictions = json.dumps(predictions, ensure_ascii=False)
with open("ranking.json", "w", encoding="utf-8") as f:
    f.write(json_predictions)

options_html = ""
for i, d in enumerate(all_dates):
    selected = "selected" if d == last_date_str else ""
    val = "report.html" if i == 0 else f"report_{d}.html"
    label = f"{d} (最新)" if i == 0 else d
    options_html += f'<option value="{val}" {selected}>{label}</option>\n'

dropdown_html = f"""
<div style="text-align: center; margin-bottom: 1.5rem; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; display: inline-block;">
    <span style="color: #00d2d3; font-weight: bold; margin-right: 10px;">📅 表示中のデータ: </span>
    <select onchange="window.location.href=this.value" style="padding: 8px 15px; border-radius: 5px; background: #2f3542; color: #fff; border: 1px solid #00d2d3; cursor: pointer; font-size: 1rem; font-weight: bold; outline: none;">
        {options_html}
    </select>
</div>
"""

html_content = f"""
<!DOCTYPE html>
<html lang=\"ja\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>スロット分析＆予測レポート</title>
    <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+JP:wght@400;700;900&display=swap\" rel=\"stylesheet\">
    <style>
        :root {{
            --primary: #f39c12;
            --secondary: #2f3542;
            --bg: #1e272e;
            --text: #f1f2f6;
            --card-bg: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
            --gold: #ffa502;
            --neon-blue: #00d2d3;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', 'Noto Sans JP', sans-serif;
            background: linear-gradient(135deg, #1e272e 0%, #2f3542 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 2rem; animation: fadeInDown 0.8s ease; }}
        h1 {{
            font-size: 2.5rem; font-weight: 900;
            background: linear-gradient(to right, #f39c12, #ff6b81);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        p.subtitle {{ color: #a4b0be; font-size: 1.1rem; }}
        .date-banner {{
            background: rgba(0, 210, 211, 0.1);
            border: 1px solid var(--neon-blue);
            color: var(--neon-blue);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            font-weight: 800;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            box-shadow: 0 0 15px rgba(0, 210, 211, 0.2);
        }}
        .tabs {{ display: flex; justify-content: center; margin-bottom: 2rem; gap: 1rem; }}
        .tab-btn {{
            background: var(--card-bg); color: var(--text);
            border: 1px solid var(--border); border-radius: 30px;
            padding: 0.8rem 2rem; font-size: 1.1rem; font-weight: 700;
            cursor: pointer; transition: all 0.3s;
        }}
        .tab-btn.active {{ background: linear-gradient(to right, #f39c12, #ff6b81); border-color: transparent; box-shadow: 0 4px 15px rgba(243, 156, 18, 0.4); }}
        .tab-content {{ display: none; animation: fadeInUp 0.5s ease; }}
        .tab-content.active {{ display: block; }}
        .date-buttons-container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-bottom: 2rem; }}
        .date-btn {{
            background: rgba(255,255,255,0.05); color: #a4b0be;
            border: 1px solid var(--border); border-radius: 8px;
            padding: 0.8rem 1.5rem; font-size: 1rem; font-weight: 700;
            cursor: pointer; transition: 0.3s;
        }}
        .date-btn:hover {{ background: rgba(255,255,255,0.1); color: #fff; }}
        .date-btn.active {{ background: #f39c12; color: #fff; border-color: #f39c12; box-shadow: 0 4px 15px rgba(243, 156, 18, 0.4); }}
        .summary-dashboard {{ display: none; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .summary-dashboard.active {{ display: grid; animation: fadeInUp 0.5s ease; }}
        .summary-card {{ background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02)); border: 1px solid var(--border); border-radius: 12px; padding: 1.2rem; text-align: center; }}
        .summary-title {{ font-size: 0.9rem; color: #a4b0be; margin-bottom: 0.5rem; }}
        .summary-value {{ font-size: 1.5rem; font-weight: 900; color: #fff; }}
        .table-container {{
            display: none; background: var(--card-bg); backdrop-filter: blur(10px);
            border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); overflow-x: auto;
        }}
        .table-container.active {{ display: block; animation: fadeInUp 0.5s ease; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap; }}
        th, td {{ padding: 1rem; border-bottom: 1px solid var(--border); }}
        th {{ font-weight: 600; color: #f39c12; cursor: pointer; }}
        tr:hover {{ background: rgba(255, 255, 255, 0.1); transform: scale(1.01); transition: 0.2s; }}
        .diff-positive {{ color: #2ed573; font-weight: 800; }}
        .diff-negative {{ color: #ff4757; font-weight: 800; }}
        .setting-good {{ color: #f39c12; font-weight: 800; }}
        .setting-ok {{ color: #eccc68; font-weight: 800; }}
        .setting-bad {{ color: #747d8c; font-weight: 400; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1.5rem; }}
        .card {{
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02));
            border: 1px solid var(--border); border-radius: 16px;
            padding: 1.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            position: relative; overflow: hidden;
        }}
        .card::before {{
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px;
            background: linear-gradient(to right, #f39c12, #ff6b81);
        }}
        .card-title {{ font-size: 1.5rem; font-weight: 900; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: flex-end; }}
        .card-score {{ color: var(--gold); font-size: 1.2rem; }}
        .score-bar-bg {{ background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; margin-bottom: 1.2rem; overflow: hidden; }}
        .score-bar-fill {{ height: 100%; background: linear-gradient(to right, #f39c12, #ff6b81); box-shadow: 0 0 10px rgba(243, 156, 18, 0.5); }}
        .card-tag {{ display: inline-block; background: rgba(243, 156, 18, 0.2); color: #ffeb3b; padding: 0.4rem 0.8rem; border-radius: 8px; font-weight: 700; margin-bottom: 1rem; }}
        .period-stats {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; background: rgba(0,0,0,0.2); border-radius: 8px; overflow: hidden; }}
        .period-stats th, .period-stats td {{ padding: 0.5rem; text-align: center; font-size: 0.9rem; border-bottom: 1px solid rgba(255,255,255,0.05); }}
        .period-stats th {{ background: rgba(255,255,255,0.05); color: #a4b0be; font-weight: 600; }}
        .period-stats tr:last-child td {{ border-bottom: none; }}
        .prob-bar-container {{ width: 120px; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; display: flex; overflow: hidden; margin-top: 4px; }}
        .prob-6 {{ background: #f39c12; }}
        .prob-5 {{ background: #ff4757; }}
        .prob-4 {{ background: #eccc68; }}
        .prob-3 {{ background: #7bed9f; }}
        .prob-2 {{ background: #747d8c; }}
        .prob-1 {{ background: #2f3542; }}
        @keyframes fadeInDown {{ from {{ opacity: 0; transform: translateY(-20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
</head>
<body>
    <div class="container">
        <div style="margin-bottom: 1rem;">
            <a href="../index.html" style="display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.1); color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 12px; font-weight: bold; transition: background 0.3s; border: 1px solid rgba(255,255,255,0.2);" onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">
                <span style="font-size: 1.2rem;">🏠</span> ポータルへ戻る
            </a>
        </div>
        <header>
            <h1>AI PREDICTION & ANALYSIS</h1>
            <p class="subtitle">キングハナハナ-30 / メガフェイス豊崎本館</p>
        </header>
        <div style="text-align: center;">
            {dropdown_html}
        </div>

        <div class="date-banner">
            📅 明日 ({tomorrow.strftime("%Y-%m-%d")}) の営業日属性: {tomorrow_info}
        </div>

        <div class="tabs">
            <button class="tab-btn" onclick="switchTab('prediction')">🎯 明日の狙い目予測</button>
            <button class="tab-btn active" onclick="switchTab('data')">📊 全データ解析</button>
        </div>

        <!-- 予測タブ -->
        <div id="prediction" class="tab-content">
            <h2 style="margin-bottom: 2rem; color: var(--gold);">🌺 AI推奨 狙い目ランキング（据え置き否定・大凹み狙い）</h2>
            <div class="grid" id="predictionGrid"></div>
        </div>

        <!-- データタブ -->
        <div id="data" class="tab-content active">
            <div class="date-buttons-container" id="dateButtons"></div>
            
            <div class="summary-dashboard" id="dailySummary">
                <div class="summary-card">
                    <div class="summary-title">平均ゲーム数</div>
                    <div class="summary-value" id="sumGames">0 G</div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">平均差枚</div>
                    <div class="summary-value" id="sumDiff" style="color: var(--gold);">+0 枚</div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">全体BIG確率</div>
                    <div class="summary-value" id="sumBig">1/0</div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">全体REG確率</div>
                    <div class="summary-value" id="sumReg">1/0</div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">全体合算</div>
                    <div class="summary-value" id="sumTotal">1/0</div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">ホール全体推測設定</div>
                    <div class="summary-value" id="sumSetting" style="color: #f39c12;">設定?</div>
                </div>
            </div>

            <div class="table-container" id="tableContainer">
                <table id="dataTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable('台番')">台番 ⇅</th>
                            <th onclick="sortTable('累計ゲーム数')">G数 ⇅</th>
                            <th onclick="sortTable('BIG回数')">BIG ⇅</th>
                            <th onclick="sortTable('REG回数')">REG ⇅</th>
                            <th onclick="sortTable('推測差枚')">推測差枚 ⇅</th>
                            <th onclick="sortTable('REG確率')">REG確率 ⇅</th>
                            <th onclick="sortTable('最有力設定')">最有力設定 ⇅</th>
                            <th>ベイズ推定(設定割合%)</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const rawData = {json_data};
        const predictions = {json_predictions};
        
        const grid = document.getElementById('predictionGrid');
        if (predictions.length === 0) {{
            grid.innerHTML = "<p>推奨台が見つかりませんでした。</p>";
        }} else {{
            const maxScore = Math.max(...predictions.map(p => p.スコア), 150);
            
            predictions.forEach((p, idx) => {{
                let rank = idx === 0 ? "👑 1位" : idx === 1 ? "🥈 2位" : idx === 2 ? "🥉 3位" : `${{idx+1}}位`;
                let barWidth = Math.max(Math.min((p.スコア / maxScore) * 100, 100), 0);
                
                grid.innerHTML += `
                    <div class="card">
                        <div class="card-title">
                            <span>${{rank}} / 台番 ${{p.台番}}</span>
                            <span class="card-score">Score: ${{p.スコア}}</span>
                        </div>
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width: ${{barWidth}}%;"></div>
                        </div>
                        <div class="card-tag">${{p.タグ}}</div>
                        <div style="margin-bottom: 0.5rem; font-size: 0.9rem;">
                            前日差枚: <strong class="${{p.前日差枚 > 0 ? 'diff-positive' : 'diff-negative'}}">${{p.前日差枚 > 0 ? '+' : ''}}${{p.前日差枚}}枚</strong>
                        </div>
                        
                        <table class="period-stats">
                            <tr>
                                <th>期間</th>
                                <th>推測差枚</th>
                                <th>総稼働ゲーム数</th>
                            </tr>
                            <tr>
                                <td>過去3日間</td>
                                <td class="${{p.diff_3 > 0 ? 'diff-positive' : 'diff-negative'}}"><strong>${{p.diff_3 > 0 ? '+' : ''}}${{p.diff_3.toLocaleString()}}枚</strong></td>
                                <td>${{p.games_3.toLocaleString()}} G</td>
                            </tr>
                            <tr>
                                <td>過去1週間</td>
                                <td class="${{p.diff_7 > 0 ? 'diff-positive' : 'diff-negative'}}"><strong>${{p.diff_7 > 0 ? '+' : ''}}${{p.diff_7.toLocaleString()}}枚</strong></td>
                                <td>${{p.games_7.toLocaleString()}} G</td>
                            </tr>
                            <tr>
                                <td>過去2週間</td>
                                <td class="${{p.diff_14 > 0 ? 'diff-positive' : 'diff-negative'}}"><strong>${{p.diff_14 > 0 ? '+' : ''}}${{p.diff_14.toLocaleString()}}枚</strong></td>
                                <td>${{p.games_14.toLocaleString()}} G</td>
                            </tr>
                        </table>
                    </div>
                `;
            }});
        }}

        
        function getCornerStyle(daiban) {{
            daiban = parseInt(daiban);
            let corner = null;
            const store = 'MEGAFACE';
            const machine = 'キング';
            
            if (store === 'MEGAFACE') {{
                if (machine === 'マイジャグラー') {{
                    if (daiban === 543 || daiban === 544) corner = 'aisle';
                    if (daiban === 533 || daiban === 554) corner = 'opposite';
                }} else if (machine === 'キング') {{
                    if (daiban === 390) corner = 'aisle';
                    if (daiban === 373) corner = 'opposite';
                }} else if (machine === 'ニューキング') {{
                    if ([319, 354, 355].includes(daiban)) corner = 'aisle';
                    if ([336, 337, 372].includes(daiban)) corner = 'opposite';
                }}
            }} else if (store === 'SUNITOMAN') {{
                if (machine === 'ドラゴン') {{
                    if (daiban === 396 || daiban === 425) corner = 'aisle';
                    if (daiban === 410 || daiban === 411) corner = 'opposite';
                }} else if (machine === 'ニューキング') {{
                    if (daiban === 336 || daiban === 365) corner = 'aisle';
                    if (daiban === 350 || daiban === 351) corner = 'opposite';
                }} else if (machine === 'マイジャグラー') {{
                    if (daiban === 273 || daiban === 304) corner = 'aisle';
                    if (daiban === 278 || daiban === 299) corner = 'opposite';
                }}
            }}
            
            if (corner === 'aisle') return 'background: rgba(255, 60, 60, 0.4); padding: 2px 6px; border-radius: 4px; font-weight: bold; color: white;';
            if (corner === 'opposite') return 'background: rgba(60, 100, 255, 0.4); padding: 2px 6px; border-radius: 4px; font-weight: bold; color: white;';
            return '';
        }}

        const dateButtonsContainer = document.getElementById('dateButtons');
        const uniqueDays = [...new Set(rawData.map(item => item['日付']))].sort().reverse();
        
        uniqueDays.forEach(day => {{
            const btn = document.createElement('button');
            btn.className = 'date-btn';
            btn.textContent = day;
            btn.onclick = () => selectDate(day, btn);
            dateButtonsContainer.appendChild(btn);
        }});
        
        let currentData = [];
        let sortAsc = true;
        let currentSortColumn = -1;
        
        function selectDate(day, btnElement) {{
            document.querySelectorAll('.date-btn').forEach(btn => btn.classList.remove('active'));
            if(btnElement) btnElement.classList.add('active');
            
            currentData = rawData.filter(row => row['日付'] === day);
            
            let totalGames = 0; let totalBig = 0; let totalReg = 0; let totalDiff = 0;
            let count = currentData.length;
            
            currentData.forEach(row => {{
                totalGames += parseInt(row['累計ゲーム数']) || 0;
                totalBig += parseInt(row['BIG回数']) || 0;
                totalReg += parseInt(row['REG回数']) || 0;
                totalDiff += parseInt(row['推測差枚']) || 0;
            }});
            
            const avgGames = count > 0 ? Math.round(totalGames / count) : 0;
            const avgDiff = count > 0 ? Math.round(totalDiff / count) : 0;
            const overallBigProb = totalBig > 0 ? Math.round(totalGames / totalBig) : 0;
            const overallRegProb = totalReg > 0 ? Math.round(totalGames / totalReg) : 0;
            const overallTotalProb = (totalBig + totalReg) > 0 ? Math.round(totalGames / (totalBig + totalReg)) : 0;
            
            let hallSetting = "設定1 (激辛)";
            if(overallRegProb > 0) {{
                if(overallRegProb <= 318) hallSetting = "設定6 (極甘)";
                else if(overallRegProb <= 348) hallSetting = "設定5 (甘)";
                else if(overallRegProb <= 385) hallSetting = "設定4 (普通)";
                else if(overallRegProb <= 420) hallSetting = "設定3 (やや辛)";
                else if(overallRegProb <= 452) hallSetting = "設定2 (辛)";
            }}
            
            document.getElementById('sumGames').textContent = `${{avgGames}} G`;
            
            const diffEl = document.getElementById('sumDiff');
            diffEl.textContent = `${{avgDiff > 0 ? '+' : ''}}${{avgDiff}} 枚`;
            diffEl.className = 'summary-value ' + (avgDiff > 0 ? 'diff-positive' : 'diff-negative');
            
            document.getElementById('sumBig').textContent = overallBigProb > 0 ? `1/${{overallBigProb}}` : '-';
            document.getElementById('sumReg').textContent = overallRegProb > 0 ? `1/${{overallRegProb}}` : '-';
            document.getElementById('sumTotal').textContent = overallTotalProb > 0 ? `1/${{overallTotalProb}}` : '-';
            document.getElementById('sumSetting').textContent = hallSetting;
            
            document.getElementById('dailySummary').classList.add('active');
            document.getElementById('tableContainer').classList.add('active');
            
            currentSortColumn = '台番';
            sortAsc = true;
            currentData.sort((a, b) => parseInt(a['台番']) - parseInt(b['台番']));
            renderTable(currentData);
        }}
        
        const tbody = document.getElementById('tableBody');
        function renderTable(data) {{
            tbody.innerHTML = '';
            data.forEach(row => {{
                const diff = parseInt(row['推測差枚']);
                let diffClass = diff > 0 ? 'diff-positive' : 'diff-negative';

                const setting = row['最有力設定'];
                let settingClass = 'setting-bad';
                if (setting.includes('6') || setting.includes('5')) settingClass = 'setting-good';
                else if (setting.includes('4')) settingClass = 'setting-ok';

                const p6 = parseFloat(row['設定6(%)']) || 0;
                const p5 = parseFloat(row['設定5(%)']) || 0;
                const p4 = parseFloat(row['設定4(%)']) || 0;
                const p3 = parseFloat(row['設定3(%)']) || 0;
                const p2 = parseFloat(row['設定2(%)']) || 0;
                const p1 = parseFloat(row['設定1(%)']) || 0;

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${{row['台番']}}</strong></td>
                    <td>${{row['累計ゲーム数']}}</td>
                    <td>${{row['BIG回数']}}</td>
                    <td>${{row['REG回数']}}</td>
                    <td class="${{diffClass}}">${{diff > 0 ? '+' : ''}}${{diff}}枚</td>
                    <td>${{row['REG確率'] || ''}}</td>
                    <td class="${{settingClass}}">${{row['最有力設定']}}</td>
                    <td>
                        <div class="prob-bar-container">
                            <div class="prob-6" style="width: ${{p6}}%"></div>
                            <div class="prob-5" style="width: ${{p5}}%"></div>
                            <div class="prob-4" style="width: ${{p4}}%"></div>
                            <div class="prob-3" style="width: ${{p3}}%"></div>
                            <div class="prob-2" style="width: ${{p2}}%"></div>
                            <div class="prob-1" style="width: ${{p1}}%"></div>
                        </div>
                    </td>`;
                tbody.appendChild(tr);
            }});
        }}
        
        function sortTable(key) {{
            if (!key) return;
            if (currentSortColumn === key) {{
                sortAsc = !sortAsc;
            }} else {{
                // 台番は昇順、それ以外（差枚、BIG等）は降順スタートが自然
                sortAsc = (key === '台番') ? true : false;
            }}
            currentSortColumn = key;

            currentData.sort((a, b) => {{
                let valA = a[key];
                let valB = b[key];
                
                if (key === '最有力設定') {{
                    if (valA < valB) return sortAsc ? -1 : 1;
                    if (valA > valB) return sortAsc ? 1 : -1;
                    return 0;
                }}
                
                // 台番、G数、BIG、REG、差枚、確率などはすべて数値比較
                valA = parseFloat(String(valA).replace(/[^0-9.-]+/g, "")) || 0;
                valB = parseFloat(String(valB).replace(/[^0-9.-]+/g, "")) || 0;
                
                if (valA < valB) return sortAsc ? -1 : 1;
                if (valA > valB) return sortAsc ? 1 : -1;
                return 0;
            }});
            renderTable(currentData);
        }}
        
                function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }}

        // 初期化処理（これを呼ばないとデータテーブルが空になる）
        if(uniqueDays.length > 0) {{
            selectDate(uniqueDays[0], dateButtonsContainer.firstChild);
        }}
    </script>
</body>
</html>
"""

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Report HTML generated: {html_file}")

# トップページの統計情報を自動更新
import subprocess
try:
    portal_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'update_portal.py')
    if os.path.exists(portal_script):
        subprocess.run(['python', portal_script])
except Exception as e:
    print(f'Portal update failed: {e}')
