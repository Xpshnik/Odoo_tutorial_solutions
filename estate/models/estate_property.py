from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class Property(models.Model):
    _name = 'estate.property'
    _description = 'Some minimal placeholder description'
    _order = 'id desc'
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be positive.'),
        ('check_selling_price', 'CHECK(selling_price > 0)', 'The selling price must be positive.'),
    ]

    def _default_date_availability(self):
        return fields.Date.add(fields.Date.context_today(self), months=3)

    name = fields.Char(required=True)
    description = fields.Text()
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    postcode = fields.Char()
    total_area = fields.Float(compute='_compute_total_area')
    date_availability = fields.Date('Available From', copy=False, default=lambda self: self._default_date_availability())
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    tag_ids = fields.Many2many('estate.property.tags', string="Tags")
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
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        copy=False,
        required=True,
        string='Status',
        store="True",
        default='new',
        compute="_compute_offer_received",
    )

    @api.depends('garden_area', 'living_area')
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.garden_area + property.living_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for property in self:
            try:
                property.best_price = max(property.mapped('offer_ids.price'))
            except ValueError:
                property.best_price = 0

    #in the tutorial, the suggested solution is to modify create method for offers so that on offer creation property state changes
    #to 'offer_received', but such solution would leave the 'offer_received' state behind even after all offers are deleted
    @api.depends('offer_ids', 'state')
    def _compute_offer_received(self):
        for property in self:
            if property.offer_ids and property.state == 'new':
                property.state = 'offer_received'
            elif not property.offer_ids and property.state == 'offer_received':
                property.state = 'new'

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for property in self:
            if not float_is_zero(property.selling_price, 2):
                if property.selling_price < property.expected_price * 0.9:
                    raise ValidationError(_('The selling price should not be lower than 90% of the expected price.'))

    @api.onchange('garden')
    def onchange_garden(self):
        if self.garden:
            self.garden_area = 10 if not self.garden_area else self.garden_area
            self.garden_orientation = 'north' if not self.garden_orientation else self.garden_orientation
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.onchange('garden_area')
    def onchange_garden_area(self):
        if self.garden_area == 0:
            self.garden = False
            self.garden_orientation = False
        elif self.garden_area or self.garden_orientation:
            self.garden = True

    @api.ondelete(at_uninstall=False)
    def _unlink_check_state(self):
        for property in self:
            if property.state not in ('new', 'cancelled'):
                raise UserError(_('Only new or cancelled properties can be deleted.'))

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'sold':
            raise UserError(_('A sold property cannot be set as cancelled.'))
        self.write({
            'state': 'cancelled',
            'active': False
        })
        return True

    def action_set_sold(self):
        self.ensure_one()
        if self.state == 'cancelled':
            raise UserError(_('A cancelled property cannot be set as sold.'))
        self.state = 'sold'
        return True
