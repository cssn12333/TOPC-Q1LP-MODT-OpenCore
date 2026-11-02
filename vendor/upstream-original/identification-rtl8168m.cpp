#include "RealtekRTL8111.hpp"
void rtl8168_get_mac_version(struct rtl8168_private *tp, void __iomem *ioaddr)
{
        u32 reg,val32;
        u32 ICVerID;

        val32 = RTL_R32(TxConfig);
        reg = val32 & 0x7c800000;
        ICVerID = val32 & 0x00700000;


        // Experimental backport of Linux commit 39f59c72ad3a:
        // XID 6c0 (RTL8168M) follows RTL8168H-2 (541), method 30.
        // All other identifiers follow the original Mieze implementation.
        if ((val32 & 0x7cf00000U) == 0x6c000000U) {
                tp->mcfg = CFG_METHOD_30;
                tp->efuse_ver = EFUSE_SUPPORT_V3;
                return;
        }

        switch (reg) {
        case 0x30000000:
                tp->mcfg = CFG_METHOD_1;
                tp->efuse_ver = EFUSE_NOT_SUPPORT;
                break;
        case 0x38000000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_2;
                } else if (ICVerID == 0x00500000) {
                        tp->mcfg = CFG_METHOD_3;
                } else {
                        tp->mcfg = CFG_METHOD_3;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_NOT_SUPPORT;
                break;
        case 0x3C000000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_4;
                } else if (ICVerID == 0x00200000) {
                        tp->mcfg = CFG_METHOD_5;
                } else if (ICVerID == 0x00400000) {
                        tp->mcfg = CFG_METHOD_6;
                } else {
                        tp->mcfg = CFG_METHOD_6;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_NOT_SUPPORT;
                break;
        case 0x3C800000:
                if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_7;
                } else if (ICVerID == 0x00300000) {
                        tp->mcfg = CFG_METHOD_8;
                } else {
                        tp->mcfg = CFG_METHOD_8;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_NOT_SUPPORT;
                break;
        case 0x28000000:
                if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_9;
                } else if (ICVerID == 0x00300000) {
                        tp->mcfg = CFG_METHOD_10;
                } else {
                        tp->mcfg = CFG_METHOD_10;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_SUPPORT_V1;
                break;
        case 0x28800000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_11;
                } else if (ICVerID == 0x00200000) {
                        tp->mcfg = CFG_METHOD_12;
                        RTL_W32(0xD0, RTL_R32(0xD0) | 0x00020000);
                } else if (ICVerID == 0x00300000) {
                        tp->mcfg = CFG_METHOD_13;
                } else {
                        tp->mcfg = CFG_METHOD_13;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_SUPPORT_V1;
                break;
        case 0x2C000000:
                if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_14;
                } else if (ICVerID == 0x00200000) {
                        tp->mcfg = CFG_METHOD_15;
                } else {
                        tp->mcfg = CFG_METHOD_15;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_SUPPORT_V2;
                break;
        case 0x2C800000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_16;
                } else if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_17;
                } else {
                        tp->mcfg = CFG_METHOD_17;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_SUPPORT_V3;
                break;
        case 0x48000000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_18;
                } else if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_19;
                } else {
                        tp->mcfg = CFG_METHOD_19;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_SUPPORT_V3;
                break;
        case 0x48800000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_20;
                } else {
                        tp->mcfg = CFG_METHOD_20;
                        tp->HwIcVerUnknown = TRUE;
                }

                tp->efuse_ver = EFUSE_SUPPORT_V3;
                break;
        case 0x4C000000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_21;
                } else if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_22;
                } else {
                        tp->mcfg = CFG_METHOD_22;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_SUPPORT_V3;
                break;
        case 0x50000000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_23;
                } else if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_27;
                } else if (ICVerID == 0x00200000) {
                        tp->mcfg = CFG_METHOD_28;
                } else {
                        tp->mcfg = CFG_METHOD_28;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_SUPPORT_V3;
                break;
        case 0x50800000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_24;
                } else if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_25;
                } else {
                        tp->mcfg = CFG_METHOD_25;
                        tp->HwIcVerUnknown = TRUE;
                }
                tp->efuse_ver = EFUSE_SUPPORT_V3;
                break;
        case 0x5C800000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_26;
                } else {
                        tp->mcfg = CFG_METHOD_26;
                        tp->HwIcVerUnknown = TRUE;
                }

                tp->efuse_ver = EFUSE_SUPPORT_V3;
                break;
        case 0x54000000:
                if (ICVerID == 0x00000000) {
                        tp->mcfg = CFG_METHOD_29;
                } else if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_30;
                } else {
                        tp->mcfg = CFG_METHOD_30;
                        tp->HwIcVerUnknown = TRUE;
                }

                tp->efuse_ver = EFUSE_SUPPORT_V3;
                break;
        case 0x54800000:
                if (ICVerID == 0x00100000) {
                        tp->mcfg = CFG_METHOD_31;
                } else if (ICVerID == 0x00200000) {
                        tp->mcfg = CFG_METHOD_32;
                } else {
                        tp->mcfg = CFG_METHOD_32;
                        tp->HwIcVerUnknown = TRUE;
                }

                tp->efuse_ver = EFUSE_SUPPORT_V3;
                break;
        default:
                printk("unknown chip version (%x)\n",reg);
                tp->mcfg = CFG_METHOD_DEFAULT;
                tp->HwIcVerUnknown = TRUE;
                tp->efuse_ver = EFUSE_NOT_SUPPORT;
                break;
        }
}
