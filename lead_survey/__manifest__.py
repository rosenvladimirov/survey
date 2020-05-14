# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Crm leads Survey",
    'category': 'Marketing',
    'version': '11.0.1.0.0',
    'depends': [
        'survey',
        'partner_survey',
    ],
    'data': [
        'views/crm_lead_views.xml',
        'wizard/survey_email_compose_message.xml',
    ],
    'author': 'Rosen Vladimirov, '
              'Tecnativa, '
              'Camptocamp, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.tecnativa.com',
    'license': 'AGPL-3',
    'installable': True,
}
