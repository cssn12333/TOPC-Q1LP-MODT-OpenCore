# 组件、来源及许可

组件原始许可证在licenses中；本文件不是额外授权。GPL网卡完整对应源代码与修改在vendor/和patches/。

| 组件 | 版本/来源 |
|---|---|
| OpenCore / OpenCanopy / OpenRuntime | [acidanthera/OpenCorePkg](https://github.com/acidanthera/OpenCorePkg)，1.0.8 RELEASE |
| HfsPlus、字体、标签 | [acidanthera/OcBinaryData](https://github.com/acidanthera/OcBinaryData) |
| Lilu | [acidanthera/Lilu](https://github.com/acidanthera/Lilu)，1.7.2 |
| WhateverGreen | [acidanthera/WhateverGreen](https://github.com/acidanthera/WhateverGreen)，1.7.1 |
| VirtualSMC / SMCProcessor | [acidanthera/VirtualSMC](https://github.com/acidanthera/VirtualSMC)，1.3.8 |
| RestrictEvents | [acidanthera/RestrictEvents](https://github.com/acidanthera/RestrictEvents)，1.1.6 |
| AirportItlwm | [laobamac/itlwm](https://github.com/laobamac/itlwm)，Tahoe2.4.0 alpha7204c69 |
| IntelBluetoothFirmware / IntelBTPatcher | [lshbluesky/IntelBluetoothFirmware](https://github.com/lshbluesky/IntelBluetoothFirmware)，2.5.2 DEBUG；Intel固件另遵循其firmware license |
| BlueToolFixup | [acidanthera/BrcmPatchRAM](https://github.com/acidanthera/BrcmPatchRAM)，2.7.2 |
| RealtekRTL8111 | [Mieze/RTL8111_driver_for_OS_X](https://github.com/Mieze/RTL8111_driver_for_OS_X)，固定a3dad34；本地6c0分支，非官方包 |
| USBToolBox / UTBMap | [USBToolBox/kext](https://github.com/USBToolBox/kext)，1.2.0；本机地图 |
| AppleALC | [acidanthera/AppleALC](https://github.com/acidanthera/AppleALC/releases/tag/1.9.8)，1.9.8 RELEASE；BSD许可见licenses |
| SimpleHDA | [laobamac/SimpleHDA](https://github.com/laobamac/SimpleHDA/releases/tag/v1.0.0)，1.0.0 RELEASE；不转存二进制，由prepare_audio.py按audio.lock.json从上游获取 |
| HoRNDIS | [iKeramat/HoRNDIS](https://github.com/iKeramat/HoRNDIS/releases/tag/mac-15.5)，mac-15.5发布包，内部版本9.2 |
| AppleMCEReporterDisabler | codeless阻止加载AppleIntelMCEReporter；Info.plist可直接审阅，无可执行文件 |
| ModernView / MeadowAppleSet | 用户提供的本地主题素材；本仓库对默认Apple/Windows图标做文件别名选择，源作者/许可未附，不重新许可 |

完整启用组件版本与二进制SHA256见manifest.json。未将macOS安装程序、苹果系统驱动或OCLP根补丁放入本仓库。

固定Wi-Fi、蓝牙、BlueToolFixup、HoRNDIS源码包URL和SHA256见sources.lock.json；另提供Sources-Public压缩包。USBToolBox/OcBinaryData根目录未提供统一许可证，不把它们重新许可为MIT；原始来源和版权继续保留。

SimpleHDA上游保留作者版权，内嵌AppleHDA适用苹果条款；见[上游NOTICE](https://github.com/laobamac/SimpleHDA/blob/v1.0.0/NOTICE.md)。下载后的文件被Git忽略，不包含在公开git archive中，不受本仓库MIT许可覆盖。
