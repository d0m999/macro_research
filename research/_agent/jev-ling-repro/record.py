#!/usr/bin/env python3
"""逐帧录屏：把 dashboard.html 的回放逐帧截图，再用 ffmpeg 合成 mp4。

用法：
    python3 record.py            # 全帧
    python3 record.py 6          # 只跑 6 帧（冒烟测试）

依赖本机 Python 3.10 的 playwright；浏览器已在 ~/Library/Caches/ms-playwright。
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
HTML = OUT / "dashboard.html"
FRAMES_DIR = OUT / "frames"
VIDEO = OUT / "trade-the-news-repro.mp4"

W, H, FPS = 1280, 720, 30


def _tool(name: str) -> str:
    """ffmpeg/ffprobe 可能不在当前进程的 PATH 里，逐一兜底。"""
    for c in (shutil.which(name), f"/opt/homebrew/bin/{name}", f"/usr/local/bin/{name}"):
        if c and Path(c).exists():
            return c
    sys.exit(f"找不到 {name}")


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if not HTML.exists():
        sys.exit(f"缺少 {HTML}，先跑 make_dashboard.mjs")

    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True)

    # 本机 playwright 期望的 chromium 构建号与已下载的不一致（1194 vs 1234），
    # 直接走系统 Chrome 通道，避免再下一个 ~150MB 的浏览器。
    channel = os.environ.get("PLAYWRIGHT_CHANNEL", "chrome")
    t0 = time.time()
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel=channel,
                                        args=["--no-sandbox", "--force-color-profile=srgb"])
        except Exception as e:
            print(f"通道 {channel} 启动失败（{e}），回退到内置 chromium")
            browser = p.chromium.launch(args=["--no-sandbox", "--force-color-profile=srgb"])
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        page.goto(HTML.as_uri())
        page.wait_for_function("() => typeof window.__seek === 'function'")
        total = page.evaluate("() => window.__total")
        n = limit or total
        print(f"总帧数 {total}，本次录制 {n} 帧 @ {FPS}fps ≈ {n / FPS:.1f}s")

        for i in range(n):
            page.evaluate("(i) => window.__seek(i)", i)
            page.screenshot(path=str(FRAMES_DIR / f"f{i:04d}.jpg"), type="jpeg", quality=92)
            if i % 48 == 0:
                print(f"  {i}/{n}  {time.time() - t0:.1f}s")
        browser.close()

    print(f"截图完成 {n} 帧，用时 {time.time() - t0:.1f}s")

    if n < 2:
        print("帧数不足，跳过合成")
        return

    subprocess.run(
        [_tool("ffmpeg"), "-v", "error", "-y", "-framerate", str(FPS),
         "-i", str(FRAMES_DIR / "f%04d.jpg"),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
         "-movflags", "+faststart", str(VIDEO)],
        check=True,
    )
    size = VIDEO.stat().st_size
    dur = subprocess.run(
        [_tool("ffprobe"), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(VIDEO)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    print(f"合成 {VIDEO}  {size / 1024:.0f} KB  时长 {dur}s")

    # 帧序列是纯中间产物（288 张 ≈ 28MB），合成成功后默认清掉；要留就设 KEEP_FRAMES=1
    if os.environ.get("KEEP_FRAMES") != "1":
        shutil.rmtree(FRAMES_DIR)
        print(f"已清理中间帧 {FRAMES_DIR}（KEEP_FRAMES=1 可保留）")


if __name__ == "__main__":
    main()
