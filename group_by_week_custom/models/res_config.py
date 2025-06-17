from odoo import fields, models, api, _
from ast import literal_eval


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    model_ids = fields.Many2many('ir.model', string="Models")
    set_globally = fields.Boolean(string="Set Golably", default=False)

    def set_values(self):
        res = super(ResConfigSettingsInherit, self).set_values()
        self.env['ir.config_parameter'].set_param('group_by_week_custom.model_ids', self.model_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param('group_by_week_custom.set_globally', self.set_globally)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        model_ids = params.get_param('group_by_week_custom.model_ids')
        res.update(
            set_globally=params.get_param('group_by_week_custom.set_globally'),
            model_ids=[(6, 0, literal_eval(model_ids))] if model_ids else False
        )
        return res