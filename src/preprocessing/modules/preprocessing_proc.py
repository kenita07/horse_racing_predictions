from src.config import *
from src.preprocessing.modules.process_race_results import process_race_results
from src.preprocessing.modules.process_horse_results import process_horse_results


def preprocessing():
    """
    レース結果と馬の結果データを前処理する関数。
    - `process_race_results()` と `process_horse_results()` を呼び出して、データのクリーニングと再構成を実行。

    Returns:
        None
    """
    # race_results.csv前処理
    process_race_results()
    # horse_results.csv前処理
    process_horse_results()
