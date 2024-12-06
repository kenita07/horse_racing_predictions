import json
from pathlib import Path


class MappingLoader:
    def __init__(self, mapping_dir: Path):
        """
        初期化メソッド。指定されたディレクトリからマッピングファイルをロードします。

        Args:
            mapping_dir (str): マッピングファイルが保存されているディレクトリのパス。
        """
        self.mapping_dir = Path(mapping_dir)
        # マッピングを格納する辞書
        self.SEX_MAPPING = {}
        self.WEATHER_MAPPING = {}
        self.RACE_TYPE_MAPPING = {}
        self.GROUND_STATE_MAPPING = {}
        self.RACE_CLASS_MAPPING = {}

    def load_mapping(self, mapping_name: str):
        """
        指定されたマッピング名に対応するJSONファイルを読み込み、辞書形式で返す関数。

        Args:
            mapping_name (str): 読み込むマッピングのファイル名（拡張子なし）。

        Returns:
            dict: JSONファイルの内容を辞書として返す。
        """
        mapping_file = self.mapping_dir / f"{mapping_name}.json"
        try:
            with open(mapping_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {mapping_name}.json not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: {mapping_name}.json is not a valid JSON file.")
            return {}

    def load_all_mappings(self):
        """
        必要なすべてのマッピングファイルを読み込み、インスタンス変数にセットする関数。

        Returns:
            None
        """
        self.SEX_MAPPING = self.load_mapping("sex")
        self.WEATHER_MAPPING = self.load_mapping("weather")
        self.RACE_TYPE_MAPPING = self.load_mapping("race_type")
        self.GROUND_STATE_MAPPING = self.load_mapping("ground_state")
        self.RACE_CLASS_MAPPING = self.load_mapping("race_class")

    def get_sex_mapping(self):
        return self.SEX_MAPPING

    def get_weather_mapping(self):
        return self.WEATHER_MAPPING

    def get_race_type_mapping(self):
        return self.RACE_TYPE_MAPPING

    def get_ground_state_mapping(self):
        return self.GROUND_STATE_MAPPING

    def get_race_class_mapping(self):
        return self.RACE_CLASS_MAPPING


# 使用
# mapping_dir = Path(__file__).parent.parent / "mapping"
# print(mapping_dir)
# mapping_loader = MappingLoader(mapping_dir=mapping_dir)
# mapping_loader.load_all_mappings()

# # マッピングを取得
# sex_mapping = mapping_loader.get_sex_mapping()
# weather_mapping = mapping_loader.get_weather_mapping()

# # 必要に応じて他のマッピングも取得可能
# print(sex_mapping)
# print(weather_mapping)
