from odoo import models, fields

class SportIssueTag(models.Model):
    _name = 'sport.issue.tag'
    _description = 'Sport Issue Tag'

    name = fields.Char(string='name', required=True)

    color=fields.Integer(string='color',default=0)

    #Ejemplo de Many2many: cada tag puede estar en varias incidencias. Configuración por defecto de la tabla intermedia
    #issues_ids = fields.Many2many('sport.issue', string='Issues')
    #Lo anterior funciona, pero en la tutoría 5 (1:44) Nacho añade parámetros al campo Many2many, para especificar cuál debe ser el nombre de la tabla intermedia y las columnas de relación
    issues_ids=fields.Many2many('sport.issue','sport_issue_tag_rel','tag_id','issue_id',string='Issues')