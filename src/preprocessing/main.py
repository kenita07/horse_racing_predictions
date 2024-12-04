# 基本ライブラリ
import os
from pathlib import Path
import re
import sys
import time
import traceback
import warnings
from urllib.request import Request, urlopen

# 外部ライブラリ
from bs4 import BeautifulSoup
import pandas as pd
import pickle
from tqdm import tqdm
from urllib.error import HTTPError, URLError

# Selenium関連のライブラリ
from selenium.webdriver.common.by import By

# スクリプトの1つ上の階層をsys.pathに追加
sys.path.append(str(Path(__file__).resolve().parent.parent))

# 自作モジュール
from logger_setting import setup_logger
from chrome_setting import get_chrome_driver

# pandas worning非表示設定
"""
warning箇所
# 有効な<table>をHTML文字列に変換して、pd.read_htmlに渡す
dfs = pd.read_html(str(valid_tables))
"""
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
RAWDF_FILE_NAME = "results.csv"
RAWDF_HORSE_FILE_NAME = "horse_results.csv"
LOOP_WAIT_SECONDS = 3  # スクレイピング間の待機時間
FLOM_DATE = "2024-01"  # スクレイピング開始年月
TO_DATE = "2024-11"  # スクレイピング終了年月

# ID抽出関連
COLUMN_RACE_ID = "race_id"
COLUMN_HORSE_ID = "horse_id"
COLUMN_JOCKEY_ID = "jockey_id"
COLUMN_TRAINER_ID = "trainer_id"
COLUMN_OWNER_ID = "owner_id"

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


def scrape_kaisai_date(from_: str, to_: str) -> list:
    """
    指定した期間内に開催されたレースの日付を取得する関数。

    指定された期間の月初日を範囲としてスクレイピングを行い、各月の開催日を取得する。
    開催日は `netkeiba` のカレンダーから取得され、日付は "YYYYMMDD" の形式で返される。

    Parameters
    ----------
    from_ : str
        開始日を指定する文字列。フォーマットは "YYYY-MM"。
    to_ : str
        終了日を指定する文字列。フォーマットは "YYYY-MM"。

    Returns
    -------
    list
        指定された期間内に開催されたレースの日付を格納したリスト。
        日付は "YYYYMMDD" の形式で返される。

    Notes
    -----
    - `pd.date_range` を使って、指定された開始日から終了日までの月初日を範囲としてスクレイピングを行う。
    - 各月のURLは `https://race.netkeiba.com/top/calendar.html` から取得し、`Calendar_Table` クラスを持つHTML要素内のリンクを解析して、開催日を抽出する。
    - `HEADERS` や `LOOP_WAIT_SECONDS` などの設定が前提となっており、これらは事前に定義されている必要がある。
    - サーバーへの負荷を軽減するため、各リクエストの間に `time.sleep(LOOP_WAIT_SECONDS)` を使って待機時間を設けている。
    """

    kaisai_date_list = []
    for date in tqdm(pd.date_range(from_, to_, freq="MS")):
        year = date.year
        month = date.month
        url = RACE_DATE_URL_TEMPLATE.format(year=year, month=month)
        time.sleep(LOOP_WAIT_SECONDS)
        request = Request(url, headers=HEADERS)
        html = urlopen(request).read()  # スクレイピング
        soup = BeautifulSoup(html, features="lxml")
        a_tag_list = soup.find("table", class_="Calendar_Table").find_all("a")
        for a in a_tag_list:
            a_tag_info = re.findall(r"kaisai_date=(\d{8})", a["href"])[0]
            kaisai_date_list.append(a_tag_info)
    return kaisai_date_list


def scrape_race_id_list(kaisai_date_list: list[str]) -> list[str]:
    """
    開催日リストに基づいて、各開催日のレースIDを取得する関数。

    指定された開催日リストに従い、`netkeiba`のレースページから各レースのIDをスクレイピングする。
    引数に開催日リストを渡さない場合、デフォルトで2024年1月から2024年10月までの開催日を使用する。

    Parameters:
    kaisai_date_list (list of str): レースの開催日を表す文字列のリスト。
                                    例: ["2024-01-01", "2024-01-02"]

    Returns:
    list of str: 取得したレースIDのリスト（12桁の文字列）。
                 例: ["123456789012", "123456789013"]
    """
    race_id_list = []
    with get_chrome_driver(headless=True) as driver:
        for kaisai_date in tqdm(kaisai_date_list):
            time.sleep(LOOP_WAIT_SECONDS)
            url = RACE_ID_LIST_URL_TEMPLATE.format(kaisai_date=kaisai_date)
            try:
                driver.get(url)
                li_list = driver.find_elements(By.CLASS_NAME, "RaceList_DataItem")
                for li in li_list:
                    href = li.find_element(By.TAG_NAME, "a").get_attribute("href")
                    race_id = re.findall(r"race_id=(\d{12})", href)[0]
                    race_id_list.append(race_id)
            except:
                logger.error("stopped at {URL}")
                break
    return race_id_list


def race_id_lsit_pickle():
    """
    指定されたpickleファイルからレースIDのリストを読み込んで返す。

    この関数は、事前に保存されたレースIDリストを格納したpickleファイルを開き、その内容をリストとして読み込む。
    ファイル名は `RACE_ID_PICKLE` で、指定された範囲の日付に対応するレースIDが保存されている。

    Returns:
        list: pickleファイルから読み込まれたレースIDのリスト。

    Raises:
        FileNotFoundError: 指定されたpickleファイルが見つからない場合。
        pickle.UnpicklingError: ファイルの読み込み中にエラーが発生した場合。
    """
    with open(RACE_ID_PICKLE, "rb") as rf:
        race_id_list = pickle.load(rf)
    return race_id_list


def scrape_html_race(race_id_list):
    """
    指定されたレースIDリストに基づき、HTMLページをスクレイピングして指定ディレクトリに保存する関数。

    この関数は、`race_id_list` から各レースIDを取得し、それに対応するHTMLページを指定されたURLからスクレイピングする。
    ダウンロードしたHTMLは、`/data/html/race` ディレクトリに `[race_id].bin` という名前で保存される。
    すでにファイルが存在する場合、そのレースIDに対するダウンロードはスキップされる。

    スクレイピングは、LOOP_WAIT_SECONDS秒間の待機を挟みながら行われる。

    Args:
        race_id_list (list): スクレイピング対象となるレースIDのリスト。

    Raises:
        Exception: スクレイピングやファイル書き込み中にエラーが発生した場合。
    """
    path_list = []
    HTML_RACE_DIR.mkdir(parents=True, exist_ok=True)
    for race_id in tqdm(race_id_list):
        html_file = str(HTML_RACE_DIR) + "\\" + race_id + ".bin"
        # binファイルが存在していればスキップ
        if Path(html_file).is_file():
            logger.info("skip:" + race_id)
            continue
        time.sleep(LOOP_WAIT_SECONDS)
        url = RACE_URL_TEMPLATE.format(race_id=race_id)
        request = Request(url, headers=HEADERS)
        path_list.append(html_file)
        html = urlopen(request).read()  # スクレイピング
        with open(html_file, "wb") as wf:
            wf.write(html)


def create_race_result(html_paths):
    """
    指定されたHTMLファイルパスリストを読み込み、HTMLからテーブルデータを抽出して結合する関数。

    この関数は、HTMLファイルを1つずつ読み込み、その中の有効なテーブルデータを抽出してPandasのDataFrameに変換する。
    有効なテーブルが複数見つかれば、それらを結合して最終的に1つのDataFrameとして返す。
    レースIDをインデックスとして設定し、最終的なDataFrameにまとめる。

    Args:
        html_paths (list): HTMLファイルのパスのリスト。各ファイルはレースIDに対応し、テーブルデータを含んでいる。

    Returns:
        pandas.DataFrame: すべてのHTMLファイルから抽出したテーブルデータを結合したDataFrame。各行はレースIDをインデックスとして持つ。

    Raises:
        Exception: HTMLのパースやテーブル抽出中にエラーが発生した場合、その情報を標準出力に表示し続行する。
    """
    html_df_dict = {}
    for html_path in tqdm(html_paths):
        with open(html_path, "rb") as rf:
            try:
                race_id = html_path.stem  # ファイル名を抽出 ../[race_id].html
                html = rf.read()
                # BeautifulSoupでHTMLをパース
                tmp_soup = BeautifulSoup(html, "html.parser")
                tables = tmp_soup.find_all("table")  # 全ての<table>を取得

                # thまたはtd要素を持つ有効な<table>を抽出
                valid_tables = [
                    table for table in tables if table.find("th") or table.find("td")
                ]

                if not valid_tables:
                    logger.warning(f"{race_id}:" + ERROR_NO_VALID_TABLE)
                    continue

                # 有効な<table>をHTML文字列に変換して、pd.read_htmlに渡す
                dfs = pd.read_html(str(valid_tables))

                if len(dfs) == 0:
                    logger.warning(f"{race_id}:" + ERROR_NO_VALID_TABLE)
                    continue

                # 最初のテーブルを取得
                df = dfs[0]

                # 各id取得関数
                soup = BeautifulSoup(html, "lxml").find(
                    "table", class_="race_table_01 nk_tb_common"
                )
                df = id_names(soup, df)

                df.index = [race_id] * len(df)
                html_df_dict[race_id] = df

            except IndexError:
                logger.error(f"{race_id}:" + ERROR_NO_VALID_TABLE)
                continue
            except Exception:
                logger.error(f"{race_id}:" + ERROR_UNEXPECTED)
                continue
    concat_df = pd.concat(html_df_dict.values())
    concat_df.index.name = COLUMN_RACE_ID
    concat_df.columns = concat_df.columns.str.replace(" ", "")
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    concat_df.to_csv(SAVE_DIR / RAWDF_FILE_NAME, sep="\t")
    return concat_df


def out_results_pickle(results_df):
    """
    指定されたDataFrameをpickleファイルとして保存する関数。

    この関数は、引数として渡されたDataFrameを指定されたファイル名でpickle形式で保存する。
    保存先ファイル名は`result_data_from202401_to202411.pickle`に固定されており、ファイルの保存先調整が必要な場合は、コード内で変更することができる。

    Args:
        results_df (pandas.DataFrame): 保存するデータを含むDataFrame。

    Returns:
        None: 関数はファイルにデータを保存するが、返り値はなし。

    Raises:
        Exception: pickleファイルの書き込み中にエラーが発生した場合。
    """
    result_pickle = RESULT_PICKLE
    with open(result_pickle, "wb") as f:
        pickle.dump(results_df, f)


def extract_ids(soup, regex_pattern, id_length):
    """
    HTML内の特定のパターンに一致するIDを抽出する汎用関数。

    Args:
        soup (bs4.BeautifulSoup): BeautifulSoupで解析されたHTMLデータ。
        regex_pattern (str): href属性の正規表現パターン。
        id_length (int): 抽出するIDの長さ。

    Returns:
        list: 抽出されたIDのリスト。
    """
    id_list = []
    a_tag_list = soup.find_all("a", href=re.compile(regex_pattern))
    for a in a_tag_list:
        id_match = re.findall(rf"\d{{{id_length}}}", a["href"])
        if id_match:
            id_list.append(id_match[0])
    return id_list


def id_names(soup, df):
    """
    HTMLから馬、騎手、調教師、馬主のIDを抽出し、指定されたDataFrameに追加する関数。

    Args:
        soup (bs4.BeautifulSoup): BeautifulSoupで解析されたHTMLデータ。
        df (pandas.DataFrame): IDを追加する対象のDataFrame。

    Returns:
        pandas.DataFrame: 各ID列が追加されたDataFrame。
    """
    id_specs = [
        (r"^/horse/", COLUMN_HORSE_ID, HORSE_ID_LENGTH),
        (r"^/jockey/", COLUMN_JOCKEY_ID, JOCKEY_ID_LENGTH),
        (r"^/trainer/", COLUMN_TRAINER_ID, TRAINER_ID_LENGTH),
        (r"^/owner/", COLUMN_OWNER_ID, OWNER_ID_LENGTH),
    ]

    for regex, column, length in id_specs:
        df[column] = extract_ids(soup, regex, length)

    return df


def scrape_html_horse(horse_id_list, skip: bool = True):
    """
    指定された馬IDリストを基にHTMLページをスクレイピングし、指定ディレクトリに保存する。

    この関数は、`horse_id_list` から各馬IDを取得し、それに対応するHTMLページを指定されたURLからスクレイピングしてダウンロードする。
    ダウンロードしたHTMLファイルは、`../data/html/horse` ディレクトリに `horse_id.bin` という名前で保存される。
    すでにファイルが存在する場合、その馬IDに対するダウンロードはスキップする（`skip=True` の場合）。

    スクレイピング中には1秒間の待機を挟みながら行う。

    Args:
        horse_id_list (list): スクレイピング対象となる馬IDのリスト。
        skip (bool, optional): ファイルが既に存在する場合にスキップするかどうか。デフォルトはTrue。

    Raises:
        Exception: スクレイピングやファイル書き込み中にエラーが発生した場合。
    """
    path_list = []
    HTML_HORSE_DIR.mkdir(parents=True, exist_ok=True)
    for horse_id in tqdm(horse_id_list):
        try:
            html_file = str(HTML_HORSE_DIR) + "\\" + horse_id + ".bin"
            # 既にファイルが存在し、スキップする設定の場合はスキップ
            if Path(html_file).is_file() and skip:
                logger.info("skip:" + horse_id)
                continue
            time.sleep(LOOP_WAIT_SECONDS)
            url = HORSE_URL_TEMPLATE.format(horse_id=horse_id)
            request = Request(url, headers=HEADERS)
            path_list.append(html_file)
            html = urlopen(request).read()  # スクレイピング
            with open(html_file, "wb") as wf:
                wf.write(html)
        except HTTPError as e:
            logger.error(f"{horse_id}:" + ERROR_INVALID_URL + "- {e}")
            continue


def create_horse_result(html_paths):
    """
    指定されたHTMLファイルパスリストからテーブルデータを抽出し、結合して1つのDataFrameにする。

    この関数は、各HTMLファイルを読み込み、ファイル内の有効なテーブルを抽出してPandasのDataFrameに変換する。
    有効なテーブルが複数あれば、それらを結合して1つのDataFrameにまとめる。最終的なDataFrameは、レースIDをインデックスとして持つ。

    Args:
        html_paths (list): HTMLファイルのパスのリスト。各ファイルはレースIDに対応し、テーブルデータを含む。

    Returns:
        pandas.DataFrame: すべてのHTMLファイルから抽出したテーブルデータを結合したDataFrame。レースIDがインデックスとなる。

    Raises:
        Exception: HTMLのパースやテーブル抽出中にエラーが発生した場合、そのエラーメッセージをログに記録し、処理を続行する。
    """
    html_df_dict = {}
    for html_path in tqdm(html_paths):
        with open(html_path, "rb") as rf:
            try:
                horse_id = html_path.stem  # ファイル名を抽出 ../[horse_id].html
                html = rf.read()
                # 対象は2番目のtableタグ
                df = pd.read_html(html)[2]
                df.index = [horse_id] * len(df)
                html_df_dict[horse_id] = df
            except IndexError:
                logger.error(f"{horse_id}:" + ERROR_NO_VALID_TABLE)
                continue
            except Exception:
                logger.error(f"{horse_id}:" + ERROR_UNEXPECTED)
                continue
    concat_df = pd.concat(html_df_dict.values())
    concat_df.index.name = COLUMN_HORSE_ID
    concat_df.columns = concat_df.columns.str.replace(" ", "")
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    concat_df.to_csv(SAVE_DIR / RAWDF_HORSE_FILE_NAME, sep="\t")
    return concat_df


if __name__ == "__main__":
    # 開催日一覧を取得
    kaisai_date_list = scrape_kaisai_date(FLOM_DATE, TO_DATE)
    # 開催日に基づいてレースID一覧を取得
    race_id_list = scrape_race_id_list(kaisai_date_list)
    # レースIDに基づいてHTMLデータをスクレイピング
    scrape_html_race(race_id_list)
    # 取得したレースHTMLデータのパス一覧を作成
    html_paths_race = list(Path(HTML_RACE_DIR).glob("*"))
    # レース結果データを生成
    race_results = create_race_result(html_paths_race)
    # レース結果から馬ID一覧を抽出
    horse_id_list = race_results[COLUMN_HORSE_ID].unique()
    # 馬IDに基づいてHTMLデータをスクレイピング
    scrape_html_horse(horse_id_list)
    # 取得した馬HTMLデータのパス一覧を作成
    html_paths_horse = list(Path(HTML_HORSE_DIR).glob("*"))
    # 馬結果データを生成
    create_horse_result(html_paths_horse)
