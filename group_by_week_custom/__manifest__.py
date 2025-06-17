{
    'name': 'Custom Week Grouping (Sun–Sat)',
    'version': '1.2',
    'author': "JD DEVS",
    'category': 'Tools',
    'depends': ['base', 'base_setup'],
    'description': 'Overrides group_by:week to use Sunday–Saturday instead of ISO Monday–Sunday',
    'data': [
        'views/settings.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
