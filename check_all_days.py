import pandas as pd
import glob

def check_machines(file_path, scraper_name, expected_start):
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    anomalies = []
    
    for date in sorted(df['日付'].unique()):
        df_date = df[df['日付'] == date]
        if len(df_date) == 0:
            continue
            
        first_daiban = int(df_date.iloc[0]['台番'])
        if first_daiban != expected_start:
            anomalies.append((date, first_daiban))
            
    if not anomalies:
        print(f"[{scraper_name}] OK: All days start with {expected_start}.")
    else:
        print(f"[{scraper_name}] ANOMALIES FOUND:")
        for date, start in anomalies:
            print(f"  - {date}: Starts with {start} instead of {expected_start}")

print("=== Checking Sunitoman Scrapers for Swapped Files ===")
check_machines('sunitoman_myjuggler_scraper/master_data.csv', 'Sunitoman MyJuggler', 273)
check_machines('sunitoman_newking_scraper/master_data.csv', 'Sunitoman New King', 336)
check_machines('sunitoman_scraper/master_data.csv', 'Sunitoman Dragon', 396)

print("\n=== Checking Megaface Scrapers ===")
check_machines('megaface_myjuggler_scraper/master_data.csv', 'Megaface MyJuggler', 533)
check_machines('megaface_newking_scraper/master_data.csv', 'Megaface New King', 72)  # Wait, megaface new king has specific numbers
check_machines('megaface_king_scraper/master_data.csv', 'Megaface King', 1)      # Megaface king specific numbers
