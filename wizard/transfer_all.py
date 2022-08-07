from odoo import api, fields, models


class TransferAllWizard(models.TransientModel):
    _name = "stock_transfer_all.wizard"
    _description = "Transfer All Wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("active_model", False) != "stock.location":
            return res

        res["company_id"] = self.env.user.company_id.id

        location = self.env["stock.location"].browse(
            self.env.context.get("active_id", False)
        )
        res["origin_location_id"] = location.id

        warehouse = self.env["stock.warehouse"].search(
            [("lot_stock_id", "=", location.id)], limit=1
        )
        if warehouse:
            res["picking_type_id"] = warehouse.int_type_id.id

        return res

    company_id = fields.Many2one("res.company", required=True, readonly=True)

    origin_location_id = fields.Many2one(
        "stock.location",
        string="Origin Location",
        required=True,
        readonly=True,
    )

    picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Picking Type",
    )

    def _get_destination_location_domain(self):
        domain = [
            "|",
            ("company_id", "=", self.env.user.company_id.id),
            ("company_id", "=", False),
        ]
        return domain

    destination_location_id = fields.Many2one(
        string="Destination Location",
        comodel_name="stock.location",
        required=True,
        domain=_get_destination_location_domain,
    )

    quantities_to_transfer = fields.Selection(
        [
            ("all", "All"),
            ("available", "Available"),
        ],
        string="Quantities To Transfer",
        default="available",
        required=True,
    )

    @api.onchange("quantities_to_transfer")
    def _onchange_quantities_to_transfer(self):
        if not self.quantities_to_transfer:
            self.transfer_line_ids = []
            return

        if self.quantities_to_transfer == "all":
            quantity_field = "quantity"

            def has_quantity(quant):
                return quant.quantity > 0

        else:
            quantity_field = "available_quantity"

            def has_quantity(quant):
                return quant.available_quantity > 0

        quants = self.env["stock.quant"].search(
            [
                ("quantity", ">", 0),
                ("location_id", "=", self.origin_location_id.id),
            ]
        )

        self.transfer_line_ids = self.env["stock_transfer_all.line"].create(
            [
                {
                    "quant_id": q.id,
                    "transfer_quantity": getattr(q, quantity_field),
                }
                for q in quants
                if has_quantity(q)
            ]
        )

    transfer_line_ids = fields.One2many(
        "stock_transfer_all.line",
        "wizard_id",
        string="Transfer Lines",
    )

    def action_create_stock_picking(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_id.id,
                "location_id": self.origin_location_id.id,
                "location_dest_id": self.destination_location_id.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": l.product_id.display_name,
                            "product_id": l.product_id.id,
                            "product_uom": l.product_uom_id.id,
                            "product_uom_qty": l.transfer_quantity,
                            "location_id": self.origin_location_id.id,
                            "location_dest_id": self.destination_location_id.id,
                        },
                    )
                    for l in self.transfer_line_ids
                ],
            }
        )

        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        form_view = [(self.env.ref("stock.view_picking_form").id, "form")]
        if "views" in action:
            action["views"] = form_view + [
                (state, view) for state, view in action["views"] if view != "form"
            ]
        else:
            action["views"] = form_view
        action["res_id"] = picking.id
        return action


class TransferAllLine(models.TransientModel):
    _name = "stock_transfer_all.line"
    _description = "Transfer All Line"

    wizard_id = fields.Many2one(
        "stock_transfer_all.wizard",
        "Wizard",
        readonly=True,
    )

    quant_id = fields.Many2one(
        "stock.quant",
        "Quant",
    )

    product_id = fields.Many2one(
        "product.product",
        "Product",
        related="quant_id.product_id",
        readonly=True,
    )

    product_uom_id = fields.Many2one(
        "uom.uom",
        "Unit of Measure",
        related="quant_id.product_uom_id",
        readonly=True,
    )

    quantity = fields.Float(
        "Quantity",
        digits="Product Unit of Measure",
        readonly=True,
        related="quant_id.quantity",
    )

    available_quantity = fields.Float(
        "Available Quantity",
        digits="Product Unit of Measure",
        readonly=True,
        related="quant_id.available_quantity",
    )

    transfer_quantity = fields.Float(
        "Quantity To Transfer",
        digits="Product Unit of Measure",
    )
