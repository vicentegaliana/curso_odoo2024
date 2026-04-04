from odoo import fields, models, api
class SportLeagueCreateMatch(models.TransientModel):
    _name = 'sport.league.create.match'
    _description = 'Create Match'
    
    date=fields.Date(string='Date',required=True)
    team_ids = fields.Many2many('sport.team', string='Teams')
    result = fields.Char(string='Result')
    winner_id = fields.Many2one('sport.team', string='Winner')

    #Añado como valor por defecto el active_id de la liga de orígen. 
    # Si partimos de una selección de varias ligas, tendrá el valor de la primera seleccionada
    league_id=fields.Many2one('sport.league',string='League', default=lambda self: self.env.context.get('active_id'))
    
    def action_league_create_match(self):
        # Recuperamos la liga de origen
        active_ids=self.env.context.get('active_ids')
        leagues=self.env['sport.league'].browse(active_ids)

        # Aunque ésto está pensado para ser invocado desde una liga individual, por si acaso codifico para un origen múltiple
        for league in leagues:
            # El deporte está implícito en la liga
            sport_id=league.sport_id.id
            # El nombre del partido lo voy a conformar concatenando el nombre de los team_ids y el literal 'vs'
            name=self.team_ids[0].name+' vs '+self.team_ids[1].name

            match=self.env['sport.match'].create({
                'name':name,
                'date':self.date,
                'sport_id':sport_id,
                'league_id':league.id,
                'team_ids':self.team_ids,
                'result':self.result,
                'winner_id':self.winner_id.id,
            })
            #Que aparezca en el chatter un mensaje con la liga asociada
            #match.message_post(body=f'Match created from league: {league.name}')
            # , pero además quiero que la liga asociada sea un enlace a la liga. 
            # Para eso uso message_post_with_source, que me permite usar el markup de Odoo para crear el enlace. 
            # El subtipo lo pongo a 'mail.mt_note' para que se muestre como una nota interna en el chatter.
            # El mensaje viene a ser "Este sport match ha sido creado de: Liga de Fútbol Amateur", y el texto creo que lo aporta mail.message_origin_link. 
            match.message_post_with_source('mail.message_origin_link', render_values={'self':match, 'origin':self.league_id}, subtype_xmlid='mail.mt_note')
        
        return {
            'name': 'Match',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'sport.match',
            'res_id': match.id,
            'target': 'current',
        }