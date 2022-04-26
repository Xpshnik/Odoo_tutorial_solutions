from odoo import fields, models

class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = "Let's get rid of the warning"
    _order = 'name'

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id') 
    sequence = fields.Integer('Sequence', default=1, help="Used to order types. Lower is better.")

    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', 'It seems the property type with specified name already exists.'),
    ]
