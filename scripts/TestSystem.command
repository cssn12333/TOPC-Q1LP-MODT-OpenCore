#!/bin/sh
# User-triggered local diagnostics; no permanent service, preference reset or kernel edits.
set -u
umask 077
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "$(uname -s)" != Darwin ]; then
  echo 'Run from 本目录 in macOS.'; exit 1
fi
if [ "$(id -u)" -eq 0 ]; then
  echo '请正常双击本脚本运行，不要使用 sudo 启动整个脚本。'; exit 1
fi
echo '本次测试：目标蓝牙设备 连接、CPU 短时频率采样、显卡监控数据。'
echo '不会删除配对记录，不修改系统电源设置，不常驻。'
if ! /usr/bin/sudo -v; then exit 1; fi
STAMP=$(date +%Y%m%d-%H%M%S)
OUT="$HERE/Logs/System/$STAMP"
mkdir -p "$OUT"
/usr/bin/sudo /sbin/dmesg >"$OUT/boot-dmesg.txt" 2>&1
/usr/sbin/sysctl kern.boottime kern.bootargs machdep.cpu.brand_string hw.physicalcpu hw.logicalcpu >"$OUT/cpu-identity.txt" 2>&1
/usr/sbin/sysctl -a 2>/dev/null | /usr/bin/grep -E '^machdep.xcpm\.|^machdep.hwp\.|^hw.cpufrequency|^hw.busfrequency' >"$OUT/cpu-power-state.txt"
/usr/bin/pmset -g custom >"$OUT/power-settings.txt" 2>&1
/usr/bin/pmset -g therm >"$OUT/thermal-state.txt" 2>&1
/usr/sbin/system_profiler SPHardwareDataType SPDisplaysDataType SPBluetoothDataType -timeout 30 >"$OUT/hardware-before.txt" 2>&1
for APP in /Applications/Stats.app "$HOME/Applications/Stats.app"; do
  if [ -f "$APP/Contents/Info.plist" ]; then
    printf '%s\n' "$APP" >>"$OUT/stats-version.txt"
    /usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$APP/Contents/Info.plist" >>"$OUT/stats-version.txt" 2>&1
  fi
done
echo '蓝牙：请先完全退出“系统设置”，收起控制中心，让 目标蓝牙设备 进入配对模式。'
echo '耳机请断开与手机/其他电脑的连接；本次先直接连接，不先持续搜索。'
printf '准备好后按回车：'; read -r READY
/bin/sleep 3
if [ -f "$HERE/enco-target.txt" ]; then
  TARGET=$(/bin/cat "$HERE/enco-target.txt")
  echo '正在尝试直接建立耳机连接。若系统询问终端的蓝牙权限，请允许。'
  /usr/bin/osascript -l JavaScript "$HERE/ConnectEnco.js" "$TARGET" >"$OUT/enco-direct-connect.txt" 2>&1
  CONNECT_STATUS=$?
  printf '%s\n' "$CONNECT_STATUS" >"$OUT/enco-command-exit.txt"
  /bin/cat "$OUT/enco-direct-connect.txt"
fi
echo '现在可打开“系统设置 → 蓝牙”，对 目标蓝牙设备 点一次连接，等约20秒。'
echo '如果已连接，播放一段声音，确认耳机实际出声。'
printf '记录结果（能连接/有声音/仍连接失败/权限提示等）：'; read -r BT_RESULT
printf '%s\n' "$BT_RESULT" >"$OUT/bluetooth-result.txt"
/usr/sbin/system_profiler SPBluetoothDataType -timeout 20 >"$OUT/bluetooth-after.txt" 2>&1
/usr/bin/log show --last 5m --style compact --info --debug --predicate 'process == "bluetoothd"' >"$OUT/bluetoothd-log.txt" 2>&1
/usr/bin/sudo /sbin/dmesg >"$OUT/dmesg-after-connect.txt" 2>&1
echo 'CPU：接下来约30秒，依次空闲、单工作线程、多工作线程采样。'
echo '这是短时负载测试，不修改倍频/电压/功耗限制。关闭其他重负载程序后继续。'
printf '按回车开始；输入 s 跳过：'; read -r CPU_CHOICE
PIDS=''
cleanup() {
  for PID in $PIDS; do /bin/kill "$PID" 2>/dev/null || :; done
  for PID in $PIDS; do wait "$PID" 2>/dev/null || :; done
  PIDS=''
}
trap 'cleanup' EXIT
trap 'cleanup; exit 130' INT TERM HUP
if [ "$CPU_CHOICE" != s ] && [ -x /usr/bin/perl ]; then
  # Bound system-tool calls so an unsupported counter cannot leave a load running.
  /usr/bin/sudo /usr/bin/perl -e 'alarm shift; exec @ARGV or die $!;' 5 /usr/bin/powermetrics --help >"$OUT/powermetrics-help.txt" 2>&1
  EXTRA=''
  if /usr/bin/grep -q -- '--show-cpu-frequency' "$OUT/powermetrics-help.txt"; then EXTRA='--show-cpu-frequency'; fi
  for PHASE in idle single multi; do
    COUNT=0
    case "$PHASE" in
      single) COUNT=1;;
      multi) COUNT=$(/usr/sbin/sysctl -n hw.logicalcpu 2>/dev/null || echo 32);;
    esac
    case "$COUNT" in ''|*[!0-9]*) COUNT=1;; esac
    [ "$COUNT" -le 64 ] || COUNT=64
    echo "CPU采样：$PHASE，$COUNT 个工作线程，约10秒。"
    INDEX=0
    while [ "$INDEX" -lt "$COUNT" ]; do
      /usr/bin/yes >/dev/null &
      PIDS="$PIDS $!"
      INDEX=$((INDEX + 1))
    done
    /usr/bin/sudo /usr/bin/perl -e 'alarm shift; exec @ARGV or die $!;' 15 /usr/bin/powermetrics --samplers cpu_power -i 1000 -n 10 $EXTRA >"$OUT/cpu-${PHASE}.txt" 2>&1
    CPU_STATUS=$?
    cleanup
    printf '%s %s\n' "$PHASE" "$CPU_STATUS" >>"$OUT/cpu-command-status.txt"
    if [ "$CPU_STATUS" -ne 0 ]; then
      echo '系统采样接口不支持本次参数，已停止负载并保留错误日志。'
      break
    fi
  done
fi
/usr/bin/pmset -g therm >"$OUT/thermal-after.txt" 2>&1
/usr/sbin/ioreg -l -w 0 -p IOService >"$OUT/ioreg.txt" 2>&1
/usr/sbin/ioreg -a -r -c IOAccelerator >"$OUT/gpu-accelerators.plist" 2>"$OUT/gpu-accelerators-errors.txt"
/usr/bin/kmutil showloaded >"$OUT/kexts.txt" 2>&1
if [ -f "$HERE/../EFI/OC/config.plist" ]; then
  /bin/cp "$HERE/../EFI/OC/config.plist" "$OUT/adjacent-config-reference.plist"
fi
echo "采集完成：$OUT"
echo '可以返回Windows，告诉我耳机是否连接/出声，以及Stats显示情况。'
printf '按回车关闭：'; read -r DONE
