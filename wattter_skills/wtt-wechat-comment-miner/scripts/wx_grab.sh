#!/bin/zsh
# 单屏采集：wx_grab.sh <屏号> <窗口ID>（截图 + OCR + 追加汇总到 /tmp/wx_full_all.txt）
N="$1"
WID="${2:?用法: wx_grab.sh <屏号> <窗口ID>；窗口 ID 每次会话都变，先用阶段 0 探测}"
OCR="$(dirname "$0")/wx_ocr"
[ -x "$OCR" ] || { echo "OCR_MISSING: 先编译 swiftc $(dirname "$0")/wx_ocr.swift -o $OCR"; exit 1; }
OUT="/tmp/wx_full"
IMG="${OUT}_${N}.png"
screencapture -x -l "$WID" -t png "$IMG" 2>/dev/null
[ -f "$IMG" ] || { echo "SCREENSHOT_FAIL"; exit 1; }
"$OCR" "$IMG" > "${OUT}_${N}.txt"
echo "===== SCREEN $N =====" >> "${OUT}_all.txt"
cat "${OUT}_${N}.txt" >> "${OUT}_all.txt"
echo "SCR $N md5=$(md5 -q "$IMG") lines=$(wc -l < "${OUT}_${N}.txt")"
