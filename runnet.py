import rumps
import subprocess
import time
import threading
import re

class MyCatApp(rumps.App):
    def __init__(self):
        super(MyCatApp, self).__init__("🐈")
        
        # 🟢 アニメーション用
        self.frames = ["⚪️"]
        self.current_frame = 0
        
        # 📡 Ping値（初期値は0）
        self.current_ping_ms = 0.0
        
        # バックグラウンドでPingを測り続ける「裏方」を開始
        self.ping_thread = threading.Thread(target=self.ping_loop, daemon=True)
        self.ping_thread.start()
        
        # アイコンを更新するタイマー
        self.timer = rumps.Timer(self.animate, 1.0)
        self.timer.start()

    def ping_loop(self):
        # 裏方係の仕事：ずっとPingを打ち続けて、最新のmsを記録する
        while True:
            try:
                # 1.1.1.1 にPingを1回送る（最大2秒まで待つ）
                result = subprocess.run(
                    ["ping", "-c", "1", "1.1.1.1"],
                    capture_output=True, text=True, timeout=2.0
                )
                if result.returncode == 0:
                    # 結果の文字から "time=〇〇 ms" の数値を抜き出す
                    match = re.search(r'time=([\d\.]+)\s*ms', result.stdout)
                    if match:
                        self.current_ping_ms = float(match.group(1))
                    else:
                        self.current_ping_ms = 9999.0
                else:
                    self.current_ping_ms = 9999.0
            except Exception:
                # オフラインなどでエラーになった時
                self.current_ping_ms = 9999.0
            
            # 2秒おきにもう一度Pingを打つ
            time.sleep(2)

    def animate(self, timer):
        # 現在記録されているPing値を取得
        ping = self.current_ping_ms
        
        # Ping値に応じてアイコンと速度を切り替え
        if ping == 0.0:
            self.frames = ["⚪️"]
            timer.interval = 1.0
        elif ping < 20.0:
            # 【超速い/快適】 🟢 ＋ ダッシュ (< 20ms)
            self.frames = ["🚀"]
            timer.interval = 0.04
        elif ping < 60.0:
            # 【普通】 🔵 ＋ 普通に走る (< 60ms)
            self.frames = ["🐎"]
            timer.interval = 0.15
        elif ping < 150.0:
            # 【ちょっと遅い/ラグい】 🟡 ＋ トコトコ (< 150ms)
            self.frames = ["🐢"]
            timer.interval = 0.4
        else:
            # 【遅い・不通】 🔴 ＋ ピコンピコン (エラー・切断)
            self.frames = ["‼️"]
            timer.interval = 1.0

        # パラパラ漫画の次のコマへ
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        
        # 数値は消して、アニメーションアイコンのみをメニューバーに表示
        self.title = self.frames[self.current_frame]

    # ポップアップでPing値を表示する機能に変更
    @rumps.clicked("現在の応答速度 (Ping) を確認")
    def show_ping(self, _):
        ping = self.current_ping_ms
        
        if ping == 0.0:
            rumps.alert("確認中...", "Pingの測定を準備中です。少し待ってから再度お試しください。")
        elif ping >= 9999.0:
            rumps.alert("接続エラー", "インターネット回線が切断されているか、応答がありません。")
        else:
            # 速度に応じたメッセージ
            if ping < 20.0:
                comment = "爆速です！🔥🚀"
            elif ping < 60.0:
                comment = "普通です。通信問題なしです🐳✨"
            elif ping < 150.0:
                comment = "少しラグがあるかもしれません🐢"
            else:
                comment = "かなり遅いかもしれません...🐌"
                
            rumps.alert("現在のPing値", f"【 {ping:.1f} ms 】\n\n{comment}")

if __name__ == "__main__":
    MyCatApp().run()
