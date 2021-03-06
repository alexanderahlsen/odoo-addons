# -*- coding: utf-8 -*-
#/#############################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2015 NuoBiT Solutions, S.L. (<http://www.nuobit.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


import logging

_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _inherit = 'sale.order'

    def delivery_set(self):
        line_ids =  super(sale_order, self).delivery_set()

        line_ids9 = []
        for line_id in line_ids:
            line_obj = self.env['sale.order.line'].search([('id', '=', line_id)])
            if line_obj.price_unit != 0.0:
                line_ids9.append(line_id)
            else:
                line_obj.unlink()

        return line_ids9



class delivery_grid(models.Model):
    _inherit = "delivery.grid"

    @api.multi
    def get_price(self, order, dt):
        total = 0
        weight = 0
        volume = 0
        quantity = 0
        total_delivery = 0.0
        total_delivery_untaxed = 0.0
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery_untaxed += line.price_subtotal
                total_delivery += line.price_subtotal + order._amount_line_tax(line)

            if not line.product_id or line.is_delivery:
                continue
            q = line.product_uom._compute_qty(line.product_uom_qty, line.product_id.uom_id.id)
            weight += (line.product_id.weight or 0.0) * q
            volume += (line.product_id.volume or 0.0) * q
            quantity += q

        total_untaxed = (order.amount_untaxed or 0.0) - total_delivery_untaxed
        total_untaxed = order.currency_id.with_context(date=order.date_order).compute(total_untaxed, order.company_id.currency_id)

        total = (order.amount_total or 0.0) - total_delivery
        total = order.currency_id.with_context(date=order.date_order).compute(total, order.company_id.currency_id)

        return self.get_price_from_picking(total_untaxed, total, weight, volume, quantity)


    def get_price_from_picking(self, total_untaxed, total, weight, volume, quantity):
        price = 0.0
        ok = False
        price_dict = {'price_untaxed': total_untaxed, 'price': total, 'volume': volume,
                      'weight': weight, 'wv': volume * weight, 'quantity': quantity}
        for line in self.line_ids:
            test = eval(line.type + line.operator + str(line.max_value), price_dict)
            if test:
                if line.price_type == 'variable':
                    price = line.list_price * price_dict[line.variable_factor]
                else:
                    price = line.list_price
                ok = True
                break
        if not ok:
            raise ValidationError(_("Unable to fetch delivery method!"), _(
                "Selected product in the delivery method doesn't fulfill any of the delivery grid(s) criteria."))

        return price

class delivery_grid_line(models.Model):
    _inherit = "delivery.grid.line"

    type = fields.Selection(selection_add=[('price_untaxed', 'Price untaxed')])

    variable_factor = fields.Selection(selection_add=[('price_untaxed', 'Price untaxed')])

