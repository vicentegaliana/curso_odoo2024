from odoo import models, fields

class SportTicket(models.Model):
    _inherit = 'sports_association.sport.ticket'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')