# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 CQ Creativi Quadrati snc
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Sistemazioni modulo mrp_repair',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'author': 'Stefano Siccardi @ Creativi Quadrati',
    'website': 'http://www.creativiquadrati.it',
    'license': 'AGPL-3',
    'depends': ['mrp_repair', 'stock'],
    'data': [
        'views/mrp_repair_views.xml',
        'views/stock_warehouse_views.xml',
        'report/mrp_repair_reports.xml',
        'report/mrp_repair_templates_repair_order.xml',
    ],
    'qweb': [
    ],
    'active': False,
    'installable': True
}
