from src.preprocessing.modules.get_raw_data import get_raw_data
from src.preprocessing.modules.preprocessing_proc import preprocessing
from src.preprocessing.modules.create_race_info import create_race_info
from src.preprocessing.modules.create_race_info import create_race_info_transformed
from src.preprocessing.modules.create_race_info import (
    create_race_info_preprocessing,
)

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

    # レース情報テーブルを生成する
    create_race_info()
    create_race_info_transformed()
    create_race_info_preprocessing()
