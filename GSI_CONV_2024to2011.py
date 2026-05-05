# -*- coding: utf-8 -*-
"""
概要:
    基盤地図情報の JGD2024 版 FG-GML ZIP を、FDGV 等の旧ツールで扱いやすいように
    「JGD2011 表記」に読み替えた ZIP として出力するスクリプトです。

重要:
    1) 国土地理院の説明では、JGD2024 への変更は水平位置の数値変更ではなく、
       測量成果との名称統一です。
       そのため本スクリプトは、基本的に「座標値そのものは変更せず」、
       CRS 識別子や表記のみを書き換えます。

    2) ただし、標高改定は別問題です。
       ElevPt（標高点）や Cntr（等高線）など、高さに関わる項目は
       単純な読み替えが不適切な可能性があるため、
       既定では変換対象から除外し、そのままコピーします。

    3) これは FDGV 通過のための暫定対応です。
       最終成果として厳密な測地・標高整合が必要な用途には、そのまま使わず、
       別途確認してください。

文字コード:
    UTF-8
"""

from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path


# =========================
# ユーザー設定
# =========================

# 入力フォルダ:
# 複数の FG-GML ZIP が入っているフォルダ
INPUT_DIR = Path(r"D:\ArcGIS_Project\2605_ChibaCity_Sample\01_GSI_DATA\01_MapORG")

# 出力フォルダ:
# 変換後 ZIP を保存するフォルダ
OUTPUT_DIR = Path(r"D:\ArcGIS_Project\2605_ChibaCity_Sample\01_GSI_DATA\02_MapCONV_JGD2011")

# 出力 ZIP 名の接尾辞
OUTPUT_SUFFIX = "_asJGD2011"

# 上書き可否
OVERWRITE = True

# 既定では高さ関連をスキップ
# True  : ElevPt, Cntr はそのままコピー
# False : それらも表記置換する（非推奨）
SKIP_VERTICAL_SENSITIVE_XML = False

# スキップ対象のファイル名キーワード
VERTICAL_SENSITIVE_KEYWORDS = ("ElevPt", "Cntr")

# XML のエンコーディング
XML_ENCODING = "utf-8"


# =========================
# 内部設定
# =========================

# 表記置換ルール
# 必要に応じて追加可能
REPLACEMENTS = [
    ("fguuid:jgd2024.bl", "fguuid:jgd2011.bl"),
    ("JGD2024", "JGD2011"),
    ("jgd2024", "jgd2011"),
    ("日本測地系2024", "日本測地系2011"),
]

# XML 宣言の encoding が utf-8 / UTF-8 でも扱えるようにする
XML_FILE_PATTERN = re.compile(r"\.xml$", re.IGNORECASE)


def is_target_zip(path: Path) -> bool:
    """対象 ZIP かどうかを判定する。"""
    return path.is_file() and path.suffix.lower() == ".zip"


def is_xml_file(name_in_zip: str) -> bool:
    """ZIP 内ファイルが XML かどうかを判定する。"""
    return XML_FILE_PATTERN.search(name_in_zip) is not None


def is_vertical_sensitive_xml(name_in_zip: str) -> bool:
    """
    高さ依存の強い XML かどうかを判定する。
    例:
        FG-GML-563926-ElevPt-20250701-0001.xml
        FG-GML-563926-Cntr-20250701-0001.xml
    """
    lower_name = name_in_zip.lower()
    return any(key.lower() in lower_name for key in VERTICAL_SENSITIVE_KEYWORDS)


def replace_jgd2024_to_jgd2011(xml_text: str) -> str:
    """XML 文字列内の JGD2024 表記を JGD2011 に置換する。"""
    result = xml_text
    for old, new in REPLACEMENTS:
        result = result.replace(old, new)
    return result


def make_output_zip_path(input_zip_path: Path) -> Path:
    """出力 ZIP パスを作成する。"""
    return OUTPUT_DIR / f"{input_zip_path.stem}{OUTPUT_SUFFIX}.zip"


def convert_one_zip(input_zip_path: Path) -> None:
    """
    1つの ZIP を処理する。
    ZIP 内の XML を必要に応じて置換し、新しい ZIP を出力する。
    """
    output_zip_path = make_output_zip_path(input_zip_path)

    if output_zip_path.exists():
        if OVERWRITE:
            output_zip_path.unlink()
        else:
            print(f"[SKIP] 既に存在: {output_zip_path}")
            return

    print(f"[INFO] 処理開始: {input_zip_path.name}")

    total_entries = 0
    converted_xml_count = 0
    skipped_vertical_count = 0
    copied_binary_count = 0

    with zipfile.ZipFile(input_zip_path, "r") as zin, \
         zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:

        for info in zin.infolist():
            total_entries += 1
            name_in_zip = info.filename

            # ディレクトリエントリはそのまま作る
            if info.is_dir():
                zout.writestr(info, b"")
                continue

            raw_data = zin.read(name_in_zip)

            # XML 以外はそのままコピー
            if not is_xml_file(name_in_zip):
                zout.writestr(info, raw_data)
                copied_binary_count += 1
                continue

            # 高さ関連 XML は既定でそのままコピー
            if SKIP_VERTICAL_SENSITIVE_XML and is_vertical_sensitive_xml(name_in_zip):
                zout.writestr(info, raw_data)
                skipped_vertical_count += 1
                print(f"  [SKIP-V] {name_in_zip}")
                continue

            # XML をテキストとして読み込み
            try:
                xml_text = raw_data.decode(XML_ENCODING)
            except UnicodeDecodeError:
                # まれに BOM 等で問題がある場合の保険
                xml_text = raw_data.decode(XML_ENCODING, errors="replace")

            new_xml_text = replace_jgd2024_to_jgd2011(xml_text)
            new_raw_data = new_xml_text.encode(XML_ENCODING)

            zout.writestr(info, new_raw_data)
            converted_xml_count += 1
            print(f"  [CONVERT] {name_in_zip}")

    print(f"[INFO] 出力完了: {output_zip_path}")
    print(
        "[INFO] 集計: "
        f"entries={total_entries}, "
        f"converted_xml={converted_xml_count}, "
        f"skipped_vertical={skipped_vertical_count}, "
        f"copied_other={copied_binary_count}"
    )
    print("-" * 60)


def main() -> None:
    """メイン処理。入力フォルダ内の ZIP をまとめて変換する。"""
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"入力フォルダが存在しません: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    zip_files = sorted([p for p in INPUT_DIR.iterdir() if is_target_zip(p)])

    if not zip_files:
        print(f"[WARN] ZIP が見つかりませんでした: {INPUT_DIR}")
        return

    print(f"[INFO] 入力フォルダ: {INPUT_DIR}")
    print(f"[INFO] 出力フォルダ: {OUTPUT_DIR}")
    print(f"[INFO] 対象 ZIP 数 : {len(zip_files)}")
    print("=" * 60)

    for zip_path in zip_files:
        convert_one_zip(zip_path)

    print("[INFO] すべての処理が完了しました。")


if __name__ == "__main__":
    main()