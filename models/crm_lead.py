# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import timedelta
from collections import defaultdict


class SalesTeam(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def get_tiles_data(self, time_interval):
        """function to return the tile data and added filter based on
        different time interval and calculated values"""
        company_id = self.env.company
        today = fields.Date.today()
        start_date = False
        if time_interval == 'year':
            start_date = today.replace(month=1, day=1)
        elif time_interval == 'quarter':
            start_date = (today - timedelta(days=today.weekday())).replace(day=1)
        elif time_interval == 'month':
            start_date = today.replace(day=1)
        elif time_interval == 'week':
            start_date = today - timedelta(days=today.weekday())
        end_date = today

        leads = self.search([('company_id', '=', self.env.company.id),
                             ('create_date', '>=', start_date),
                             ('create_date', '<=', end_date),
                             ('user_id', '=', self.env.user.id)])

        my_leads = leads.filtered(lambda a: a.type == 'lead')
        my_opportunity = leads.filtered(lambda a: a.type == 'opportunity')
        currency = company_id.currency_id.symbol
        expected_revenue = sum(my_opportunity.mapped('expected_revenue'))
        won_opportunity = my_opportunity.filtered(lambda a: a.stage_id.is_won)

        lost_opportunity = my_opportunity.search([('active', '=', False),
                                                  ('probability', '=', 0)])

        win_ratio = len(won_opportunity) / len(lost_opportunity) * 100
        invoices = self.env['account.move'].search([('create_date', '>=', start_date),
                                                    ('create_date', '<=', end_date),
                                                    ('user_id', '=', self.env.user.id)])

        revenue = sum(invoices.filtered(lambda r: r.currency_id == company_id.currency_id).
                      mapped('amount_total'))

        lost_leads = my_leads.search([('probability', '=', 0), ('active', '=', False), ])
        lost_opportunity = my_opportunity.search(
            [('probability', '=', 0), ('active', '=', False)])
        lost_opportunities_count = len(lost_opportunity)

        lost_leads_by_month = defaultdict(int)
        for lead in lost_leads:
            month_year = lead.create_date.strftime('%Y-%m')
            lost_leads_by_month[month_year] += 1
        lost_leads_data = [{'month': month, 'lost_lead_count': count}
                           for month, count in lost_leads_by_month.items()]
        lead_by_campaign = []
        campaigns = self.env['utm.campaign'].search([])
        for campaign in campaigns:
            lead_count = self.search_count([('campaign_id', '=', campaign.id),
                                            ('user_id', '=', self.env.user.id),
                                            ('create_date', '>=', start_date),
                                            ('create_date', '<=', end_date)])
            lead_by_campaign.append({'campaign_name': campaign.name,
                                     'lead_count': lead_count})
        lead_by_medium = []
        mediums = self.env['utm.medium'].search([])
        for medium in mediums:
            lead_count = self.search_count([('medium_id', '=', medium.id),
                                            ('user_id', '=', self.env.user.id),
                                            ('create_date', '>=', start_date),
                                            ('create_date', '<=', end_date)])
            lead_by_medium.append({'medium_name': medium.name,
                                   'lead_count': lead_count})

        activities = self.env['mail.activity'].search(
            [('create_date', '>=', start_date),
             ('create_date', '<=', end_date),
             ('user_id', '=', self.env.user.id)])
        activity_count = len(activities)
        leads_by_month = defaultdict(int)
        for lead in leads:
            month_key = lead.create_date.strftime('%Y-%m')
            leads_by_month[month_key] += 1
        leads_by_month_data = [{'month': month, 'lead_count': count} for
                               month, count in leads_by_month.items()]
        lead_activities = self.env['mail.activity'].search_count(
            [('res_model', '=', 'crm.lead'), ('res_id', 'in', leads.ids)])
        opportunity_activities = self.env['mail.activity'].search_count(
            [('res_model', '=', 'crm.lead'),
             ('res_id', 'in', my_opportunity.ids)])
        lost_leadss = self.search_count([
            ('create_date', '>=', start_date),
            ('create_date', '<=', end_date),
            ('type', '=', 'lead'),
            ('active', '=', False)
        ])

        lost_opportunities = self.search_count([
            ('create_date', '>=', start_date),
            ('create_date', '<=', end_date),
            ('type', '=', 'opportunity'),
            ('active', '=', False)
        ])
        activities = self.env['mail.activity'].search(
            [('res_model', '=', 'crm.lead'),
             ('user_id', '=', self.env.user.id),
             ('create_date', '>=', start_date),
             ('create_date', '<=', end_date)
             ])
        activity_counts = defaultdict(int)
        for activity in activities:
            activity_counts[activity.activity_type_id.name] += 1
        activity_data = [{'activity_type': key, 'count': value} for key, value
                         in activity_counts.items()]

        return {
            'activity_data': activity_data,
            'total_leads': len(my_leads),
            'total_opportunity': len(my_opportunity),
            'expected_revenue': expected_revenue,
            'total_win_ratio': f"{win_ratio:.0f}%",
            'total_revenue': f"{revenue:.0f}",
            'currency': currency,
            'lost_opportunities_count': lost_opportunity,
            'lost_leads_data': lost_leads_data,
            'lost_leadss': lost_leadss,
            'lost_opportunities': lost_opportunities,
            'lead_by_campaign': lead_by_campaign,
            'lead_by_medium': lead_by_medium,
            'activity_count': activity_count,
            'leads_by_month_data': leads_by_month_data,
            'lead_activities': lead_activities,
            'opportunity_activities': opportunity_activities,
        }
