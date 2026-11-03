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
