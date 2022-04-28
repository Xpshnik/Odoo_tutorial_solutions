from odoo import models, fields


class EstatePropertyTags(models.Model):
    _name = 'estate.property.tags'
    _description = 'Estate property tag'
    _order = 'name'
    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)', 'It seems the property tag with specified name already exists.'),
    ]

    name = fields.Char(required=True)
    color = fields.Integer()
