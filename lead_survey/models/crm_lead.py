# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Lead(models.Model):
    _inherit = "crm.lead"

#    survey_input_lines = fields.One2many(
#        comodel_name='survey.user_input_line', inverse_name='partner_id',
#        string='Surveys answers')
#    survey_inputs = fields.One2many(
#        comodel_name='survey.user_input', inverse_name='partner_id',
#        string='Surveys')
    survey_input_count = fields.Integer(
        string='Survey number', compute='_compute_survey_input_count',
        store=False)

    @api.depends('email_from')
    def _compute_survey_input_count(self):
        for survey in self:
            survey_emails = self.env['survey.user_input'].search([('email', '=', survey.email_from)])
            survey.survey_input_count = len(survey_emails)

    @api.multi
    def _create_lead_partner(self):
        res = super(Lead, self)._create_lead_partner()
        if res:
            survey_emails = self.env['survey.user_input'].search([('email', '=', res.email)])
            survey_emails.write({'partner_id': res.parent_id and res.parent_id.id or res.id})
        return res

    @api.multi
    def action_send_survey(self):
        """ Open a window to compose an email, pre-filled with the survey message """

        template = self.env.ref('survey.email_template_survey', raise_if_not_found=False)
        survey = self.env['survey.survey'].search([('stage_id.closed', '!=', True)], limit=1)
        local_context = dict(
            self.env.context,
            default_model='survey.survey',
            default_res_id=survey.id,
            default_survey_id=False,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment'
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'survey.mail.compose.message',
            'target': 'new',
            'context': local_context,
        }
