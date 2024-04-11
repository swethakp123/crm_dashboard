# -*- coding: utf-8 -*-
{
    'name': "CRM Dashboard",
    'version': '17.0.1.0.0',
    'depends': ['base','crm','sale'],
    'category': '',
    'description': """
    CRM Dashboard
    """,
    'data': [
                'security/ir.model.access.csv',
                'views/crm_team_views.xml',
                'views/crm_dashboard_views.xml',
                'views/menu.xml',
             ],
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/chart.js',
            'crm_dashboard/static/src/css/dashboard.css',
            'crm_dashboard/static/src/js/dashboard.js',
            'crm_dashboard/static/src/xml/dashboard.xml',
        ],
    },
    'application': 'True',
    'installable': True,
}