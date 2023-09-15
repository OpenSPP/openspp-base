import logging

from odoo import api, models

_logger = logging.getLogger(__package__)


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

    def _add_action(self):
        if not self.action_id:
            # Check action menu if view audit logs for a model is already existing
            ir_act_window_id = self.env["ir.actions.act_window"].search(
                [
                    ("binding_model_id", "=", self.model_id.id),
                    ("res_model", "=", "audit.log"),
                    ("name", "=", "View audit logs"),
                ],
                limit=1,
            )

            if ir_act_window_id:
                # If action menu is existing, save existing action menu to action_id
                self.action_id = ir_act_window_id
            else:
                # Create action menu
                super()._add_action()

                # Save newly created action menu to all audit rules with the same model
                audit_rule_ids = self.env["audit.rule"].search(
                    [("model_id", "=", self.model_id.id), ("action_id", "=", False)],
                )
                audit_rule_ids.write({"action_id": self.action_id})
        return

    def _deactivate(self):
        if self.action_id:
            # Get number of audit rule using the same action menu
            audit_rule_count = self.env["audit.rule"].search(
                [
                    ("action_id", "=", self.action_id.id),
                    ("active", "=", True),
                ],
                count=True,
            )
            if audit_rule_count == 0:
                # unlink action menu
                super()._deactivate()

        return

    def unlink(self):
        # get number of audit rule with the same model
        audit_rule_count = self.env["audit.rule"].search(
            [("model_id", "=", self.model_id.id)],
            count=True,
        )

        # if only 1 and with menu action, unlink menu action
        if audit_rule_count == 1 and self.action_id:
            self.action_id.unlink()

        super().unlink()

        return
