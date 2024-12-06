from modules.config import *
from modules.scrape_kaisai_date import scrape_kaisai_date
from modules.scrape_race_id_list import scrape_race_id_list
from modules.scrape_html_race import scrape_html_race
from modules.create_race_result import create_race_result
from modules.scrape_html_horse import scrape_html_horse
from modules.create_horse_result import create_horse_result


def get_raw_data():
    """
    生データを取得し、レース結果データと馬の結果データをスクレイピングする関数。
    - 開催日一覧を取得し、そこからレースID一覧を生成。
    - 各レースIDに基づいてHTMLデータを取得。
    - 取得したHTMLデータを基に、レース結果と馬の結果データを生成する。

    Returns:
        None
    """
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
