# 闲鱼规则来源与边界

核对日期 2026-10-07。目标是闲鱼交易 App 和 goofish.com 网页，保持可独立引用的 Surge `RULE-SET` 格式。

## 六个固定来源

- SukkaW 的 `Source/non_ip/domestic.conf` 没有独立闲鱼集合，仅有宽泛的淘宝 User-Agent，不混入闲鱼专用集。
- blackmatrix7 的 `rule/Surge/XianYu/XianYu.list` 作为专用基线，16 条后缀全部保留，包括 `xianyu.mobi` 和历史分享短链域名。该集合缺少 `goofish.com`、聊天和共享业务依赖，不能直接作为完整规则交付。
- Rabbit-Spec 的 `Rules/China.list` 交叉核对核心和依赖域名，仅输出已审核的端点，不合并 China 总集。
- ConnersHua RuleGo 的 `Surge/Ruleset/Direct.list` 没有闲鱼专项覆盖，不使用泛化分类或淘宝广告拦截替代业务分流。
- Loyalsoldier 的 `surge-rules/release/direct.txt` 交叉核对域名归属和国内服务分类，不导入直连全集。
- Yuu518 的 `surge/geosite/alibaba.list` 交叉核对阿里体系的业务依赖，不导入 Alibaba 全集。

自动更新拉取 blackmatrix7、Rabbit-Spec、Loyalsoldier、Yuu518。每个已审核共享端点及 `goofish.com` 必须在后三个来源中至少得到两家覆盖确认。广泛来源只用于验证已有审核对象，不因包含新域名而扩张输出；新依赖需要额外核实后加入。专用基线新增条目会合并，历史有效条目保留，来源数量异常时停止写入。

## 第一方证据

[闲鱼官网](https://www.goofish.com/) 的当前页面使用 `gw.alicdn.com`、`g.alicdn.com`、`img.alicdn.com`、`o.alicdn.com`、`gm.mmstat.com`、`log.mmstat.com`，并引用以下可追溯的生产版本资源。

[布局与聊天代码](https://g.alicdn.com/idle-pc/xy-site/0.0.176/js/p_layout.js) 明确含有生产聊天配置 `wss-goofish.dingtalk.com`，公共聊天 SDK 的生产通道 `wss-cntaobao.dingtalk.com` 和 `wss.im.dingtalk.cn`，以及 `down.dingtalk.com`、`down-cdn.dingtalk.com`、`down.im.dingtalk.cn`、`impaas-static.dingtalk.com`、`static.dingtalk.com`、`i01.lw.aliimg.com` 等消息资源。SDK 代码中的测试、预发和 mock 钉钉端点未作为生产依赖加入。

[主页代码](https://g.alicdn.com/idle-pc/xy-site/0.0.176/js/p_index.js) 与布局代码含有 `stream-upload.goofish.com`、多个 `alicdn.com` 图片端点、`a.tbcdn.cn` 和 `wwc.taobaocdn.com`。[主资源](https://g.alicdn.com/idle-pc/xy-site/0.0.176/js/main.js) 含有 `xianyu-video.alicdn.com`。全部 `goofish.com` 子域名通过一条后缀规则覆盖，包括 API、H5、登录、上传、分享、协议和活动端点。

[自动登录插件](https://o.alicdn.com/vip/goofish-auto-login/plugin.js) 使用 `passport.goofish.com` 和 `s-gm.mmstat.com`。官网同时加载 [淘宝登录库](https://g.alicdn.com/mtb/lib-login/3.5.1/login.js) 与 [MTOP 库](https://g.alicdn.com/mtb/lib-mtop/2.7.3/mtop.js)。据此保留登录和 MTOP 的常用精确端点及旧闲鱼入口。某端点出现在 SDK 代码中表示代码具备该能力，不代表每次使用闲鱼都会请求它。

[闲鱼 SDK 披露](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao202103091502_25532.html) 确认支付宝支付、淘宝登录、阿里云对象存储、播放器、音视频通信、号码认证、高德定位等组件。[支付宝官方常见问题](https://opendocs.alipay.com/mini/00g3k8) 列出 `mobilegw.alipay.com`；支付/H5 精确端点纳入依赖，支付宝主域总集不加入。

[blackmatrix7 上游误杀报告](https://github.com/blackmatrix7/ios_rule_script/issues/838) 指出拦截 `amdc.m.taobao.com` 可能导致闲鱼频繁验证，[另一份报告](https://github.com/blackmatrix7/ios_rule_script/issues/391) 涉及 `acs.m.taobao.com`。保留业务接口用于分流，不把去广告策略写入这个集合。`heic.alicdn.com` 为已有闲鱼图片/去广告配置中出现的图片端点，采用精确规则。

## 不能由这份集合独立保证的部分

共享端点也可能被淘宝、钉钉或其他 App 使用。iOS 的域名规则无法区分同一主机名来自哪个 App；精确主机名只能缩小影响范围，不能实现按 App 隔离。需要单独使用闲鱼策略时，该规则必须放在 China、Alibaba、淘宝、GEOIP 和 FINAL 等总集之前；去广告误杀需在对应模块中处理，分流规则不能取消 Map Local、脚本、重写或 pre-matching 拦截。

没有直接证据的阿里云 OSS 桶、云认证端点、音视频节点及整个 `aliyuncs.com`、`amap.com`、`qq.com`、`dingtalk.com`、`alicdn.com`、`taobao.com` 后缀和共享 ASN/IP 段不加入。第三方广告/统计 SDK 和跳转后打开的微信、支付宝、高德等独立 App 沿用各自策略；不把 SDK 隐私政策网址当作运行时接口。

[历史 HTTPDNS 抓包报告](https://github.com/VirgilClyne/GetSomeFries/issues/76) 列出 7 个硬编码 IP 和不具体的 `*.zijieapi.com`。该报告来自 2024-12，缺少用户当前版本请求及归属确认，保留为待实机核对项，不将其写入正式规则。`extended-matching` 可以匹配直接连 IP 时可见的 TLS SNI/HTTP Host，但无法识别没有域名信息的裸 IP 连接。

目前验证覆盖第一方公开生产代码和固定上游专用规则，不等于已经验证用户设备全部功能。验收实机完整性需观察当前版本的启动、搜索、商品详情、图片/视频加载、聊天和消息图片、发布上传、登录、支付、号码认证、定位及音视频请求；发现新端点时先确认用途与共享边界再补充。
