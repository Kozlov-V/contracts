# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	contr_details = get_contract_details()
	cnt_item_map = get_purchased_items_cost()
	se_item_map = get_issued_items_cost()
	dn_item_map = get_delivered_items_cost()

	data = []
	for contract in contr_details:
		data.append([contract.name, cnt_item_map.get(contract.name, 0),
			se_item_map.get(contract.name, 0), dn_item_map.get(contract.name, 0),
			contract.contract_name, contract.status, contract.company,
			contract.customer, contract.estimated_costing, contract.expected_start_date,
			contract.expected_end_date])

	return columns, data

def get_columns():
	return [_("Contract Id") + ":Link/Contract:140", _("Cost of Purchased Items") + ":Currency:160",
		_("Cost of Issued Items") + ":Currency:160", _("Cost of Delivered Items") + ":Currency:160",
		_("Contract Name") + "::120", _("Contract Status") + "::120", _("Company") + ":Link/Company:100",
		_("Customer") + ":Link/Customer:140", _("Contract Value") + ":Currency:120",
		_("Contract Start Date") + ":Date:120", _("Completion Date") + ":Date:120"]

def get_contract_details():
	return frappe.db.sql(""" select name, contract_name, status, company, customer, estimated_costing,
		expected_start_date, expected_end_date from tabContract where docstatus < 2""", as_dict=1)

def get_purchased_items_cost():
	pr_items = frappe.db.sql("""select contract_name, sum(base_net_amount) as amount
		from `tabPurchase Receipt Item` where ifnull(contract_name, '') != ''
		and docstatus = 1 group by contract_name""", as_dict=1)

	pr_item_map = {}
	for item in pr_items:
		pr_item_map.setdefault(item.contract_name, item.amount)

	return pr_item_map

def get_issued_items_cost():
	se_items = frappe.db.sql("""select se.contract_name, sum(se_item.amount) as amount
		from `tabStock Entry` se, `tabStock Entry Detail` se_item
		where se.name = se_item.parent and se.docstatus = 1 and ifnull(se_item.t_warehouse, '') = ''
		and ifnull(se.contract_name, '') != '' group by se.contract_name""", as_dict=1)

	se_item_map = {}
	for item in se_items:
		se_item_map.setdefault(item.contract_name, item.amount)

	return se_item_map

def get_delivered_items_cost():
	dn_items = frappe.db.sql("""select dn.contract_name, sum(dn_item.base_net_amount) as amount
		from `tabDelivery Note` dn, `tabDelivery Note Item` dn_item
		where dn.name = dn_item.parent and dn.docstatus = 1 and ifnull(dn.contract_name, '') != ''
		group by dn.contract_name""", as_dict=1)

	si_items = frappe.db.sql("""select si.contract_name, sum(si_item.base_net_amount) as amount
		from `tabSales Invoice` si, `tabSales Invoice Item` si_item
		where si.name = si_item.parent and si.docstatus = 1 and si.update_stock = 1
		and si.is_pos = 1 and ifnull(si.contract_name, '') != ''
		group by si.contract_name""", as_dict=1)


	dn_item_map = {}
	for item in dn_items:
		dn_item_map.setdefault(item.contract_name, item.amount)

	for item in si_items:
		dn_item_map.setdefault(item.contract_name, item.amount)

	return dn_item_map
