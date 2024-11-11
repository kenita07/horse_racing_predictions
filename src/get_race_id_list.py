# 基本ライブラリ
import re
import time
import traceback

# Selenium関連のライブラリ
from selenium.webdriver.common.by import By

# 外部ライブラリ
from tqdm.notebook import tqdm

# 自作モジュール
import get_race_date
from logger_setting import setup_logger
from chrome_setting import get_chrome_driver

# jupyter用 auto restart
# %load_ext autoload

# ロガーの取得
logger = setup_logger(__name__)

# 定数の定義
# TODO フロントを用いてfrom toを調整できるようにしたい 優先度:低
FLOM_ = "2024-01"
TO_ = "2024-10"
URL_TMPLATE = "https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}"
LOOP_MINUTE = 1


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
    # kaisai_date_listが渡されていない場合は、デフォルトで日付リストを取得
    if not kaisai_date_list:
        kaisai_date_list = get_race_date.scrape_kaisai_date(from_=FLOM_, to_=TO_)
        logger.info(f"取得した開催日リスト: {kaisai_date_list}")
    kaisai_date_list = get_race_date.scrape_kaisai_date(from_=FLOM_, to_=TO_)
    race_id_list = []
    with get_chrome_driver(headless=True) as driver:
        for kaisai_date in tqdm(kaisai_date_list):
            url = URL_TMPLATE.format(kaisai_date=kaisai_date)
            try:
                driver.get(url)
                time.sleep(LOOP_MINUTE)
                # TODO XPATHで取得するようにしたい　優先度:中
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
