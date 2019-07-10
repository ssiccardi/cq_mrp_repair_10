# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 CQ Creativi Quadrati snc
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

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class Repair(models.Model):
    _inherit = 'mrp.repair'
    
    ## magazzino di default a magazzino riparazioni WH-Ri
    @api.model
    def _default_stock_location(self):
        warehouse = self.env['stock.warehouse'].search([('is_repair','=',True)])
        if warehouse:
            return warehouse.lot_stock_id.id
        else:
            raise UserError(_("Create default Repair Warehouse."))
        return False
    
    location_id = fields.Many2one(
        'stock.location', 'Current Location',
        default=_default_stock_location,
        index=True, readonly=True, required=True,
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', True)]})
    location_dest_id = fields.Many2one(
        'stock.location', 'Delivery Location',
        readonly=True, required=True,
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', True)]})
    ## metodo di fatturazione default : after_repair
    invoice_method = fields.Selection([
        ("none", "No Invoice"),
        ("b4repair", "Before Repair"),
        ("after_repair", "After Repair")], string="Invoice Method",
        default='after_repair', index=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]},
        help='Selecting \'Before Repair\' or \'After Repair\' will allow you to generate invoice before or after the repair is done respectively. \'No invoice\' means you don\'t want to generate invoice for this repair order.')
    ## riutilizzo la tabella fees_lines per gestire operazioni extra dopo la conferma del preventivo di riparazione
    fees_lines = fields.One2many(
        'mrp.repair.fee', 'repair_id', 'Fees',
        copy=True, readonly=True, states={'under_repair': [('readonly', False)], 'ready': [('readonly', False)]})
    ## data preventivo
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)]}, copy=False, default=fields.Datetime.now)

    
    ## nel caso di servizi, non creo stock_move
    @api.multi
    def action_repair_done(self):
        """ Creates stock move for operation and stock move for final product of repair order.
        @return: Move ids of final products

        """
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        res = {}
        Move = self.env['stock.move']
        for repair in self:
            moves = self.env['stock.move']
            for operation in repair.operations:
                if operation.product_id.type == 'service':
                    continue
                move = Move.create({
                    'name': operation.name,
                    'product_id': operation.product_id.id,
                    'restrict_lot_id': operation.lot_id.id,
                    'product_uom_qty': operation.product_uom_qty,
                    'product_uom': operation.product_uom.id,
                    'partner_id': repair.address_id.id,
                    'location_id': operation.location_id.id,
                    'location_dest_id': operation.location_dest_id.id,
                })
                moves |= move
                operation.write({'move_id': move.id, 'state': 'done'})
            ## gestisco anche i prodotti inseriti nella tabella fees_lines delle operazioni extra
            for extra_operation in repair.fees_lines:
                if extra_operation.product_id.type == 'service':
                    continue
                if extra_operation.product_id.tracking != 'none' and not extra_operation.lot_id:
                    raise UserError(_("Serial number is required for extra operation line with product '%s'") % (extra_operation.product_id.name))
                move = Move.create({
                    'name': extra_operation.name,
                    'product_id': extra_operation.product_id.id,
                    'restrict_lot_id': extra_operation.lot_id.id,
                    'product_uom_qty': extra_operation.product_uom_qty,
                    'product_uom': extra_operation.product_uom.id,
                    'partner_id': repair.address_id.id,
                    'location_id': extra_operation.location_id.id,
                    'location_dest_id': extra_operation.location_dest_id.id,
                })
                moves |= move
                extra_operation.write({'move_id': move.id})
            move = Move.create({
                'name': repair.name,
                'product_id': repair.product_id.id,
                'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
                'product_uom_qty': repair.product_qty,
                'partner_id': repair.address_id.id,
                'location_id': repair.location_id.id,
                'location_dest_id': repair.location_dest_id.id,
                'restrict_lot_id': repair.lot_id.id,
            })
            moves |= move
            moves.action_done()
            res[repair.id] = move.id
        return res
    
    
    ##restituisco la fattura creata
    @api.multi
    def action_repair_invoice_create(self):
        self.action_invoice_create()
        if self.invoice_method == 'b4repair':
            self.action_repair_ready()
        elif self.invoice_method == 'after_repair':
            self.write({'state': 'done'})
        
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        action['res_id'] = self.invoice_id.id
        return action
        #return True

class RepairFee(models.Model):
    _inherit = 'mrp.repair.fee'

    type = fields.Selection([
        ('add', 'Add'),
        ('remove', 'Remove')], 'Type', required=True)
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        index=True, required=True)
    location_dest_id = fields.Many2one(
        'stock.location', 'Dest. Location',
        index=True, required=True)
    move_id = fields.Many2one(
        'stock.move', 'Inventory Move',
        copy=False, readonly=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot')


    @api.onchange('type', 'repair_id')
    def onchange_operation_type(self):
        """ On change of operation type it sets source location, destination location
        and to invoice field.
        @param product: Changed operation type.
        @param guarantee_limit: Guarantee limit of current record.
        @return: Dictionary of values.
        """
        if not self.type:
            self.location_id = False
            self.Location_dest_id = False
        elif self.type == 'add':
            args = self.repair_id.company_id and [('company_id', '=', self.repair_id.company_id.id)] or []
            warehouse = self.env['stock.warehouse'].search(args, limit=1)
            self.location_id = warehouse.lot_stock_id
            self.location_dest_id = self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id
            self.to_invoice = self.repair_id.guarantee_limit and datetime.strptime(self.repair_id.guarantee_limit, '%Y-%m-%d') < datetime.now()
        else:
            self.location_id = self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id
            self.location_dest_id = self.env['stock.location'].search([('scrap_location', '=', True)], limit=1).id
            self.to_invoice = False

