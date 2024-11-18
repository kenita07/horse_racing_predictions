# 基本ライブラリ
from pathlib import Path
import re
import time
import traceback
from urllib.request import Request, urlopen

# 外部ライブラリ
from bs4 import BeautifulSoup
import pandas as pd
import pickle
from tqdm.notebook import tqdm

# Selenium関連のライブラリ
from selenium.webdriver.common.by import By

# 自作モジュール
from logger_setting import setup_logger
from chrome_setting import get_chrome_driver

# ロガーの取得
logger = setup_logger(__name__)

# 定数の定義
GET_RACE_DATE_URL = "https://race.netkeiba.com/top/calendar.html?year=2024&month=10"
GET_RACE_ID_LIST_URL = (
    "https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}"
)
GET_RESULTS_URL = "https://db.netkeiba.com/race/{race_id}"

LOOP_MINUTE = 1
FLOM_ = "2024-01"
TO_ = "2024-10"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}


def scrape_kaisai_date(from_, to_):
    """
    指定した期間内に開催されたレースの日付を取得する関数。
    Parameters
    ----------
    from_ : str
        開始日を指定する文字列。フォーマットは "YYYY-MM"。
    to_ : str
        終了日を指定する文字列。フォーマットは "YYYY-MM"。
    Returns
    -------
    list
        指定した期間内に開催されたレースの日付を格納したリスト。
        日付は "YYYYMMDD" の形式で返される。
    Notes
    -----
    - `pd.date_range` を用いて指定した月の初日を範囲としてスクレイピングを行う。
    - 各月のURLを `https://race.netkeiba.com/top/calendar.html` から取得し、
      `Calendar_Table` クラスを持つHTML要素内のリンクを解析して、開催日を抽出。
    - `HEADERS` や `LOOP_MINUTE` 変数は予め定義されていることが前提。
    - スクレイピングの際には `time.sleep(LOOP_MINUTE)` で指定した秒数待機することで、
      サーバーへの負荷を軽減している。

    Examples
    --------
    >>> scrape_kaisai_date("2023-01", "2023-03")
    ['20230105', '20230112', '20230208', ...]

    """

    kaisai_date_list = []
    for date in tqdm(pd.date_range(from_, to_, freq="MS")):
        year = date.year
        month = date.month
        url = f"https://race.netkeiba.com/top/calendar.html?year={year}&month={month}"
        request = Request(url, headers=HEADERS)
        html = urlopen(request).read()  # スクレイピング
        soup = BeautifulSoup(html)
        a_tag_list = soup.find("table", class_="Calendar_Table").find_all("a")
        for a in a_tag_list:
            # TODO XPATHで取得するようにしたい
            a_tag_info = re.findall(r"kaisai_date=(\d{8})", a["href"])[0]
            kaisai_date_list.append(a_tag_info)
        time.sleep(LOOP_MINUTE)
    return kaisai_date_list


def scrape_race_id_list(kaisai_date_list: list[str]):
    """
    指定された開催日リストに基づいて、各開催日のレースIDを取得する関数。

    この関数は、与えられた開催日リスト（kaisai_date_list）に従い、`netkeiba`のレースページから
    各レースのIDをスクレイピングします。指定されていない場合は、デフォルトで2024年1月から
    2024年10月までの開催日リストを取得する。

    Parameters:
    kaisai_date_list (list of str): レースの開催日を表す文字列のリスト。
                                    (例: ["2024-01-01", "2024-01-02"])

    Returns:
    list of str: レースIDのリスト（12桁の文字列）を返す。
                 例: ["123456789012", "123456789013"]
    """
    race_id_list = []
    with get_chrome_driver(headless=True) as driver:
        for kaisai_date in tqdm(kaisai_date_list):
            url = GET_RACE_ID_LIST_URL.format(kaisai_date=kaisai_date)
            try:
                driver.get(url)
                time.sleep(LOOP_MINUTE)
                # TODO XPATHで取得するようにしたい
                li_list = driver.find_elements(By.CLASS_NAME, "RaceList_DataItem")
                for li in li_list:
                    href = li.find_element(By.TAG_NAME, "a").get_attribute("href")
                    race_id = re.findall(r"race_id=(\d{12})", href)[0]
                    race_id_list.append(race_id)
            except:
                logger.error("stopped at {URL}")
                logger.debug(traceback.format_exc())
                break
    return race_id_list


# mainに一応記載
def get_race_id_lsit_pickle():
    """
    指定されたpickleファイルからレースIDのリストを読み込み、返す関数。

    この関数は、事前に保存されたレースIDのリストを格納したpickleファイルを開き、その内容をリストとして読み込みます。
    ファイル名は "race_id_from202401_to202411.pickle" で、指定された範囲の日付に対応するレースIDが保存されています。

    Returns:
        list: pickleファイルから読み込まれたレースIDのリスト。

    Raises:
        FileNotFoundError: 指定されたpickleファイルが存在しない場合。
        pickle.UnpicklingError: ファイルの読み込み中にエラーが発生した場合。
    """
    # TODO output先調整
    race_id_pickle = "race_id_from202401_to202411.pickle"
    with open(race_id_pickle, "rb") as rf:
        race_id_list = pickle.load(rf)
    return race_id_list


def html_download(race_id_list):
    """
    レースIDリストに基づき、各レースのHTMLページをダウンロードして指定ディレクトリに保存する関数。

    この関数は、`race_id_list` から各レースIDを取得し、それに対応するHTMLページを指定されたURLからスクレイピングします。
    ダウンロードしたHTMLは、`../data/html/race` ディレクトリに`race_id.bin`という名前で保存されます。
    同じレースIDのHTMLファイルがすでに存在する場合は、スキップされます。

    処理は各レースIDごとに行われ、HTMLが保存された後、次のリクエストまで1秒の待機時間が挿入されます。

    Raises:
        Exception: スクレイピングやファイル書き込み中にエラーが発生した場合。
    """
    for race_id in race_id_list:
        html_dir = Path("..", "data", "html", "race")
        html_file = str(html_dir) + "/" + race_id + ".bin"
        # ファイルがすでに存在する場合はスキップ
        if Path(html_file).exists():
            print(f"File already exists: {html_file}")
            continue
        url = GET_RESULTS_URL.format(race_id=race_id)
        request = Request(url, headers=HEADERS)
        html = urlopen(request).read()  # スクレイピング
        with open(html_file, "wb") as wf:
            wf.write(html)
        time.sleep(LOOP_MINUTE)


def scrape_html_race(race_id_list):
    """
    指定されたレースIDリストに基づき、HTMLページをスクレイピングして指定ディレクトリに保存する関数。

    この関数は、`race_id_list` から各レースIDを取得し、それに対応するHTMLページを指定されたURLからスクレイピングします。
    ダウンロードしたHTMLは、`../data/html/race` ディレクトリに `race_id.bin` という名前で保存されます。
    すでにファイルが存在する場合、そのレースIDに対するダウンロードはスキップされます。

    スクレイピングは、1秒間の待機を挟みながら行われます。

    Args:
        race_id_list (list): スクレイピング対象となるレースIDのリスト。

    Returns:
        str: HTMLファイルが保存されるディレクトリのパス。

    Raises:
        Exception: スクレイピングやファイル書き込み中にエラーが発生した場合。
    """
    path_list = []
    for race_id in tqdm(race_id_list):
        html_dir = str(Path("..", "data", "html", "race"))
        html_file = html_dir + "\\" + race_id + ".bin"
        url = GET_RESULTS_URL.format(race_id=race_id)
        request = Request(url, headers=HEADERS)
        path_list.append(html_file)
        if Path(html_file).is_file():
            print("skip:" + race_id)
            continue
        else:
            html = urlopen(request).read()  # スクレイピング
            time.sleep(1)
            with open(html_file, "wb") as wf:
                wf.write(html)
    return html_dir


def get_result(html_paths):
    """
    指定されたHTMLファイルパスリストを読み込み、HTMLからテーブルデータを抽出して結合する関数。

    この関数は、HTMLファイルを1つずつ読み込み、その中の有効なテーブルデータを抽出してPandasのDataFrameに変換します。
    有効なテーブルが複数見つかれば、それらを結合して最終的に1つのDataFrameとして返します。
    レースIDをインデックスとして設定し、最終的なDataFrameにまとめます。

    Args:
        html_paths (list): HTMLファイルのパスのリスト。各ファイルはレースIDに対応し、テーブルデータを含んでいます。

    Returns:
        pandas.DataFrame: すべてのHTMLファイルから抽出したテーブルデータを結合したDataFrame。各行はレースIDをインデックスとして持つ。

    Raises:
        Exception: HTMLのパースやテーブル抽出中にエラーが発生した場合、その情報を標準出力に表示し続行する。
    """
    html_df_dict = {}
    for html_path in tqdm(html_paths):
        with open(html_path, "rb") as rf:
            race_id = html_path.stem  # ファイル名を抽出 ../[race_id].html
            html = rf.read()
            try:
                """
                取得したhtmlファイルをpd.read_htmlすると一部で
                IndexError: list index out of range
                になるのでBeautifulSoupでHTMLをパース
                """
                soup = BeautifulSoup(html, "html.parser")
                tables = soup.find_all("table")  # 全ての<table>を取得

                # thまたはtd要素を持つ有効な<table>を抽出
                valid_tables = [
                    table for table in tables if table.find("th") or table.find("td")
                ]

                if not valid_tables:
                    print(f"{race_id}: 有効な<table>が見つかりませんでした")
                    continue
                # 有効な<table>をHTML文字列に変換して、pd.read_htmlに渡す
                dfs = pd.read_html(str(valid_tables))

                # 最初のテーブルを取得し、レースIDでインデックスを設定
                df = dfs[0]
                if not df.empty:
                    df.index = [race_id] * len(df)
                    html_df_dict[race_id] = df
                else:
                    print(f"{race_id}: 結合するデータフレームがありません")
            except Exception as e:
                print(f"{race_id}: エラーが発生しました - {e}")
    concat_html_df = pd.concat(html_df_dict.values())
    concat_html_df.index.name = "race_id"
    return concat_html_df


def out_results_pickle(results_df):
    # TODO output先調整
    result_pickle = "result_data_from202401_to202411.pickle"
    with open(result_pickle, "wb") as f:
        pickle.dump(results_df, f)


if __name__ == "__main__":
    kaisai_date_list = scrape_kaisai_date(FLOM_, TO_)
    race_id_list = scrape_race_id_list(kaisai_date_list)
    html_download(race_id_list)
    html_dir = scrape_html_race(race_id_list)
    html_paths = list(Path(html_dir).glob("*"))
    results_df = get_result(html_paths)
    out_results_pickle(results_df)
