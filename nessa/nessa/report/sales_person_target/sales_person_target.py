# Copyright (c) 2023, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None): 
	months = [
			"Apr",
			"May",
			"Jun",
			"Jul",
			"Aug",
			"Sep",
			"Oct",
			"Nov",
			"Dec",
			"Jan",
			"Feb",
			"Mar"			
		]	
	columns = [
		{
			"label": "Sales Person",
			"fieldtype": "Link",
			"fieldname": "sales_person_name",
			"width": 180,
			"options" : "Sales Person"
		},
		{
			"label": "Month",
			"fieldtype": "Data",
			"fieldname": "month",
			"width": 70,
		},		
		{
			"label": "Target Amt",
			"fieldtype": "Currency",
			"fieldname": "target_amount",
			"width": 120,
		},		
		{
			"label": "Achieved Amt",
			"fieldtype": "Currency",
			"fieldname": "allocated_amount",
			"width": 140,
		},		
		{
			"label": "Amt Eligibile For Commission",
			"fieldtype": "Currency",
			"fieldname": "amount_eligible_for_comission",
			"width": 200,
		},		
		{
			"label": "% Commission",
			"fieldtype": "Percent",
			"fieldname": "commission_rate",
			"width": 50,
		},
		{
		    "label": "Commission Amt",
		    "fieldtype": "Currency",
		    "fieldname": "commission_amount",
		    "width": 150,
		},
		{
		    "label": "Performance Target",
		    "fieldtype": "Currency",
		    "fieldname": "performance_target_cf",
		    "width": 150,
		}		
	   
	]
	data =[]
	if not filters.get("sales_person_name"):
		sales_person_name='Sales Team' 
	else:
		sales_person_name=filters.get("sales_person_name") 
	lft, rgt = frappe.get_value("Sales Person", sales_person_name, ["lft", "rgt"])	
	filters['lft']=lft
	filters['rgt']=rgt

	sales_person_list=frappe.db.sql(
		"""select sp.name,IFNULL(sp.commission_rate,0) as commission_rate,sp.performance_target_cf,td.target_amount/12 as per_month_target_amount from `tabSales Person`  sp
			left outer join `tabTarget Detail` td
			on td.parent=sp.name
			{where_conditions}
			order by name asc""".format(
            where_conditions=get_sales_person_conditions(filters),
        ),
        filters,
        as_dict=True)

	if len(sales_person_list)>0:

		valid_sales_persons = [d.name for d in sales_person_list]
		where_fiscal_filter=''
		if filters.get('fiscal_year'):
			fiscal_year = get_fiscal_year(fiscal_year=filters.get('fiscal_year'), as_dict=True)
			where_fiscal_filter=" and si.posting_date between '{year_start_date}' and '{year_end_date}'".format(year_start_date=fiscal_year.year_start_date,year_end_date=fiscal_year.year_end_date)

		allocated_amount_list = frappe.db.sql(
			"""select LEFT(MONTHNAME(STR_TO_DATE( MONTH(si.posting_date), '%%m')),3) as si_month,sum(allocated_amount) as achieved_amount,st.sales_person
	from `tabSales Team` st inner join `tabSales Invoice` si on st.parent=si.name  
	where st.docstatus=1 and st.parent=si.name 
	{where_fiscal_filter} and st.sales_person in ({valid_sales_person})
	group by st.sales_person,MONTH(si.posting_date)
	order by st.sales_person,si.posting_date
		""".format(where_fiscal_filter=where_fiscal_filter,valid_sales_person=",".join(["%s"]*len(valid_sales_persons))),
		tuple(valid_sales_persons),
		as_dict=True)
		for sales_person in sales_person_list:
			found_sales_person=False
			for list_month in months:
				found_month_for_sales_person=False
				for allocated_amount in allocated_amount_list:
					if allocated_amount.si_month==list_month and allocated_amount.sales_person==sales_person.name:
							found_sales_person=True
							found_month_for_sales_person=True
							amount_eligible_for_comission=allocated_amount.achieved_amount-flt(sales_person.per_month_target_amount,2)
							commission_amount=flt(((amount_eligible_for_comission/100)*(flt(sales_person.commission_rate))),2)
							data.append([allocated_amount.sales_person,allocated_amount.si_month,flt(sales_person.per_month_target_amount,2),allocated_amount.achieved_amount,
		    					amount_eligible_for_comission,flt(sales_person.commission_rate,2),commission_amount,sales_person.performance_target_cf])
				if found_month_for_sales_person==False:
					amount_eligible_for_comission=0-flt(sales_person.per_month_target_amount,2)
					commission_amount=flt(((amount_eligible_for_comission/100)*(flt(sales_person.commission_rate))),2)
					data.append([sales_person.name,list_month,flt(sales_person.per_month_target_amount,2),0,amount_eligible_for_comission,flt(sales_person.commission_rate,2),commission_amount,sales_person.performance_target_cf])					
			# if found_sales_person==False:
			# 	for list_month in months:
			# 		amount_eligible_for_comission=0-flt(sales_person.per_month_target_amount,2)
			# 		commission_amount=flt(((amount_eligible_for_comission/100)*(flt(sales_person.commission_rate))),2)
			# 		data.append([sales_person.name,list_month,flt(sales_person.per_month_target_amount,2),0,amount_eligible_for_comission,flt(sales_person.commission_rate,2),commission_amount,sales_person.performance_target_cf])					

	
	message="for the selected Fiscal Year, Sales Person will show up only if Sales Person->Sales Person Targets(child table)->Fiscal Year value is defined."	
	return columns, data,message

def get_sales_person_conditions(filters):
	where_clause = []

	where_clause.append("sp.lft >=  %(lft)s")
	where_clause.append("sp.rgt  <=  %(rgt)s")
	where_clause.append("sp.enabled=1")

	if filters.get('fiscal_year'):
		fiscal_year = get_fiscal_year(fiscal_year=filters.get('fiscal_year'), as_dict=True)
		where_clause.append("td.fiscal_year=%(fiscal_year)s")	
	condition_for_sp=" where " + " and ".join(where_clause) if where_clause else ""
	return 	condition_for_sp