from modules.config import *


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
