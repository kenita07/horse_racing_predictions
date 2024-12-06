from modules.config import *


def create_horse_result(html_paths):
    """
    指定されたHTMLファイルパスリストからテーブルデータを抽出し、結合して1つのDataFrameにする。

    この関数は、各HTMLファイルを読み込み、ファイル内の有効なテーブルを抽出してPandasのDataFrameに変換する。
    有効なテーブルが複数あれば、それらを結合して1つのDataFrameにまとめる。最終的なDataFrameは、レースIDをインデックスとして持つ。

    Args:
        html_paths (list): HTMLファイルのパスのリスト。各ファイルはレースIDに対応し、テーブルデータを含む。

    Returns:
        pandas.DataFrame: すべてのHTMLファイルから抽出したテーブルデータを結合したDataFrame。レースIDがインデックスとなる。

    Raises:
        Exception: HTMLのパースやテーブル抽出中にエラーが発生した場合、そのエラーメッセージをログに記録し、処理を続行する。
    """
    html_df_dict = {}
    for html_path in tqdm(html_paths):
        with open(html_path, "rb") as rf:
            try:
                horse_id = html_path.stem  # ファイル名を抽出 ../[horse_id].html
                html = rf.read()
                # 対象は2番目のtableタグ
                df = pd.read_html(html)[2]
                df.index = [horse_id] * len(df)
                html_df_dict[horse_id] = df
            except IndexError:
                logger.error(f"{horse_id}:" + ERROR_NO_VALID_TABLE)
                continue
            except Exception:
                logger.error(f"{horse_id}:" + ERROR_UNEXPECTED)
                continue
    concat_df = pd.concat(html_df_dict.values())
    concat_df.index.name = COLUMN_HORSE_ID
    concat_df.columns = concat_df.columns.str.replace(" ", "")
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    concat_df.to_csv(SAVE_DIR / RAWDF_HORSE_FILE_NAME, sep="\t")
    return concat_df
