def get_corner_type(store_name, machine_name, daiban):
    """
    台番から角台（通路側 / 反対側）の判定を行う。
    戻り値: 'aisle' (通路側), 'opposite' (反対側), または None
    """
    try:
        daiban = int(daiban)
    except ValueError:
        return None

    # MEGAFACE
    if store_name == 'MEGAFACE':
        # マイジャグラー (反対側 533, 554 / 通路側 543, 544)
        if 'マイジャグ' in machine_name:
            if daiban in [543, 544]: return 'aisle'
            if daiban in [533, 554]: return 'opposite'
            
        # キング (一番下=通路側, 一番上=反対側 -> 390=通路側, 373=反対側)
        elif 'キング' in machine_name and 'ニュー' not in machine_name:
            if daiban == 390: return 'aisle'
            if daiban == 373: return 'opposite'
            
        # ニューキング (通路側: 1, 36, 37 / 反対側: 18, 19, 54)
        # 台番: 319〜372 -> 319, 354, 355 (通路) / 336, 337, 372 (反対)
        elif 'ニューキング' in machine_name:
            if daiban in [319, 354, 355]: return 'aisle'
            if daiban in [336, 337, 372]: return 'opposite'
            
    # SUNITOMAN
    elif store_name == 'SUNITOMAN':
        # ドラゴン (通路側: 1, 30 / 反対側: 15, 16)
        # 台番: 396〜425 -> 396, 425 (通路) / 410, 411 (反対)
        if 'ドラゴン' in machine_name:
            if daiban in [396, 425]: return 'aisle'
            if daiban in [410, 411]: return 'opposite'
            
        # ニューキング (通路側: 1, 30 / 反対側: 15, 16)
        # 台番: 336〜365 -> 336, 365 (通路) / 350, 351 (反対)
        elif 'ニューキング' in machine_name:
            if daiban in [336, 365]: return 'aisle'
            if daiban in [350, 351]: return 'opposite'
            
        # マイジャグラー (通路側: 1, 12 / 反対側: 6, 7)
        # 台番: 273〜278, 299〜304 -> 273, 304 (通路) / 278, 299 (反対)
        elif 'マイジャグ' in machine_name:
            if daiban in [273, 304]: return 'aisle'
            if daiban in [278, 299]: return 'opposite'
            
    return None

def get_corner_style(corner_type):
    if corner_type == 'aisle':
        # 通路側：赤透明
        return "background: rgba(255, 60, 60, 0.4); padding: 2px 6px; border-radius: 4px; font-weight: bold; color: white;"
    elif corner_type == 'opposite':
        # 反対側：青透明
        return "background: rgba(60, 100, 255, 0.4); padding: 2px 6px; border-radius: 4px; font-weight: bold; color: white;"
    return ""
