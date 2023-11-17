from odoo import api, fields, models


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

    @api.model
    @api.returns("self", lambda value: value.id)
    def create_data_source(self, vals):
        name = vals.get("name")

        data_source_id = self.env["spp.data.source"].search(
            [("name", "=", name)], limit=1
        )

        if not data_source_id:
            paths = []
            if vals.get("paths"):
                paths = vals.pop("paths")

            data_source_id = self.env["spp.data.source"].create(vals)

            for path in paths:
                self.env["spp.data.source.path"].create(
                    {
                        "data_source_id": data_source_id.id,
                        "name": path.get("name"),
                        "path": path.get("path"),
                    }
                )

        return data_source_id
