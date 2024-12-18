from src.config import *
from src.preprocessing.modules.extract_ids import extract_ids


def id_names(soup, df):
    """
    HTMLから馬、騎手、調教師、馬主のIDを抽出し、指定されたDataFrameに追加する関数。

    Args:
        soup (bs4.BeautifulSoup): BeautifulSoupで解析されたHTMLデータ。
        df (pandas.DataFrame): IDを追加する対象のDataFrame。

    Returns:
        pandas.DataFrame: 各ID列が追加されたDataFrame。
    """
    id_specs = [
        (r"^/horse/", COLUMN_HORSE_ID, HORSE_ID_LENGTH),
        (r"^/jockey/", COLUMN_JOCKEY_ID, JOCKEY_ID_LENGTH),
        (r"^/trainer/", COLUMN_TRAINER_ID, TRAINER_ID_LENGTH),
        (r"^/owner/", COLUMN_OWNER_ID, OWNER_ID_LENGTH),
    ]

    for regex, column, length in id_specs:
        df[column] = extract_ids(soup, regex, length)

    return df
