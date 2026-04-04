from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sport_ticket_ids = fields.One2many('sport.ticket', 'sale_order_id', string='Sport Tickets')

    def action_cancel(self):
        res = super().action_cancel()
        self.sport_ticket_ids.unlink()
        return res

    # En la última tutoría, Nacho propone que, al incluir algún artículo en el pedido que tenga isTicket (p.e. el artículo Entradas), y confirmar el pedido, se cree un ticket deportivo (sport.ticket) asociado al pedido. 
    # Para ello, se puede sobreescribir el método action_confirm del modelo sale.order y añadir la lógica para crear el ticket deportivo si el pedido contiene un artículo con isTicket.
    def action_confirm(self):
        res = super().action_confirm()
        for line in self.order_line:
            if line.product_id.is_ticket:
                self.create_sport_ticket()
                break  # Si ya se ha encontrado un artículo con isTicket, no es necesario seguir buscando
        return res
    
    def create_sport_ticket(self):
        #originalmente le dabamos un name al ticket, pero posteriormente se implementún un contador autonumérico para el nombre del ticket, no te vuelvas loco, el ticket que se cree no se va a crear con gift Ticket with your order: "+self.name, sino que se le asignará un nombre automáticamente con el contador autonumérico.
        vals = {
            'name': "gift Ticket with your order: "+self.name,
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
        }
        self.env['sport.ticket'].create(vals)