"""
这里记录系统实现的配置步骤

1、新建账套，安装sale模块

2、安装multi_company multi_company_account multi_company_stock multi_company_product 系列模块
   - 安装multi_company_price遇到问题
   - 安装新模块oecn_multi_company,已给销售订单加上公司代码。给采购订单加公司代码。

3、建立测试用主数据
   - 业务伙伴 mrsf_cn mrsf_be be_customer
   - 公司 mrsf_cn mrsf_be
   - 用户 acc_cn acc_be
   - 科目 ap_cn ar_cn ap_be ar_be
   - 产品 
   - 库位
   - 仓库 mrsf_cn mrsf_be
   - 价格表

4、安装oecn_so_2_po模块

5、新建销售订单，测试保存后可生成另一公司的销售订单，确认后可生成另一公司的采购订单

6、修改另一公司销售订单，确认价格随业务伙伴变动更改
"""
