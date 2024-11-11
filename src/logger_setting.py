import logging


# ログの設定を行う関数
def setup_logger(name=__name__, level=logging.INFO):
    """
    ログの設定を行い、ロガーオブジェクトを返す関数。

    この関数は、指定された名前とログレベルに基づいて、コンソールにログを出力するロガーを設定。

    Parameters:
    name (str): ロガーの名前。デフォルトは現在のモジュール名。
    level (int): ログレベル。デフォルトは `logging.INFO`。

    Returns:
    logging.Logger: 設定されたロガーオブジェクト。
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # 同じ設定が複数回行われないようにする
        logger.setLevel(level)

        # コンソールハンドラの設定
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # フォーマッタの設定
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        # ハンドラをロガーに追加
        logger.addHandler(console_handler)

    return logger
