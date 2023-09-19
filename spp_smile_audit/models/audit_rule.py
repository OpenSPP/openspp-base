# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

class AuditRule(models.Model):
    _inherit = "audit.rule"

    @api.model
    @api.returns("self", lambda value: value.id)
    def create_rules(self, vals):
        # Used in creation of rules when installing or upgrading this module
        model_id = vals.get("model_id")
        group_id = vals.get("group_id")

        # to avoid sql constraints error when upgrading this module
        if model_id and group_id:
            rule = self.env["audit.rule"].search(
                [
                    ("model_id", "=", model_id),
                    ("group_id", "=", group_id),
                ],
                limit=1,
            )
            if rule:
                return rule

        return self.env["audit.rule"].create(vals)
