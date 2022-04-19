from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError

class Offer(models.Model):
    _name = 'estate.property.offer'
    _description = "Don't shout at me, console"

    price = fields.Float()
    status = fields.Selection(copy=False, selection=[
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ])
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7)
    deadline_date = fields.Date()#compute='_compute_deadline_date', inverse='_inverse_deadline_date')

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The offer price must be positive.'),
    ]

    """@api.depends('validity', 'create_date')
    def _compute_deadline_date(self):
        for record in self:
            if record.create_date:
                record.deadline_date = fields.Date.to_date(record.create_date) + relativedelta(days=3)
            else:
                record.deadline_date = fields.Date.add(fields.Date.today(), days=record.validity)

    @api.depends('deadline_date', 'create_date')
    def _inverse_deadline_date(self):
        for record in self:
            record.validity = fields.Date.subtract(record.deadline_date, fields.Date.to_date(record.create_date)) """

    def action_accept_offer(self):
        for record in self:
            #Pay attention: in real life only one offer can be accepted for a given property!
            #will this work or should I go via record.mapped('property_id') somehow?
            if record.property_id.selling_price:
                raise UserError('The buyer has already been set.')
            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_ids = [(4, record.partner_id.id, 0)]
            record.property_id.state = 'offer_accepted'
        return True

    def action_refuse_offer(self):
        for record in self:
            record.status = 'refused'
        return True