# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import uuid

from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import pycompat

emails_split = re.compile(r"[;,\n\r]+")
email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")

class SurveyMailComposeMessage(models.TransientModel):
    _inherit = 'survey.mail.compose.message'

    public = fields.Selection(selection_add=[('direct_private', 'Write private survey (only one response per recipient and per invitation).')])
    email = fields.Char(string='Email', help="This email of recipients will not be converted in contact.")

    #------------------------------------------------------
    # Wizard validation and send
    #------------------------------------------------------
    @api.multi
    def open_url(self):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed """

        SurveyUserInput = self.env['survey.user_input']
        Partner = self.env['res.partner']
        context = self.env.context
        for wizard in self:
            #if not wizard.email and context.get('default_email'):
            #    wizard.email = context.get('default_email')

            def create_token(wizard, partner_id, email):
                if context.get("survey_resent_token"):
                    survey_user_input = SurveyUserInput.search([('survey_id', '=', wizard.survey_id.id),
                        ('state', 'in', ['new', 'skip']), '|', ('partner_id', '=', partner_id),
                        ('email', '=', email)], limit=1)
                    if survey_user_input:
                        return survey_user_input.token
                if wizard.public != 'direct_private':
                    return None
                else:
                    token = pycompat.text_type(uuid.uuid4())
                    # create response with token
                    survey_user_input = SurveyUserInput.create({
                        'survey_id': wizard.survey_id.id,
                        'deadline': wizard.date_deadline,
                        'date_create': fields.Datetime.now(),
                        'type': 'link',
                        'state': 'new',
                        'token': token,
                        'partner_id': partner_id,
                        'email': email})
                    return survey_user_input.token

            #set url
            url = wizard.survey_id.public_url
            url = urls.url_parse(url).path[1:]  # dirty hack to avoid incorrect urls
            partner = Partner.search([('email', '=', wizard.email)], limit=1)
            token = create_token(wizard, partner.parent_id and partner.parent_id.id or partner.id, wizard.email)

            if token:
                url = url + '/' + token

            return {
                'type': 'ir.actions.act_url',
                'name': "Start Survey",
                'target': 'self',
                'url': url
            }
