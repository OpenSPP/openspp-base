from odoo import api, models


class IrModuleModule(models.AbstractModel):
    _inherit = "ir.module.module"

    # Override function to fix error when uninstalling smile_audit module
    @api.model
    def _get_audit_rule(self, method):
        for module in self:
            if module.name == "smile_audit" and module.state == "to remove":
                # Return None to not execute _check_audit_rule of audit_rule
                return None
        return super()._get_audit_rule(method)
