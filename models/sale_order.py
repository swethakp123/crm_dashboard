# -*- coding: utf-8 -*-
from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def action_confirm(self):
        print("working")
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            print('self')
            print('order.team_id', order.team_id)
            print('order.team_id.stage_id', order.team_id.stage_id)
            if order.team_id and order.team_id.stage_id:
                opportunity = order.opportunity_id
                print('opportunity', opportunity)
                print('opportunity.stage_id', opportunity.stage_id)
                if opportunity.stage_id != order.team_id.stage_id:
                    opportunity.stage_id = order.team_id.stage_id
        return res
