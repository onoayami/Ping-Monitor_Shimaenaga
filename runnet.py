import rumps
import subprocess
import psutil
import time

class MyCatApp(rumps.App):
    def __init__(self):
        super(MyCatApp, self).__init__("🍥")
        
        # 🟢 最初は「普通・安定（緑）」のコマでスタート
        self.frames = ["🟢"]
        self.current_frame = 0
        
        # ⏱ 速度計算用の記録
        self.last_io = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        self.last_time = time.time()
        
        self.timer = rumps.Timer(self.animate, 0.3)
        self.timer.start()

    def animate(self, timer):
        # 1. 現在の「通信量」と「今の時間」を取得
        current_io = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        current_time = time.time()
        
        # 2. 経過時間の計算
        elapsed = current_time - self.last_time
        if elapsed <= 0:
            elapsed = 0.01
            
        # 3. 1秒あたり何MB（メガバイト）通信したかを計算
        bytes_diff = current_io - self.last_io
        speed_mb = (bytes_diff / elapsed) / 1024 / 1024
        
        self.last_io = current_io
        self.last_time = current_time
        
        # 4. 速度（speed_mb）に応じて、走る速さと「色丸」を変化させる！
        if speed_mb < 0.05:
            # 【ほぼ通信なし・超低速】 🔴赤丸 ＋ 1.0秒に1コマ（まったり）
            self.frames = ["🐢"]
            timer.interval = 1.0
        elif speed_mb < 0.5:
            # 【軽い通信・低速】 🟡黄丸 ＋ 0.4秒に1コマ（トコトコ）
            self.frames = ["🐇"]
            timer.interval = 0.4
        elif speed_mb < 2.0:
            # 【中くらいの通信・中速】 🔵青丸 ＋ 0.15秒に1コマ（そこそこ速い）
            self.frames = ["🚗"]
            timer.interval = 0.15
        else:
            # 【激しい通信・高速】 🟢緑丸 ＋ 0.04秒に1コマ（猛ダッシュ！！！）
            self.frames = ["🚀"]
            timer.interval = 0.04

        # 5. パラパラ漫画を表示
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.title = self.frames[self.current_frame]

    # 回線チェック機能（そのまま）
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