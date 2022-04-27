# -*- coding: utf-8 -*-


{
    'name': 'Real Estate',
    'depends': [
        'base',
	],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/res_users.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'GPL-3'
}
