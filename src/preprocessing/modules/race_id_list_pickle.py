from modules.config import *


def race_id_lsit_pickle():
    """
    指定されたpickleファイルからレースIDのリストを読み込んで返す。

    この関数は、事前に保存されたレースIDリストを格納したpickleファイルを開き、その内容をリストとして読み込む。
    ファイル名は `RACE_ID_PICKLE` で、指定された範囲の日付に対応するレースIDが保存されている。

    Returns:
        list: pickleファイルから読み込まれたレースIDのリスト。

    Raises:
        FileNotFoundError: 指定されたpickleファイルが見つからない場合。
        pickle.UnpicklingError: ファイルの読み込み中にエラーが発生した場合。
    """
    with open(RACE_ID_PICKLE, "rb") as rf:
        race_id_list = pickle.load(rf)
    return race_id_list
