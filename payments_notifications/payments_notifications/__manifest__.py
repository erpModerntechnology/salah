# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Odoo14 installments ',
    'version': '14',
    'category': 'Installments ',
    'summary': ' installments and Management  For Odoo14 ',
    'sequence': '5',
    'author': 'Ahmed khalil',
    'depends': ['account','account_reports'],
    'data': [
        # 'security/groups.xml',
        'security/ir.model.access.csv',
        'views/payments.xml',
        'views/installment_report.xml',
        'views/installment_template.xml',

        'data/crons.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
    #'images': ['static/description/banner.gif'],
}

