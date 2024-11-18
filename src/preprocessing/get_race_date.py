# 基本ライブラリ
import re
import time
from urllib.request import Request, urlopen

# 外部ライブラリ
import pandas as pd
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm

# 定数の定義
# TODO フロントを用いてfrom toを調整できるようにしたい 優先度:低
FLOM_ = "2024-01"
TO_ = "2024-10"
LOOP_MINUTE = 1
TEST_URL = "https://db.netkeiba.com/race/202304040509"
URL = "https://race.netkeiba.com/top/calendar.html?year=2024&month=10"
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
