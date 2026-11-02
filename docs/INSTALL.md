# 安装和迁移

这不是通用EFI，也不包含macOS安装镜像。系统版本限定Darwin25.x；不要直接用于Sequoia或其他CPU。
公开模板身份留空是有意设置，ocvalidate结构通过不等于可直接启动或iServices已配置。

## 使用前

- 核对TOPC Q1LP MODT的具体BIOS、PCI/USB设备ID；本机CPUID B0671，CPU spoof为A0655。
- 保持核显关闭；当前ACPI路径为PC00.LPCB，PLUG-ALT覆盖MADT UID 0–31。
- 保留UEFI启动、AHCI、合适的CFG Lock/VT-d设置，参考本机已有稳定BIOS，不盲刷其他主板固件。
- 生成自己的MacPro7,1 SMBIOS。ROM为你自己固定网卡地址的6字节值；不要复用他人身份。
- 本项目没有修改BIOS、NIC固件、WindowsBCD，也没有OCLP根补丁、AMFI放行或SIP关闭。

先复制仓库到私有工作目录，再改身份，避免将个人值提交回Git。配置示例（替换所有占位符）：
```
python scripts/configure_identity.py --config /path/to/private/EFI/OC/config.plist --serial YOUR_SERIAL --mlb YOUR_MLB --uuid YOUR_UUID --rom YOUR_12_HEX_ROM
```
需要网卡fallback时额外使用`--ethernet-mac YOUR_OWN_MAC`，格式为冒号分隔六组十六进制。

## 启动与恢复

U盘根目录为EFI/BOOT/BOOTx64.efi和EFI/OC/config.plist。先通过主板UEFI菜单选U盘。
正常安装按安装阶段选择目标；完成后选择Macintosh。不要因常规安装重启、Preboot非系统卷Not Found就直接抹盘。
此前模板迁移阶段曾正常完成并主动重启；反复重装不是本项目的修复前提。
新版不需要为去掉-v而Reset NVRAM：配置的Delete包含boot-args。
若需诊断，在自己的工作副本添加-v keepsyms=1 debug=0x100并保留原版；使用匹配版本的DEBUG OpenCore。
菜单空格显示恢复与Reset NVRAM。Ctrl+Enter保存默认项，单独Enter仅启动一次。
