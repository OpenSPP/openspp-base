from odoo import fields, models


class SppDataSourcePath(models.Model):
    _name = "spp.data.source.path"
    _description = "SPP Data Source Path"

    data_source_id = fields.Many2one("spp.data.source")
    name = fields.Char("Data Source Path Name", required=True)
    path = fields.Char("URL Path", required=True)
