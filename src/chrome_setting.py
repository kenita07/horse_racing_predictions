from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_chrome_driver(headless: bool = True):
    """
    Chrome WebDriverを設定して返す関数。

    この関数は、指定されたオプションに従って、Chromeブラウザをヘッドレスモード（または通常モード）で起動する
    WebDriverを返します。主にWebスクレイピングで使用されます。`webdriver-manager`を使用して、必要なChrome
    ドライバを自動的にインストールする。

    Parameters:
    headless (bool): Trueの場合、Chromeをヘッドレスモードで起動。デフォルトはTrue。
                      ヘッドレスモードではブラウザのUIが表示されず、バックグラウンドで動作する。

    Returns:
    webdriver.Chrome: 設定されたオプションを持つChrome WebDriverオブジェクト。
    """

    # Chromeオプション設定
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # ヘッドレスモードを有効にする
    chrome_options.add_argument("--disable-gpu")  # GPUを無効にする（特にWindowsで推奨）
    # chrome_options.add_argument(
    #     "--no-sandbox"
    # )  # サンドボックスモードを無効にする（Linuxで推奨）

    # USB: usb_service_win.cc:105 SetupDiGetDevicePropertyのエラー非表示
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Chromeドライバーパスを取得
    chromedriver_path = ChromeDriverManager().install()
    service = Service(chromedriver_path)

    # ドライバーオブジェクトを返す
    return webdriver.Chrome(service=service, options=chrome_options)
