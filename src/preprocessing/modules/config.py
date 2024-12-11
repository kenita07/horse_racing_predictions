# 基本ライブラリ
from pathlib import Path
import re
import sys
import time
import warnings
from urllib.request import Request, urlopen
import ast

# 外部ライブラリ
from bs4 import BeautifulSoup
import pandas as pd
import pickle
from tqdm import tqdm
from urllib.error import HTTPError

# Selenium関連のライブラリ
from selenium.webdriver.common.by import By

# スクリプトの1つ上の階層をsys.pathに追加
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(str(Path(__file__).resolve().parent))

# 自作モジュール
from logger_setting import setup_logger
from chrome_setting import get_chrome_driver
from mapping import MappingLoader

# pandas warning非表示設定
warnings.simplefilter("ignore", FutureWarning)

# ロガーの取得
logger = setup_logger(__name__)

# 定数の定義
HTML_DIR = Path("data", "html")
SAVE_DIR = Path("data", "rawdf")

# URL定義
RACE_DATE_URL_TEMPLATE = (
    "https://race.netkeiba.com/top/calendar.html?year={year}&month={month}"
)
RACE_ID_LIST_URL_TEMPLATE = (
    "https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}"
)
RACE_URL_TEMPLATE = "https://db.netkeiba.com/race/{race_id}"
HORSE_URL_TEMPLATE = "https://db.netkeiba.com/horse/{horse_id}"

# スクレイピング関連定数
HTML_RACE_DIR = HTML_DIR / "race"
HTML_HORSE_DIR = HTML_DIR / "horse"
RAWDF_RACE_FILE_NAME = "race_results.csv"
RAWDF_HORSE_FILE_NAME = "horse_results.csv"
RAWDF_PREPROCESSED_RACE_FILE_NAME = "preprocessed_race_results.csv"
RAWDF_PREPROCESSED_HORSE_FILE_NAME = "preprocessed_horse_results.csv"
LOOP_WAIT_SECONDS = 3  # スクレイピング間の待機時間
FLOM_DATE = "2024-01"  # スクレイピング開始年月
TO_DATE = "2024-11"  # スクレイピング終了年月

# カラム列名
COLUMN_RACE_ID = "race_id"
COLUMN_HORSE_ID = "horse_id"
COLUMN_JOCKEY_ID = "jockey_id"
COLUMN_TRAINER_ID = "trainer_id"
COLUMN_OWNER_ID = "owner_id"
COLUMN_RANK = "rank"
COLUMN_WAKUBAN = "wakuban"
COLUMN_UMABAN = "umaban"
COLUMN_SEX = "sex"
COLUMN_AGE = "age"
COLUMN_WEIGHT = "weight"
COLUMN_WEIGHT_DIFF = "weight_diff"
COLUMN_TANSYO = "tansyo"
COLUMN_POPULARITY = "popularity"
COLUMN_IMPOST = "impost"
COLUMN_DATE = "date"
COLUMN_WEATHER = "weather"
COLUMN_RACE_TYPE = "race_type"
COLUMN_COURSE_LEN = "course_len"
COLUMN_GROUND_STATE = "ground_state"
COLUMN_RANK_DIFF = "rank_diff"
COLUMN_PRIZE = "prize"
COLUMN_RACE_CLASS = "race_class"
COLUMN_AROUND = "around"
COLUMN_PLACE = "place"

HORSE_ID_LENGTH = 10
JOCKEY_ID_LENGTH = 5
TRAINER_ID_LENGTH = 5
OWNER_ID_LENGTH = 6

# User-Agent 定義
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

# メッセージ定数
PROCESS_MESSAGE = ":process start"
RACE_ID_PICKLE = "race_id_from202401_to202411.pickle"
RESULT_PICKLE = "result_data_from202401_to202411.pickle"

# エラーメッセージ
ERROR_NO_VALID_TABLE = "HTMLドキュメントに有効な<table>要素が見つかりませんでした。"
ERROR_UNEXPECTED = "予期せぬエラーが発生しました。"
ERROR_INVALID_URL = "無効なURLが指定されました。"
ERROR_TITLE = "対象外のタイトルです。"

RACE_INFO_CSV = "race_info.csv"
RACE_INFO_TRANSFORMED = "race_info_transformed.csv"
RACE_INFO_PREPROCESSING = "race_info_preprocessing.csv"

# 正規表現パターン
RACE_TYPE_PATTERN = r"(芝|ダ|障)"
AROUND_PATTERN = r"(右|左)"
CORCE_LEN_PATTERN = r"(\d+)m"
GROUND_STATE_PATTERN = r"(芝|ダート|障):(.+)"
PLACE_D_PATTERN = r"(\d+回(\w+)\d{1,2}日目)"
PLACE_DD_PATTERN = r"([^\d]+)(\d{1})?"
DATE_PATTERN = r"\d{4}年\d{1,2}月\d{1,2}日"

# mappingファイル読み込み
mapping_loader = MappingLoader(mapping_dir=Path(__file__).parent.parent / "mapping")
mapping_loader.load_all_mappings()
