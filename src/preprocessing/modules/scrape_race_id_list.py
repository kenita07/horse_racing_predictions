from modules.config import *


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
