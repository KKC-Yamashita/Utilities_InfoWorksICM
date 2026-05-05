# -*- coding: utf-8 -*-
"""
指定フォルダ内のファイル名から先頭9文字を削除するスクリプト
"""

import os

# ===== 設定 =====
tgt_folder = r"D:\ArcGIS_Project\2605_ChibaCity_Sample\01_GSI_DATA\04_SHP"  # 対象フォルダ

# ===== 処理 =====
for filename in os.listdir(tgt_folder):
    old_path = os.path.join(tgt_folder, filename)

    # フォルダは対象外
    if not os.path.isfile(old_path):
        continue

    # ファイル名が9文字以下の場合はスキップ
    if len(filename) <= 9:
        print(f"[SKIP] {filename}（文字数不足）")
        continue

    # 先頭9文字を削除
    new_filename = filename[9:]
    new_path = os.path.join(tgt_folder, new_filename)

    # リネーム実行
    os.rename(old_path, new_path)
    print(f"[RENAME] {filename} → {new_filename}")

print("処理完了")