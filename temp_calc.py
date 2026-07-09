import pandas as pd
df = pd.read_csv('sunitoman_newking_scraper/master_data.csv', encoding='utf-8-sig')
df_336 = df[df['台番'] == 336].sort_values('日付')

total_diff = 0
print('【サンシャイン糸満 336番台 (ベース35G計算)】')
for _, row in df_336.iterrows():
    games = float(row['累計ゲーム数'])
    big = float(row['BIG回数'])
    reg = float(row['REG回数'])
    
    # 50 coins / 35G = 1.42857...
    coin_loss = games * (50.0 / 35.0)
    coin_gain = (big * 312) + (reg * 130)
    diff = int(coin_gain - coin_loss)
    total_diff += diff
    
    print(f"{row['日付']}: {int(games)}G BIG:{int(big)} REG:{int(reg)} -> 差枚: {diff}")

print(f"\n6日間合計差枚: {total_diff}")
