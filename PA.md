## 一、总体目标

该方案旨在解决  **“个人智能体（Personal Agent, PA）” 的可信身份构建与监管揭露问题** 。

当前主流智能体协议（如 MCP、A2A、ANP）各有缺陷：

* **MCP** ：只关注模型与外部资源交互，不考虑身份。
* **A2A** ：面向企业工作流，无身份层。
* **ANP** ：具去中心化身份（DID），但未绑定自然人。

因此本方案提出了一种结合：

* **自我主权性（Self-Sovereignty）** ，
* **隐私保护性（Privacy Protection）** ，
* **可监管性（Regulability）**

  的身份机制，来实现  **自然人与其个人智能体之间的可信绑定与身份揭露能力** 。

---

## 二、系统核心思想

核心理念：

让用户拥有一个唯一且自我主权的身份锚点（SCID），

* 能自主生成并管理自己的智能体（PA），
* 能保护身份隐私（TP 不保存真实信息），
* 但在恶意行为发生时，TP 可以揭露其真实身份。

其技术基础包括：

* **SCID（Self-Certified Identity）** ：由用户自生成的自认证身份标识。
* **PHC（Personhood Credential）** ：人格凭证，由信任提供方 TP 签发。
* **AF（Anchoring Factor）** ：锚定因子，用变色龙哈希绑定身份与监管因子。
* **RF（Regulation Factor）** ：监管因子，用于身份揭露。
* **DID（Decentralized Identifier）** ：最终对外标识的去中心化身份标识。
* **Paillier 同态加密** 与 **变色龙哈希算法** 用于加密监管与可验证修改。
* **IPFS** ：分布式存储，用于加密存储用户隐私数据。

---

## 三、系统模型与交互流程

涉及实体：

* **User（自然人）**
* **TP（Trust Provider）** ：负责身份验证与监管。
* **AP（Agent Provider）** ：为用户生成个性化 PA。
* **IPFS** ：加密数据存储。

### 流程概述（9步）：

1️⃣ 用户生成锚定因子 AF，并绑定自己的身份 ID。

2️⃣ 用户将 AF、个人识别信息 PII、生物信息 BI 发送给 TP。

3️⃣ TP 验证后：

 - 加密敏感数据存入 IPFS；

 - 用 Paillier 公钥加密 ID 生成 RF；

 - 盲化生成 CRF；

 - 构造 SCID = (AF, RF)；

 - 创建 PHC 并返回给用户（含用户 DID）。

4️⃣ 用户验证 PHC 与 AF/RF 正确性。

5️⃣ 用户向 AP 请求个人智能体（PA），提交 PHC。

6️⃣ AP 验证 PHC 正确性与签名。

7️⃣ 用户选择 PA 配置信息（个性化模块）。

8️⃣ AP 根据配置生成哈希链并绑定到 AF，返回 PA。

9️⃣ 用户使用 DID 驱动 PA 进行网络活动。若有恶意行为，TP 可通过 RF 揭露身份。

---

## 四、PHC（人格凭证）结构与生成细节

PHC 采用  **JSON-LD 语义描述格式** ，包含四个主要部分：

* `"ASO"`（Agent Self-Owned）：包含智能体自描述，如时间戳、CDID（加密 DID）、AF、CMI（自定义模块哈希链）。
* `"TPA"`（TP Attestation）：TP 公钥及签名。
* `"APA"`（AP Attestation）：AP 公钥及签名。
* `"PROOF"`：变色龙哈希签名与验证方法。

生成逻辑：

1. TP 初次创建 PHC，可修改 ASO、TPA、APA 字段；
2. TP 计算 TPCH 与 APCH（变色龙哈希值）；
3. 拼接签名形成 PHC 总签名；
4. TP 将 APCH 的陷门交给 AP，使其能合法更新 APA/CMI 而不破坏整体签名。

这一机制保证了：

* TP 与 AP 均可独立修改其职责范围的字段；
* 整体 PHC 签名仍然有效；
* 支撑可验证修改与链上监管追溯。

---

## 五、DID（去中心化身份）结构设计

DID 格式：

<pre class="overflow-visible!" data-start="1917" data-end="1957"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>did:</span><span>wba:</span><span><</span><span>SCID</span><span>></span><span>:<domain></span><span>[</span><span>:<path></span><span>]
</span></span></code></div></div></pre>

其中：

* **SCID = (AF, RF)** ：用户自生成的自认证标识符；
* **AF** ：锚定因子，绑定身份与智能体；
* **RF** ：监管因子，可被 TP 解密揭露；
* **domain** ：表示 DID 所属域；
* **path** ：可选路径扩展。

特性：

* 用户身份由自己控制；
* 可跨平台复用；
* 具备可监管可追溯能力。

---

## 六、系统参数与密码学支撑

涉及多方密钥体系：

* 用户密钥对：`(ska, pka)`
* AP 密钥对：`(skap, pkap)`
* TP 密钥对：`(sktp, pktp)`
* Paillier 密钥对：`(λ, (n,g1))`
* 各方拥有彼此公钥。
* 哈希机制：
  * **标准变色龙哈希 CH**
  * **自定义变色龙哈希 CCH** （用于 PA 自定义部分）

此外，还定义了：

* **CM** ：智能体模块序号与功能描述；
* **CMC** ：模块的具体代码；
* **HCGen** ：哈希链生成算法；
* **PAGen** ：生成智能体算法。

---

## 七、恢复与更新机制

PPT 还特别设计了三种恢复场景：

1️⃣  **PA 丢失** ：可根据 PHC 重新生成。

2️⃣  **PHC 丢失** ：由 TP 验证后重签发。

3️⃣  **PA 与 PHC 都丢失** ：需 TP、AP 联合验证恢复。

PA 更新时：

* 用户先验证 PHC 与哈希链；
* AP 重新生成 CMI（模块哈希链）；
* 用变色龙哈希保持签名一致性；
* 用户重新绑定 AF。

这一机制保证系统的 **持续性与安全性** 。

---

## 八、身份揭露机制（Trace）

当某个 PA 被认定为恶意时：

1. TP 根据其公开 DID，定位到 PHC；
2. 提取其中的加密监管因子 RF；
3. 使用 Paillier 私钥 λ 解密，得到用户真实 ID；
4. 通过 IPFS 索引 CID，获取并验证身份数据；
5. 揭露真实用户，实现 **可追责性** 。

---

## 九、整体实现思路总结

**核心思路一句话概括：**

> 利用自认证身份标识（SCID） + 人格凭证（PHC） + 可变哈希与同态加密，实现“自我主权 + 隐私保护 + 可监管揭露”三者统一的个人智能体身份体系。

**技术亮点：**

* 双方（TP/AP）可验证修改的可变签名结构；
* DID 扩展机制支持绑定自然人；
* Paillier 同态加密实现身份监管；
* IPFS 实现分布式隐私存储；
* 哈希链机制支持个性化与可验证扩展。
