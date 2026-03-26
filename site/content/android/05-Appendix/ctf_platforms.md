---
title: "CTF 与练习平台"
date: 2025-03-16
type: posts
tags: ["Native层", "资源", "Android", "参考", "IDA Pro", "Root检测"]
weight: 10
---

# CTF 与练习平台

实践是掌握逆向工程技术的关键。本页面整理了提供 Android 逆向挑战的 CTF 平台和 CrackMe 网站，同时涵盖学习社区、比赛资源和入门建议。

---

## CTF 平台推荐

### 国际平台

| 平台名称 | 链接 | 专长方向 | 难度 | 语言 | 说明 |
| --- | --- | --- | --- | --- | --- |
| CTFtime | [ctftime.org](https://ctftime.org/) | 赛事聚合 / 全方向 | 全难度 | 英文 | 全球最大的 CTF 赛事聚合与排名平台，可追踪所有即将举办的比赛 |
| Hack The Box | [hackthebox.com](https://www.hackthebox.com/) | 渗透测试 / 逆向 / Mobile | 中-高 | 英文 | 知名渗透测试平台，Mobile 和 Reversing 分类下有优质 Android 题目 |
| TryHackMe | [tryhackme.com](https://tryhackme.com/) | 网络安全入门 / 引导式学习 | 低-中 | 英文 | 对初学者极其友好，提供有引导性的 Android 逆向 Room |
| PicoCTF | [picoctf.org](https://picoctf.org/) | 综合 CTF 入门 | 低-中 | 英文 | 卡内基梅隆大学主办，面向学生群体，包含 Reverse Engineering 入门题 |
| OverTheWire | [overthewire.org](https://overthewire.org/wargames/) | Linux / 二进制基础 | 低-中 | 英文 | 经典 Wargame 平台，Narnia/Behemoth 系列适合练习二进制基础 |
| pwnable.kr | [pwnable.kr](https://pwnable.kr/) | Pwn / 二进制漏洞利用 | 中-高 | 英文 | 专注于系统级漏洞利用，题目经典且质量高 |
| pwnable.tw | [pwnable.tw](https://pwnable.tw/) | Pwn / 二进制漏洞利用 | 高 | 英文 | 题目难度较 pwnable.kr 更高，适合进阶选手 |
| Root Me | [root-me.org](https://www.root-me.org/) | 全方向 / Cracking | 低-高 | 英/法文 | Cracking 和 App-Script 分类下有移动应用相关挑战 |
| W3Challs | [w3challs.com](https://w3challs.com/) | 综合 CTF | 中-高 | 英文 | 包含 Reverse、Crypto、Web 等多类别题目 |
| RingZer0 | [ringzer0ctf.com](https://ringzer0ctf.com/) | 综合 CTF | 中 | 英文 | 涵盖 Reverse、Coding、Crypto 等方向 |

### 国内平台

| 平台名称 | 链接 | 专长方向 | 难度 | 说明 |
| --- | --- | --- | --- | --- |
| BUUCTF | [buuoj.cn](https://buuoj.cn/) | 综合 CTF / 题目收录 | 低-高 | 国内最大的综合 CTF 刷题平台，收录了大量历年赛题，包含 Reverse 方向 |
| 攻防世界 (XCTF) | [adworld.xctf.org.cn](https://adworld.xctf.org.cn/) | 综合 CTF | 低-高 | XCTF 联赛官方练习平台，题目分新手区和进阶区，逆向题丰富 |
| i春秋 | [ichunqiu.com](https://www.ichunqiu.com/) | 综合安全 / CTF 培训 | 低-中 | 提供 CTF 靶场和在线课程，有移动安全相关内容 |
| CTFHub | [ctfhub.com](https://www.ctfhub.com/) | CTF 技能树 / 工具集 | 低-中 | 按技能树组织题目，有系统化的学习路径 |
| NSSCTF | [nssctf.cn](https://www.nssctf.cn/) | 综合 CTF / 高校赛题 | 低-高 | 收录大量国内高校 CTF 赛题，更新速度快 |
| 看雪 CTF | [ctf.kanxue.com](https://ctf.kanxue.com/) | 逆向 / Pwn / 移动安全 | 中-高 | 看雪论坛主办的 CTF 比赛，题目偏向逆向和二进制分析 |
| 蓝桥杯 CTF | [dasai.lanqiao.cn](https://dasai.lanqiao.cn/) | 综合 CTF | 低-中 | 面向学生的比赛平台，有安全方向赛道 |
| Bugku | [bugku.com](https://bugku.com/) | 综合 CTF | 低-中 | 题目种类丰富，包含逆向和移动安全方向 |
| 实验吧 | [shiyanbar.com](http://www.shiyanbar.com/) | 综合安全 / CTF | 低-中 | 老牌安全学习平台，包含逆向和 CTF 练习环境 |

---

## Android 逆向专项

Android 逆向是 CTF 中一个独立且重要的方向。以下是专门针对 Android 逆向的资源。

### OWASP UnCrackable Apps

- **描述**: OWASP 官方提供的一系列 Android 和 iOS 逆向挑战应用，分为 Level 1 到 Level 4 不同难度。是学习移动安全测试标准 (MSTG) 的最佳配套练习。
- **链接**: [OWASP MSTG Repo](https://github.com/OWASP/owasp-mastg/tree/master/Crackmes)

### Google CTF (Mobile Category)

- **描述**: Google 每年举办的 CTF 比赛中的 Mobile 类目题目。这些题目通常质量很高，涉及各种 Android 特性和新颖的保护机制。
- **链接**: [Google CTF Archives](https://capturetheflag.withgoogle.com/) (查看历年题目)

### Android App Reverse Engineering 101 Crackmes

- **描述**: Maddie Stone 在她的 Workshop 中使用的练习题目，非常适合 Android 逆向入门。
- **链接**: [GitHub Repo](https://github.com/maddiestone/AndroidAppRE)

### 更多 Android 专项挑战资源

| 资源名称 | 链接 | 说明 |
| --- | --- | --- |
| DIVA (Damn Insecure and Vulnerable App) | [GitHub](https://github.com/payatu/diva-android) | 专为学习 Android 安全漏洞设计的练习应用 |
| InsecureBankv2 | [GitHub](https://github.com/dineshshetty/Android-InsecureBankv2) | 模拟银行应用，包含多种常见安全漏洞 |
| MSTG Hacking Playground | [GitHub](https://github.com/nicnocquee/mstg-hacking-playground) | OWASP MSTG 配套练习应用 |
| InjuredAndroid | [GitHub](https://github.com/B3nac/InjuredAndroid) | CTF 风格的 Android 挑战应用，涵盖多种攻击向量 |
| AndroGoat | [GitHub](https://github.com/satishpatnayak/AndroGoat) | OWASP 风格的 Android 漏洞练习应用 |
| hpAndro | [hpandro.raviramesh.info](http://hpandro.raviramesh.info/) | 涵盖 OWASP Top 10 Mobile 的 Android CTF 挑战 |
| KGB Messenger | [GitHub](https://github.com/tlamb96/kgb_messenger) | 知名的 Android 逆向 CTF 挑战，三个关卡难度递进 |
| CyberTruck Challenge | [GitHub](https://github.com/nicnocquee/cyber-truck-challenge) | 结合 Android 逆向和嵌入式安全的挑战 |
| Android-Security | [GitHub](https://github.com/AmanSharma1419/Android-Security) | Android 安全相关的 CTF 题目收集 |

### Android CrackMe 收集

| 来源 | 链接 | 说明 |
| --- | --- | --- |
| Crackmes.one (Android 标签) | [crackmes.one](https://crackmes.one/) | 搜索 "Android" 或 "APK" 标签，大量不同难度的 CrackMe |
| 吾爱破解 CrackMe 合集 | [52pojie.cn](https://www.52pojie.cn/) | 论坛 CrackMe 板块有大量中文 Android 逆向练习 |
| 看雪 CrackMe | [bbs.kanxue.com](https://bbs.kanxue.com/) | CrackMe 板块长期活跃，有移动端相关题目 |
| r/ReverseEngineering | [Reddit](https://www.reddit.com/r/ReverseEngineering/) | 社区中偶尔会有 Android CrackMe 分享 |

---

## 逆向工程练习资源

除了综合 CTF 平台外，以下网站专注于逆向工程方向的练习。

| 平台名称 | 链接 | 方向 | 难度 | 说明 |
| --- | --- | --- | --- | --- |
| Crackmes.one | [crackmes.one](https://crackmes.one/) | CrackMe 收集 | 低-高 | 全球最大的 CrackMe 收集网站，支持按平台、难度筛选 |
| reversing.kr | [reversing.kr](http://reversing.kr/) | 逆向挑战 | 中-高 | 韩国知名逆向练习平台，题目经典，涵盖 Windows/Linux/Android |
| challenges.re | [challenges.re](https://challenges.re/) | 逆向挑战 | 中-高 | 《Reverse Engineering for Beginners》作者创建的练习集 |
| begin.re | [begin.re](https://www.begin.re/) | 逆向入门 | 低 | 面向完全初学者的逆向工程入门教程与练习 |
| Microcorruption | [microcorruption.com](https://microcorruption.com/) | 嵌入式逆向 | 中 | 基于浏览器的嵌入式设备 CTF，适合理解底层逻辑 |
| Flare-On | [flare-on.com](https://flare-on.com/) | 恶意软件逆向 | 高 | FireEye/Mandiant 主办的年度逆向挑战赛，题目极具深度 |
| CSAW 365 | [365.csaw.io](https://365.csaw.io/) | 综合 CTF / 逆向 | 低-中 | NYU 主办，全年开放的 CTF 练习环境 |
| IO Wargame | [io.netgarage.org](http://io.netgarage.org/) | 二进制分析 | 中 | 经典的 Linux 二进制 Wargame |

### 逆向工程电子书与参考

| 资源 | 链接 | 说明 |
| --- | --- | --- |
| RE for Beginners | [beginners.re](https://beginners.re/) | Dennis Yurichev 著，免费电子书，逆向入门经典 |
| Nightmare | [GitHub](https://guyinatuxedo.github.io/) | 基于 CTF 题目的二进制逆向与漏洞利用课程 |
| LiveOverflow (YouTube) | [YouTube](https://www.youtube.com/c/LiveOverflow) | 高质量的 CTF 和安全研究视频，包含逆向内容 |
| Malware Unicorn RE101 | [malwareunicorn.org](https://malwareunicorn.org/workshops/re101.html) | 逆向工程 Workshop，面向初学者 |

---

## 在线学习平台与社区

安全社区是获取最新技术、交流经验的重要渠道。

### 国内核心社区

| 平台名称 | 链接 | 类型 | 说明 |
| --- | --- | --- | --- |
| 看雪学院 (Kanxue) | [kanxue.com](https://www.kanxue.com/) | 论坛 / 培训 | 国内最权威的安全技术论坛，逆向工程板块极为活跃，包含 Android 逆向专区 |
| 看雪安全培训 | [edu.kanxue.com](https://edu.kanxue.com/) | 在线课程 | 提供系统化的逆向工程和安全课程，包括 Android 逆向专题 |
| 吾爱破解 (52pojie) | [52pojie.cn](https://www.52pojie.cn/) | 论坛 | 国内最大的逆向工程与软件分析社区，CrackMe 和教程资源丰富 |
| i春秋 | [ichunqiu.com](https://www.ichunqiu.com/) | 培训 / 靶场 | 网络安全在线教育平台，提供 CTF 实训和安全课程 |
| FreeBuf | [freebuf.com](https://www.freebuf.com/) | 资讯 / 社区 | 国内安全资讯平台，经常发布逆向分析和移动安全文章 |
| 安全客 | [anquanke.com](https://www.anquanke.com/) | 资讯 / 社区 | 360 旗下安全媒体平台，收录大量安全技术文章和 CTF Writeup |
| 先知社区 | [xz.aliyun.com](https://xz.aliyun.com/) | 社区 | 阿里巴巴旗下安全社区，技术文章质量较高 |
| 合天网安实验室 | [hetianlab.com](https://www.hetianlab.com/) | 培训 / 实验 | 在线安全实验环境，包含移动安全相关实验 |

### 国际社区与平台

| 平台名称 | 链接 | 类型 | 说明 |
| --- | --- | --- | --- |
| r/ReverseEngineering | [Reddit](https://www.reddit.com/r/ReverseEngineering/) | 社区 | Reddit 逆向工程子版，讨论活跃 |
| r/netsec | [Reddit](https://www.reddit.com/r/netsec/) | 社区 | Reddit 网络安全子版，经常有逆向相关内容 |
| Tuts4You | [tuts4you.com](https://tuts4you.com/) | 论坛 / 教程 | 老牌逆向工程论坛，教程和工具资源丰富 |
| OpenSecurityTraining2 | [ost2.fyi](https://ost2.fyi/) | 在线课程 | 免费的高质量安全培训课程，包含逆向和二进制分析 |
| RPISEC MBE | [GitHub](https://github.com/RPISEC/MBE) | 课程 | RPI 大学的现代二进制漏洞利用课程，公开课件和 Lab |
| Azeria Labs | [azeria-labs.com](https://azeria-labs.com/) | 教程 | ARM 逆向和漏洞利用教程，对理解 Android Native 层有帮助 |
| Hex-Rays Blog | [hex-rays.com/blog](https://hex-rays.com/blog/) | 博客 | IDA Pro 官方博客，发布新功能介绍和逆向分析技巧 |

---

## 推荐 CTF 战队与 Writeup

### 知名 CTF 战队

了解顶尖战队的解题思路对提升水平很有帮助。

| 战队名称 | 所属地区 | 说明 |
| --- | --- | --- |
| PPP (Plaid Parliament of Pwning) | 美国 (CMU) | 多次 DEF CON CTF 冠军，全球顶尖战队 |
| perfect blue | 国际 | 近年活跃度极高的国际战队，常年 CTFtime 排名前列 |
| Organizers | 国际 | 由多支顶尖战队合并而成 |
| Tea Deliverers | 中国 | 国内顶尖战队，多次在国际赛事中取得优异成绩 |
| r3kapig | 中国 | 活跃在国际赛场的中国战队 |
| Nu1L | 中国 | 国内知名战队，在 Reverse 和 Pwn 方向实力强劲 |
| Redbud | 中国 (清华) | 清华大学 CTF 战队 |
| AAA | 中国 (浙大) | 浙江大学 CTF 战队 |
| 0ops | 中国 (上交) | 上海交通大学 CTF 战队 |
| Blue-Lotus | 中国 (清华) | 清华大学蓝莲花战队，DEF CON CTF 常客 |
| Shellphish | 美国 (ASU) | 亚利桑那州立大学战队，以自动化漏洞利用著称 |

### Writeup 资源汇总

Writeup (解题报告) 是学习 CTF 解题思路的最佳途径之一。

| 来源 | 链接 | 说明 |
| --- | --- | --- |
| CTFtime Writeups | [ctftime.org/writeups](https://ctftime.org/writeups/) | 全球最大的 CTF Writeup 聚合平台，可按赛事和方向搜索 |
| GitHub CTF Writeups | GitHub 搜索 "ctf writeup" | 很多选手和战队会将 Writeup 发布在 GitHub 上 |
| 看雪论坛 CTF 板块 | [bbs.kanxue.com](https://bbs.kanxue.com/) | 国内高质量的中文 CTF Writeup |
| BUUCTF Writeup | 各大博客平台 | BUUCTF 题目的 Writeup 在 CSDN、博客园等平台大量存在 |
| 先知社区 | [xz.aliyun.com](https://xz.aliyun.com/) | 收录大量赛后 Writeup |
| 安全客 | [anquanke.com](https://www.anquanke.com/) | 定期收录 CTF 赛后分析 |
| 个人博客推荐 | 各类技术博客 | 关注 R0ysue (肉丝)、hluwa、evilpan 等知名安全研究员的博客 |

> **提示**: 搜索引擎中输入 `"赛事名称" + "writeup"` 或 `"题目名称" + "wp"` 是找到特定题目解题报告的最快方式。

---

## 入门路径建议

对于想要入门 Android 逆向和 CTF 的学习者，建议按以下路径循序渐进。

### 阶段一: 基础知识储备 (1-2 个月)

| 学习内容 | 推荐资源 | 目标 |
| --- | --- | --- |
| 计算机基础 | 《深入理解计算机系统》(CSAPP) | 理解内存、汇编、编译链接等底层概念 |
| Java 基础 | 官方文档 / 在线教程 | 能读懂 Java 代码逻辑 |
| Android 基础 | Android 官方文档 | 理解四大组件、Activity 生命周期、APK 结构 |
| Linux 基础 | OverTheWire Bandit | 熟悉命令行操作和基本 Shell 脚本 |

### 阶段二: 逆向入门 (2-3 个月)

| 学习内容 | 推荐资源 | 目标 |
| --- | --- | --- |
| APK 静态分析 | jadx, APKTool | 熟练使用反编译工具分析 Java/Smali 代码 |
| Smali 语法 | 《Android 软件安全与逆向分析》 | 能读懂并修改 Smali 代码 |
| 简单 CrackMe | OWASP UnCrackable Level 1 | 完成第一个 Android 逆向挑战 |
| 动态调试基础 | Android Studio Debugger | 掌握断点调试和运行时分析 |
| CTF 入门 | PicoCTF, CTFHub 新手区 | 体验 CTF 解题流程 |

### 阶段三: 工具进阶 (2-3 个月)

| 学习内容 | 推荐资源 | 目标 |
| --- | --- | --- |
| Frida 入门 | 本教程、R0ysue 教程 | 掌握 Frida Hook Java 和 Native 函数 |
| IDA Pro 基础 | 《IDA Pro 权威指南》 | 能分析 Native SO 文件 |
| ARM 汇编 | Azeria Labs ARM 教程 | 读懂 ARM 汇编代码 |
| OWASP Level 2-3 | OWASP UnCrackable Apps | 处理 Root 检测、Native 代码保护 |
| CTF 逆向题 | BUUCTF Reverse 分类、攻防世界 | 积累解题经验 |

### 阶段四: 实战深入 (持续)

| 学习内容 | 推荐资源 | 目标 |
| --- | --- | --- |
| 加壳与脱壳 | 看雪论坛脱壳板块 | 理解常见加固方案和脱壳方法 |
| 反混淆 | challenges.re, Flare-On | 应对 OLLVM 等代码混淆 |
| 协议分析 | 实际应用抓包分析 | 分析加密通信协议 |
| 漏洞挖掘 | Google CTF Mobile 题目 | 理解 Android 安全漏洞利用 |
| 参加正式比赛 | CTFtime 上的赛事 | 在限时环境下检验能力 |

### 阶段五: 专精与研究 (长期)

| 方向 | 说明 |
| --- | --- |
| Android 系统安全 | 深入内核、驱动、SELinux 策略等系统层面 |
| 恶意软件分析 | 分析 APT 组织的 Android 样本 |
| 自动化分析 | 开发 Frida 脚本、IDA 插件，构建自动化分析流水线 |
| 漏洞研究 | 专注于 Android 0day 研究和利用 |
| 安全对抗 | 研究最新的保护方案和绕过技术 |

---

## 比赛日历与赛事追踪

### 如何追踪即将举办的 CTF 比赛

| 渠道 | 链接 | 说明 |
| --- | --- | --- |
| CTFtime | [ctftime.org/event/list/upcoming](https://ctftime.org/event/list/upcoming) | 全球最权威的 CTF 赛事日历，支持 iCal 订阅 |
| CTFtime 权重赛事 | [ctftime.org](https://ctftime.org/) | 关注权重 (weight) 较高的比赛，通常质量更好 |
| 各平台公告 | BUUCTF、攻防世界等 | 国内平台会在首页公告即将举办的比赛 |
| 安全客赛事栏目 | [anquanke.com](https://www.anquanke.com/) | 定期整理国内外安全赛事信息 |
| 微信公众号 | 各战队和社区公众号 | 关注 "看雪学院"、"i春秋" 等公众号获取赛事通知 |
| Twitter/X | 关注 @ctftime 等账号 | 国际赛事信息的第一手来源 |

### 年度重点赛事

以下是逆向工程和移动安全方向值得关注的年度赛事。

| 赛事名称 | 时间 (大致) | 类型 | 说明 |
| --- | --- | --- | --- |
| DEF CON CTF | 每年 8 月 | 线下总决赛 | 全球最顶级的 CTF 赛事，需经过预选赛晋级 |
| Google CTF | 每年 6-7 月 | 线上 | Google 主办，Mobile 方向题目质量极高 |
| Flare-On Challenge | 每年 9-10 月 | 线上 | FireEye 逆向挑战赛，纯逆向方向 |
| 看雪 KCTF | 每年多期 | 线上 | 看雪论坛主办，偏重逆向和 Pwn |
| 强网杯 | 每年不定期 | 线上+线下 | 国内高水平综合 CTF |
| TCTF / 0CTF | 每年不定期 | 线上+线下 | 国内顶级赛事，国际化程度高 |
| Real World CTF | 每年 1 月 | 线上+线下 | 侧重真实场景漏洞利用 |
| HITCON CTF | 每年 8-11 月 | 线上 | 中国台湾举办，题目质量和难度都很高 |
| CSAW CTF | 每年 9 月 | 线上 | 面向学生的大型 CTF，适合入门 |
| 网鼎杯 | 每年不定期 | 线上+线下 | 国内大型行业 CTF 赛事 |

### CTFtime 使用技巧

1. **注册账号**: 在 CTFtime 注册后可以关注感兴趣的赛事，获取提醒通知
2. **日历订阅**: 在 CTFtime 获取 iCal 链接，导入 Google Calendar 或 Apple Calendar 自动同步赛事
3. **筛选比赛**: 使用 `Format` 筛选 Jeopardy (解题赛) 类型的比赛，这是最常见的 CTF 赛制
4. **查看权重**: CTFtime 权重 (weight) 反映比赛质量，建议优先参加权重 25 以上的赛事
5. **赛后复盘**: 比赛结束后在 CTFtime 查找 Writeup，学习其他选手的解题思路

---

## 实用建议

### 工具准备清单

在开始 CTF 和逆向练习之前，建议准备好以下工具环境:

| 类别 | 工具 | 说明 |
| --- | --- | --- |
| 反编译 | jadx, APKTool, JEB | APK 静态分析必备 |
| 动态分析 | Frida, Objection | 运行时 Hook 和分析 |
| 调试器 | IDA Pro, Ghidra, GDB | Native 层调试和分析 |
| 抓包 | Burp Suite, mitmproxy | 网络流量分析 |
| 模拟器 | Android Emulator, Genymotion | 提供分析环境 |
| 脚本语言 | Python 3 | 编写自动化脚本和 Exploit |
| 十六进制编辑 | 010 Editor, HxD | 二进制文件编辑 |

### 解题思路总结

Android 逆向 CTF 题目的一般解题流程:

1. **信息收集**: 使用 `file`、`unzip` 等命令确认文件类型，使用 `jadx` 反编译查看整体结构
2. **静态分析**: 阅读 Java/Kotlin 层代码，定位关键逻辑 (如验证函数、加密算法)
3. **识别保护**: 确认是否有加壳、混淆、Root 检测、反调试等保护手段
4. **动态分析**: 使用 Frida Hook 关键函数，打印参数和返回值
5. **Native 分析**: 如果关键逻辑在 SO 文件中，使用 IDA Pro/Ghidra 分析
6. **编写脚本**: 根据分析结果编写解题脚本，还原 Flag

---
