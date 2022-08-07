# Copyright 2022 <mj@ayudoo.bg>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

{
    "author": "Michael Jurke, Ayudoo EOOD",
    "name": "Stock Transfer All",
    "version": "0.1",
    "summary": "Transfer stock form one location to another",
    "description": """
        Select the desired product and with a helper dialog you can transfer all
        products, available or not reserved stock from one location to another using
        an internal transfer.
    """,
    "license": "LGPL-3",
    "category": "Inventory/Inventory",
    "support": "support@ayudoo.bg",
    "depends": [
        "base",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_location_view.xml",
        "wizard/transfer_all_view.xml",
    ],
    "application": True,
    "installable": True,
    "demo": [],
}
