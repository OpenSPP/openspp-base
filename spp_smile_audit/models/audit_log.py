# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models
from odoo.tools.safe_eval import datetime, safe_eval

_logger = logging.getLogger(__name__)


class AuditLog(models.Model):
    _inherit = "audit.log"

    def _get_sub_logs(self):
        self.ensure_one()
        sub_logs = []
        log_model = self.env[self.model].sudo()
        log_res = log_model.browse(self.res_id)
        if not log_res.exists():
            return sub_logs
        for (_fname, field) in log_model._fields.items():
            if field.type not in ("one2many", "many2many"):
                continue
            related_records = getattr(log_res, field.name, None)
            if not related_records:
                continue
            related_logs = self.search(
                [
                    ("model", "=", related_records._name),
                    ("res_id", "in", related_records.ids),
                    (
                        "create_date",
                        ">=",
                        fields.Datetime.add(self.create_date, seconds=-1),
                    ),
                    ("user_id", "=", self.user_id.id),
                ]
            )
            if not related_logs:
                continue
            sub_logs.append((field.string, related_logs))
        return sub_logs

    def _get_content(self):
        self.ensure_one()
        content = []
        data = safe_eval(self.data or "{}", {"datetime": datetime})
        _logger.info("Data: %s" % data)
        RecordModel = self.env[self.model_id.model]
        for fname in set(data["new"].keys()) | set(data["old"].keys()):
            field = RecordModel._fields.get(fname)
            if field and (
                not field.groups or self.user_has_groups(groups=field.groups)
            ):
                old_value = self._format_value(field, data["old"].get(fname, ""))
                new_value = self._format_value(field, data["new"].get(fname, ""))
                if old_value != new_value:
                    label = field.get_description(self.env)["string"]
                    content.append([label, old_value, new_value])
        for (fname, sub_logs) in self._get_sub_logs():
            for sub_log in sub_logs:
                sub_log_content = sub_log._get_content()
                _logger.info("SUB LOG: %s" % sub_log_content)
                for log in sub_log_content:
                    log[0] = f"{fname} -> {log[0]}"
                content += sub_log_content
        return content
