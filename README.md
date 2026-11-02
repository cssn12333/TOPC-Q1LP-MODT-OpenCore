# TOPC Q1LP MODT · OpenCore · macOS Tahoe

TOPC Q1LP MODT 平台、微星魔龙 Radeon RX 6800 XT、Intel AX200 的实机 EFI 与排障交接。
维护者：cssn12333。记录日期：2026-11-02；目标系统 macOS Tahoe 26.4（25E246），OpenCore 1.0.8 RELEASE。

**公开 EFI 是去除机器身份的模板，配置自己的 SMBIOS 后才能使用。** 本机成功不代表所有同名板卡、BIOS或ES批次通用；未宣称完美、全功能或长期稳定。

## 硬件和条件

| 部件 | 本机配置 |
|---|---|
| 主板/平台 | TOPC Q1LP MODT；固件上报 Z790M GAMING WIFI D4 / RaptorLakeHX；AMI Leo-Patch1.5 |
| CPU | Q1LP ES，原始 CPUID B0671，24核32线程；不是已确认的零售14900KS |
| 显卡 | MSI 微星魔龙 RX 6800 XT 16GB，1002:73BF，子系统39511462 |
| Wi-Fi / 蓝牙 | Intel AX200，PCI 8086:2723；蓝牙USB 8087:0029，在HS13 |
| 有线 | PCI 10EC:8168 / 子系统012310EC / REV2B；高度疑似RTL8168M，内部XID未实读 |
| 存储 | macOS使用SATA；独立Windows硬盘，本项目不改Windows EFI/BCD |

BIOS核显保持关闭，这是本机既有睡眠条件。不要把兼容CPUID A0655或自定义显示名当作真实CPU型号。

## 实测状态

| 功能 | 结论 |
|---|---|
| 进入桌面 / AMD Metal | 已进入桌面；RX6800XT识别16GB和Metal3 |
| AX200 Wi-Fi | 系统原生Wi-Fi界面可联网，无HeliPort常驻 |
| 有线网络 | 本地RTL8168M条件分支补丁后，用户实测联网成功 |
| 蓝牙 | OPPO Enco X3配对并播放声音；日志出现AVDTP STREAMING |
| 安卓USB共享 | Xiaomi 15 Pro实测正常，HoRNDIS |
| USB映射 | 实测选择15条逻辑通道；全部已测USB2口保留，部分高速通道取舍 |
| 睡眠/唤醒 | 旧15.4.1在关核显时可用；当前Tahoe长期/反复测试未完成 |
| CPU最高睿频 | XCPM已加载，上限参数50倍频；未完成单/多线程负载采样，未证实达到5GHz |
| Stats显卡数据显示 | 仍待排查；底层曾输出温度、功耗和显存频率，Stats3.0.24显示不完整 |
| AirDrop / AWDL | 当前AirportItlwm分支不支持；蓝牙可用不等于完整连续互通 |
| 板载ALC897模拟声卡 | 未启用；Tahoe音频方案未处理 |

## 使用

1. 阅读[安装与迁移](docs/INSTALL.md)和[已知问题](docs/KNOWN-ISSUES.md)。备份现有EFI，用独立U盘先测试。
2. 为MacPro7,1生成**自己的**SystemSerialNumber、MLB、SystemUUID、ROM；可使用[GenSMBIOS](https://github.com/corpnewt/GenSMBIOS)。填写`EFI/OC/config.plist`，或运行`scripts/configure_identity.py --help`。
3. 按自己硬件验证USB映射与ACPI路径。不要将本机地图当作通用USB补丁。
4. 使用OpenCore1.0.8配套ocvalidate检查配置，再复制EFI到U盘。保留可启动的Windows入口与旧EFI。
5. 正常版关闭-v，OpenCanopy使用ModernView主题，macOS显示苹果标志和进度条；菜单手动选择，空格显示辅助项。

根目录EFI仅保留启用的kext及启动资源。旧itlwm、CpuTopologyRebuild、DebugEnhancer、调试日志和个人备份不进入公开仓库。
个人工作版曾用14900KS作为显示名；公开版去掉该命名，保留真实ES说明。
公开版同时移除作者专属网卡fallbackMAC；正常读取网卡地址，若需要fallback必须填自己的地址。

## 目录

- `EFI/`：清理并脱敏的正常引导模板。
- `acpi/`：对应DSL源文件。
- `patches/rtl8168m/`、`vendor/`：自定义网卡修改、完整固定版本源代码和原始驱动二进制。
- `scripts/`：身份配置、SDK准备、校验及macOS一次性诊断。
- `docs/HANDOFF.md`：继续排查CPU/GPU的交接；`docs/USB.md`为映射取舍。
- `docs/ETHERNET.md`：网卡补丁原理、边界和复现步骤。
- `THIRD_PARTY.md`、`licenses/`：组件来源与各自许可证；仓库自有文档/脚本许可不替代上游许可。

详细来源见[第三方组件](THIRD_PARTY.md)。请勿上传个人EFI、日志、序列号或MAC地址到Issue。
