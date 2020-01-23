# -*- coding: utf-8 -*-
{
    'name': "Financial Statement Indonesia",

    'summary': """
        Laporan Keuangan Indonesia Full""",

    'description': """
        Long description of module's purpose
    """,

    
    'author': 'firmanrizaldiyusup@gmail.com',
    'website': 'http://www.vitraining.com',


    'category': 'Uncategorized',
    'version': '0.1',


    'depends': ['base','website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/template.xml',
        'views/assets.xml',
        'data/vit_financial_statements.csv',
        'data/inherit_menu.xml',
        'data2/vit_financial_statements.csv',
    ],
}