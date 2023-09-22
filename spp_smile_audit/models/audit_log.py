# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, fields, models
from odoo.tools.safe_eval import datetime, safe_eval

_logger = logging.getLogger(__name__)
CUSTOM_LOG_MODELS = ["g2p.program"]


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
                    (
                        "create_date",
                        "<=",
                        fields.Datetime.add(self.create_date, seconds=1),
                    ),
                    ("user_id", "=", self.user_id.id),
                ]
            )
            if not related_logs:
                continue
            sub_logs.append((field.string, related_logs))
        custom_logs = self._get_custom_logs()
        if custom_logs:
            sub_logs += custom_logs
        return sub_logs

    def _get_custom_logs(self):
        self.ensure_one()
        res = []
        if self.model not in CUSTOM_LOG_MODELS:
            return res
        if self.model == "g2p.program":
            all_manager_model_names = [
                item[0]
                for item in self.env[
                    "g2p.eligibility.manager"
                ]._selection_manager_ref_id()
            ]
            for manager_model in all_manager_model_names:
                related_records = (
                    self.env[manager_model]
                    .sudo()
                    .search([("program_id", "=", self.res_id)])
                )
                related_logs = self.search(
                    [
                        ("model", "=", manager_model),
                        ("res_id", "in", related_records.ids),
                        (
                            "create_date",
                            ">=",
                            fields.Datetime.add(self.create_date, seconds=-1),
                        ),
                        (
                            "create_date",
                            "<=",
                            fields.Datetime.add(self.create_date, seconds=1),
                        ),
                        ("user_id", "=", self.user_id.id),
                    ]
                )
                res.append(("Manager", related_logs))
            return res

    def _get_content(self):
        self.ensure_one()
        content = []
        data = safe_eval(self.data or "{}", {"datetime": datetime})
        _logger.info("Data: %s" % data)
        RecordModel = self.env[self.model_id.model]
        record = f"{self.model}({self.res_id})"
        for fname in set(data["new"].keys()) | set(data["old"].keys()):
            field = RecordModel._fields.get(fname)
            if field and (
                not field.groups or self.user_has_groups(groups=field.groups)
            ):
                old_value = self._format_value(field, data["old"].get(fname, ""))
                new_value = self._format_value(field, data["new"].get(fname, ""))
                if old_value != new_value:
                    label = field.get_description(self.env)["string"]
                    content.append([label, record, old_value, new_value])
        for (fname, sub_logs) in self._get_sub_logs():
            for sub_log in sub_logs:
                sub_log_content = sub_log._get_content()
                _logger.info("SUB LOG: %s" % sub_log_content)
                for log in sub_log_content:
                    log[0] = f"{fname} -> {log[0]}"
                content += sub_log_content
        return content

    def _render_html(self):
        for rec in self:
            thead = ""
            for head in (_("Field"), _("Record"), _("Old value"), _("New value")):
                thead += "<th>%s</th>" % head
            thead = "<thead><tr>%s</tr></thead>" % thead
            tbody = ""
            for line in rec._get_content():
                row = ""
                for item in line:
                    row += "<td>%s</td>" % item
                tbody += "<tr>%s</tr>" % row
            tbody = "<tbody>%s</tbody>" % tbody
            rec.data_html = (
                '<table class="o_list_view table table-condensed "'
                '"table-striped">%s%s</table>' % (thead, tbody)
            )
