from odoo import fields, models, api


class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = "Proprty type"
    _order = 'sequence, name'
    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', 'It seems the property type with specified name already exists.'),
    ]

    sequence = fields.Integer('Sequence', default=1, help='Used to order types. Lower is better.')
    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id') 
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute='_compute_offer_count')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for prop_type in self:
            prop_type.offer_count = len(prop_type.offer_ids)
