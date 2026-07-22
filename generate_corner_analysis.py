import pandas as pd
import glob
import os
from corner_utils import get_corner_type

scrapers = {
    "MEGAFACE_NEWKING": ("megaface_newking_scraper", "MEGAFACE", "ニューキング"),
    "MEGAFACE_KING": ("megaface_king_scraper", "MEGAFACE", "キング"),
    "MEGAFACE_MYJUGGLER": ("megaface_myjuggler_scraper", "MEGAFACE", "マイジャグ"),
    "SUNITOMAN_DRAGON": ("sunitoman_scraper", "SUNITOMAN", "ドラゴン"),
    "SUNITOMAN_NEWKING": ("sunitoman_newking_scraper", "SUNITOMAN", "ニューキング"),
    "SUNITOMAN_MYJUGGLER": ("sunitoman_myjuggler_scraper", "SUNITOMAN", "マイジャグ")
}

def compute_stats():
    results = []
    
    for key, (folder, store, machine_type) in scrapers.items():
        csv_path = os.path.join(folder, "master_data.csv")
        if not os.path.exists(csv_path):
            continue
            
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        if "推測差枚" not in df.columns or "累計ゲーム数" not in df.columns:
            continue
            
        def get_corner(row):
            return get_corner_type(store, machine_type, row['台番'])
            
        df['corner_type'] = df.apply(get_corner, axis=1)
        
        all_avg_diff = df['推測差枚'].mean()
        all_avg_games = df['累計ゲーム数'].mean()
        
        corner_df = df[df['corner_type'].notna()]
        non_corner_df = df[df['corner_type'].isna()]
        
        corner_avg_diff = corner_df['推測差枚'].mean() if not corner_df.empty else 0
        non_corner_avg_diff = non_corner_df['推測差枚'].mean() if not non_corner_df.empty else 0
        
        corner_avg_games = corner_df['累計ゲーム数'].mean() if not corner_df.empty else 0
        non_corner_avg_games = non_corner_df['累計ゲーム数'].mean() if not non_corner_df.empty else 0
        
        aisle_df = df[df['corner_type'] == 'aisle']
        opposite_df = df[df['corner_type'] == 'opposite']
        
        aisle_avg_diff = aisle_df['推測差枚'].mean() if not aisle_df.empty else 0
        opposite_avg_diff = opposite_df['推測差枚'].mean() if not opposite_df.empty else 0
        
        aisle_avg_games = aisle_df['累計ゲーム数'].mean() if not aisle_df.empty else 0
        opposite_avg_games = opposite_df['累計ゲーム数'].mean() if not opposite_df.empty else 0
        
        results.append({
            'store': store,
            'machine_type': machine_type,
            'all_avg_diff': all_avg_diff,
            'corner_avg_diff': corner_avg_diff,
            'non_corner_avg_diff': non_corner_avg_diff,
            'aisle_avg_diff': aisle_avg_diff,
            'opposite_avg_diff': opposite_avg_diff,
            'all_avg_games': all_avg_games,
            'corner_avg_games': corner_avg_games,
            'non_corner_avg_games': non_corner_avg_games,
            'aisle_avg_games': aisle_avg_games,
            'opposite_avg_games': opposite_avg_games,
            'corner_count': len(corner_df),
            'non_corner_count': len(non_corner_df),
            'aisle_count': len(aisle_df),
            'opposite_count': len(opposite_df)
        })
        
    return results

def generate_html(results):
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>角台 比較・検証レポート</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #ff4757;
            --bg: #0f141e;
            --text: #f1f2f6;
            --card-bg: rgba(255, 255, 255, 0.03);
            --border: rgba(255, 255, 255, 0.08);
            --aisle-color: rgba(255, 60, 60, 0.2);
            --aisle-border: rgba(255, 60, 60, 0.8);
            --opposite-color: rgba(60, 100, 255, 0.2);
            --opposite-border: rgba(60, 100, 255, 0.8);
            --other-color: rgba(255, 255, 255, 0.05);
            --other-border: rgba(255, 255, 255, 0.3);
        }}
        body {{
            font-family: 'Inter', 'Noto Sans JP', sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #fff, #a4b0be);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
        }}
        .card-header {{
            font-size: 1.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            text-align: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
        }}
        .comparison-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
            gap: 1rem;
        }}
        .stat-box {{
            flex: 1;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border-left: 4px solid;
        }}
        .stat-box.aisle {{
            background: var(--aisle-color);
            border-color: var(--aisle-border);
        }}
        .stat-box.opposite {{
            background: var(--opposite-color);
            border-color: var(--opposite-border);
        }}
        .stat-box.other {{
            background: var(--other-color);
            border-color: var(--other-border);
        }}
        .stat-label {{
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #a4b0be;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 900;
            color: #fff;
        }}
        .stat-sub {{
            font-size: 0.75rem;
            color: #747d8c;
            margin-top: 0.2rem;
        }}
        .positive {{ color: #ff4757; }}
        .negative {{ color: #00d2d3; }}
        .back-btn {{
            display: block;
            width: max-content;
            margin: 2rem auto;
            padding: 1rem 2rem;
            background: rgba(255,255,255,0.1);
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            transition: 0.3s;
        }}
        .back-btn:hover {{
            background: rgba(255,255,255,0.2);
            transform: scale(1.05);
        }}
        .store-badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
            background: rgba(255,255,255,0.1);
        }}
        .MEGAFACE .store-badge {{ color: #ff6b81; background: rgba(255, 71, 87, 0.1); }}
        .SUNITOMAN .store-badge {{ color: #ffa502; background: rgba(255, 165, 2, 0.1); }}
    </style>
</head>
<body>
    <h1>角台 比較・検証レポート (過去全データ)</h1>
    <a href="index.html" class="back-btn">← ポータルへ戻る</a>
    
    <div class="grid">
"""
    for r in results:
        diff_fmt = lambda x: f"<span class='{'positive' if x>0 else 'negative'}'>{'+' if x>0 else ''}{x:,.0f}枚</span>"
        
        html += f"""
        <div class="card {r['store']}">
            <div style="text-align: center;">
                <span class="store-badge">{r['store'] == 'MEGAFACE' and 'メガフェイス豊崎' or 'サンシャイン糸満'}</span>
            </div>
            <div class="card-header">{r['machine_type']}</div>
            
            <div style="font-size: 0.9rem; margin-bottom: 0.5rem; color: #a4b0be; text-align: center;">角台 vs その他の台</div>
            <div class="comparison-row">
                <div class="stat-box" style="background: rgba(255, 165, 2, 0.1); border-color: #ffa502;">
                    <div class="stat-label">角台 全体</div>
                    <div class="stat-value">{diff_fmt(r['corner_avg_diff'])}</div>
                    <div class="stat-sub">平均 {r['corner_avg_games']:,.0f}G (のべ{r['corner_count']}件)</div>
                </div>
                <div class="stat-box other">
                    <div class="stat-label">その他の台</div>
                    <div class="stat-value">{diff_fmt(r['non_corner_avg_diff'])}</div>
                    <div class="stat-sub">平均 {r['non_corner_avg_games']:,.0f}G (のべ{r['non_corner_count']}件)</div>
                </div>
            </div>
            
            <div style="font-size: 0.9rem; margin-bottom: 0.5rem; margin-top: 1.5rem; color: #a4b0be; text-align: center;">通路側 vs 反対側</div>
            <div class="comparison-row">
                <div class="stat-box aisle">
                    <div class="stat-label">通路側 (赤)</div>
                    <div class="stat-value">{diff_fmt(r['aisle_avg_diff'])}</div>
                    <div class="stat-sub">平均 {r['aisle_avg_games']:,.0f}G (のべ{r['aisle_count']}件)</div>
                </div>
                <div class="stat-box opposite">
                    <div class="stat-label">反対側 (青)</div>
                    <div class="stat-value">{diff_fmt(r['opposite_avg_diff'])}</div>
                    <div class="stat-sub">平均 {r['opposite_avg_games']:,.0f}G (のべ{r['opposite_count']}件)</div>
                </div>
            </div>
        </div>
        """
        
    html += """
    </div>
</body>
</html>"""

    with open("corner_analysis.html", "w", encoding="utf-8") as f:
        f.write(html)
        
if __name__ == "__main__":
    print("Computing corner stats...")
    results = compute_stats()
    print("Generating HTML...")
    generate_html(results)
    print("Done: corner_analysis.html")
