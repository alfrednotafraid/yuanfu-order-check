-- 自动生成 by scripts/import_excel.py
-- 订单数据/生产订单.xlsx  (1379 行)
CREATE TABLE `prod_order` (
`row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `交期子单号` VARCHAR(64) NULL,
  `发货单号` VARCHAR(64) NULL,
  `订单号` VARCHAR(64) NULL,
  `订单原单号` VARCHAR(64) NULL,
  `购买意向单` VARCHAR(64) NULL,
  `全屋编码` VARCHAR(64) NULL,
  `手工合同号` VARCHAR(64) NULL,
  `业务类型` VARCHAR(64) NULL,
  `订单类型` VARCHAR(64) NULL,
  `交期子单类型` VARCHAR(64) NULL,
  `发货仓库` VARCHAR(64) NULL,
  `发货单位` VARCHAR(64) NULL,
  `经销商名称` VARCHAR(64) NULL,
  `经销商编号` VARCHAR(64) NULL,
  `门店名称` VARCHAR(64) NULL,
  `门店编号` VARCHAR(64) NULL,
  `展厅名称` VARCHAR(64) NULL,
  `展厅编号` VARCHAR(64) NULL,
  `订单收货单位` VARCHAR(64) NULL,
  `订单收货人` VARCHAR(64) NULL,
  `收货联系电话` VARCHAR(64) NULL,
  `订单收货省市区` VARCHAR(64) NULL,
  `订单收货详细地址` VARCHAR(64) NULL,
  `订单安装省市区` VARCHAR(64) NULL,
  `订单安装详细地址` VARCHAR(64) NULL,
  `订单安装联系人` VARCHAR(64) NULL,
  `订单安装联系电话` VARCHAR(64) NULL,
  `齐套状态` VARCHAR(64) NULL,
  `齐套时间` VARCHAR(64) NULL,
  `发货状态` VARCHAR(64) NULL,
  `发货时间` VARCHAR(64) NULL,
  `发货数量` BIGINT NULL,
  `到货状态` VARCHAR(64) NULL,
  `到货时间` VARCHAR(64) NULL,
  `到货数量` BIGINT NULL,
  `入库状态` VARCHAR(64) NULL,
  `入库时间` VARCHAR(64) NULL,
  `入库数量` BIGINT NULL,
  `收货状态` VARCHAR(64) NULL,
  `收货时间` VARCHAR(64) NULL,
  `作废标识` VARCHAR(64) NULL,
  `作废操作人` VARCHAR(64) NULL,
  `作废时间` VARCHAR(64) NULL,
  `主单的下单时间` VARCHAR(64) NULL,
  `交期子单的下单时间` VARCHAR(64) NULL,
  `交期子单的交期时间` VARCHAR(64) NULL,
  `主单的排产时间` VARCHAR(64) NULL,
  `主单的出货期限` VARCHAR(64) NULL,
  `创建时间` VARCHAR(64) NULL,
  `更新时间` VARCHAR(64) NULL,
  `备注` VARCHAR(64) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `prod_order` ADD INDEX `idx_交期子单号` (`交期子单号`)
ALTER TABLE `prod_order` ADD INDEX `idx_发货单号` (`发货单号`)
ALTER TABLE `prod_order` ADD INDEX `idx_订单号` (`订单号`)
ALTER TABLE `prod_order` ADD INDEX `idx_订单原单号` (`订单原单号`)

-- 订单数据/物流订单.xlsx  (588 行)
CREATE TABLE `logistics_order` (
`row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `发货单号` VARCHAR(64) NULL,
  `订单号` VARCHAR(64) NULL,
  `订单原单号` VARCHAR(64) NULL,
  `运输单号` VARCHAR(64) NULL,
  `发货时间` DATETIME NULL,
  `发货基地` VARCHAR(64) NULL,
  `承运商` VARCHAR(64) NULL,
  `费用承担方` VARCHAR(64) NULL,
  `到站网点` VARCHAR(64) NULL,
  `承运类型` VARCHAR(64) NULL,
  `送货模式` VARCHAR(64) NULL,
  `运输状态` VARCHAR(64) NULL,
  `门店名称` VARCHAR(64) NULL,
  `门店编码` VARCHAR(64) NULL,
  `手工合同号` VARCHAR(64) NULL,
  `发货单品类` VARCHAR(64) NULL,
  `发货单类型` VARCHAR(64) NULL,
  `货品信息` TEXT NULL,
  `体积` DECIMAL(18,4) NULL,
  `发货单数量` BIGINT NULL,
  `确认状态` VARCHAR(64) NULL,
  `关闭状态` VARCHAR(64) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `logistics_order` ADD INDEX `idx_发货单号` (`发货单号`)
ALTER TABLE `logistics_order` ADD INDEX `idx_订单号` (`订单号`)
ALTER TABLE `logistics_order` ADD INDEX `idx_订单原单号` (`订单原单号`)
ALTER TABLE `logistics_order` ADD INDEX `idx_运输单号` (`运输单号`)

-- 订单数据/配送订单.xlsx  (426 行)
CREATE TABLE `delivery_order` (
`row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `发货单号` VARCHAR(64) NULL,
  `订单号` VARCHAR(64) NULL,
  `手工合同号` VARCHAR(64) NULL,
  `运输单号` VARCHAR(64) NULL,
  `承运商名称` VARCHAR(64) NULL,
  `仓库` VARCHAR(64) NULL,
  `派送单号` VARCHAR(64) NULL,
  `门店编码` VARCHAR(64) NULL,
  `门店名称` VARCHAR(64) NULL,
  `派送状态` VARCHAR(64) NULL,
  `送货模式` VARCHAR(64) NULL,
  `配送方式` VARCHAR(64) NULL,
  `发货时间` DATETIME NULL,
  `预约送货日期` DATETIME NULL,
  `签收时间` DATETIME NULL,
  `签收来源` VARCHAR(64) NULL,
  `货品名称` TEXT NULL,
  `货品净重（吨）` DECIMAL(18,4) NULL,
  `货品毛重（吨）` DECIMAL(18,4) NULL,
  `物品体积（方）` DECIMAL(18,4) NULL,
  `货品包装` VARCHAR(64) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `delivery_order` ADD INDEX `idx_发货单号` (`发货单号`)
ALTER TABLE `delivery_order` ADD INDEX `idx_订单号` (`订单号`)
ALTER TABLE `delivery_order` ADD INDEX `idx_运输单号` (`运输单号`)

-- 订单数据/配送订单（自提单）.xlsx  (31 行)
CREATE TABLE `pickup_order` (
`row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `仓库` VARCHAR(64) NULL,
  `自提单号` VARCHAR(64) NULL,
  `发货单号` VARCHAR(64) NULL,
  `订单号` VARCHAR(64) NULL,
  `手工合同号` VARCHAR(64) NULL,
  `运输单号` VARCHAR(64) NULL,
  `门店编码` VARCHAR(64) NULL,
  `门店名称` VARCHAR(64) NULL,
  `自提单状态` VARCHAR(64) NULL,
  `送货模式` VARCHAR(64) NULL,
  `配送方式` VARCHAR(64) NULL,
  `发货时间` VARCHAR(64) NULL,
  `入库时间` VARCHAR(64) NULL,
  `派单时间` VARCHAR(64) NULL,
  `预约自提时间` VARCHAR(64) NULL,
  `完成时间` VARCHAR(64) NULL,
  `提货人` VARCHAR(64) NULL,
  `提货人身份证号` VARCHAR(64) NULL,
  `提货人电话` VARCHAR(64) NULL,
  `提货人手机号` VARCHAR(64) NULL,
  `安装联系人` VARCHAR(64) NULL,
  `安装联系手机` VARCHAR(64) NULL,
  `安装地址` VARCHAR(64) NULL,
  `收货人` VARCHAR(64) NULL,
  `收货人电话` VARCHAR(64) NULL,
  `收货地址` VARCHAR(64) NULL,
  `客户批次` VARCHAR(64) NULL,
  `货品名称` VARCHAR(64) NULL,
  `货品净重（吨）` DECIMAL(18,4) NULL,
  `货品毛重（吨）` DECIMAL(18,4) NULL,
  `物品体积（方）` DECIMAL(18,4) NULL,
  `货品包装` VARCHAR(64) NULL,
  `数量（件）` BIGINT NULL,
  `标准件` BIGINT NULL,
  `大件` BIGINT NULL,
  `超大件` BIGINT NULL,
  `委托单号` VARCHAR(64) NULL,
  `备注` VARCHAR(64) NULL,
  `创建人` VARCHAR(64) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `pickup_order` ADD INDEX `idx_发货单号` (`发货单号`)
ALTER TABLE `pickup_order` ADD INDEX `idx_订单号` (`订单号`)
ALTER TABLE `pickup_order` ADD INDEX `idx_运输单号` (`运输单号`)

-- 货品编码/物流订单-货品编码.xlsx  (12017 行)
CREATE TABLE `code_logistics` (
`row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `发货单号` VARCHAR(64) NULL,
  `运输单号` VARCHAR(64) NULL,
  `箱码编码` VARCHAR(64) NULL,
  `货品名称` VARCHAR(64) NULL,
  `数量` BIGINT NULL,
  `重量` DECIMAL(18,4) NULL,
  `体积` DECIMAL(18,4) NULL,
  `品类` VARCHAR(64) NULL,
  `箱码名称` VARCHAR(64) NULL,
  `件型` VARCHAR(64) NULL,
  `生产单号` VARCHAR(64) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `code_logistics` ADD INDEX `idx_发货单号` (`发货单号`)
ALTER TABLE `code_logistics` ADD INDEX `idx_运输单号` (`运输单号`)
ALTER TABLE `code_logistics` ADD INDEX `idx_箱码编码` (`箱码编码`)
ALTER TABLE `code_logistics` ADD INDEX `idx_生产单号` (`生产单号`)

-- 货品编码/配送（派送）订单-货品编码.xlsx  (8808 行)
CREATE TABLE `code_delivery` (
`row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `发货单号` VARCHAR(64) NULL,
  `运输单号` VARCHAR(64) NULL,
  `箱码编码` VARCHAR(64) NULL,
  `货品名称` VARCHAR(64) NULL,
  `数量` BIGINT NULL,
  `重量` DECIMAL(18,4) NULL,
  `体积` DECIMAL(18,4) NULL,
  `品类` VARCHAR(64) NULL,
  `箱码名称` VARCHAR(64) NULL,
  `件型` VARCHAR(64) NULL,
  `生产单号` VARCHAR(64) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `code_delivery` ADD INDEX `idx_发货单号` (`发货单号`)
ALTER TABLE `code_delivery` ADD INDEX `idx_运输单号` (`运输单号`)
ALTER TABLE `code_delivery` ADD INDEX `idx_箱码编码` (`箱码编码`)
ALTER TABLE `code_delivery` ADD INDEX `idx_生产单号` (`生产单号`)

-- 货品编码/配送（自提）订单-货品编码.xlsx  (364 行)
CREATE TABLE `code_pickup` (
`row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `发货单号` VARCHAR(64) NULL,
  `运输单号` VARCHAR(64) NULL,
  `箱码编码` VARCHAR(64) NULL,
  `货品名称` VARCHAR(64) NULL,
  `数量` BIGINT NULL,
  `重量` DECIMAL(18,4) NULL,
  `体积` DECIMAL(18,4) NULL,
  `品类` VARCHAR(64) NULL,
  `箱码名称` VARCHAR(64) NULL,
  `件型` VARCHAR(64) NULL,
  `生产单号` VARCHAR(64) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `code_pickup` ADD INDEX `idx_发货单号` (`发货单号`)
ALTER TABLE `code_pickup` ADD INDEX `idx_运输单号` (`运输单号`)
ALTER TABLE `code_pickup` ADD INDEX `idx_箱码编码` (`箱码编码`)
ALTER TABLE `code_pickup` ADD INDEX `idx_生产单号` (`生产单号`)
