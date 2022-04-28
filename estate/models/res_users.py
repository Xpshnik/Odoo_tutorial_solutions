from datetime import date
from odoo import models, fields


class UserProperties(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='salesperson_id', domain=[('date_availability', '<=', date.today()), ("state", "in", ["new", "offer_received"])])
