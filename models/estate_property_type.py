from odoo import fields, models

class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = "Let's get rid of the warning"

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'id')

    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', 'It seems the property type with specified name already exists.'),
    ]