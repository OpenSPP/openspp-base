from odoo import api, fields, models


class G2pProgramMembershipManager(models.AbstractModel):
    _inherit = "g2p.program_membership.manager"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if self._get_audit_rule("create") and self.program_id._get_audit_rule("write"):
            for rec in res:
                rec.program_id.write({"write_date": fields.Datetime.now()})
        return res

    def write(self, vals):
        res = super().write(vals)
        if self._get_audit_rule("write") and self.program_id._get_audit_rule("write"):
            self.program_id.write({"write_date": fields.Datetime.now()})
        return res
