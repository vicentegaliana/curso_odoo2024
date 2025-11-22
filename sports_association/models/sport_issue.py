from odoo import models, fields, Command, api, _
from odoo.exceptions import ValidationError

class SportIssue(models.Model):
    _name = 'sport.issue'
    _description = 'Sport Issue'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    
    name=fields.Char(string='Name',required=True)

    # Añado el campo active. Por el hecho de tener este campo, automáticamente 
    # Odoo aportará funcionalidad para poder archivar / desarchivar incidencias
    active=fields.Boolean(string='Active',default=True,help='If unchecked, allow you to hide the issue without removing it')

    description=fields.Text(string='Description')
    date=fields.Datetime(string='Date', default=fields.Date.today)
    assistance=fields.Boolean(string='Assistance',help='Show if the issue is related to assistance')
    state=fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('done', 'Done'),
    ], string='State', default='draft', tracking=True)
    color=fields.Integer(string='Color',default=0)

    #función para el valor por defecto de user_id
    def _default_user_id(self):
        return self.env.user.id

    #valor por defecto con función normal
    # user_id=fields.Many2one('res.users',string='User', default=_default_user_id)
    #valor por defecto con función lambda
    user_id=fields.Many2one('res.users',string='User', default=lambda self: self.env.user.id)
    
    
    secuence = fields.Integer(string='Secuence', default=10)
    solution = fields.Html(string='Solution')
    player_id = fields.Many2one('sport.player', string='Player')

    #Ejemplo de campo calculado no almacenado
    assigned=fields.Boolean(string='Assigned',compute='_compute_assigned',inverse='_inverse_assigned',search='_search_assigned')

    
    #Ejemplo de Many2one: cada incidencia pertenece a una clínica (una sola)
    clinic_id=fields.Many2one('sport.clinic',string='Clinic')
    #Ejemplo de Many2many: cada incidencia puede tener varios tags
    tag_ids=fields.Many2many('sport.issue.tag',string='Tags')

    #Ejemplo de campo float, nos vendrá bien para poder medir en la vista pivot
    cost = fields.Float('cost')

    #Ejemplo de campo relacional, vamos a almacenar en el campo user_phone el teléfono del usuario
    user_phone=fields.Char(string='User Phone',related='user_id.phone',store=True, readonly=False)

    #Ejemplo de campo one2many, cada incidencia puede tener varias acciones
    action_ids=fields.One2many('sport.issue.action','issue_id',string='Actions to do')

    _sql_constraints = [
	('name_uniq','unique (name)','El nombre de la incidencia debe ser único')]


    def _compute_assigned(self):
        for record in self:
            record.assigned=bool(record.user_id)

    def _inverse_assigned(self):
        for record in self:
            if not record.assigned:
                record.user_id=False
            else:
                record.user_id=self.env.user.id

    def _search_assigned(self,operator,value):
        if operator=='=':
            if(value):
                return [('user_id','!=',False)]
            else:
                return [('user_id','=',False)]
        else:
            return []

    def action_open(self):
        #Para procesar un solo registro ésto estaría bien
        # self.ensure_one()
        # self.state='open'

        # Pero, ¿porque limitarnos? Es posible que queramos llamar 
        # este método desde otros métodos que sí estén procesando varios registros	
        # Así que es mejor dejarlo preparado
        # para que acepte y procese un recordset de uno o de varios registros
        # for record in self:
            # record.state='open'
            
        # Pero ésto tampoco sería lo ideal, es incluso mejor hacer uso de la función write
        # que es más eficiente y rápida
        for record in self:
            record.write({'state':'open'})

    def action_done(self):
        for record in self:
            if(record.date==False):
                raise ValidationError(_('Date is required'))
            record.write({'state':'done'})
            # Envío un mensaje personalizado al cambiar el estado de la incidencia a las actividades relacionadas
            # Usamos argumentos posicionales para poder pasar los valores de record.state y record.date. 
            # NO usar f-strings, ya que se pelean con la traducción (los f-string se pueden usar sin problema, siempre y cundo no haya traducción)
            msgBody=_('Issue changed its state to %s on %s'%(record.state,record.date))
            record.message_post(body=msgBody)

    def action_draft(self):
        for record in self:
            record.write({'state':'draft'})

    def action_open_all_issues(self):
        issues=self.env['sport.issue'].search([])
        issues.action_open()

    def action_create_tag_test(self):
        tag = self.env['sport.issue.tag'].create({'name':'Test Tag'})

    def action_copy_issue(self):
        for record in self:
            copy_issue=record.copy({'name':'Copia de '+record.name,'state':'draft'})
            
    def action_add_tags(self):
        #Crea y añade dos nuevas etiquetas a la incidencia
        for record in self:
            record.write({'tag_ids':[(0, 0, {'name':'New Tag 1'}),(0, 0, {'name':'New Tag 2'})]})
            

    def action_add_grave_urgente_tags(self):
        #Añade las etiquetas Grave y Urgente a la incidencia
        for record in self:
            # import pdb;pdb.set_trace()
            grave_tag=self.env['sport.issue.tag'].search([('name','=','Grave')],limit=1)
            urgente_tag=self.env['sport.issue.tag'].search([('name','=','Urgente')],limit=1)
            record.write({'tag_ids':[(4, grave_tag.id),(4, urgente_tag.id)]})

    def action_add_extrema_tag(self):
        #Crea y añade la etiqueta Extrema a la incidencia
        for record in self:
            record.tag_ids=[Command.create({'name':'Extrema'})]
            
    def action_add_all_tags(self):
        #Añade todas las etiquetas a la incidencia
        for record in self:
            tags=self.env['sport.issue.tag'].search([])
            #Cualquiera de las dos formas es válida:
            # record.write({'tag_ids':[(6, 0, tags.ids)]})
            record.tag_ids=[Command.set(tags.ids)]

    def action_remove_all_tags(self):
        #Quita sin borrar todas las etiquetas de la incidencia
        for record in self:
            record.tag_ids=[Command.clear()]

    #Defino una restricción @api.constrains para evitar que el coste pueda ser negativo
    @api.constrains('cost')
    def _check_cost(self):
        for record in self:
            if record.cost<0:
                raise ValidationError(_('Cost must be positive'))    
            
    #Defino un método que se ejeuctará cuando cambie el campo clinic_id. Cuando tenga el valor 'Hospital Virgen de la Arrixaca', el campo assistance se pondrá a True
    @api.onchange('clinic_id')
    def _onchange_clinic_id(self):
        for record in self:
            if record.clinic_id.name=='Hospital Virgen de la Arrixaca':
                self.assistance=True
    