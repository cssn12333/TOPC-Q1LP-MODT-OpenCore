# 版本记录

## 2026-11-02 · 初始公开整理

- 从已成功进桌面的Tahoe26.4配置逐项恢复网络。
- 使用laobamac原生AirportItlwm，无需HeliPort；AX200蓝牙固件升级并确认耳机配对和声音。
- 完成USB实测15通道取舍和安卓RNDIS共享；加入RTL8168M条件识别实验补丁并实测有线联网。
- 使用OpenCore1.0.8 RELEASE、ModernView主题和苹果正常启动画面。
- 精简禁用组件；公开包清空SMBIOS及个人MAC，增加源码、复现、状态边界和macOS交接。

## 2026-11-03

- 完成公开仓库与下载发布，补全macOS诊断脚本执行权限和明确运行命令。
- EFI二进制与实机功能配置没有变化。

## 2026-11-03 音频候选与交接更新

- 配置ALC897：AppleALC 1.9.8 RELEASE + SimpleHDA 1.0.0 RELEASE、alcid=12，实际出声待实测。
- 通过固定URL和SHA256直接获取SimpleHDA，不转存其专有载荷；CI先准备依赖再校验。
- 关闭OpenCore panic转存，保留SIP和正常图形引导。
- 补充CPU/显卡的macOS采集流程，以及Windows负载对照和硬盘启动黑屏未定的交接。

## 2026-11-03 板载声卡实测确认

- 用户确认本次AppleALC + SimpleHDA方案的板载声卡可以使用，更新为基本播放已验证。
- 前置接口、麦克风、睡眠恢复、CPU睿频、Stats显卡字段和此前硬盘黑屏反馈继续分别跟踪。

## 2026-11-21 修复 CPU 睿频锁 4.0 GHz（CPUFriend hwp=off）

- 定位根因：`MacPro7,1` 系统频率矢量默认开启 `hwp=on`，而 Intel 12/13/14 代 P-Core 的 HWP 性能单位为 `78.741 MHz/单位`（非 10 代的 `100 MHz/单位`），导致 macOS XCPM 写入上限 `50` 时 P 核实际被压在 `50 × 78.741 ≈ 3.9~4.0 GHz`（且请求 `20` 时 P 核 4~7 仅跑 `1.50 GHz`）。
- 解决方案：引入 `CPUFriend.kext` 1.3.0 RELEASE（原生支持 Tahoe / macOS 26）与定制 `CPUFriendDataProvider.kext`（仅将 `Mac-27AD2F918AE68F61.plist` 中的 `hwp` 由 `on` 改为 `off`），使 Comet Lake 伪装（`0xA5`）下的 XCPM 回退至 1:1 倍频的传统 `IA32_PERF_CTL` 调频。
- 实机复测确认：
  - 单核 P-Core 真实指令周期频率从 `3.85~3.88 GHz` 提升至 `4.72~4.81 GHz`（`PowerLog` 上限达 `5000 MHz`）。
  - 16 线程负载下全部 8 个 P-Core 均达 `4.36~4.40 GHz`（原 P4~P7 仅 `1.50 GHz`），E-Core 达 `3.67 GHz`，整包功耗释放至 `96W`（温度 `44°C`）。
  - 更高目标倍频（例如 BIOS 已验证稳定的 P 核 5.2 GHz / E 核 4.0 GHz）直接在主板 BIOS 设定倍频与功耗墙，macOS XCPM 会按 `TURBO_PCT=100` 自动跟随，无需再修改 EFI 或关闭 SIP。
- 未加入 `CpuTopologyRebuild.kext`（v2.0.2 在 Tahoe 26 存在调度崩溃风险）。
