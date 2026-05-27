import rumps
import subprocess
import time
import threading
import re
import AppKit
import random
import sys
import os
import tempfile
import shutil

# MacのDock（下のバー）にPythonのアイコンを出さないようにする魔法のおまじない
AppKit.NSApplication.sharedApplication().setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)

class PingMonitor(rumps.App):
    def __init__(self):
        super(PingMonitor, self).__init__("")
        
        # 🟢 アニメーション用
        self.frames = ["fly1.PNG"]
        self.icon = self.frames[0]
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
            
            # Pingを打つ間隔を長くしてCPU負荷を下げる (5秒)
            time.sleep(5)

    def animate(self, timer):
        # 現在記録されているPing値を取得
        ping = self.current_ping_ms
        
        # Ping値に応じてアイコンと速度を切り替え
        if ping == 0.0:
            frames = ["kyurun-1.PNG"]
            new_interval = 1.0
        elif ping < 20.0:
            # 【超速い/快適】 🟢 ＋ パッタパった (< 20ms)
            frames = ["fly1.PNG","fly2.PNG","fly3.PNG","fly4.PNG","fly5.PNG","fly4-2.PNG","fly3.PNG","fly2.PNG"]
            new_interval = 0.1
        elif ping < 60.0:
            # 【普通】 🔵 ＋ 普通にパタパタ (< 60ms)
            frames = ["fly1.PNG","fly2.PNG","fly3.PNG","fly4.PNG","fly5.PNG","fly4-2.PNG","fly3.PNG","fly2.PNG"]
            new_interval = 0.5
        elif ping < 150.0:
            # 【ちょっと遅い/ラグい】 🟡 ＋ きゅるん (< 150ms)
            frames = ["kyurun-1.PNG", "kyurun-2.PNG","kyurun-2.PNG","kyurun-2.PNG","kyurun-1.PNG","kyurun-1.PNG","kyurun-1.PNG"]
            new_interval = 0.5
        else:
            # 【遅い・不通】 🔴 ＋ おねむ (エラー・切断)
            frames = ["sleepy-1.PNG", "sleepy-2.PNG", "sleepy-3.PNG", "sleepy-4.PNG"]
            new_interval = 0.4

        # アニメーションの内容や速度が変わったときだけ更新する
        if timer.interval != new_interval or self.frames != frames:
            self.frames = frames
            timer.interval = new_interval
            self.current_frame = 0 # 状態が変わったら最初のコマからリセット
        else:
            # パラパラ漫画の次のコマへ
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        
        # 次に表示するアイコン
        new_icon = self.frames[self.current_frame]

        # 実際に画像が変わったときだけメニューバーを更新する（CPU負荷を劇的に下げる対策）
        if getattr(self, "_current_icon_file", None) != new_icon:
            self.title = ""
            self.icon = new_icon
            self._current_icon_file = new_icon

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
                comment = "🦅 爆速です 🦅"
            elif ping < 60.0:
                comment = "普通です。通信問題なしです🕊️"
            elif ping < 150.0:
                comment = "少しラグがある🦆しれません"
            else:
                comment = "かなり遅いかもしれません...🐣"
                
            rumps.alert("現在のPing値", f"【 {ping:.1f} ms 】\n\n{comment}")

    @rumps.clicked("きゅるん")
    def random_kyurun(self, _):
        # 画像ファイル名をランダムで選ぶ
        image_file = random.choice(["kyurun-1.PNG", "kyurun-2.PNG"])
        
        # アプリとして書き出した（py2app）時と、通常実行した時の画像パスの違いを吸収します！
        if 'RESOURCEPATH' in os.environ:
            image_path = os.path.join(os.environ['RESOURCEPATH'], image_file)
        else:
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_file)

        # 【追加】すでにウィンドウが開いていたら安全に閉じておく
        if getattr(self, 'kyurun_window', None) is not None:
            try:
                self.kyurun_window.close()
            except Exception:
                pass
        
        # アプリ化すると別のPythonプロセスを起動(subprocess.Popen)する裏技がブロックされてしまうため、
        # 今動いているシステム（rumps）内で直接ウィンドウを作って表示するように書き直します！
        
        image = AppKit.NSImage.alloc().initWithContentsOfFile_(image_path)
        if not image:
            rumps.alert("エラー", f"画像が見つかりません...泣\n{image_path}")
            return

        size = image.size()
        mask = 1 | 2 # 1: Titled (タイトルバーあり), 2: Closable (閉じるボタンあり)
        
        # RuntimeErrorを防ぐため、self.kyurun_windowとしてウィンドウの情報をアプリ側に持たせます
        self.kyurun_window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            AppKit.NSMakeRect(0, 0, size.width, size.height), mask, 2, False
        )
        self.kyurun_window.setTitle_("きゅるん")
        self.kyurun_window.center()
        self.kyurun_window.setLevel_(3) # 常に最前面

        # 【重要】ウィンドウが閉じられた時にメモリから自動削除されないようにする（これでクラッシュを完全に防ぎます！）
        self.kyurun_window.setReleasedWhenClosed_(False)
        
        # ウィンドウの背景を指定のこだわりのカラー (#F2E2FF) にする
        bg_color = AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(242/255.0, 226/255.0, 255/255.0, 1.0)
        self.kyurun_window.setBackgroundColor_(bg_color)
        
        # ここが裏技：画像をクリックしたら閉じる設定を、ボタンとして割り当てます
        btn = AppKit.NSButton.alloc().initWithFrame_(AppKit.NSMakeRect(0, 0, size.width, size.height))
        btn.setImage_(image)
        btn.setBordered_(False) # ボタンの線や影を消して画像と一体化
        btn.setAction_(AppKit.NSSelectorFromString("close")) # performClose ではなく直接 close を呼ぶのが安全！
        btn.setTarget_(self.kyurun_window)
        
        self.kyurun_window.setContentView_(btn)
        self.kyurun_window.makeKeyAndOrderFront_(None)
        AppKit.NSApp.activateIgnoringOtherApps_(True)

if __name__ == "__main__":
    PingMonitor().run()
