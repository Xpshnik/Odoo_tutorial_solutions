from odoo import models, Command


class PropertyInvoice(models.Model):
    _inherit = 'estate.property'

    def action_set_sold(self):
        sold_property = super().action_set_sold()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        
        for property in self:
            self.env['account.move'].create(
                {
                    "invoice_line_ids": [
                        Command.create({
                            'name': property.name,
                            'quantity': '1.0',
                            'price_unit': property.selling_price / 100.0 * 6,
                        }),
                        Command.create({
                            'name': 'Administrative fees',
                            'quantity': '1.0',
                            'price_unit': '100.00',
                        }),
                    ],
                    'partner_id': property.buyer_id.id,
                    'move_type': 'out_invoice',
                    'journal_id': journal.id,
                }
        )
        return sold_property
