from odoo import fields, models


class SppDataSource(models.Model):
    _name = "spp.data.source"
    _description = "SPP Data Source"

    AUTH_TYPE_CHOICES = [
        ("basic_authentication", "Basic Authentication"),
        ("bearer_authentication", "Bearer Authentication"),
        ("api_keys", "API Keys"),
    ]

    name = fields.Char("Data Source Name", required=True)
    url = fields.Char(string="Target URL", required=True)

    auth_type = fields.Selection(AUTH_TYPE_CHOICES, required=True)

    data_source_path_ids = fields.One2many(
        "spp.data.source.path", "data_source_id", string="URL Paths"
    )

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The name of the data source must be unique !"),
    ]
