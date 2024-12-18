from src.config import *


def out_results_pickle(results_df):
    """
    指定されたDataFrameをpickleファイルとして保存する関数。

    この関数は、引数として渡されたDataFrameを指定されたファイル名でpickle形式で保存する。
    保存先ファイル名は`result_data_from202401_to202411.pickle`に固定されており、ファイルの保存先調整が必要な場合は、コード内で変更することができる。

    Args:
        results_df (pandas.DataFrame): 保存するデータを含むDataFrame。

    Returns:
        None: 関数はファイルにデータを保存するが、返り値はなし。

    Raises:
        Exception: pickleファイルの書き込み中にエラーが発生した場合。
    """
    result_pickle = RESULT_PICKLE
    with open(result_pickle, "wb") as f:
        pickle.dump(results_df, f)
