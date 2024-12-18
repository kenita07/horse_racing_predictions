from src.config import *


def process_horse_results():
    """
    馬の結果データを処理し、必要なカラムを抽出して前処理を行う関数。
    - 必要なカラムに変換を施し、不足しているデータは削除。
    - 指定したカラム名に基づいてデータを再構成し、最終的にファイルに出力。

    Returns:
        None
    """
    df = pd.read_csv(SAVE_DIR / RAWDF_HORSE_FILE_NAME_CSV, sep="\t")
    df[COLUMN_RANK] = pd.to_numeric(df["着順"], errors="coerce")
    df.dropna(subset=[COLUMN_RANK], inplace=True)
    df[COLUMN_DATE] = pd.to_datetime(df["日付"])
    df[COLUMN_WEATHER] = df["天気"].map(mapping_loader.get_weather_mapping())
    df[COLUMN_RACE_TYPE] = df["距離"].str[0].map(mapping_loader.get_race_type_mapping())
    df[COLUMN_COURSE_LEN] = df["距離"].str.extract(r"(\d+)").astype(int)
    df[COLUMN_GROUND_STATE] = df["馬場"].map(mapping_loader.get_ground_state_mapping())
    df[COLUMN_RANK_DIFF] = df["着差"].map(lambda x: 0 if x < 0 else x)
    df[COLUMN_PRIZE] = df["賞金"].fillna(0)
    regex_race_class = "|".join(mapping_loader.get_race_class_mapping().keys())
    df[COLUMN_RACE_CLASS] = (
        df["レース名"]
        .str.extract(rf"({regex_race_class})")[0]
        .map(mapping_loader.get_race_class_mapping())
    )
    df.rename(columns={"頭数": "n_horses"}, inplace=True)

    df = df[
        # ここに使用する列名を列挙
        [
            COLUMN_HORSE_ID,
            COLUMN_DATE,
            COLUMN_RANK,
            COLUMN_PRIZE,
            COLUMN_RANK_DIFF,
            COLUMN_WEATHER,
            COLUMN_RACE_TYPE,
            COLUMN_COURSE_LEN,
            COLUMN_GROUND_STATE,
            COLUMN_RACE_CLASS,
            "n_horses",
        ]
    ]
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAVE_DIR / RAWDF_PREPROCESSED_HORSE_FILE_NAME_CSV, sep="\t", index=False)
