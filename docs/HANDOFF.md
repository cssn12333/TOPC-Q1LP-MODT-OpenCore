# macOS排查交接

更新2026-11-21，目标Tahoe26.4（25E246 / 25G342）；所有原始日志和机器身份不在GitHub。

## 已知可用基线

OpenCore1.0.8 RELEASE，Lilu1.7.2，CPUFriend1.3.0 + CPUFriendDataProvider（`MacPro7,1` 改 `hwp=off`），WhateverGreen1.7.1，MacPro7,1，CPUID A0655，ProvideCurrentCpuInfo=true，AppleXcpmCfgLock=true。
RX6800XT使用agdpmod=pikera；核显BIOS关闭。SecureBootModel Disabled，但SIP保持启用，未做根补丁。
蓝牙保留实测可用的FW2.5.2 DEBUG + IntelBTPatcher2.5.2 DEBUG + BlueToolFixup2.7.2。
DEBUG是组件构建类型，不等于屏幕跑码；正常EFI已去除-v/临时调试参数/DebugEnhancer，并使用RELEASE OpenCore。
不要无依据一起升级/更换全部功能驱动。无线、有线、USB共享、板载音频播放、ENCO X3声音和CPU正常睿频已有用户/实机确认。

## CPU睿频排查结果（2026-11-21 已解决）

根因已实机定位并经XNU内核反汇编与指令周期测频双重确认：
- `MacPro7,1` 系统电源表 `Mac-27AD2F918AE68F61.plist` 默认设置 `hwp=on`。
- Intel 12/13/14代 P-Core 的 HWP 缩放单位为 `78.741 MHz/单位`（`HYBRID_SCALING_FACTOR_ADL`），而 macOS XNU 按 10 代 `100 MHz/单位` 写入上限 `50`（和低档 `20`），导致 P-Core 0~3 实际被压在 `50 × 78.741 ≈ 3.88~3.90 GHz`（最高封顶 4.0 GHz）、P-Core 4~7 在 `request=20` 时被压在 `1.50 GHz`；E-Core 因 1:1 缩放表现为 2.0 GHz。
- XNU `_xcpm_bootstrap` 对 Comet Lake 伪装（`0xA5`）默认不开启 HWP，仅在读取 `FrequencyVectors` 中 `hwp=on` 时启用。
- 加入 `CPUFriend.kext` 1.3.0 RELEASE（原生支持 `KernelVersion::Tahoe`）和 `CPUFriendDataProvider.kext`（仅将 `hwp` 改为 `off`）后，XCPM 回退至传统 `IA32_PERF_CTL` 1:1 倍频控制。

实机复测前后对比（默认 BIOS 固件 `MSR_TURBO_RATIO_LIMIT=0x2C2C2E2E30303232`）：
- 修复前（`hwp=on`）：单核 P-Core 实测最高 `3.88 GHz`，16线程负载 P0~P3 `3.86~3.90 GHz`、P4~P7 `1.50 GHz`、E 核 `2.00 GHz`，整包 `58W`。
- 修复后（`hwp=off`）：单核 P-Core 指令周期实测 `4.72 GHz`、`PowerLog` 峰值 `4.81~5.00 GHz`；16线程负载下全部 8 个 P-Core 达 `4.36~4.40 GHz`（满额 44x 全核睿频）、E 核达 `3.67 GHz`，整包瞬时释放 `96W`（温度 `44°C`）。
- 更高目标倍频（如 BIOS 已测试稳定的 P=5.2 GHz / E=4.0 GHz 与自定义功耗墙）应直接在主板 BIOS 中设定：常规 OpenCore EFI 与 `CPUFriend` 只能按固件 `MSR_TURBO_RATIO_LIMIT` 上限调频，不能直接软超频；也不建议用自定义 UEFI `.efi` 驱动在引导阶段硬写超频 MSR（易被 `OC_LOCK` 阻断卡死，且缺少核心电压/防掉压 LLC/电流墙协同）。BIOS 调整后，macOS XCPM 频率矢量最高档 `TURBO_PCT=100` 会自动跟随新上限，无需再改 EFI 或关闭 SIP。
- 实测调度与待机策略：ACPI 逻辑核顺序为 `core 0~15`（8 个 P-Core）在前、`core 16~31`（16 个 E-Core）在后，macOS 低编号核心优先聚集（Low-index packing）策略天然将轻载单核任务调度在 P0~P3（`core 0~7`），16 个 E-Core 轻载基本休眠；`MacPro7,1` 工作站电源表（`2000→2500→3000→3500→100% TURBO`，6ms 冲顶、100ms 粘滞、`pcps_mode=0`）为典型的 Race-to-Idle 激进单核响应策略，1.5% 轻载待机实测约 `55~66W / 44~48°C`。
- macOS 仍上报 32 物理/32 逻辑、HT Disabled；`CpuTopologyRebuild` v2.0.2 在 Tahoe 26 存在调度崩溃风险，继续不加载。

## 隔空播放（AirPlay）与隔空投送（AirDrop）边界（2026-11-21 记录）

- **AirDrop（隔空投送文件）**：强依赖 AWDL，当前 Intel AX200 + `AirportItlwm` 驱动不支持。
- **AirPlay（Apple Music 隔空播放）**：实测 `fairplayd` 0 报错，非 DRM 阻断；由于无 `awdl0` 点对点兜底，发送端完全依赖干净的同网段局域网 TCP + mDNS。实机日志抓到的发送端超时（`AirPlayXPCHelper` `-6722 kTimeoutErr`）系有线/无线双网卡指向不同网关路由冲突、叠加代理 TUN 模式未排除局域网及 IPv6 ULA（`fc00::/7`、`fe80::/10`）所致；保持与目标设备同路由单网卡并在 TUN 中排除局域网网段即可规避。

## 显卡下一步

Stats字段缺失应在macOS端排查：需要当时的IORegistry、AMD驱动节点和Stats设备选择。Windows可以验证硬件性能和温度，但不能代替macOS的驱动节点采样。

系统信息确认RX6800XT 16GB、PCIe x16、Metal3，AMDMTLGFX10和IOAccelerator存在。
已有IOReg PerformanceStatistics：Temperature(C)=45、Total Power(W)=21、Memory Clock(MHz)=1984，Core Clock(MHz)=0。
Stats3.0.24仍缺部分显示；不要先归咎显卡未驱动。下一步核对Stats枚举的IOAccelerator/IOGPU、字段类型、选中设备和空闲/负载差异。
特别留意Tahoe中的IOServiceCompatibility假兼容GPU节点，避免监控工具只读取到兼容节点。
未加入SMCRadeonSensors，不承诺功率/风扇/频率全部传感器接口都可用。

## 板载音频与启动迁移

ALC897已配置AppleALC1.9.8 + SimpleHDA1.0.0 RELEASE、alcid=12，SIP保持启用，正常启动日志与跑码关闭。2026-11-03用户确认板载声卡可以使用，基本播放已验证；前置、麦克风、睡眠恢复尚未分别确认。公开包必须先运行 `python3 scripts/prepare_audio.py`。参见[AUDIO.md](AUDIO.md)。

内置SATA硬盘与U盘曾只读核对249个工作文件完全相同，用户仍报告硬盘经过同样OC菜单、选Macintosh后在苹果进度条后黑屏。固件存在原生Mac OS X旧入口，本机New Boot Entry才明确指向该盘EFI/BOOT/BOOTx64.efi，但不能仅凭旧入口断定这次黑屏原因。随后音频配置增加4个驱动文件，当前个人EFI为253个工作文件；这次新增音频不代表前述黑屏已解决。

## 蓝牙历史

AX200在HS13，FirmwareLoaded=true曾不足以证明本次重新上传。断电冷启动后完整日志确认ibt-20-1-3.sfi/DDC上传与设备重启成功。
早期无法扫描；后来可发现ENCO X3但Classic ACL/SDP连接返回712（HCI0x0C Command Disallowed）。
发现连接与Inquiry Cancel的时序可能相关，但未证明最终根因，也未修改HCI内核时序。
随后系统原生配对成功并出现AVDTP OPEN->STREAMING，有声音。直连JXA辅助脚本当次因Windows CRLF地址校验失败，并非成功原因；现已trim修正但该API流程未实机验证。
掉线后的持续重连、麦克风、其他设备及睡眠后的蓝牙仍需复测。AirDrop/AWDL仍不支持。

## 在macOS继续

把仓库、个人EFI备份和这份交接带过去。官方桌面客户端下载页当前标注macOS Apple Silicon，本机Intel平台不要假设可安装该桌面包；先用macOS浏览器使用ChatGPT并提供采集日志。若使用Codex CLI，按官方文档核对本机架构对应安装方式与授权。Windows聊天的本机文件权限不会自动转移。
官方参考：https://learn.chatgpt.com/docs/app ，https://learn.chatgpt.com/docs/codex/cli 。
在macOS终端进入仓库目录后，运行 `sh scripts/TestSystem.command --performance-only` 手动采集CPU/GPU，跳过已完成的蓝牙连接测试。可选择跳过CPU负载；脚本记录显卡节点的前后快照，在提示时手动运行已有图形程序。通过Git克隆时脚本也保留可执行权限；ZIP解压工具若丢失权限，仍可使用上述sh命令。脚本对powermetrics设置超时，不安装后台服务；这些新流程仍待实机验证，不承诺该ES支持全部采样接口。
日志保存scripts/Logs（被Git忽略）；公开前删除序列号、UUID、MAC、SSID、个人路径。诊断失败应保留错误，不把缺数据当成正常结果。
