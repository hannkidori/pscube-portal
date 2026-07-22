import os
import pandas as pd
import re
from corner_utils import get_corner_type, get_corner_style

base_dir = os.path.dirname(os.path.abspath(__file__))

stores = {
    "MEGAFACE": {
        "folders": [
            "megaface_newking_scraper",
            "megaface_king_scraper",
            "megaface_myjuggler_scraper"
        ],
        "name": "メガフェイス豊崎本館"
    },
    "SUNITOMAN": {
        "folders": [
            "sunitoman_scraper",
            "sunitoman_newking_scraper",
            "sunitoman_myjuggler_scraper"
        ],
        "name": "サンシャイン糸満店"
    }
}

html_file = os.path.join(base_dir, "index.html")
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# Read anomalies
anomaly_html = ""
anomalies_path = os.path.join(base_dir, "anomalies.json")
if os.path.exists(anomalies_path):
    try:
        import json
        with open(anomalies_path, "r", encoding="utf-8") as f:
            anomalies = json.load(f)
            
        if anomalies:
            anomaly_html += """
            <div style="background: rgba(231, 76, 60, 0.1); border: 1px solid #e74c3c; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: inset 0 0 20px rgba(231, 76, 60, 0.2);">
                <div style="text-align: center; color: #e74c3c; font-size: 1.2rem; margin-bottom: 1rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 10px;">
                    <span style="font-size: 1.5rem;">🚨</span> システムによる異常データ検知アラート
                </div>
                <div style="font-size: 0.9rem; color: #fff; line-height: 1.6;">
                    以下の台データは、ホールのデータ機器バグ等により数値が異常である可能性が高いです。<br>
                    <ul style="margin-top: 10px; margin-bottom: 0;">
            """
            for a in anomalies:
                reasons = "、".join(a['reasons'])
                anomaly_html += f"<li><strong>{a['date']} {a['store']} {a['daiban']}番台</strong>: {reasons} (G:{a['games']} BIG:{a['big']} REG:{a['reg']} 差枚:{a['diff']}枚)</li>"
            
            anomaly_html += """
                    </ul>
                </div>
            </div>
            """
    except Exception as e:
        print(f"Error reading anomalies.json: {e}")

# Inject anomaly_html at the top of the container
pattern_anomaly = re.compile(r"(<!-- ANOMALY_ALERT_START -->)(.*?)(<!-- ANOMALY_ALERT_END -->)", re.DOTALL)
if "<!-- ANOMALY_ALERT_START -->" in html_content:
    html_content = pattern_anomaly.sub(rf"\1\n{anomaly_html}\n        \3", html_content)

for store_key, info in stores.items():
    all_data = []
    
    for folder in info["folders"]:
        csv_path = os.path.join(base_dir, folder, "master_data.csv")
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path, encoding="utf-8-sig")
                all_data.append(df)
            except Exception as e:
                print(f"Error reading {csv_path}: {e}")
                
    if not all_data:
        continue
        
    merged_df = pd.concat(all_data, ignore_index=True)
    merged_df['日付'] = pd.to_datetime(merged_df['日付'])
    
    # Find the latest date (前日)
    latest_date = merged_df['日付'].max()
    
    # 前日（最新データ）
    df_yesterday = merged_df[merged_df['日付'] == latest_date]
    diff_yesterday = df_yesterday['推測差枚'].sum()
    games_yesterday = df_yesterday['累計ゲーム数'].sum()
    count_yesterday = len(df_yesterday)
    avg_g_yesterday = int(games_yesterday / count_yesterday) if count_yesterday > 0 else 0
    date_str_yesterday = latest_date.strftime("%m/%d")
    sign_yesterday = "+" if diff_yesterday > 0 else ""
    color_yesterday = '#2ed573' if diff_yesterday > 0 else '#ff4757'
    
    # 前々日
    two_days_ago = latest_date - pd.Timedelta(days=1)
    df_2days_ago = merged_df[merged_df['日付'] == two_days_ago]
    diff_2days_ago = df_2days_ago['推測差枚'].sum()
    games_2days_ago = df_2days_ago['累計ゲーム数'].sum()
    count_2days_ago = len(df_2days_ago)
    avg_g_2days_ago = int(games_2days_ago / count_2days_ago) if count_2days_ago > 0 else 0
    date_str_2days_ago = two_days_ago.strftime("%m/%d")
    sign_2days_ago = "+" if diff_2days_ago > 0 else ""
    color_2days_ago = '#2ed573' if diff_2days_ago > 0 else '#ff4757'
    
    # 7日間合算
    seven_days_ago = latest_date - pd.Timedelta(days=6)
    df_7days = merged_df[merged_df['日付'] >= seven_days_ago]
    diff_7days = df_7days['推測差枚'].sum()
    games_7days = df_7days['累計ゲーム数'].sum()
    count_7days = len(df_7days)
    avg_g_7days = int(games_7days / count_7days) if count_7days > 0 else 0
    date_str_7days = f"{seven_days_ago.strftime('%m/%d')}〜{latest_date.strftime('%m/%d')}"
    sign_7days = "+" if diff_7days > 0 else ""
    color_7days = '#2ed573' if diff_7days > 0 else '#ff4757'
    
    # Read ranking.json for Top 3 targets
    all_predictions = []
    machine_names = {
        "megaface_newking_scraper": "ニューキング",
        "megaface_king_scraper": "キングハナハナ",
        "megaface_myjuggler_scraper": "マイジャグラーV",
        "sunitoman_scraper": "ドラゴンハナハナ",
        "sunitoman_newking_scraper": "ニューキング",
        "sunitoman_myjuggler_scraper": "マイジャグラーV"
    }
    
    for folder in info["folders"]:
        ranking_path = os.path.join(base_dir, folder, "ranking.json")
        if os.path.exists(ranking_path):
            try:
                import json
                with open(ranking_path, "r", encoding="utf-8") as f:
                    preds = json.load(f)
                    for p in preds:
                        p["machine_name"] = machine_names.get(folder, "不明")
                    all_predictions.extend(preds)
            except Exception as e:
                print(f"Error reading {ranking_path}: {e}")
                
    # Sort and get Top 10
    all_predictions.sort(key=lambda x: x.get("スコア", 0), reverse=True)
    top10 = all_predictions[:10]
    
    if top10:
        top10_html = f"""
                <details style="background: rgba(243, 156, 18, 0.1); border: 1px solid #f39c12; border-radius: 12px; margin-bottom: 1rem; box-shadow: inset 0 0 15px rgba(243, 156, 18, 0.2);">
                    <summary style="cursor: pointer; padding: 1rem; text-align: center; color: #f39c12; font-size: 0.95rem; font-weight: 800; letter-spacing: 1px; display: flex; align-items: center; justify-content: center; gap: 8px; list-style: none;">
                        <span style="font-size: 1.2rem;">🔥</span> {(latest_date + pd.Timedelta(days=1)).strftime('%m/%d')} 当日の狙い目 BEST10 <span style="font-size: 0.8rem; opacity: 0.7;">(クリックで開閉)</span>
                    </summary>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem; padding: 0 1rem 1rem 1rem;">
        """
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        colors = ["#f1c40f", "#bdc3c7", "#cd7f32", "#a4b0be", "#a4b0be", "#a4b0be", "#a4b0be", "#a4b0be", "#a4b0be", "#a4b0be"]
        for i, p in enumerate(top10):
            medal = medals[i] if i < 10 else ""
            color = colors[i] if i < 10 else "#a4b0be"
            corner = get_corner_type(store_key, p['machine_name'], p['台番'])
            c_style = get_corner_style(corner)
            if c_style:
                daiban_html = f'<span style="{c_style} font-size: 0.8rem;">{p["台番"]}番台</span>'
            else:
                daiban_html = f'<span style="color: #a4b0be; font-size: 0.8rem;">{p["台番"]}番台</span>'
                
            top10_html += f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); padding: 0.6rem 1rem; border-radius: 8px; border-left: 4px solid {color};">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 1.2rem;">{medal}</span>
                                <span style="color: #fff; font-weight: 700; font-size: 0.9rem;">{p['machine_name']}</span>
                                {daiban_html}
                            </div>
                            <div style="color: #f39c12; font-weight: 900; font-size: 1.1rem;">
                                Score: {p['スコア']}
                            </div>
                        </div>
            """
        top10_html += """
                    </div>
                </details>
        """
    else:
        top10_html = "<!-- 狙い目データなし -->"
        
    pattern_top3 = re.compile(rf"(<!-- {store_key}_TOP3_START -->)(.*?)(<!-- {store_key}_TOP3_END -->)", re.DOTALL)
    html_content = pattern_top3.sub(rf"\1\n{top10_html}\n                \3", html_content)
    
    # Generate HTML snippet (Stats)
    stats_html = f"""
                <div style="background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.2rem; box-shadow: inset 0 0 20px rgba(0,0,0,0.5);">
                    <div style="text-align: center; color: #a4b0be; font-size: 0.85rem; margin-bottom: 0.8rem; font-weight: 600; letter-spacing: 1px;">
                        📊 店舗全体データ (3機種合算)
                    </div>
                    
                    <!-- 前日 -->
                    <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px dashed rgba(255,255,255,0.1);">
                        <div style="text-align: center; color: #00d2d3; font-size: 0.8rem; margin-bottom: 0.5rem; font-weight: bold;">
                            ▶ 前日 ({date_str_yesterday})
                        </div>
                        <div style="display: flex; justify-content: space-around; align-items: center;">
                            <div style="text-align: center; width: 45%;">
                                <div style="color: #a4b0be; font-size: 0.75rem; margin-bottom: 0.3rem;">合計差枚 (全{count_yesterday}台)</div>
                                <div style="font-size: 1.2rem; font-weight: 900; color: {color_yesterday};">
                                    {sign_yesterday}{int(diff_yesterday):,} 枚
                                </div>
                            </div>
                            <div style="width: 1px; height: 30px; background: rgba(255,255,255,0.1);"></div>
                            <div style="text-align: center; width: 45%;">
                                <div style="color: #a4b0be; font-size: 0.75rem; margin-bottom: 0.3rem;">平均ゲーム数</div>
                                <div style="font-size: 1.2rem; font-weight: 900; color: #fff;">
                                    {avg_g_yesterday:,} G
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 前々日 -->
                    <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px dashed rgba(255,255,255,0.1);">
                        <div style="text-align: center; color: #f39c12; font-size: 0.8rem; margin-bottom: 0.5rem; font-weight: bold;">
                            ▶ 前々日 ({date_str_2days_ago})
                        </div>
                        <div style="display: flex; justify-content: space-around; align-items: center;">
                            <div style="text-align: center; width: 45%;">
                                <div style="color: #a4b0be; font-size: 0.75rem; margin-bottom: 0.3rem;">合計差枚 (全{count_2days_ago}台)</div>
                                <div style="font-size: 1.2rem; font-weight: 900; color: {color_2days_ago};">
                                    {sign_2days_ago}{int(diff_2days_ago):,} 枚
                                </div>
                            </div>
                            <div style="width: 1px; height: 30px; background: rgba(255,255,255,0.1);"></div>
                            <div style="text-align: center; width: 45%;">
                                <div style="color: #a4b0be; font-size: 0.75rem; margin-bottom: 0.3rem;">平均ゲーム数</div>
                                <div style="font-size: 1.2rem; font-weight: 900; color: #fff;">
                                    {avg_g_2days_ago:,} G
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 過去7日間合算 -->
                    <div>
                        <div style="text-align: center; color: #ff6b81; font-size: 0.8rem; margin-bottom: 0.5rem; font-weight: bold;">
                            ▶ 7日間合算 ({date_str_7days})
                        </div>
                        <div style="display: flex; justify-content: space-around; align-items: center;">
                            <div style="text-align: center; width: 45%;">
                                <div style="color: #a4b0be; font-size: 0.75rem; margin-bottom: 0.3rem;">合計差枚 (延べ{count_7days}台)</div>
                                <div style="font-size: 1.2rem; font-weight: 900; color: {color_7days};">
                                    {sign_7days}{int(diff_7days):,} 枚
                                </div>
                            </div>
                            <div style="width: 1px; height: 30px; background: rgba(255,255,255,0.1);"></div>
                            <div style="text-align: center; width: 45%;">
                                <div style="color: #a4b0be; font-size: 0.75rem; margin-bottom: 0.3rem;">平均ゲーム数</div>
                                <div style="font-size: 1.2rem; font-weight: 900; color: #fff;">
                                    {avg_g_7days:,} G
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
"""
    
    # Replace in HTML
    pattern = re.compile(rf"(<!-- {store_key}_STATS_START -->)(.*?)(<!-- {store_key}_STATS_END -->)", re.DOTALL)
    html_content = pattern.sub(rf"\1\n{stats_html}\n                \3", html_content)

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Portal index.html has been updated with the latest store stats and Top 3 targets.")

# 今日の狙い目（超絶凹み台ランキング）ページを生成する
import subprocess
try:
    print("Generating today's targets page...")
    subprocess.run(['python', 'generate_todays_targets.py'], cwd=base_dir, check=True)
except Exception as e:
    print(f"Error generating today's targets: {e}")

try:
    subprocess.run(['python', 'generate_corner_analysis.py'], cwd=base_dir, check=True)
except Exception as e:
    print(f"Error generating corner analysis: {e}")
