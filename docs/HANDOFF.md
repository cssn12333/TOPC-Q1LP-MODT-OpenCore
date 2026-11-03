# macOS排查交接

更新2026-11-03，目标Tahoe26.4 25E246；当前从Windows整理，所有原始日志和机器身份不在GitHub。

## 已知可用基线

OpenCore1.0.8 RELEASE，Lilu1.7.2，WhateverGreen1.7.1，MacPro7,1，CPUID A0655，ProvideCurrentCpuInfo=true，AppleXcpmCfgLock=true。
RX6800XT使用agdpmod=pikera；核显BIOS关闭。SecureBootModel Disabled，但SIP保持启用，未做根补丁。
蓝牙保留实测可用的FW2.5.2 DEBUG + IntelBTPatcher2.5.2 DEBUG + BlueToolFixup2.7.2。
DEBUG是组件构建类型，不等于屏幕跑码；正常EFI已去除-v/临时调试参数/DebugEnhancer，并使用RELEASE OpenCore。
不要无依据一起升级/更换全部功能驱动。无线、有线、USB共享和ENCO X3声音已有用户确认。

## CPU下一步

主要在macOS验证XCPM和实际频率表现，同时保留Windows下相同单/多线程负载的对照。如果Windows也受限，先检查BIOS、功耗和温度；如果Windows正常而macOS异常，再聚焦macOS电源管理和工具读数。两边都应先确认工具支持这颗ES混合架构，不把平均频率当成最高P核频率。

用户在Intel Power Gadget看到约4.0GHz。实际Q1LP为ES，24C32T；不能用显示名14900KS的零售规格判断。
旧固件读取MSR_TURBO_RATIO_LIMIT=0x2C2C2E2E30303232；macOS XCPM mode=1，hard/soft最高允许倍频50。
这些只说明允许上限，不证明真实核心达到5GHz。单/多线程采样未完成，不能宣布解决或锁频。
macOS上报32物理/32逻辑、HT Disabled，与真实24C32T不同，是待核对的混合架构拓扑显示；CpuTopologyRebuild当前不加载。
先用powermetrics/现有Power Gadget记录空闲、单工作线程、多工作线程频率、温度、功耗和限制原因；将P/E核心频率分开理解。
不要仅根据1.7GHz静态Processor Speed/sysctl值、平均频率、或错误拓扑改busratio/功耗。CPUFriend尚未加入。

## 显卡下一步

Stats字段缺失应在macOS端排查：需要当时的IORegistry、AMD驱动节点和Stats设备选择。Windows可以验证硬件性能和温度，但不能代替macOS的驱动节点采样。

系统信息确认RX6800XT 16GB、PCIe x16、Metal3，AMDMTLGFX10和IOAccelerator存在。
已有IOReg PerformanceStatistics：Temperature(C)=45、Total Power(W)=21、Memory Clock(MHz)=1984，Core Clock(MHz)=0。
Stats3.0.24仍缺部分显示；不要先归咎显卡未驱动。下一步核对Stats枚举的IOAccelerator/IOGPU、字段类型、选中设备和空闲/负载差异。
特别留意Tahoe中的IOServiceCompatibility假兼容GPU节点，避免监控工具只读取到兼容节点。
未加入SMCRadeonSensors，不承诺功率/风扇/频率全部传感器接口都可用。

## 板载音频与启动迁移

ALC897已配置AppleALC1.9.8 + SimpleHDA1.0.0 RELEASE、alcid=12，SIP保持启用，正常启动日志与跑码关闭。实际出声尚未确认；公开包必须先运行 `python3 scripts/prepare_audio.py`。参见[AUDIO.md](AUDIO.md)。

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
