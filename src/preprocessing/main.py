# 基本ライブラリ
from pathlib import Path
import re
import time
import traceback
import warnings
from urllib.request import Request, urlopen

# 外部ライブラリ
from bs4 import BeautifulSoup
import pandas as pd
import pickle
from tqdm.notebook import tqdm
from urllib.error import HTTPError, URLError

# Selenium関連のライブラリ
from selenium.webdriver.common.by import By

# 自作モジュール
from logger_setting import setup_logger
from chrome_setting import get_chrome_driver

# pandas worning非表示設定
"""
# 有効な<table>をHTML文字列に変換して、pd.read_htmlに渡す
dfs = pd.read_html(str(valid_tables))
"""
warnings.simplefilter("ignore", FutureWarning)


# ロガーの取得
logger = setup_logger(__name__)

# 定数の定義
HTML_DIR = Path("..", "data", "html")

RACE_DATE_URL = "https://race.netkeiba.com/top/calendar.html?year=2024&month=10"
RACE_ID_LIST_URL = (
    "https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}"
)
RACE_URL = "https://db.netkeiba.com/race/{race_id}"
HTML_RACE_DIR = HTML_DIR / "race"

HORSE_URL = "https://db.netkeiba.com/horse/{horse_id}"
HTML_HORSE_DIR = HTML_DIR / "horse"

SAVE_DIR = Path("..", "data", "rawdf")
RAWDF_FILE_NAME = "results.csv"
RAWDF_HORSE_FILE_NAME = "horse_results.csv"

LOOP_MINUTE = 3
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
        time.sleep(LOOP_MINUTE)
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
            time.sleep(LOOP_MINUTE)
            url = RACE_ID_LIST_URL.format(kaisai_date=kaisai_date)
            try:
                driver.get(url)
                # TODO XPATHで取得するようにしたい
                li_list = driver.find_elements(By.CLASS_NAME, "RaceList_DataItem")
                for li in li_list:
                    href = li.find_element(By.TAG_NAME, "a").attribute("href")
                    race_id = re.findall(r"race_id=(\d{12})", href)[0]
                    race_id_list.append(race_id)
            except:
                logger.error("stopped at {URL}")
                logger.debug(traceback.format_exc())
                break
    return race_id_list


# mainに一応記載
def race_id_lsit_pickle():
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

    この関数は、`race_id_list` から各レースIDを取得し、それに対応するHTMLページを指定されたURLからスクレイピングする。
    ダウンロードしたHTMLは、`../data/html/race` ディレクトリに `race_id.bin` という名前で保存される。
    同じレースIDのHTMLファイルがすでに存在する場合は、スキップされる。

    処理は各レースIDごとに行われ、HTMLが保存された後、次のリクエストまで1秒の待機時間が挿入される。

    Raises:
        Exception: スクレイピングやファイル書き込み中にエラーが発生した場合。
    """
    for race_id in race_id_list:
        time.sleep(LOOP_MINUTE)
        html_file = str(HTML_RACE_DIR) + "/" + race_id + ".bin"
        # ファイルがすでに存在する場合はスキップ
        if Path(HTML_RACE_DIR).exists():
            print(f"File already exists: {html_file}")
            continue
        url = RACE_URL.format(race_id=race_id)
        request = Request(url, headers=HEADERS)
        html = urlopen(request).read()  # スクレイピング
        with open(html_file, "wb") as wf:
            wf.write(html)


def scrape_html_race(race_id_list):
    """
    指定されたレースIDリストに基づき、HTMLページをスクレイピングして指定ディレクトリに保存する関数。

    この関数は、`race_id_list` から各レースIDを取得し、それに対応するHTMLページを指定されたURLからスクレイピングする。
    ダウンロードしたHTMLは、`../data/html/race` ディレクトリに `race_id.bin` という名前で保存される。
    すでにファイルが存在する場合、そのレースIDに対するダウンロードはスキップされる。

    スクレイピングは、1秒間の待機を挟みながら行われる。

    Args:
        race_id_list (list): スクレイピング対象となるレースIDのリスト。

    Raises:
        Exception: スクレイピングやファイル書き込み中にエラーが発生した場合。
    """
    path_list = []
    HTML_RACE_DIR.mkdir(parents=True, exist_ok=True)
    for race_id in tqdm(race_id_list):
        time.sleep(LOOP_MINUTE)
        html_file = str(HTML_RACE_DIR) + "\\" + race_id + ".bin"
        url = RACE_URL.format(race_id=race_id)
        request = Request(url, headers=HEADERS)
        path_list.append(html_file)
        # binファイルが存在していればスキップ
        if Path(html_file).is_file():
            print("skip:" + race_id)
            continue
        else:
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
                    print(f"{race_id}: 有効な<table>が見つかりませんでした")
                    continue

                # 有効な<table>をHTML文字列に変換して、pd.read_htmlに渡す
                dfs = pd.read_html(str(valid_tables))

                if len(dfs) == 0:
                    print(f"{race_id}: pd.read_htmlでテーブルが抽出できませんでした")
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

            except IndexError as e:
                print(f"{race_id}: pd.read_htmlでのインデックスエラー - {e}")
                continue
            except Exception as e:
                print(f"{race_id}: 予期せぬエラーが発生しました - {e}")
                continue
    concat_df = pd.concat(html_df_dict.values())
    concat_df.index.name = "race_id"
    concat_df.columns = concat_df.columns.str.replace(" ", "")
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    concat_df.to_csv(SAVE_DIR / "results.csv", sep="\t")
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
    # TODO output先調整
    result_pickle = "result_data_from202401_to202411.pickle"
    with open(result_pickle, "wb") as f:
        pickle.dump(results_df, f)


def id_names(soup, df):
    """
    HTMLから馬、騎手、調教師、馬主のIDを抽出し、指定されたDataFrameに追加する関数。

    この関数は、BeautifulSoupで解析されたHTMLデータから特定のID（馬、騎手、調教師、馬主）の情報を抽出し、渡されたDataFrameにそのIDを新たな列として追加します。

    Args:
        soup (bs4.BeautifulSoup): BeautifulSoupで解析されたHTMLデータ。
        df (pandas.DataFrame): IDを追加する対象のDataFrame。各行にはレースまたは馬に関連する情報が含まれている。

    Returns:
        pandas.DataFrame: 'horse_id', 'jockey_id', 'trainer_id', 'owner_id'の列が追加されたDataFrame。

    Raises:
        KeyError: soup内に期待される構造やhrefパターンが存在しない場合に発生する可能性があります。

    注意:
        - 正規表現を用いて、HTML内の特定の<a>タグからIDを抽出します。
        - 以下のURLパターンに基づいてIDを取得します：
            - 馬: `/horse/<10桁のID>`
            - 騎手: `/jockey/<5桁のID>`
            - 調教師: `/trainer/<5桁のID>`
            - 馬主: `/owner/<6桁のID>`
        - 抽出されたIDの数がDataFrameの行数と一致しない場合、不足分は適切に処理される必要があります。
    """

    horse_id_list = []
    jockey_id_list = []
    trainer_id_list = []
    owner_id_list = []

    # 各列名となるaタグリストを取得
    a_tag_horse_list = soup.find_all("a", href=re.compile(r"^/horse/"))
    a_tag_jockey_list = soup.find_all("a", href=re.compile(r"^/jockey/"))
    a_tag_traine_rlist = soup.find_all("a", href=re.compile(r"^/trainer/"))
    a_tag_owner_list = soup.find_all("a", href=re.compile(r"^/owner/"))

    for a in a_tag_horse_list:
        horse_id = re.findall(r"\d{10}", a["href"])[0]
        horse_id_list.append(horse_id)
    df["horse_id"] = horse_id_list

    # jockey_id取得
    for a in a_tag_jockey_list:
        jockey_id = re.findall(r"\d{5}", a["href"])[0]
        jockey_id_list.append(jockey_id)
    df["jockey_id"] = jockey_id_list

    # trainer_id取得
    for a in a_tag_traine_rlist:
        trainer_id = re.findall(r"\d{5}", a["href"])[0]
        trainer_id_list.append(trainer_id)
    df["trainer_id"] = trainer_id_list

    # owner_id取得
    for a in a_tag_owner_list:
        owner_id = re.findall(r"\d{6}", a["href"])[0]
        owner_id_list.append(owner_id)
    df["owner_id"] = owner_id_list

    return df


def scrape_html_horse(horse_id_list, skip: bool = True):
    """
    指定された馬IDリストに基づき、HTMLページをスクレイピングして指定ディレクトリに保存する関数。

    この関数は、`horse_id_list` から各馬IDを取得し、それに対応するHTMLページを指定されたURLからスクレイピングする。
    ダウンロードしたHTMLは、`../data/html/horse` ディレクトリに `horse_id.bin` という名前で保存される。
    すでにファイルが存在する場合、その馬IDに対するダウンロードはスキップされる。

    スクレイピングは、1秒間の待機を挟みながら行われる。

    Args:
        horse_id_list (list): スクレイピング対象となる馬IDのリスト。
        skip (bool, optional): ファイルが既に存在する場合にスキップするかどうか。デフォルトはTrue。

    Raises:
        Exception: スクレイピングやファイル書き込み中にエラーが発生した場合。
    """

    path_list = []
    HTML_HORSE_DIR.mkdir(parents=True, exist_ok=True)
    for horse_id in tqdm(horse_id_list):
        time.sleep(LOOP_MINUTE)
        try:
            html_file = str(HTML_HORSE_DIR) + "\\" + horse_id + ".bin"
            url = HORSE_URL.format(horse_id=horse_id)
            request = Request(url, headers=HEADERS)
            path_list.append(html_file)
            # 随時対象htmlが更新されるため、binファイルが存在してskipがTrueであればスキップする
            if Path(html_file).is_file() and skip:
                print("skip:" + horse_id)
                continue
            else:
                html = urlopen(request).read()  # スクレイピング
                with open(html_file, "wb") as wf:
                    wf.write(html)
        except HTTPError as e:
            print(f"{horse_id}: 無効なURLです - {e}")
            continue


def create_horse_result(html_paths):
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
            try:
                horse_id = html_path.stem  # ファイル名を抽出 ../[horse_id].html
                html = rf.read()
                # 対象は2番目のtableタグ
                df = pd.read_html(html)[2]
                df.index = [horse_id] * len(df)
                html_df_dict[horse_id] = df
            except IndexError as e:
                print(f"{horse_id}: pd.read_htmlでのインデックスエラー - {e}")
                continue
            except Exception as e:
                print(f"{horse_id}: 予期せぬエラーが発生しました - {e}")
                continue
    print(html_df_dict)
    concat_df = pd.concat(html_df_dict.values())
    concat_df.index.name = "horse_id"
    concat_df.columns = concat_df.columns.str.upper()
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    concat_df.to_csv(SAVE_DIR / RAWDF_HORSE_FILE_NAME, sep="\t")
    return concat_df


if __name__ == "__main__":
    kaisai_date_list = scrape_kaisai_date(FLOM_, TO_)
    race_id_list = scrape_race_id_list(kaisai_date_list)
    html_download(race_id_list)
    scrape_html_race(race_id_list)
    html_paths = list(Path(HTML_RACE_DIR).glob("*"))
    results_df = create_race_result(html_paths)
    out_results_pickle(results_df)
