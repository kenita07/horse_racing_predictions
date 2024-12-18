from src.config import *


class FeatureCreator:
    def __init__(
        self,
        results_filepath: Path = SAVE_DIR / RAWDF_RACE_FILE_NAME_CSV,
        race_info_filepath: Path = SAVE_DIR / RACE_INFO_PREPROCESSING_CSV,
        horse_results_filepath: Path = SAVE_DIR / RAWDF_HORSE_FILE_NAME_CSV,
        output_dir: Path = SAVE_DIR,
    ):
        self.results = pd.read_csv(results_filepath, sep="\t")
        self.race_info = pd.read_csv(race_info_filepath, sep="\t")
        self.horse_results = pd.read_csv(horse_results_filepath, sep="\t")
        self.output_dir = output_dir
        # 学習母集団の作成
        self.population = self.results[[COLUMN_RACE_ID, COLUMN_HORSE_ID]].merge(
            self.race_info[[COLUMN_RACE_ID, COLUMN_DATE]], on=COLUMN_RACE_ID
        )


def agg_horse_n_races(
    self,
    n_races: list[int] = [
        RANK_0003_RACE,
        RANK_0005_RACE,
        RANK_0010_RACE,
        RANK_1000_RACE,
    ],
):
    # 直近nレースの着順と賞金の平均を集計する関数。
    grouped_df = (
        self.population.merge(
            self.horse_results, on=[COLUMN_RACE_ID], suffixes=("", "_horse")
        )
        .query("date > date_horse")
        .sort_values("date_horse", ascending=False)
        .groupby([COLUMN_RACE_ID, COLUMN_RACE_ID])
    )
    merged_df = self.population.copy()
    for n_race in n_races:
        df = (
            grouped_df.head(n_race)
            .groupby([COLUMN_RACE_ID, COLUMN_RACE_ID])[[COLUMN_RANK, COLUMN_PRIZE]]
            .mean()
        ).add_suffix(f"_{n_race}-races")
        merged_df = merged_df.merge(
            df,
            on=[COLUMN_RACE_ID, COLUMN_RACE_ID],
        )
    self.agg_horse_n_races_df = merged_df


def create_features(self):
    """
    特徴量作成処理を実行し、populationテーブルに全ての特徴量を結合する。
    """
    self.agg_horse_n_races()
    features = (
        self.population.merge(self.results, on=[COLUMN_RACE_ID, COLUMN_RACE_ID])
        .merge(self.race_info, on=[COLUMN_RACE_ID, COLUMN_DATE])
        .merge(
            self.agg_horse_n_races_df,
            on=[COLUMN_RACE_ID, COLUMN_DATE, COLUMN_RACE_ID],
            how="left",
        )
    )
    features.to_csv(self.output_dir / FEATURES_CSV, sep="\t", index=None)
    return features
