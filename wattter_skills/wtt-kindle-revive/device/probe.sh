#!/bin/sh
# Name: WTT Probe
# Author: WTT
# A read-only device probe, except its receipts under WTT/bootstrap.
set -eu
base=/mnt/us/WTT/bootstrap
mkdir -p "$base"
exec > "$base/probe.log" 2>&1
uid=$(id -u)
serial=$(tr -d '\000\r\n' < /proc/usid)
serial_sha256=$(printf '%s' "$serial" | sha256sum | cut -d ' ' -f 1)
unset serial
firmware=$(sed -n 's/^Kindle \([0-9.]*\).*/\1/p' /mnt/us/system/version.txt)
font=
for f in /usr/java/lib/fonts/CJK.ttf /usr/java/lib/fonts/code2000.ttf /usr/share/fonts/CJK.ttf; do
    if [ -r "$f" ]; then font=$f; break; fi
done
ota_blocked=0
if [ ! -e /usr/bin/otaupd ] && [ -f /usr/bin/otaupd.bck ]; then ota_blocked=1; fi
machine=$(uname -m)
case "$machine" in ''|*[!A-Za-z0-9_.-]*) echo 'invalid machine'; exit 2;; esac
printf '{"ok":true,"probe_kind":"shell_execution_v2","machine":"%s"}\n' "$machine" > "$base/probe.json.tmp"
result=0
mv "$base/probe.json.tmp" "$base/probe.json"
{
    printf 'challenge=@CHALLENGE@\n'
    printf 'serial_sha256=%s\nuid=%s\nfirmware=%s\nfont=%s\nota_blocked=%s\nprobe_exit=%s\n' "$serial_sha256" "$uid" "$firmware" "$font" "$ota_blocked" "$result"
} > "$base/probe.meta.tmp"
mv "$base/probe.meta.tmp" "$base/probe.meta"
sync
echo 'WTT probe finished. Reconnect USB and run bootstrap-check.'
