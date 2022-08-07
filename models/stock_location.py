from odoo import _, api, fields, models


class Location(models.Model):
    _inherit = "stock.location"

    def open_transfer_all_wizard(self):
        view_id = self.env.ref("stock_transfer_all.view_transfer_all_wizard").id

        return {
            "name": _("Transfer All"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock_transfer_all.wizard",
            "view_id": view_id,
            "views": [(view_id, "form")],
            "target": "new",
            "context": {},
        }
