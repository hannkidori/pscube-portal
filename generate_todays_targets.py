import os
import pandas as pd
from datetime import datetime, timedelta
import sys

# カスタムユーティリティをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from corner_utils import get_corner_type, get_corner_style

base_dir = os.path.dirname(os.path.abspath(__file__))

megaface_folders = [
    "megaface_newking_scraper",
    "megaface_king_scraper",
    "megaface_myjuggler_scraper"
]
sunitoman_folders = [
    "sunitoman_scraper",
    "sunitoman_newking_scraper",
    "sunitoman_myjuggler_scraper"
]

def load_data(folders, store_name):
    dfs = []
    for f in folders:
        csv_path = os.path.join(base_dir, f, "master_data.csv")
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                df['店舗'] = store_name
                if '推測差枚' in df.columns:
                    df = df[['日付', '店舗', '機種名', '台番', '推測差枚']]
                    dfs.append(df)
            except Exception as e:
                print(f"Error reading {csv_path}: {e}")
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

def main():
    print("Loading data...")
    megaface_df = load_data(megaface_folders, "MEGAFACE")
    sunitoman_df = load_data(sunitoman_folders, "SUNITOMAN")
    all_df = pd.concat([megaface_df, sunitoman_df], ignore_index=True)

    if all_df.empty:
        print("No data found.")
        return

    # Parse dates
    all_df['日付'] = pd.to_datetime(all_df['日付'], errors='coerce')
    all_df = all_df.dropna(subset=['日付'])
    
    max_date = all_df['日付'].max()
    print(f"Latest date in data: {max_date.strftime('%Y-%m-%d')}")

    def calc_stats(df, max_date):
        stats = []
        grouped = df.groupby(['店舗', '機種名', '台番'])
        for (store, machine, daiban), group in grouped:
            d1 = group[group['日付'] == max_date]['推測差枚'].sum()
            
            d7_limit = max_date - timedelta(days=6)
            d7 = group[(group['日付'] >= d7_limit) & (group['日付'] <= max_date)]['推測差枚'].sum()
            
            d14_limit = max_date - timedelta(days=13)
            d14 = group[(group['日付'] >= d14_limit) & (group['日付'] <= max_date)]['推測差枚'].sum()
            
            stats.append({
                '店舗': store,
                '機種名': machine,
                '台番': daiban,
                '前日差枚': int(d1) if pd.notnull(d1) else 0,
                '7日間差枚': int(d7) if pd.notnull(d7) else 0,
                '14日間差枚': int(d14) if pd.notnull(d14) else 0
            })
        return pd.DataFrame(stats)

    print("Calculating stats...")
    stats_df = calc_stats(all_df, max_date)

    stats_df = stats_df.sort_values('7日間差枚', ascending=True)

    megaface_top = stats_df[stats_df['店舗'] == "MEGAFACE"].head(15)
    sunitoman_top = stats_df[stats_df['店舗'] == "SUNITOMAN"].head(15)

    def format_row(row, rank):
        def fmt_num(num):
            return f"+{num}" if num > 0 else str(num)
        
        # アイコン判定
        icon = "🎰"
        if "マイジャグ" in row['機種名']: icon = "🤡"
        elif "ハナハナ" in row['機種名']: icon = "🌺"
        if "ドラゴン" in row['機種名']: icon = "🐉"
        elif "キング" in row['機種名'] and "ハナハナ" not in row['機種名']: icon = "👑"
        
        medal_icon = f"[{rank}]"
        if rank == 1: medal_icon = "🥇"
        elif rank == 2: medal_icon = "🥈"
        elif rank == 3: medal_icon = "🥉"

        # 角台ハイライトの適用
        corner = get_corner_type(row['店舗'], row['機種名'], row['台番'])
        c_style = get_corner_style(corner)
        daiban_html = f"<span style='{c_style}'>{row['台番']}番台</span>" if c_style else f"<span class='target-daiban'>{row['台番']}番台</span>"

        return f"""
        <div class="target-item">
            <div class="target-header">
                <div class="target-rank">{medal_icon}</div>
                <div class="target-machine">
                    <span class="target-icon">{icon}</span>
                    <span class="target-name">{row['機種名']}</span>
                    {daiban_html}
                </div>
            </div>
            <div class="target-stats">
                <div class="stat-box">
                    <span class="stat-label">前日</span>
                    <span class="stat-val {'plus' if row['前日差枚'] > 0 else 'minus'}">{fmt_num(row['前日差枚'])}枚</span>
                </div>
                <div class="stat-box highlight">
                    <span class="stat-label">過去7日間</span>
                    <span class="stat-val {'plus' if row['7日間差枚'] > 0 else 'minus'}">{fmt_num(row['7日間差枚'])}枚</span>
                </div>
                <div class="stat-box">
                    <span class="stat-label">過去14日間</span>
                    <span class="stat-val {'plus' if row['14日間差枚'] > 0 else 'minus'}">{fmt_num(row['14日間差枚'])}枚</span>
                </div>
            </div>
        </div>
        """

    megaface_html = "".join([format_row(row, i+1) for i, row in enumerate(megaface_top.to_dict('records'))])
    sunitoman_html = "".join([format_row(row, i+1) for i, row in enumerate(sunitoman_top.to_dict('records'))])

    html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>今日の狙い目ランキング - SLOT AI PORTAL</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #ff4757;
            --secondary: #2f3542;
            --bg: #0f141e;
            --text: #f1f2f6;
            --card-bg: rgba(255, 255, 255, 0.03);
            --border: rgba(255, 255, 255, 0.08);
            --gold: #ffa502;
            --neon-blue: #00d2d3;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', 'Noto Sans JP', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(255, 71, 87, 0.05), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(0, 210, 211, 0.05), transparent 25%);
        }}

        .header {{
            text-align: center;
            margin-bottom: 3rem;
        }}

        .title {{
            font-size: 2.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #fff, #a4b0be);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: var(--neon-blue);
            font-size: 1rem;
            font-weight: 600;
            letter-spacing: 2px;
        }}
        
        .back-btn {{
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1.5rem;
            background: rgba(255,255,255,0.1);
            color: #fff;
            text-decoration: none;
            border-radius: 20px;
            font-weight: 600;
            transition: 0.3s;
        }}
        .back-btn:hover {{ background: rgba(255,255,255,0.2); }}

        .container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }}

        @media (max-width: 900px) {{
            .container {{
                grid-template-columns: 1fr;
            }}
        }}

        .store-section {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(10px);
        }}

        .store-title {{
            font-size: 1.8rem;
            font-weight: 900;
            text-align: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }}

        .megaface .store-title {{ color: #ff6b81; }}
        .sunitoman .store-title {{ color: #ffa502; }}

        .target-item {{
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: 0.3s;
        }}
        .target-item:hover {{
            background: rgba(255,255,255,0.1);
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.2);
        }}

        .target-header {{
            display: flex;
            align-items: center;
            margin-bottom: 0.8rem;
            gap: 10px;
        }}

        .target-rank {{
            font-size: 1.5rem;
            font-weight: 900;
            color: var(--gold);
            min-width: 30px;
        }}

        .target-machine {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-grow: 1;
        }}

        .target-icon {{ font-size: 1.2rem; }}
        .target-name {{ font-weight: 700; font-size: 1.1rem; }}
        .target-daiban {{ 
            background: rgba(255,255,255,0.1); 
            padding: 0.2rem 0.6rem; 
            border-radius: 4px; 
            font-size: 0.85rem; 
            color: #a4b0be;
        }}

        .target-stats {{
            display: grid;
            grid-template-columns: 1fr 1.5fr 1fr;
            gap: 0.5rem;
        }}

        .stat-box {{
            background: rgba(0,0,0,0.4);
            padding: 0.6rem;
            border-radius: 8px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .stat-box.highlight {{
            background: rgba(255, 71, 87, 0.1);
            border: 1px solid rgba(255, 71, 87, 0.3);
        }}

        .stat-label {{
            font-size: 0.7rem;
            color: #a4b0be;
            margin-bottom: 0.3rem;
        }}

        .stat-box.highlight .stat-label {{ color: #ff6b81; font-weight: 700; }}

        .stat-val {{ font-weight: 900; font-size: 1rem; }}
        .stat-box.highlight .stat-val {{ font-size: 1.2rem; }}
        
        .stat-val.plus {{ color: #2ecc71; }}
        .stat-val.minus {{ color: #e74c3c; }}

    </style>
</head>
<body>

    <div class="header">
        <h1 class="title">🎯 今日の狙い目ランキング</h1>
        <p class="subtitle">過去7日間で最も差枚がマイナス（凹み）の台トップ15</p>
        <a href="index.html" class="back-btn">← ポータルに戻る</a>
    </div>

    <div class="container">
        <div class="store-section megaface">
            <h2 class="store-title">メガフェイス豊崎本館</h2>
            <div class="targets-list">
                {megaface_html}
            </div>
        </div>

        <div class="store-section sunitoman">
            <h2 class="store-title">サンシャイン糸満店</h2>
            <div class="targets-list">
                {sunitoman_html}
            </div>
        </div>
    </div>

</body>
</html>
"""

    output_path = os.path.join(base_dir, "todays_targets.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    main()
