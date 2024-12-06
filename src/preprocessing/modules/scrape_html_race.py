from modules.config import *


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
