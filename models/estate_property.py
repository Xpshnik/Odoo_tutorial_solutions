import string
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

class Property(models.Model):
    _name = 'estate.property'
    _description = 'Some minimal placeholder description'
    _order = 'id desc'

    name = fields.Char(required=True)
    description = fields.Text()
    property_type_id = fields.Many2one('estate.property.type', string='Type')
    postcode = fields.Char()
    total_area = fields.Float(compute='_compute_total_area')
    date_availability = fields.Date('Available From', copy=False, default=lambda self: fields.Datetime.add(fields.Datetime.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    tag_ids = fields.Many2many('estate.property.tags')
    salesperson_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', copy=False, string='Buyer')
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    best_price = fields.Float(compute='_compute_best_price')
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ('east', 'East'),
            ('west', 'West'),
            ('south', 'South'),
            ('north', 'North'),
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection([('new', 'New'),
                              ('offer_received', 'Offer Received'),
                              ('offer_accepted', 'Offer Accepted'),
                              ('sold', 'Sold'),
                              ('cancelled', 'Cancelled'),
                            ],
                            copy=False, required=True, string='Status', store="True",
                            compute="_compute_offer_received") #default='new' removed, as compute overrides default value

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be positive.'),
        ('check_selling_price', 'CHECK(selling_price > 0)', 'The selling price must be positive.'),
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, 2):
                if record.selling_price < record.expected_price * 0.9:
                    raise ValidationError('The selling price should not be lower than 90% of the expected price.')

    @api.depends('garden_area', 'living_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            try:
                record.best_price = max(record.mapped('offer_ids.price'))
            except ValueError:
                record.best_price = 0

    @api.depends('offer_ids', 'state')
    def _compute_offer_received(self):
        for record in self:
            record.state = 'new' if not record.state else record.state
            if record.offer_ids and record.state == 'new':
                record.state = 'offer_received'
            elif not record.offer_ids and record.state == 'offer_received':
                record.state = 'new'

    @api.onchange('garden')
    def onchange_garden(self):
        if self.garden:
            self.garden_area = 10 if not self.garden_area else self.garden_area
            self.garden_orientation = 'north' if not self.garden_orientation else self.garden_orientation
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.onchange('garden_area')
    def onchange_garden_area(self):
        if self.garden_area == 0:
            self.garden = False
            self.garden_orientation = ''
        elif self.garden_area or self.garden_orientation:
            self.garden = True

    def action_cancel(self):
        """ for record in self:
            if record.state == 'sold':
                raise UserError('A sold property cannot be set as cancelled.')
            record.state = 'cancelled'
        return True """
        if self.state == 'sold':
            raise UserError('A sold property cannot be set as cancelled.')
        self.write({
            'state': 'cancelled',
            'active': False
        })

    def action_set_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError('A cancelled property cannot be set as sold.')
            record.state = 'sold'
        return True
