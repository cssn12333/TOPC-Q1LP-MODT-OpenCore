# 已知限制

- 当前为单台设备、单套固件的工作记录，长期稳定性、冷/热启动和睡眠压力测试不完整。
- 当前AirportItlwm Tahoe alpha不支持AWDL/AirDrop/WPA3-only/强制PMF/MLO；HE默认关闭。
- AX200蓝牙音频成功不等于全部BLE HID、通话、Handoff、自动解锁已验证。
- USB地图按15端口限制取舍，HS01/02对应插口没有SuperSpeed；USB-C双面未完整验证。
- 有线采用本地局部重链接实验补丁，非Mieze官方发行；XID未现场直接测量。
- CPU 睿频锁 4.0 GHz 已通过 `CPUFriend` 1.3.0 + `CPUFriendDataProvider`（`hwp=off`）修复并实测恢复全额睿频；混合架构拓扑显示（32 物理核 / HT Disabled）、Stats 显卡数据显示、当前 Tahoe 睡眠仍待继续排查。
- ALC897使用AppleALC+SimpleHDA、alcid=12，本机基本播放已获用户确认；前置、麦克风与睡眠恢复尚未分别验证。公开包必须先运行prepare_audio.py补齐驱动。
- 内置硬盘与U盘曾核对启动文件完全一致，但用户报告硬盘启动在苹果进度条后黑屏；根因未确定。避免把旧固件入口或显卡初始化当作已确认原因。
- 公开模板留空SMBIOS身份，并去掉个性化CPU名称和fallbackMAC，不能直接当成作者已验证的个人EFI启动。
- ModernView由维护者提供本地素材，源作者/独立许可未附带；不把它声明为本仓库MIT作品。见THIRD_PARTY。
