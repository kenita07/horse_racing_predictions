from modules.get_raw_data import get_raw_data
from modules.preprocessing_proc import preprocessing

if __name__ == "__main__":
    """
    メイン処理を実行する。
    - 生データの取得を行い、その後前処理を実施する。

    Returns:
        None
    """
    # 生データ取得
    get_raw_data()

    # データ前処理
    preprocessing()
