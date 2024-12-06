from modules.config import *


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
