from src.config import *


def process_race_results():
    """
    レース結果の生データを処理し、必要なカラムを抽出して前処理を行う関数。
    - 必要なカラムに変換を施し、不足しているデータは削除。
    - 指定したカラム名に基づいてデータを再構成し、最終的にファイルに出力。

    Returns:
        None
    """
    df = pd.read_csv(SAVE_DIR / RAWDF_RACE_FILE_NAME_CSV, sep="\t")
    df[COLUMN_RANK] = pd.to_numeric(df["着順"], errors="coerce")
    df.dropna(subset=[COLUMN_RANK], inplace=True)
    df[COLUMN_SEX] = (
        df["性齢"].str[0].map(mapping_loader.get_sex_mapping()).value_counts()
    )
    df[COLUMN_AGE] = df["性齢"].str[1:].astype(int)
    df[COLUMN_WEIGHT] = df["馬体重"].str.extract(r"(\d+)").astype(int)
    df[COLUMN_WEIGHT] = pd.to_numeric(df[COLUMN_WEIGHT], errors="coerce")
    df[COLUMN_WEIGHT_DIFF] = df["馬体重"].str.extract(r"\((.+)\)").astype(int)
    df[COLUMN_WEIGHT_DIFF] = pd.to_numeric(df[COLUMN_WEIGHT_DIFF], errors="coerce")
    df[COLUMN_TANSYO] = df["単勝"].astype(float)
    df[COLUMN_POPULARITY] = pd.to_numeric(df["人気"], errors="coerce")
    df.dropna(subset=[COLUMN_POPULARITY], inplace=True)
    df[COLUMN_IMPOST] = df["斤量"].astype(int)
    df[COLUMN_WAKUBAN] = df["枠番"].astype(int)
    df[COLUMN_UMABAN] = df["馬番"].astype(int)

    # ここに使用する列名を列挙
    df = df[
        [
            COLUMN_RACE_ID,
            COLUMN_HORSE_ID,
            COLUMN_JOCKEY_ID,
            COLUMN_TRAINER_ID,
            COLUMN_OWNER_ID,
            COLUMN_RANK,
            COLUMN_WAKUBAN,
            COLUMN_UMABAN,
            COLUMN_SEX,
            COLUMN_AGE,
            COLUMN_WEIGHT,
            COLUMN_WEIGHT_DIFF,
            COLUMN_TANSYO,
            COLUMN_POPULARITY,
            COLUMN_IMPOST,
        ]
    ]
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAVE_DIR / RAWDF_PREPROCESSED_RACE_FILE_NAME_CSV, sep="\t", index=False)
