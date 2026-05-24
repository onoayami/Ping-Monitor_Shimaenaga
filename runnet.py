import rumps
import subprocess

class MyCatApp(rumps.App):
    def __init__(self):
        # 最初は普通のネコ
        super(MyCatApp, self).__init__("🥚")
        
        # ① パラパラ漫画の「コマ」を絵文字で用意
        self.frames = ["🥚", "🐣", "🐥", "🐓"]
        self.current_frame = 0 # 今何コマ目か
        
        # ② タイマーをセット（0.3秒ごとに self.animate という関数を実行する）
        self.timer = rumps.Timer(self.animate, 0.3)
        self.timer.start() # タイマー開始！

    # ③ 0.3秒ごとに呼び出されるパラパラ漫画の処理
    def animate(self, _):
        # 次のコマに進める（4コマ目までいったら0コマ目に戻る計算）
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        
        # メニューバーの表示（title）を最新のコマに書き換える
        self.title = self.frames[self.current_frame]

    # 前回作ったPing機能（そのまま残します）
    @rumps.clicked("回線チェック (Ping)")
    def check_ping(self, _):
        rumps.alert("確認中...", "Pingを打っています。少しお待ちください。")
        try:
            result = subprocess.run(["ping", "-c", "1", "1.1.1.1"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                rumps.alert("結果：大成功！", "無事にインターネットに繋がっています！")
            else:
                rumps.alert("結果：失敗...", "回線が途切れているかもしれません。")
        except Exception as e:
            rumps.alert("エラー", "何かがおかしいようです。")

if __name__ == "__main__":
    MyCatApp().run()