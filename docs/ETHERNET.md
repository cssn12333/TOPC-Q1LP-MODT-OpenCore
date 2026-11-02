# 有线网卡条件补丁

硬件ID10EC:8168、SUBSYS012310EC、REV2B无法唯一证明芯片型号。结合Linux报告高度疑似RTL8168M；本机内部TxConfig/XID尚未直接读取。
Mieze固定源版本a3dad34ed4f1e72805ce42f6d506f6917fdf79a0对应二进制CFBundleVersion3.0.4（发行包V3.0.0）。

原识别函数不认识6c0。Linux上游[39f59c72ad3a](https://github.com/torvalds/linux/commit/39f59c72ad3a1eaab9a60f0671bc94d2bc826d21)将RTL8168M按H2（541，方法30）处理。本地仅加入以下条件：
```cpp
if ((val32 & 0x7cf00000U) == 0x6c000000U) {
    tp->mcfg = CFG_METHOD_30;
    tp->efuse_ver = EFUSE_SUPPORT_V3;
    return;
}
```
其余XID沿用原识别分支。不是将所有8168设备强行识别成H系列。

## 实现与边界

Windows LLVM20.1.8的ld64.lld不能完整链接-kext，因此不是完整重编译链接驱动。
对固定二进制中的一个1202字节识别函数，从固定上游源码重新编译并局部重链接，修正IOLog外部重定位，保留其余布局和代码。
移除修改后失效的Mach-O签名命令/CodeResources，赋予新UUID244BD8AD-D5EB-7E38-733A-24238A09FC98。
原二进制SHA256 a9a99d105518bf2e1905321e35c68d127bb0414bca9ec0d40ad50cc43b55ef16。
补丁SHA256 f58b8660a5b6eacb0265c161b72ece99822d98fe28b84463860b8187a70e8b76。
2560组差分模拟检查结构写入、栈、被调用者保存寄存器：2556非目标输入保持，4个目标掩码变体按H2返回。
此后用户实际确认网口可联网；不代表所有PHY、EEE、睡眠唤醒或长期流量测试通过。
保留disableASPM=true、EEE/TSO/CSO6禁用的兼容设置，尚无证据证明每一项都必要。
作者机器的fallbackMAC已从公开包删除；如硬件读址异常，只能填自己的MAC。

## 重现

需要Python3、LLVM20.1.8（CXX可指向clang++），以及固定MacKernelSDK。不提供系统级驱动安装或BIOS写入脚本。
```
python -m pip install -r requirements-build.txt
python scripts/prepare_driver_sdk.py
python patches/rtl8168m/compile.py
python patches/rtl8168m/link_and_test.py
```
输出位于.build/rtl8168m，模拟报告在.build中。先比对上述SHA256；不要用别的原始二进制强行补丁。
只有确认ABI、重定位、签名状态和差分检查通过才在备用U盘验证。完整上游驱动源码在vendor/RTL8111-driver-source。
