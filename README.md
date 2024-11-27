# 競馬予想AI

このプロジェクトは、競馬のレース結果を予測するAIモデルを作ることを目的としたもの。データ解析、特徴量エンジニアリング、モデル学習、予測を通じて競馬予想を行う。

## ディレクトリ構成

プロジェクトのディレクトリ構成は以下の通り。

```directory
競馬予想AI/
├── data/                       # データセット用
│   ├── html/                   # HTMLデータ
│   │   ├── horse/              # 馬に関するHTMLデータ
│   │   └── race/               # レースに関するHTMLデータ
│   ├── processed/              # 前処理済みデータ（クリーンデータ）
│   ├── race_id_pickle/         # レースIDに関連するpickleファイル
│   └── rawdata/                # 生データ
│
├── notebooks/                  # Jupyter Notebook（データ探索・モデル実験用）
│   └── __pycache__/            # コンパイル済みのPythonファイル（自動生成される）
│
├── src/                        # ソースコード（プロジェクトのロジック）
│   ├── evaluation/             # モデル評価スクリプト
│   ├── prediction/             # 予測用スクリプト
│   ├── preprocessing/          # データ前処理スクリプト
│   ├── training/               # モデル学習スクリプト
│   └── __pycache__/            # コンパイル済みのPythonファイル（自動生成される）
│
├── requirements.txt            # 必要なPythonパッケージ
└── README.md                   # プロジェクト概要（使い方やセットアップ手順など）


```


### ディレクトリ詳細
- **.ipynb_checkpoints/**: Jupyter Notebookのチェックポイントファイルが格納されるディレクトリ。通常、手動で編集することはない。
- **.vscode/**: Visual Studio Codeの設定ファイル。
- **data/**: 生データや前処理済みデータを格納するディレクトリ。
  - `html/`:
    - `horse/`: 馬に関するHTMLデータ。
    - `race/`: レースに関するHTMLデータ。
  - `processed/`: 前処理済みのデータ（クリーンデータ）を格納。
  - `race_id_pickle/`: レースIDに関連するpickleファイル。
  - `rawdf/`: 生データフレーム。
  
- **notebooks/**: Jupyter Notebookでデータ探索やモデル実験を行う場所。

- **src/**: ソースコードのディレクトリ。
  - `evaluation/`: モデル評価スクリプト。
  - `prediction/`: 予測用スクリプト。
  - `preprocessing/`: データ前処理スクリプト。
  - `training/`: モデル学習スクリプト。

- **requirements.txt**: 必要なPythonパッケージが記載されたファイル。

## 使用方法

1. **データの準備**:
   - `data/rawdf/`に競馬の生データを配置。
   - 前処理を行いたい場合は、`src/preprocessing/`のスクリプトを使って処理を行う。

2. **モデル学習**:
   - `src/training/`のスクリプトでモデルの学習を行う。
   - ハイパーパラメータの設定は`configs/`内で行う。

3. **予測**:
   - 学習したモデルを使って予測を行うには、`src/prediction/`のスクリプトを使用する。

4. **評価**:
   - モデルの性能評価は、`src/evaluation/`のスクリプトで行う。

## ライセンス

このプロジェクトはMITライセンスの下で提供。詳細は`LICENSE`ファイルを参照。


## インストール

まず、依存関係をインストールするには以下のコマンドを実行。

```bash
pip install -r requirements.txt
```

## 使用方法

1. **データの準備**:
   - `data/raw/`に競馬の生データを配置する。
   - 前処理を行いたい場合は、`src/preprocessing/`のスクリプトを使って処理を行う。

2. **モデル学習**:
   - `src/training/`のスクリプトでモデルの学習を行う。
   - ハイパーパラメータの設定は`configs/`内で行う。

3. **予測**:
   - 学習したモデルを使って予測を行うには、`src/prediction/`のスクリプトを使用する。

4. **評価**:
   - モデルの性能評価は、`src/evaluation/`のスクリプトで行う。