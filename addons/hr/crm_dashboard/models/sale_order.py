from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def get_top_customers_chart(self):
        """Returns data formatted for Chart.js (Top 10 Customers by Sales)."""
        query = """
            SELECT partner_id, SUM(amount_total) as total_sales
            FROM sale_order
            WHERE state IN ('sale', 'done')  -- Consider only confirmed orders
            GROUP BY partner_id
            ORDER BY total_sales DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        customers = self.env["res.partner"].browse([rec[0] for rec in results])

        return {
            "labels": [customer.name for customer in customers],
            "data": [rec[1] for rec in results],
        }

    @api.model
    def get_top_customers_chart_new(self):
        """Returns top 10 customers by total sales."""
        query = """
            SELECT partner_id, SUM(amount_total) as total_sales
            FROM sale_order
            WHERE state IN ('sale', 'done')  -- Consider only confirmed orders
            GROUP BY partner_id
            ORDER BY total_sales DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        # Fetch customer names
        customers = self.env["res.partner"].browse([rec[0] for rec in results])

        return [
            {
                "customer": customer.name,  # Customer name
                "total_sales": rec[1],  # Total sales amount
            }
            for rec, customer in zip(results, customers)
        ]


    @api.model
    def get_top_vendors_chart_new(self):
        """Returns top 10 vendors by total sales."""
        query = """
            SELECT partner_id, SUM(amount_total) as total_sales
            FROM sale_order
            WHERE state IN ('sale', 'done')  -- Only confirmed orders
            GROUP BY partner_id
            ORDER BY total_sales DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        # Fetch vendor names (assuming vendors are also stored in the 'res.partner' model)
        vendors = self.env["res.partner"].browse([rec[0] for rec in results])

        return [
            {
                "vendor": vendor.name,  # Vendor name
                "total_sales": rec[1],  # Total sales amount
            }
            for rec, vendor in zip(results, vendors)
        ]


        from datetime import datetime, timedelta

    @api.model
    def get_monthly_sales_chart(self):
        """Returns total sales per month for the last 12 months."""
        query = """
            SELECT TO_CHAR(date_order, 'YYYY-MM') AS month, SUM(amount_total) as total_sales
            FROM sale_order
            WHERE state IN ('sale', 'done')  -- Only confirmed orders
            AND date_order >= (CURRENT_DATE - INTERVAL '12 months')
            GROUP BY month
            ORDER BY month ASC
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        return {
            "labels": [rec[0] for rec in results],  # Month-Year format (e.g., "2024-01")
            "data": [rec[1] for rec in results],  # Total sales for each month
        }





    # @api.model
    # def get_top_products_chart(self):
    #     """Returns top 10 products by sales amount."""
    #     query = """
    #         SELECT sol.product_id, SUM(sol.price_total) as total_sales
    #         FROM sale_order_line sol
    #         JOIN sale_order so ON sol.order_id = so.id
    #         WHERE so.state IN ('sale', 'done')  -- Only confirmed orders
    #         GROUP BY sol.product_id
    #         ORDER BY total_sales DESC
    #         LIMIT 10
    #     """
    #     self._cr.execute(query)
    #     results = self._cr.fetchall()

    #     products = self.env["product.product"].browse([rec[0] for rec in results])

    #     return {
    #         "labels": [product.name for product in products],
    #         "data": [rec[1] for rec in results],
    #     }

    @api.model
    def get_top_products_chart(self):
        """Returns top 10 products by sales amount."""
        query = """
            SELECT sol.product_id, SUM(sol.price_total) as total_sales
            FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id = so.id
            WHERE so.state IN ('sale', 'done')  -- Only confirmed orders
            GROUP BY sol.product_id
            ORDER BY total_sales DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        return [
            {
                "product": self.env["product.product"].browse(rec[0]).name,  # Product name
                "sales_amount": rec[1],  # Total sales amount
            }
            for rec in results
        ]



    @api.model
    def get_top_quotations_chart(self):
        """Returns top 10 quotations by revenue."""
        query = """
            SELECT so.id, so.name, so.amount_total
            FROM sale_order so
            WHERE so.state = 'draft'  -- Only quotations
            ORDER BY so.amount_total DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        return [
            {
                "quotation": rec[1],  # Quotation number (e.g., S00023)
                "revenue": rec[2],  # Quotation total amount
            }
            for rec in results
        ]

    @api.model
    def get_top_customers_chart(self):
        """Returns top 10 customers by total sales amount."""
        query = """
            SELECT so.partner_id, SUM(so.amount_total) as total_sales
            FROM sale_order so
            WHERE so.state IN ('sale', 'done')  -- Only confirmed orders
            GROUP BY so.partner_id
            ORDER BY total_sales DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        customers = self.env["res.partner"].browse([rec[0] for rec in results])

        return {
            "labels": [customer.name for customer in customers],
            "data": [rec[1] for rec in results],
        }


    @api.model
    def get_top_rfq_chart(self):
        """Returns top 10 RFQs (Requests for Quotation) by amount."""
        query = """
            SELECT id, name, amount_total
            FROM purchase_order
            WHERE state = 'draft'  -- Only RFQs
            ORDER BY amount_total DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        return [
            {
                "rfq": rec[1],  # RFQ Number (e.g., PO00012)
                "revenue": rec[2],  # RFQ total amount
            }
            for rec in results
        ]

    @api.model
    def get_top_orders_chart(self):
        """Returns top 10 purchase orders by total amount."""
        query = """
            SELECT id, name, amount_total
            FROM purchase_order
            WHERE state IN ('purchase', 'done')  -- Only confirmed orders
            ORDER BY amount_total DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        return [
            {
                "order": rec[1],  # Purchase Order Number (e.g., PO00023)
                "revenue": rec[2],  # Order total amount
            }
            for rec in results
        ]

    @api.model
    def get_top_vendors_chart(self):
        """Returns top 10 vendors by total purchase amount."""
        query = """
            SELECT partner_id, SUM(amount_total) as total_spent
            FROM purchase_order
            WHERE state IN ('purchase', 'done')  -- Only confirmed orders
            GROUP BY partner_id
            ORDER BY total_spent DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        vendors = self.env["res.partner"].browse([rec[0] for rec in results])

        return {
            "labels": [vendor.name for vendor in vendors],
            "data": [rec[1] for rec in results],
        }



    @api.model
    def get_top_sales_orders_chart(self):
        """Returns top 10 sales orders by revenue."""
        query = """
            SELECT so.id, so.name, so.amount_total
            FROM sale_order so
            WHERE so.state IN ('sale', 'done')  -- Only confirmed orders
            ORDER BY so.amount_total DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        return [
            {
                "order": rec[1],  # Sales order number (e.g., SO0001)
                "revenue": rec[2],  # Sales order total amount
            }
            for rec in results
        ]



    # @api.model
    # def get_top_invoices_chart(self):
    #     """Returns top 10 invoices by total amount."""
    #     query = """
    #         SELECT id, number, amount_total
    #         FROM account_move
    #         WHERE move_type = 'out_invoice' AND state = 'posted'  -- Only posted invoices
    #         ORDER BY amount_total DESC
    #         LIMIT 10
    #     """
    #     self._cr.execute(query)
    #     results = self._cr.fetchall()

    #     return [
    #         {
    #             "invoice": rec[1],  # Invoice Number (e.g., INV/2025/001)
    #             "revenue": rec[2],  # Invoice total amount
    #         }
    #         for rec in results
    #     ]










































# from odoo import models, fields, api

# class HREmployee(models.Model):
#     _inherit = "hr.employee"

#     @api.model
#     def get_hr_metrics_chart(self):
#         """Returns data formatted for Chart.js for various HR metrics."""
        
#         # Contract Running vs Exit
#         query_contracts = """
#             SELECT state, COUNT(*)
#             FROM hr_contract
#             GROUP BY state
#         """
#         self._cr.execute(query_contracts)
#         results_contracts = self._cr.fetchall()
#         contract_labels = ["Running", "Exit"]
#         contract_data = [0, 0]
#         for state, count in results_contracts:
#             if state == 'open':
#                 contract_data[0] = count
#             elif state == 'close':
#                 contract_data[1] = count

#         # Turnover Rate
#         query_turnover = """
#             SELECT COUNT(*)
#             FROM hr_employee
#             WHERE active = False
#         """
#         self._cr.execute(query_turnover)
#         turnover_count = self._cr.fetchone()[0]

#         query_total_employees = """
#             SELECT COUNT(*)
#             FROM hr_employee
#             WHERE active = True
#         """
#         self._cr.execute(query_total_employees)
#         total_employees = self._cr.fetchone()[0]

#         turnover_rate = (turnover_count / total_employees) * 100 if total_employees > 0 else 0

#         # Absent Rate
#         query_absent = """
#             SELECT COUNT(*)
#             FROM hr_leave
#             WHERE state = 'validate'
#         """
#         self._cr.execute(query_absent)
#         absent_count = self._cr.fetchone()[0]

#         absent_rate = (absent_count / total_employees) * 100 if total_employees > 0 else 0

#         # Pending Leaves
#         query_pending_leaves = """
#             SELECT COUNT(*)
#             FROM hr_leave
#             WHERE state = 'confirm'
#         """
#         self._cr.execute(query_pending_leaves)
#         pending_leaves = self._cr.fetchone()[0]

#         # Contract Expiration Dates
#         query_contract_expiration = """
#             SELECT date_end, COUNT(*)
#             FROM hr_contract
#             WHERE date_end IS NOT NULL
#             GROUP BY date_end
#             ORDER BY date_end
#         """
#         self._cr.execute(query_contract_expiration)
#         results_contract_expiration = self._cr.fetchall()
#         contract_expiration_labels = [str(rec[0]) for rec in results_contract_expiration]
#         contract_expiration_data = [rec[1] for rec in results_contract_expiration]

#         return {
#             "contract_running_vs_exit": {
#                 "labels": contract_labels,
#                 "data": contract_data,
#             },
#             "turnover_rate": turnover_rate,
#             "absent_rate": absent_rate,
#             "pending_leaves": pending_leaves,
#             "contract_expiration": {
#                 "labels": contract_expiration_labels,
#                 "data": contract_expiration_data,
#             },
#         }




# from odoo import models, fields, api

# class HREmployee(models.Model):
#     _inherit = "hr.employee"

#     @api.model
#     def get_hr_metrics_chart(self):
#         """Returns data formatted for Chart.js for various HR metrics."""
        
#         # Contract Running vs Exit
#         query_contracts = """
#             SELECT state, COUNT(*)
#             FROM hr_contract
#             GROUP BY state
#         """
#         self._cr.execute(query_contracts)
#         results_contracts = self._cr.fetchall()
#         contract_labels = ["Running", "Exit"]
#         contract_data = [0, 0]
#         for state, count in results_contracts:
#             if state == 'open':
#                 contract_data[0] = count
#             elif state == 'close':
#                 contract_data[1] = count

#         # Turnover Rate
#         query_turnover = """
#             SELECT COUNT(*)
#             FROM hr_employee
#             WHERE active = False
#         """
#         self._cr.execute(query_turnover)
#         turnover_count = self._cr.fetchone()[0]

#         query_total_employees = """
#             SELECT COUNT(*)
#             FROM hr_employee
#             WHERE active = True
#         """
#         self._cr.execute(query_total_employees)
#         total_employees = self._cr.fetchone()[0]

#         turnover_rate = (turnover_count / total_employees) * 100 if total_employees > 0 else 0

#         # Absent Rate
#         query_absent = """
#             SELECT COUNT(*)
#             FROM hr_leave
#             WHERE state = 'validate'
#         """
#         self._cr.execute(query_absent)
#         absent_count = self._cr.fetchone()[0]

#         absent_rate = (absent_count / total_employees) * 100 if total_employees > 0 else 0

#         # Pending Leaves
#         query_pending_leaves = """
#             SELECT COUNT(*)
#             FROM hr_leave
#             WHERE state = 'confirm'
#         """
#         self._cr.execute(query_pending_leaves)
#         pending_leaves = self._cr.fetchone()[0]

#         # Contract Expiration Dates
#         query_contract_expiration = """
#             SELECT date_end, COUNT(*)
#             FROM hr_contract
#             WHERE date_end IS NOT NULL
#             GROUP BY date_end
#             ORDER BY date_end
#         """
#         self._cr.execute(query_contract_expiration)
#         results_contract_expiration = self._cr.fetchall()
#         contract_expiration_labels = [str(rec[0]) for rec in results_contract_expiration]
#         contract_expiration_data = [rec[1] for rec in results_contract_expiration]

#         # Total Jobs
#         query_total_jobs = """
#             SELECT COUNT(*) FROM hr_job
#         """
#         self._cr.execute(query_total_jobs)
#         total_jobs = self._cr.fetchone()[0]

#         # Total Leaves
#         query_total_leaves = """
#             SELECT COUNT(*) FROM hr_leave
#         """
#         self._cr.execute(query_total_leaves)
#         total_leaves = self._cr.fetchone()[0]

#         return {
#             "contract_running_vs_exit": {
#                 "labels": contract_labels,
#                 "data": contract_data,
#             },
#             "turnover_rate": turnover_rate,
#             "absent_rate": absent_rate,
#             "pending_leaves": pending_leaves,
#             "contract_expiration": {
#                 "labels": contract_expiration_labels,
#                 "data": contract_expiration_data,
#             },
#             "total_jobs": total_jobs,
#             "total_leaves": total_leaves,
#         }







from odoo import models, fields, api

class HREmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def get_hr_metrics_chart(self):
        """Returns data formatted for Chart.js for various HR metrics."""
        
        # Contract Running vs Exit
        query_contracts = """
            SELECT state, COUNT(*)
            FROM hr_contract
            GROUP BY state
        """
        self._cr.execute(query_contracts)
        results_contracts = self._cr.fetchall()
        contract_labels = ["Running", "Exit"]
        contract_data = [0, 0]
        for state, count in results_contracts:
            if state == 'open':
                contract_data[0] = count
            elif state == 'close':
                contract_data[1] = count

        # Turnover Rate
        query_turnover = """
            SELECT COUNT(*)
            FROM hr_employee
            WHERE active = False
        """
        self._cr.execute(query_turnover)
        turnover_count = self._cr.fetchone()[0]

        query_total_employees = """
            SELECT COUNT(*)
            FROM hr_employee
            WHERE active = True
        """
        self._cr.execute(query_total_employees)
        total_employees = self._cr.fetchone()[0]

        turnover_rate = (turnover_count / total_employees) * 100 if total_employees > 0 else 0

        # Absent Rate
        query_absent = """
            SELECT COUNT(*)
            FROM hr_leave
            WHERE state = 'validate'
        """
        self._cr.execute(query_absent)
        absent_count = self._cr.fetchone()[0]

        absent_rate = (absent_count / total_employees) * 100 if total_employees > 0 else 0

        # Pending Leaves
        query_pending_leaves = """
            SELECT COUNT(*)
            FROM hr_leave
            WHERE state = 'confirm'
        """
        self._cr.execute(query_pending_leaves)
        pending_leaves = self._cr.fetchone()[0]

        # Contract Expiration Dates
        query_contract_expiration = """
            SELECT date_end, COUNT(*)
            FROM hr_contract
            WHERE date_end IS NOT NULL
            GROUP BY date_end
            ORDER BY date_end
        """
        self._cr.execute(query_contract_expiration)
        results_contract_expiration = self._cr.fetchall()
        contract_expiration_labels = [str(rec[0]) for rec in results_contract_expiration]
        contract_expiration_data = [rec[1] for rec in results_contract_expiration]

        # Total Jobs
        query_total_jobs = """
            SELECT COUNT(*) FROM hr_job
        """
        self._cr.execute(query_total_jobs)
        total_jobs = self._cr.fetchone()[0]

        # Total Leaves
        query_total_leaves = """
            SELECT COUNT(*) FROM hr_leave
        """
        self._cr.execute(query_total_leaves)
        total_leaves = self._cr.fetchone()[0]

        # Total Departments
        query_total_departments = """
            SELECT COUNT(*) FROM hr_department
        """
        self._cr.execute(query_total_departments)
        total_departments = self._cr.fetchone()[0]

        # Total Active Employees with Running Contracts
        query_active_employees_with_contract = """
            SELECT COUNT(*)
            FROM hr_employee e
            JOIN hr_contract c ON e.id = c.employee_id
            WHERE e.active = True AND c.state = 'open'
        """
        self._cr.execute(query_active_employees_with_contract)
        total_active_employees_with_contract = self._cr.fetchone()[0]

        return {
            "contract_running_vs_exit": {
                "labels": contract_labels,
                "data": contract_data,
            },
            "turnover_rate": turnover_rate,
            "absent_rate": absent_rate,
            "pending_leaves": pending_leaves,
            "contract_expiration": {
                "labels": contract_expiration_labels,
                "data": contract_expiration_data,
            },
            "total_jobs": total_jobs,
            "total_leaves": total_leaves,
            "total_departments": total_departments,
            "total_active_employees_with_running_contract": total_active_employees_with_contract,
        }

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def get_top_invoices_chart(self):
        """Returns top 10 invoices by total amount."""
        query = """
            SELECT id, name, amount_total
            FROM account_move
            WHERE move_type = 'out_invoice' AND state = 'posted'  -- Only posted invoices
            ORDER BY amount_total DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        return [
            {
                "invoice": rec[1],  # Invoice Number (e.g., INV/2025/001)
                "revenue": rec[2],  # Invoice total amount
            }
            for rec in results
        ]


    @api.model
    def get_monthly_sales_chart(self):
        """Returns monthly sales revenue for the past 12 months."""
        query = """
            SELECT DATE_TRUNC('month', invoice_date) AS month, SUM(amount_total) as total_revenue
            FROM account_move
            WHERE move_type = 'out_invoice' AND state = 'posted'
            GROUP BY month
            ORDER BY month ASC
            LIMIT 12
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        return {
            "labels": [rec[0].strftime('%Y-%m') for rec in results],  # Format: YYYY-MM
            "data": [rec[1] for rec in results],
        }

    @api.model
    def get_all_events(self):
        """Fetches all events from the event module."""
        events = self.env['event.event'].search([])
        return [
            {
                "name": event.name,
                "start_date": event.date_begin,
                "end_date": event.date_end,
                "location": event.address_id.name if event.address_id else "",
            }
            for event in events
        ]


from odoo import models, api

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # @api.model
    # def get_top_manufactured_products_chart(self):
    #     """Returns the top 10 manufactured products by quantity produced."""
    #     query = """
    #         SELECT product_id, SUM(product_qty) as total_produced
    #         FROM mrp_production
    #         WHERE state = 'done'  -- Only completed manufacturing orders
    #         GROUP BY product_id
    #         ORDER BY total_produced DESC
    #         LIMIT 10
    #     """
    #     self._cr.execute(query)
    #     results = self._cr.fetchall()

    #     products = self.env["product.product"].browse([rec[0] for rec in results])

    #     return {
    #         "labels": [product.name for product in products],
    #         "data": [rec[1] for rec in results],
    #     }

    @api.model
    def get_top_manufactured_products_chart(self):
        """Returns top 10 manufactured products by quantity produced."""
        query = """
            SELECT product_id, SUM(product_qty) as total_produced
            FROM mrp_production
            WHERE state = 'done'  -- Only completed manufacturing orders
            GROUP BY product_id
            ORDER BY total_produced DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        # Fetch product names from product.product model
        products = self.env["product.product"].browse([rec[0] for rec in results])

        return [
            {
                "product": product.name,  # Product name
                "total_produced": rec[1],  # Total quantity produced
            }
            for rec, product in zip(results, products)
        ]



class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    # @api.model
    # def get_top_workcenters_chart(self):
    #     """Returns the top 10 work centers by total operation duration (hours)."""
    #     query = """
    #         SELECT workcenter_id, SUM(duration) / 60.0 as total_hours
    #         FROM mrp_workorder
    #         WHERE state = 'done'  -- Only completed work orders
    #         GROUP BY workcenter_id
    #         ORDER BY total_hours DESC
    #         LIMIT 10
    #     """
    #     self._cr.execute(query)
    #     results = self._cr.fetchall()

    #     workcenters = self.env["mrp.workcenter"].browse([rec[0] for rec in results])

    #     return {
    #         "labels": [workcenter.name for workcenter in workcenters],
    #         "data": [rec[1] for rec in results],  # Total hours
    #     }

    @api.model
    def get_top_workcenters_chart(self):
        """Returns top 10 work centers by total operation duration (hours)."""
        query = """
            SELECT workcenter_id, SUM(duration) / 60.0 as total_hours
            FROM mrp_workorder
            WHERE state = 'done'  -- Only completed work orders
            GROUP BY workcenter_id
            ORDER BY total_hours DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        # Fetch work center names
        workcenters = self.env["mrp.workcenter"].browse([rec[0] for rec in results])

        return [
            {
                "workcenter": workcenter.name,  # Work center name
                "total_hours": rec[1],  # Total hours
            }
            for rec, workcenter in zip(results, workcenters)
        ]

