# ALC897 板载音频

本机 Windows 确认 codec `10EC:0897`，控制器 `8086:7A50`。本次启用 **AppleALC 1.9.8 RELEASE + SimpleHDA 1.0.0 RELEASE**，`alcid=12` 沿用维护者提供的 15.4.1 EFI，作为首测布局。配置和文件校验通过，**Tahoe 下实际播放、前置接口和麦克风仍待用户确认**。

## 准备公开模板

SimpleHDA 的[上游 NOTICE](https://github.com/laobamac/SimpleHDA/blob/v1.0.0/NOTICE.md)保留作者版权，并说明内嵌 AppleHDA 属于苹果专有组件。本仓库不转存这些二进制。公开配置已经启用对应条目，但克隆或解压后必须先运行：

```sh
python3 scripts/prepare_audio.py
python3 scripts/validate.py
```

Windows 可将 `python3` 换为已安装的 `python`。脚本只从[上游正式发布](https://github.com/laobamac/SimpleHDA/releases/tag/v1.0.0)下载固定的 RELEASE ZIP，并校验包大小、包 SHA256 和两个驱动文件的 SHA256。下载地址与校验值在 `audio.lock.json`。它只准备当前 EFI 中的驱动，不修改系统卷、SIP、NVRAM 或固件启动项，不运行安装器。

离线时可用同一个官方压缩包：

```sh
python3 scripts/prepare_audio.py --archive /path/to/SimpleHDA-Tahoe-v1.0.0-RELEASE.zip
```

驱动顺序为 `Lilu -> AppleALC -> SimpleHDA`。保留 `keepsyms=1`；这不会开启跑码。SIP 保持启用，OpenCore 日常日志写盘关闭。HAL 安装包是上游可选组件，此方案先使用未安装 HAL 时的普通 IOAudio 路径。不要与其他 AppleHDA 恢复方案重复加载。

## 实机验证

1. 补齐自己的 SMBIOS，运行配套 OpenCore 1.0.8 的 ocvalidate；先用独立 U 盘验证。
2. 进入 macOS 后在“系统设置 → 声音 → 输出”选择内建或线路输出，先测试后置绿色 3.5mm 接口。
3. 再测前置耳机、麦克风、音量控制和睡眠后的恢复。`alcid=12` 不保证适用于所有同名主板或接线。
4. 若未出现设备，手动记录 `system_profiler SPAudioDataType` 和已加载的 Lilu/AppleALC/SimpleHDA。不要因为更换 layout 后没声音就直接降低 SIP 或做根补丁。

下载后生成的 `EFI/OC/Kexts/SimpleHDA.kext` 被 Git 忽略。公开打包使用 `git archive`，不要把个人身份、手动日志或下载的专有载荷误传到仓库或公开附件。
