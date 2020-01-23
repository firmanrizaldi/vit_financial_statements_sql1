
from odoo import api, fields, models
import time
import datetime
import logging
_logger = logging.getLogger(__name__)


class financialStatement(models.Model):
    _name = 'vit_financial_statements'
    _description = 'vit_financial_statements'

    name = fields.Char(string='Report name',required=True, )
    code = fields.Char(string='Code',required=True, )
    parent_id = fields.Many2one(string='Parent',comodel_name='vit_financial_statements',)
    criteria = fields.Char(string='Criteria', required=False, )
    source = fields.Selection([("header","Header"),
                               ("formula","Formula"),
                               ("account","Account"),], string='Source', default='header', required=True, )
    level = fields.Integer(string='Level', required=False, )
    
    
    
    
    
    
    
    

