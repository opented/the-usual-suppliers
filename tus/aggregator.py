import math
from flask import url_for
from sqlalchemy import func, select, and_
from sqlalchemy.dialects.postgresql import FLOAT

from monnet.ted.util import documents_table, contracts_table
#from monnet.ted.util import references_table, cpvs_table
from monnet.ted.util import engine

from tus.util import arg_default


PAGE_SIZE = 15

contract_alias = contracts_table.table.alias('contract')
document_alias = documents_table.table.alias('document')
_tables = [contract_alias, document_alias]


def name_to_field(name):
    table, column = name.split('_', 1)
    for alias in _tables:
        if alias.name == table:
                return alias.columns[column]


class AggregateState(object):
    pass


def aggregate_request():
    filters = []
    state = AggregateState()

    state.drilldown_options = {
        'contract_operator_official_name': "Supplier",
        'contract_authority_official_name': "Authority",
        #'contract_operator_country': "Supplier country",
        #'contract_authority_country': "Authority country",
        'document_title_text': "Contract",
    }
    state.drilldown = arg_default('drilldown', 'contract_operator_official_name')

    state.sort_options = {
        '_drilldown': "Alphabetically",
        'total_value_cost_eur': "Total value of contracts",
        'count': "Number of contracts"
    }
    state.sort = arg_default('sort', 'total_value_cost_eur')
    if state.sort == '_drilldown':
        state.sort = state.drilldown

    state.country_options = []
    for c in documents_table.distinct('country_common', 'iso_country'):
        state.country_options.append((c.get('iso_country'),
                                      c.get('country_common')))
    state.country_options = [('', 'All countries')] + state.country_options

    state.country = arg_default('country', '')
    if state.country:
        f = document_alias.c.iso_country == state.country
        filters.append(f)

    state.q = arg_default('q', None)
    if state.q is not None:
        f = name_to_field(state.drilldown)
        filters.append(f.ilike('%%%s%%' % state.q))

    state.page = int(arg_default('page', 1))
    offset = (state.page - 1) * PAGE_SIZE

    query = {'q': state.q, 'sort': state.sort, 'country': state.country,
             'drilldown': state.drilldown, 'page': state.page}

    count, results = aggregate(group_by=[state.drilldown],
                               order_by=[(state.sort, 'desc')],
                               _filters=filters, offset=offset)
    
    state.next = None
    if state.page < math.ceil(count / PAGE_SIZE):
        q = query.copy()
        q['page'] = q['page'] + 1
        state.next = url_for('index', **q)

    state.prev = None
    if state.page > 1:
        q = query.copy()
        q['page'] = q['page'] - 1
        state.prev = url_for('index', **q)

    state.count = count
    state.results = results
    return state


def aggregate(group_by=[], order_by=[('total_value_cost_eur', 'desc'), ], _filters=[],
              limit=PAGE_SIZE, offset=0):
    _filters = list(_filters)

    _fields = [
        func.count(func.distinct(contract_alias.c.id)).label('count'),
        func.sum(func.cast(contract_alias.c.total_value_cost_eur, FLOAT)).label('total_value_cost_eur'),
        #func.sum(func.cast(contract_alias.c.initial_value_cost_eur, FLOAT)).label('initial_value_cost_eur'),
        #func.sum(func.cast(contract_alias.c.contract_value_cost_eur, FLOAT)).label('contract_value_cost_eur')
        ]

    _filters.append(contract_alias.c.doc_no == document_alias.c.doc_no)
    _filters.append(contract_alias.c.total_value_cost_eur != None)
    _filters.append(contract_alias.c.total_value_currency == 'EUR')
    _filters = and_(*_filters)
    
    _group_by = []
    for group in group_by:
        f = name_to_field(group)
        if f is not None:
            _group_by.append(f)
            _fields.append(f)
            _filters.append(f != None)

    _order_by = []
    for field in _fields:
        for name, direction in order_by:
            if field._label == name:
                _order_by.append(field.desc().nullslast() if direction == 'desc' else field.asc())

    q = select(_group_by, _filters, _tables, use_labels=True,
               group_by=_group_by).alias('foo')
    count = list(engine.query(q.count())).pop().values().pop()
    q = select(_fields, _filters, _tables, use_labels=True,
               group_by=_group_by, order_by=_order_by,
               limit=limit, offset=offset)
    return count, engine.query(q)


def contracts_request():
    filters = []

    val = arg_default('value', '')
    if val:
        drilldown = arg_default('drilldown', '')
        if drilldown:
            f = name_to_field(drilldown) == val
            filters.append(f)

    country = arg_default('country', '')
    if country:
        f = document_alias.c.iso_country == country
        filters.append(f)

    return list_contracts(_filters=filters)


def list_contracts(_filters=[]):
    _filters = list(_filters)

    _fields = [
        document_alias.c.doc_url,
        document_alias.c.title_text,
        document_alias.c.oj_date,
        contract_alias.c.total_value_cost_eur,
        contract_alias.c.operator_official_name
    ]

    _filters.append(contract_alias.c.doc_no == document_alias.c.doc_no)
    _filters.append(contract_alias.c.doc_no != None)
    #_filters.append(contract_alias.c.total_value_currency == 'EUR')
    _filters = and_(*_filters)
    
    _order_by = [document_alias.c.oj_date.asc()]
    
    q = select(_fields, _filters, _tables, use_labels=True,
               order_by=_order_by)
    return engine.query(q)

