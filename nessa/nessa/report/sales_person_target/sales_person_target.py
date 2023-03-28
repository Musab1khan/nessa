# Copyright (c) 2023, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt



def execute(filters=None): 
	columns = [
		{
			"label": "Sales Person",
			"fieldtype": "Link",
			"fieldname": "sales_person_name",
			"width": 150,
			"options" : "Sales Person"
		},
		{
			"label": "Commission %",
			"fieldtype": "Float",
			"fieldname": "commission_rate",
			"width": 100,
		},
		{
			"label": "Target Amount",
			"fieldtype": "Currency",
			"fieldname": "target_amount",
			"width": 120,
		},
		{
			"label": "Achieved Amount",
			"fieldtype": "Currency",
			"fieldname": "allocated_amount",
			"width": 120,
		},
		{
			"label": "Amount elibile for Commission",
			"fieldtype": "Currency",
			"fieldname": "amount_eligible_for_commission",
			"width": 120,
		},
		{
			"label": "Posting Date",
			"fieldtype": "Date",
			"fieldname": "posting_date",
			"width": 100,
		},
		{
			"label": "Month",
			"fieldtype": "Data",
			"fieldname": "month",
			"width": 100,
		},
		{
		    "label": "Commission Amount",
		    "fieldtype": "Currency",
		    "fieldname": "commission_amount",
		    "width": 150,
		}
	   
	]
	data =[]
	
	
	commissions = frappe.get_all("Sales Person",filters=filters,fields=["sales_person_name","commission_rate"])

	print('commisssion',commissions)

	
	
	for commission in commissions:

		target_amount = 0.0
		allocated_amount =0.0
		amount_eligible_for_commission =0.0
		commission_amount = 0.0

		targets = frappe.db.get_all("Target Detail", filters={"parent": commission.sales_person_name}, fields=["target_amount"])
		print(targets)
		
		
		for target in targets:
			target_amount += flt(target.target_amount)
			

		#end of commision loop 
	
		invoices = frappe.get_all("Sales Invoice", fields=["name", "posting_date"],
								   filters=[["Sales Team", "sales_person", "=", commission.sales_person_name]]
								   )
		print('invoicee',invoices)
		
		posting_date = None
		month = None
		for invoice in invoices:
			posting_date = invoice["posting_date"]
			# break
		
			month =(posting_date).strftime('%B')
			print(month)
			

			sales_team = frappe.get_list("Sales Team",filters={"parent": invoice["name"]},fields=["sales_person","allocated_amount"],as_list=True)
			print('sales team',sales_team)
		
			# Loop through each Sales Team record and filter by the specified salesperson
			for team_member in sales_team:
				if team_member[0] == commission.sales_person_name:
					allocated_amount = team_member[1]
					print(allocated_amount)

				amount_eligible_for_commission = (allocated_amount) - (target_amount)
				print('amount eligible for commission',amount_eligible_for_commission)

				commission_amount = flt((amount_eligible_for_commission/100)*flt(commission.commission_rate))
				print('commission amount',commission_amount)
					 
				data.append([commission.sales_person_name,
					commission.commission_rate,
					target_amount,
					allocated_amount,
					amount_eligible_for_commission,
					posting_date,
					month,
					commission_amount])
	print(data)
		
	return columns, data