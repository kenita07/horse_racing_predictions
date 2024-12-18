from src.config import *


def create_race_info():
    """
    レース情報をHTMLファイルから抽出し、CSVに保存する。

    この関数は、`HTML_RACE_DIR`内のすべてのHTMLファイルを読み込み、指定されたレース情報を抽出して、
    DataFrameに格納する。抽出された情報は`title`、`info1`、`info2`として保存され、最終的に
    それらを1つのDataFrameにまとめ、`SAVE_DIR / RACE_INFO_CSV`としてCSVファイルに保存する。

    処理の流れ:
    - HTMLファイルを読み込み、`BeautifulSoup`で解析
    - `data_intro`クラスを持つ`div`タグ内の情報を抽出
    - レース情報として`title`、`info1`、`info2`を取得
    - `race_id`をファイル名から取得し、DataFrameに格納
    - 抽出した情報を全て1つのDataFrameにまとめ、CSVとして保存

    返り値:
        なし
    """
    dfs = {}
    for html_path in tqdm(list((HTML_RACE_DIR).glob("*bin"))):
        with open(html_path, "rb") as f:
            try:
                html = f.read()
                soup = BeautifulSoup(html, "lxml").find("div", class_="data_intro")
                info_dict = {}
                info_dict["title"] = soup.find("h1").text
                p_list = soup.find_all("p")
                # レース名取得
                info_dict["info1"] = re.findall(
                    r"[\w:]+", p_list[0].text.replace(" ", "")
                )
                # 日付を含むpタグ取得
                for i, p_2 in enumerate(p_list):
                    if re.search(DATE_PATTERN, p_2.text):
                        break  # 最初に見つかったものだけ欲しいなら break
                info_dict["info2"] = re.findall(r"[\w:]+", p_2.text)
                df = pd.DataFrame.from_dict(info_dict, orient="index").T
                # ファイル名からrace_idを取得
                race_id = html_path.stem
                df.index = [race_id] * len(df)
                dfs[race_id] = df
            except IndexError as e:
                logger.error(ERROR_TITLE)
                continue
            except AttributeError as e:
                logger.error(ERROR_TITLE)
                continue
    concat_df = pd.concat(dfs.values())
    concat_df.index.name = COLUMN_RACE_ID
    concat_df.columns = concat_df.columns.str.replace(" ", "")
    SAVE_DIR.mkdir(exist_ok=True, parents=True)
    concat_df.to_csv(SAVE_DIR / RACE_INFO_CSV, sep="\t")


def get_match(pattern, string, group_num=1):
    """
    正規表現で文字列からパターンに一致する部分を取得する。

    この関数は、指定された正規表現パターンと文字列に対して検索を行い、
    一致する部分があれば、その部分を取得して返す。

    引数:
        pattern (str): 正規表現パターン
        string (str): 検索対象の文字列
        group_num (int, オプション): 取得するキャプチャグループの番号（デフォルトは1）

    返り値:
        str または None: 一致する部分文字列（キャプチャグループが指定された場合はその部分）
                         一致しなかった場合は None
    """
    match = re.search(pattern, string)
    return match.group(group_num) if match else None


def create_race_info_transformed():
    """
    レース情報を変換して、新しいファイルに保存する。

    この関数は、`SAVE_DIR / RACE_INFO_CSV`からタブ区切りのCSVファイルを読み込み、
    各行について必要な情報を抽出し、新しい形式で変換してから
    `SAVE_DIR / race_info_TRANSFORMED`に保存する。

    変換の内容:
    - `info1` と `info2` 列のデータを辞書またはリストに変換
    - 各列の値を計算し、適切な形式で新しい行を作成
    - 最終的に必要なカラムのみを保持したデータを保存

    返り値:
        なし
    """
    race_infos = pd.read_csv(SAVE_DIR / RACE_INFO_CSV, sep="\t")
    # 必要な列名
    columns = [
        COLUMN_RACE_ID,
        COLUMN_DATE,
        COLUMN_RACE_TYPE,
        COLUMN_AROUND,
        COLUMN_COURSE_LEN,
        COLUMN_WEATHER,
        COLUMN_GROUND_STATE,
        COLUMN_RACE_CLASS,
        COLUMN_PLACE,
    ]

    # 空のデータフレームを作成（最終結果を格納）
    result_df = pd.DataFrame(columns=columns)

    # 各行をループ処理
    for index, row in race_infos.iterrows():
        # info1 と info2 を文字列から辞書またはリストに変換
        info1 = ast.literal_eval(row["info1"])
        info2 = ast.literal_eval(row["info2"])

        # 各列の値を計算
        race_id = row["race_id"]
        formatted_date = re.sub(r"(\d+)年(\d+)月(\d+)日", r"\1-\2-\3", info2[0])
        formatted_date = re.sub(r"-(\d)-", r"-0\1-", formatted_date)  # 月の0埋め
        formatted_date = re.sub(r"-(\d)$", r"-0\1", formatted_date)  # 日の0埋め
        race_type = get_match(RACE_TYPE_PATTERN, info1[0])
        around = get_match(AROUND_PATTERN, info1[0])
        course_len = get_match(CORCE_LEN_PATTERN, info1[0])
        weather = info1[1][3:]
        ground_state = get_match(GROUND_STATE_PATTERN, info1[2], group_num=2)
        race_class = info2[2]
        place = get_match(PLACE_D_PATTERN, info2[1], group_num=2)
        # 新しい行を作成
        new_row = {
            COLUMN_RACE_ID: race_id,
            COLUMN_DATE: formatted_date,
            COLUMN_RACE_TYPE: race_type,
            COLUMN_AROUND: around,
            COLUMN_COURSE_LEN: course_len,
            COLUMN_WEATHER: weather,
            COLUMN_GROUND_STATE: ground_state,
            COLUMN_RACE_CLASS: race_class,
            COLUMN_PLACE: place,
        }

        # 新しい行を DataFrame に追加
        result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)

    # 保存処理
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(SAVE_DIR / RACE_INFO_PREPROCESSING_CSV, sep="\t", index=False)


def create_race_info_preprocessing():
    """
    レース情報を前処理して、指定のディレクトリに保存する。

    この関数は、`SAVE_DIR / race_info_TRANSFORMED`からタブ区切りのCSVファイルを読み込み、
    各カラムに対して定義されたマッピングを適用して前処理を行う。
    処理後、必要なカラムだけを抽出し、`SAVE_DIR / RACE_INFO_PREPROCESSING_CSV`に再保存する。

    前処理の内容:
    - レースの日付を日時型に変換
    - 各カラムに対してマッピングを適用
    - 必要なカラムのみを抽出して保存

    返り値:
        なし
    """
    df = pd.read_csv(SAVE_DIR / RACE_INFO_PREPROCESSING_CSV, sep="\t")
    df[COLUMN_DATE] = pd.to_datetime(df[COLUMN_DATE])
    df[COLUMN_RACE_TYPE] = df[COLUMN_RACE_TYPE].map(
        mapping_loader.get_race_type_mapping()
    )
    df[COLUMN_AROUND] = df[COLUMN_AROUND].map(mapping_loader.get_around_mapping())
    df[COLUMN_WEATHER] = df[COLUMN_WEATHER].map(mapping_loader.get_weather_mapping())
    df[COLUMN_GROUND_STATE] = df[COLUMN_GROUND_STATE].map(
        mapping_loader.get_ground_state_mapping()
    )
    df[COLUMN_RACE_CLASS] = df[COLUMN_RACE_CLASS].map(
        mapping_loader.get_race_class_info_mapping()
    )
    place_perse_list = pd.Series(
        [get_match(PLACE_DD_PATTERN, i) for i in df[COLUMN_PLACE].values]
    )
    df[COLUMN_PLACE] = place_perse_list.map(mapping_loader.get_place_mapping())
    # ここに使用する列名を列挙
    df = df[
        [
            COLUMN_RACE_ID,
            COLUMN_DATE,
            COLUMN_RACE_TYPE,
            COLUMN_AROUND,
            COLUMN_COURSE_LEN,
            COLUMN_WEATHER,
            COLUMN_GROUND_STATE,
            COLUMN_RACE_CLASS,
            COLUMN_PLACE,
        ]
    ]
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAVE_DIR / RACE_INFO_PREPROCESSING_CSV, sep="\t", index=False)
