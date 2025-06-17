from odoo.models import BaseModel
from odoo import api
import datetime
import dateutil.relativedelta
import logging
import pytz
from ast import literal_eval
import ast
import operator

_logger = logging.getLogger(__name__)

_original_process_groupby = BaseModel._read_group_process_groupby

@api.model
def patched_read_group_process_groupby(self, gb, query):
    split = gb.split(':')
    field_name = split[0]
    gb_function = split[1] if len(split) == 2 else None

    field = self._fields.get(field_name)
    if not field or field.type not in ('date', 'datetime') or gb_function != 'week':
        return _original_process_groupby(self, gb, query)

    set_globally = self.env['ir.config_parameter'].sudo().get_param('group_by_week_custom.set_globally')

    if not set_globally:
        def get_model_list():
            model_ids_str = self.env['ir.config_parameter'].sudo().get_param('group_by_week_custom.model_ids')
            model_ids = ast.literal_eval(model_ids_str)
            if len(model_ids) > 0:
                ids = f"in {tuple(model_ids)}" if len(model_ids) > 1 else f"= {model_ids[0]}"
                query = f"""select model from ir_model where id {ids}"""
                self._cr.execute(query)
                models_list = self._cr.fetchall()
                return list(map(operator.itemgetter(0), models_list))
            return False

        model_list = get_model_list()
        if not model_list or self._name not in model_list:
            return _original_process_groupby(self, gb, query)

    tz_convert = field.type == 'datetime' and self._context.get('tz') in pytz.all_timezones
    qualified_field = self._inherits_join_calc(self._table, field_name, query)

    if tz_convert:
        qualified_field = "timezone('%s', timezone('UTC',%s))" % (self._context.get('tz', 'UTC'), qualified_field)
    qualified_field = f"""(
        date_trunc('day', {qualified_field}::timestamp) - 
        ((EXTRACT(DOW FROM {qualified_field}::timestamp))::int) * INTERVAL '1 day'
    )"""

    return {
        'field': field_name,
        'groupby': gb,
        'type': field.type,
        'display_format': "'W'w yyyy",
        'interval': datetime.timedelta(days=7),
        'granularity': 'week',
        'tz_convert': tz_convert,
        'qualified_field': qualified_field,
    }

if not hasattr(BaseModel, "_custom_week_process_groupby_patched"):
    BaseModel._read_group_process_groupby = patched_read_group_process_groupby
    BaseModel._custom_week_process_groupby_patched = True
    _logger.info("✅ GroupBy:week patched  for Sun–Sat week logic.")


# @api.model
# def patched_read_group_process_groupby(self, gb, query):
#
#     if self._name not in ['mrp.production', 'mrp.workorder']:
#         return _original_process_groupby(self, gb, query)
#
#     split = gb.split(':')
#     field_name = split[0]
#     gb_function = split[1] if len(split) == 2 else None
#
#     field = self._fields.get(field_name)
#     if not field or field.type not in ('date', 'datetime') or gb_function != 'week':
#         print("📊------------------------------------------ Other model '%s', field: '%s'",
#               self._name, gb)
#         return _original_process_groupby(self, gb, query)
#
#     print("📊------------------------------------------ Custom groupby:week triggered for model '%s', field: '%s'",
#           self._name, gb)
#     tz_convert = field.type == 'datetime' and self._context.get('tz') in pytz.all_timezones
#     qualified_field = self._inherits_join_calc(self._table, field_name, query)
#
#     if tz_convert:
#         qualified_field = "timezone('%s', timezone('UTC',%s))" % (self._context.get('tz', 'UTC'), qualified_field)
#
#     qualified_field = f"""(
#         date_trunc('day', {qualified_field}::timestamp) -
#         ((EXTRACT(DOW FROM {qualified_field}::timestamp))::int) * INTERVAL '1 day'
#     )"""
#
#     return {
#         'field': field_name,
#         'groupby': gb,
#         'type': field.type,
#         'display_format': "'W'w yyyy",
#         'interval': datetime.timedelta(days=7),
#         'granularity': 'week',
#         'tz_convert': tz_convert,
#         'qualified_field': qualified_field,
#     }
#
# if not hasattr(BaseModel, "_custom_week_process_groupby_patched"):
#     BaseModel._read_group_process_groupby = patched_read_group_process_groupby
#     BaseModel._custom_week_process_groupby_patched = True
#     _logger.info("✅ GroupBy:week patched globally for Sun–Sat week logic.")