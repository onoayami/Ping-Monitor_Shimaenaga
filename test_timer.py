import rumps
import time

class App(rumps.App):
    def __init__(self):
        super(App, self).__init__("Timer Test")
        self.last_time = time.time()
        self.count = 0
        self.timer = rumps.Timer(self.tick, 1.0)
        self.timer.start()
        
    def tick(self, sender):
        now = time.time()
        print(f"Tick {self.count}: {now - self.last_time:.3f} sec passed")
        self.last_time = now
        self.count += 1
        # re-assign interval like in runnet.py
        sender.interval = 1.0
        if self.count >= 5:
            rumps.quit_application()

if __name__ == '__main__':
    App().run()
