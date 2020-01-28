
from odoo import http
import simplejson
import datetime
from odoo import api, fields, models
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class financialStatement(http.Controller):

    @http.route('/financial/index', auth='user',website=True)
    def index(self, **kw):
        return http.request.render('vit_financial_statements.index', {
        })
        
    @http.route('/financial/company', auth='public', csrf=False)
    def get_company(self):
        company = http.request.env['res.company'].search_read([], fields=['id','name'])
        data= []
        for dir in company :
            data.append({
                'id': dir['id'],
                'text': dir['name'],
            })
            
        return simplejson.dumps(data)  
      
    @http.route('/financial/report', auth='public', csrf=False)
    def get_report(self):
        report = http.request.env['vit_financial_statements'].search_read([('parent_id','=', False)], fields=['id','name'])
        data= []
        for dir in report :
            data.append({
                'id': dir['id'],
                'text': dir['name'],
            })
            
        return simplejson.dumps(data)  


    @http.route('/financial/data', auth='public')
    def directories(self,**kw):
      
        if 'report_id' in kw:
          report_id = kw['report_id']
        else :
          report_id = 0

        if 'company_id' in kw:
          company_id = kw['company_id']
        else : 
          company_id = 0
          
        if 'date_start' in kw:
          date_start = datetime.datetime.strptime(kw['date_start'], '%m/%d/%Y').strftime('%Y/%m/%d') # merubah format tanggal
        else :
          date_start = '1999-01-01'

          
        if 'date_end' in kw:
          date_end = datetime.datetime.strptime(kw['date_end'], '%m/%d/%Y').strftime('%Y/%m/%d') # merubah format tanggal
        else :
          date_end = '1999-01-01'
        
        sql =""" WITH RECURSIVE parent (id, parent_id, code, name, level, criteria, source) AS (
            SELECT
              line.id,
              line.parent_id,
              line.code,
              line.name,
              line.level,
              line.criteria,
              line.source,
              array[line.id] as path_info
            FROM
              vit_financial_statements as line
            WHERE
              line.parent_id is NULL
              AND line.id = %s
            UNION ALL
              SELECT
                  child.id,
                  child.parent_id,
                  child.code,
                  child.name,
                  child.level,
                  child.criteria,
                  child.source,
                  parent.path_info||child.id
              FROM
                  vit_financial_statements as child
              INNER JOIN parent ON child.parent_id = parent.id
            ) SELECT
                parent.id as id_first,
                parent.level,
                parent.name as parent_name,
                parent.criteria,
                parent.code,
                path_info,
                parent.parent_id,
                parent.source,
                aat.name,
                aa.id,
                aa.name,
                aa.code as code_account,
                case 
                when aat.name in ('Income','Other Income','Equity','Payable','Credit Card','Current Liabilities','Non-current Liabilities') then
                    sum(coalesce(aml.credit,0) - coalesce(aml.debit,0)) 
                else
                    sum(coalesce(aml.debit,0) - coalesce(aml.credit,0))
            end as balance
            FROM
                parent
                
            LEFT JOIN account_account aa  
              on aa.code like parent.criteria
              and aa.company_id = %s
                  LEFT join account_account_type aat 
              on aat.id = aa.user_type_id

            LEFT join account_move_line aml 
              on aml.account_id = aa.id
                and aml.date between %s and %s 

            LEFT join account_move am
                on aml.move_id = am.id 
                and am.state = 'posted' 
                
              where parent.parent_id != 0
                    group by 
                        parent.id,
                        parent.level,
                        parent.name,
                        parent.criteria,
                        parent.code,
                        path_info,
                        parent.parent_id,
                        parent.source,
                        aat.name,
                        aa.id,
                        aa.name,
                        aa.code
                    order by path_info
        
        """
            
        cr = http.request.env.cr

        cr.execute(sql,(report_id, company_id, date_start, date_end))
        result = cr.dictfetchall()
   
        id_menu = 0
        id_submenu = 0
        data = []
        data_master = []
        data_sub_master = []
        data_sub_master_level1 = []
        children = []
        # balance_master = 0
        # balance_sale = 0
        # balance_cogs = 0
        # balance_gross = 0
        # balance_adm = 0
        # balance_other = 0
        lendata = 0
        lendata_minus = 0
        # i = 0
        # m = -1
        for dir in result:
          # i += 1
          # m += 1
          lendata_minus = len(data) -1
          lendata = len(data)    
          
# //////////////////////// masukin level 1 ==== sales,cogs,dll
          if dir['level'] == 1 :
            
            if id_menu != dir['id_first'] :
              if dir ['balance'] == 0 :
                data.append({
                      'id': dir['id_first'],
                      'name': dir['parent_name'],
                      'code' : dir['code'],
                      'source' : dir['source'],
                      'balance' : dir['balance']
                    })
                data_sub_master_level1 = []
              else :
                data.append({
                  'id': dir['id_first'],
                  'name': dir['parent_name'],
                  'code' : dir['code'],
                  'source' : dir['source'],
                  'balance' : dir['balance'],
                  'children' : ({
                        'id': dir['id_first'],
                        'name': dir['name'],
                        'code' : dir['code'],
                        'balance' : dir['balance'],
                        'source' : dir['source'],               
                    })
                })
                
            else :
              if dir ['balance'] != 0 : 
                
                if id_menu == dir['id_first']:
                  if data_sub_master_level1 == [] :
                    data_sub_master_level1 = []
                    for x in data[lendata_minus:lendata] :
                        data_sub_master_level1.append({
                                      "id" : x['id'],
                                      "name" : x['name'],
                                      'code' : x['code'],
                                      'source' : x['source'],
                                      "balance" : x['balance'],
                                      "children" : ({
                                        'id': dir['id_first'],
                                        'name': dir['name'],
                                        'code' : dir['code'],
                                        'balance' : dir['balance'],
                                        'source' : dir['source']
                                        })
                                      })
                        
                    data[lendata_minus:lendata] = data_sub_master_level1
                  
                  else :
                    plus = [list(d.values())[5] for d in data[lendata_minus:lendata]]
                    plus.append({
                                'id': dir['id_first'],
                                'name': dir['name'],
                                'code' : dir['code'],
                                'balance' : dir['balance'],
                                'source' : dir['source']
                                })
                  
                    for x in data[lendata_minus:lendata] :
                        x['children'] = plus
                      
                        

            id_menu = dir['id_first']
                      
                      
                      
                      
#  //////////////////////////////////// masukan level 2 ===== parentnya sales,cogs dll
          elif dir['level'] == 2 :
            if id_submenu != dir['id_first'] :
              if data_master == [] :
                data_master = []
                if dir['balance'] == 0 :
                  for x in data[lendata_minus:lendata] :
                      data_master.append({
                                    'id' : x['id'],
                                    'name' : x['name'],
                                    'code' : x['code'],
                                    'source' : x['source'],
                                    'balance' : x['balance'],
                                    'children' : ({
                                          'id' : dir['id_first'],
                                          'name' : dir['parent_name'],
                                          'code' : dir['code'],
                                          'source' : dir['source'],
                                          'balance' : dir['balance'],
                                      })
                                    })
                      
                      data[lendata_minus:lendata] = data_master
                
              else :
                plus = [list(d.values())[5] for d in data[lendata_minus:lendata]]
                plus.append({
                                'id' : dir['id_first'],
                                'name' : dir['parent_name'],
                                'code' : dir['code'],
                                'source' : dir['source'],
                                'balance' : dir['balance'],
                            })
              
                for x in data[lendata_minus:lendata] :
                    x['children'] = plus
            
            else :
              # ////////////////////////masukan yang ada akunnya
              if data_sub_master == [] :
                data_sub_master = []
                if dir['balance'] != 0 :
                  for x in data[lendata_minus:lendata] :
                      data_sub_master.append({
                                    'id' : x['id'],
                                    'name' : x['name'],
                                    'code' : x['code'],
                                    'source' : x['source'],
                                    'balance' : x['balance'],
                                    'children' : ({
                                          'id' : x['children']['id'],
                                          'name' : x['children']['name'],
                                          'code' : x['children']['code'],
                                          'source' : x['children']['source'],
                                          'balance' : x['children']['balance'],
                                          'children' : ({
                                              'id' : dir['id_first'],
                                              'name' : dir['name'],
                                              'code' : dir['code'],
                                              'source' : dir['source'],
                                              'balance' : dir['balance'],
                                          })
                                          
                                      })
                                    })
                      
                      data[lendata_minus:lendata] = data_sub_master
                
              else :
                if dir['balance'] != 0 and id_submenu == dir['id_first']:
                  plus = [list(d.values())[5] for d in data[lendata_minus:lendata]]
                  plus_sub = [list(z.values())[5] for z in plus]
                  plus_sub.append({
                                  'id' : dir['id'],
                                  'name' : dir['name'],
                                  'code' : dir['code'],
                                  'source' : dir['source'],
                                  'balance' : dir['balance'],
                              })
                  for x in data[lendata_minus:lendata] :
                      x['children']['children'] = plus_sub
            
            
              
            id_submenu = dir['id_first']
            plus = []
            
          
            
        return simplejson.dumps(data)


            

          # children = ({
          #   'id': dir['id_first'],
          #   'name': dir['name'],
          #   'balance' : dir['balance']
          # })
          
          # if id_first != dir['id_first'] :
          #   balance_first = dir['balance'] == 0
          #   if dir['code'] == "GROSS" :
          #     balance_gross = balance_sale - balance_cogs
          #     balance = balance_sale - balance_cogs
          #   elif dir['code'] == "NP" :
          #     balance = balance_gross - balance_adm + balance_other
          #   else :
          #     balance = dir['balance']
                
          #   if balance_first :
              
          #     data.append({
          #       'id': dir['id_first'],
          #       'name': dir['parent_name'],
          #       'code' : dir['code'],
          #       'source' : dir['source'],
          #       'balance' : balance
          #     })
          #     data_master = []
          #   else :
          #     data.append({
          #       'id': dir['id_first'],
          #       'name': dir['parent_name'],
          #       'code' : dir['code'],
          #       'source' : dir['source'],
          #       'balance' : balance,
          #       'children' : children
          #     })
          #   id_first = dir['id_first']
              
            
          #   lendata_minus = len (data) -1
          #   lendata = len(data)
            
          # elif id_first == dir['id_first'] and dir['balance'] != 0:
          #   balance_master = dir['balance']
          #   if balance_first :
          #     if data_master == [] :
              
          #       data_master = []
          #       for x in data[lendata_minus:lendata] :
          #           data_master.append({
          #                         "id" : x['id'],
          #                         "name" : x['name'],
          #                         'code' : dir['code'],
          #                         'source' : x['source'],
          #                         "balance" : balance_master,
          #                         "children" : children
          #                         })
                    
          #       data[lendata_minus:lendata] = data_master
          #     else :
          #       plus = [list(d.values())[5] for d in data[lendata_minus:lendata]]
          #       plus.append(children)
              
          #       for x in data[lendata_minus:lendata] :
          #           x['children'] = plus
          #           x['balance'] = x['balance'] + balance_master
                    
          #           if x['code'] == 'sale' :
          #             balance_sale = x['balance'] + balance_master
          #           elif x['code'] == 'HPP' :
          #             balance_cogs = x['balance'] + balance_master
          #           elif x['code'] == 'ADM' :
          #             balance_adm = x['balance'] + balance_master
          #           elif x['code'] == 'OTHER':
          #             balance_other = x['balance'] + balance_master
          #           else :
          #             balance = x['balance']