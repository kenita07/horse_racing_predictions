from src.config import *
from src.preprocessing.modules.id_names import id_names


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
                    logger.warning(f"{race_id}:" + ERROR_NO_VALID_TABLE)
                    continue

                # 有効な<table>をHTML文字列に変換して、pd.read_htmlに渡す
                dfs = pd.read_html(str(valid_tables))

                if len(dfs) == 0:
                    logger.warning(f"{race_id}:" + ERROR_NO_VALID_TABLE)
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

            except IndexError:
                logger.error(f"{race_id}:" + ERROR_NO_VALID_TABLE)
                continue
            except Exception:
                logger.error(f"{race_id}:" + ERROR_UNEXPECTED)
                continue
    concat_df = pd.concat(html_df_dict.values())
    concat_df.index.name = COLUMN_RACE_ID
    concat_df.columns = concat_df.columns.str.replace(" ", "")
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    concat_df.to_csv(SAVE_DIR / RAWDF_RACE_FILE_NAME_CSV, sep="\t")
    return concat_df
