# 远孚 · 定制家居订单交付链校核助手

2025 全国人工智能应用创新大赛企业赛道省二项目的重做版（Coze 智能体 + 自建数据服务）。
解决的问题：定制家居订单在 生产→发货→运输→配送 各环节的**串货、少件、漏件**人工核对量大、易漏检。

## 它能做什么
- 输入一个单号，返回该订单的生产齐套、发货完整、城配仓到货结论
- 输入运输单/派送单 + 实扫箱码清单，检出：漏件、多件、串货（他车货物）、分货错误（同车错单）、重复扫码
- 一键跑批：515 个订单全量状态校核，输出 Markdown 差异报告
- 对话入口在 Coze 智能体（工作流经 HTTP 调用本服务）；**判定全部由确定性代码完成，LLM 只做意图理解与结果转述**

## 快速开始
```bash
# 1. 建库导入（需本地 MySQL，或改用 sql/schema.sql + sql/sample_data.sql 先跑通）
cp config.example.ini config.ini   # 填入 MySQL 连接信息
python scripts/import_excel.py     # 需素材 Excel；clone 用户可用下方样例数据

# 2. 启动校核服务
python -m uvicorn app.main:app --port 8000

# 3. 跑断言测试（9 条：正常/漏件/串货/分错/重复/跨表单号解析…）
python tests/test_checks.py

# 4. 生成跑批报告
python scripts/run_report.py
```
样例数据：新建空库后 `mysql 新库名 < sql/schema.sql && mysql 新库名 < sql/sample_data.sql`，再把 config.ini 指到该库（含 1 个完整订单链路，电话已脱敏，可跑通全部测试）。样例文件不含任何 DELETE/TRUNCATE，但请勿导入已有数据的库（会叠加重复行）。

## 五个说明（按招聘方投递要求）
1. **解决了什么问题**：交付链四环节校核从人工逐单核对变为秒级自动比对，差异精确到箱码。
2. **哪些部分是自己完成的**：方案设计、数据建模、规则→代码的翻译决策、测试构造、验证全部本人主导；代码由 AI 编程助手（Qoder）辅助生成，每段生成代码经本地运行+断言验证后保留。
3. **用了哪些工具**：Coze（智能体/工作流）、Python + FastAPI、MySQL、phpStudy、内网穿透、Git/GitHub、AI 辅助编程。
4. **遇到什么困难、如何解决并验证**：
   - Coze 内置库单表 20 字段上限装不下 51 字段的生产订单 → 改自建 MySQL + HTTP 节点，全字段落地；
   - 样例数据订单号跨表号段不一致导致"查无此单" → 加单号解析层，逐级解析后联查；
   - 原始数据全为正常态、异常分支无法触发 → 输入侧构造串/少/漏/分错样本，9 条断言全绿。
5. **演示**：`tests/test_checks.py` 输出即演示；样例报告在 `reports/`。

## 目录
```
app/       校核服务（main=HTTP 层, checks=四场景规则实现, db=连接）
scripts/   import_excel.py 全字段导入 / run_report.py 跑批报告
tests/     断言测试（构造异常样本）
sql/       schema.sql + sample_data.sql
docs/      design.md 架构与取舍（面试向）
reports/   生成的 Markdown 校核报告
```

数据说明：订单与箱码数据为大赛提供的模拟业务数据，仓库仅含脱敏样例子集。
