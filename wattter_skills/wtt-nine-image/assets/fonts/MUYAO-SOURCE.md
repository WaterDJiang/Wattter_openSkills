# 沐瑶随心手写体：封面默认字体

- 独立本机字体路径：`~/.local/share/nine-image/fonts/MuyaoPleased.ttf`；通过 [本地解析器](../../scripts/resolve_font.py)加载。兼容旧 `assets/fonts/local/MuyaoPleased.ttf`，命中旧路径后登记到独立目录，避免运行树重建丢失。不安装系统字体、不纳入 Git 或分发包；旧目录由 .gitignore 排除字体二进制。
- 内部 family：MuyaoPleased / 沐瑶随心手写体；原文件未修改。勿混淆沐瑶软笔手写体。
- 文件来源：[Free Font 收录文件](https://github.com/jaywcjlove/free-font/tree/main/docs/fonts/沐瑶字体系列)，不是作者官网；获取日期 2026-10-08。
- 远端实际文件名 `沐瑶随心手写体.ttf`，与本地规范名 `MuyaoPleased.ttf` 不同。先查本地；只有确实缺失才从已记录目录获取并登记，不能用本地名猜下载链接或反复请求GitHub目录API。
- 作者：春颜秋色；[作者发布页](https://www.zcool.com.cn/work/ZMzYwMzk2MjA=.html)本次被访问挑战阻挡，未直接读取。
- [100font 授权与更新记录](https://www.100font.com/thread-104.htm)明确列出个人、企业免费使用，包含商业广告、自媒体、电商；并列出修改、衍生、商标、转售、嵌入用途限制。此处是第三方转载证据，不冒充作者独立授权书。
- 本次公众号/X 封面静态图片属于上述自媒体用途。未核实字体再分发许可，不将字体打包到公开 skill；喜脉的 OFL.txt 不适用于本字体。
- 新环境经本地解析确认缺少字体后，从来源获取并核对内部名称及授权，再运行 `resolve_font.py --usage cover --install-cover-from '/实际本机路径/沐瑶随心手写体.ttf'` 登记；不可静默替换为喜脉或其他字体。缺字列出字符，换字或换字体须用户决定。
- 真实样张已渲染；每次制作仍须 cmap 检查、逐字复核。2021 年更新记录包含错字修复，不能仅凭 cmap 存在断言字形正确。

- 本次文件大小：3505188 字节；SHA-256：`62ab940ead12688125ea63824d9b7c16a4f3ee13fe85a0375843dcbe07ef374a`。
