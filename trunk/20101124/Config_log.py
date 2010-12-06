"""
这里记录系统实现的配置步骤

1、新建账套，安装sale模块

2、安装multi_company multi_company_account multi_company_stock multi_company_product 系列模块
   - 安装multi_company_price遇到问题
   - 销售订单和采购订单上没有公司字段，但根据仓库字段可以确定公司
     - A plan: 研究record Rule是否可以直接写warehouse_id.company_id
     - B Plan: 在这两个model上加company_id字段和on_change_warehouse方法

3、建立测试用主数据
   - 业务伙伴 mrsf_cn mrsf_be be_customer
   - 公司 mrsf_cn mrsf_be
   - 用户 acc_cn acc_be
   - 科目 ap_cn ar_cn ap_be ar_be
   - 产品 
   - 库位
   - 仓库 wh_cn wh_be
   - 价格表

4、安装oecn_so_2_po模块

5、新建销售订单，测试确认后可生成另一公司的采购订单和销售订单

6、修改另一公司销售订单，确认价格随业务伙伴变动更改
"""
