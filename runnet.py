import rumps
import subprocess

class MyCatApp(rumps.App):
    def __init__(self):
        # メニューバーに表示する最初の文字（後で画像に変えます）
        super(MyCatApp, self).__init__("🍥")

    # メニューのボタンが押された時の処理
    @rumps.clicked("回線チェック (Ping)")
    def check_ping(self, _):
        # ここでPing係が動きます
        rumps.alert("確認中...", "Pingを打っています。少しお待ちください。")
        
        try:
            # Macの裏側で「ping -c 1 1.1.1.1」を実行する
            result = subprocess.run(["ping", "-c", "1", "1.1.1.1"], capture_output=True, text=True, timeout=5)
            
            # 結果をポップアップで表示
            if result.returncode == 0:
                rumps.alert("結果：大成功！", "無事にインターネットに繋がっています！")
            else:
                rumps.alert("結果：失敗...", "回線が途切れているかもしれません。")
        except Exception as e:
            rumps.alert("エラー", "何かがおかしいようです。")

if __name__ == "__main__":
    MyCatApp().run()