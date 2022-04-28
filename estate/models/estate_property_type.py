from odoo import fields, models, api

class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = "Proprty type"
    _order = 'name'

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id') 
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute='_compute_offer_count')
    sequence = fields.Integer('Sequence', default=1, help='Used to order types. Lower is better.')

    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', 'It seems the property type with specified name already exists.'),
    ]

    @api.depends()
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
