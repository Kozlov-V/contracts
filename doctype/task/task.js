// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.contract");

cur_frm.add_fetch("contract", "company", "company");

frappe.ui.form.on("Task", {
	refresh: function(frm) {
		var doc = frm.doc;
		if(doc.__islocal) {
			if(!frm.doc.exp_end_date) {
				frm.set_value("exp_end_date", frappe.datetime.add_days(new Date(), 7));
			}
		}


		if(!doc.__islocal) {
			if(frappe.model.can_read("Time Log")) {
				frm.add_custom_button(__("Time Logs"), function() {
					frappe.route_options = {"contract": doc.contract, "task": doc.name}
					frappe.set_route("List", "Time Log");
				}, "icon-list", true);
			}
			if(frappe.model.can_read("Expense Claim")) {
				frm.add_custom_button(__("Expense Claims"), function() {
					frappe.route_options = {"contract": doc.contract, "task": doc.name}
					frappe.set_route("List", "Expense Claim");
				}, "icon-list", true);
			}

			if(frm.perm[0].write) {
				if(frm.doc.status!=="Closed" && frm.doc.status!=="Cancelled") {
					frm.add_custom_button("Close", function() {
						frm.set_value("status", "Closed");
						frm.save();
					});
				} else {
					frm.add_custom_button("Reopen", function() {
						frm.set_value("status", "Open");
						frm.save();
					});
				}
			}
		}
	},

	setup: function(frm) {
		frm.fields_dict.contract.get_query = function() {
			return {
				query: "erpnext.contract.doctype.task.task.get_contract"
			}
		};
	},

	contract: function(frm) {
		if(frm.doc.contract) {
			return get_server_fields('get_contract_details', '','', frm.doc, frm.doc.doctype,
				frm.doc.name, 1);
		}
	},

	validate: function(frm) {
		frm.doc.contract && frappe.model.remove_from_locals("Contract",
			frm.doc.contract);
	},

});

cur_frm.add_fetch('task', 'subject', 'subject');
