from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Offer(models.Model):
    _name = 'estate.property.offer'
    _description = 'An offer'
    _order = 'price desc'
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The offer price must be positive.'),
    ]

    price = fields.Float(required=True)
    state = fields.Selection(
        selection=[
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
        ],
        copy=False,
        string="Status",
    )
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7, string='Validity (days)')
    deadline_date = fields.Date(string='Deadline', compute='_compute_deadline_date', inverse='_inverse_deadline_date')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store='True')

    @api.depends('validity')
    def _compute_deadline_date(self):
        for offer in self:
            if offer.create_date:
                offer.deadline_date = fields.Date.to_date(offer.create_date) + relativedelta(days=offer.validity)
            else:
                offer.deadline_date = fields.Date.add(fields.Date.today(), days=offer.validity)

    def _inverse_deadline_date(self):
        for offer in self:
            if offer.create_date:
                offer.validity = (offer.deadline_date - fields.Date.to_date(offer.create_date)).days
            else:
                offer.validity = (offer.deadline_date - fields.Date.today()).days

    @api.model
    def create(self, vals):
        targeted_property = self.env['estate.property'].browse(vals.get('property_id'))
        if vals.get('price') <= targeted_property.best_price:
            raise ValidationError(_('There\'s already an offer with a better price.'))
        return super().create(vals)

    def action_accept_offer(self):
        self.ensure_one()
        if self.property_id.buyer_id:
            raise UserError(_('The buyer has already been set.'))
        self.state = 'accepted'
        self.env['estate.property'].browse(self.property_id.id).write({
            'selling_price': self.price,
            'buyer_id': self.partner_id.id,
            'state': 'offer_accepted',
        })
        return True

    def action_refuse_offer(self):
        self.ensure_one()
        self.state = 'refused'
        return True
