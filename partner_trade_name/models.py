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

from openerp import api, models, fields

class ResPartnerNext(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def name_get(self):
        u = super(ResPartnerNext, self).name_get()
        res = []
        for r in self:
            name9 = r.name
            if r.is_company:
                if r.comercial:
                    name9 += " (%s)" % r.comercial
            else:
                if r.parent_id:
                    name9 = r.parent_id.name
                    if r.parent_id.comercial:
                        name9 += " (%s)" % r.parent_id.comercial
                    name9+=', %s' % r.name

            res.append((r.id, name9))

        return res

