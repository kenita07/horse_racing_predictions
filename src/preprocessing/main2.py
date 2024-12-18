from src.preprocessing.modules.feature_setting import FeatureCreator

if __name__ == "__main__":
    """
    メイン処理を実行する。
    - 生データの取得を行い、その後前処理を実施する。

    Returns:
        None

    """
    # 生データ取得
    fc = FeatureCreator()
    print(fc)
