from odoo import models, fields

class SportMatch(models.Model):
    _name = 'sport.match'
    _description = 'Sport Match'

    name = fields.Char(string='Name', required=True)
    date = fields.Datetime(string='Date', required=True)
    sport_id = fields.Many2one('sport', string='Sport')
    league_id=fields.Many2one('sport.league',string='League')
    team_ids = fields.Many2many('sport.team', string='Teams')
    result = fields.Char(string='Result')
    winner_id = fields.Many2one('sport.team', string='Winner')