from src.config import *


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
