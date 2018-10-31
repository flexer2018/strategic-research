from elasticsearch_dsl import Q, Search

# from StrategicResearch.elastic import client
from elasticsearch import Elasticsearch
AWS_EP = "https://search-strategic-research-67yfnme5nbl3c45vigirwnko4q.us-east-2.es.amazonaws.com/"
client = Elasticsearch(AWS_EP)


def get_element_filter(name):

	ALL = {
		"bool":{
			"must":[],
			"should":[],
			"must_not":[]
		}
	}

	bridges = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title":"bridge"}},
						{"match": {"abstract": "bridge"}}
					]
					}
				}
			],
			"should":[],
			"must_not":[]
		}
	}

	deck = {
		"bool": {
			"must": [
				{
					"bool": {
					"should": [
						{"match": {"title":"decks"}},
						{"match": {"abstract":"decks"}}
					]
					}
				}
			],
			"should": [],
			"must_not":[
				{
					"bool": {
						"should": [
							{"match": {"title":"overlay"}},
							{"match": {"abstract": "overlay"}},
							{"match": {"title.bigram":"wearing surface"}},
							{"match": {"abstract.bigram": "wearing surface"}}
						]
					}
				}
			]
		}
	}

	overlay = {
		"bool":{
			"must":[
				{
					"bool": {
						"should": [
							{"match": {"title":"overlay"}},
							{"match": {"abstract": "overlay"}},
							{"match": {"title.bigram":"wearing surface"}},
							{"match": {"abstract.bigram": "wearing surface"}}
						]
					}
				}
			],
			"should":[],
			"must_not":[]
		}
	}

	joints = {
		"bool":{
			"must":[
				{
					"bool": {
						"should": [
							{"match": {"title":"joints"}},
							{"match": {"abstract": "joints"}}
						]
					}
				}
			],
			"should":[],
			"must_not":[]
		}
	}

	bearings = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title":"bearings"}},
						{"match": {"abstract": "bearings"}}
					]
					}
				}
			],
			"should":[],
			"must_not":[]
		}
	}


	filters = dict(
		all=ALL,
		bridges=bridges,
		untreated_deck=deck,
		treated_deck=overlay,
		joints=joints,
		bearings=bearings
	)

	return filters.get(name)


def get_filter_clause(filters, index=None):

	element = get_element_filter(filters.get("element"))

	selected_status = filters.get("status")
	if selected_status == "all":
		status = {
			"bool":{
				"must":[],
				"should":[],
				"must_not":[]
			}
		}
	elif selected_status != None:
		status = {
			"bool":{
				"must":[{"term": {"status": selected_status}}],
				"should":[],
				"must_not":[]
			}
		}
	else:
		status = None

	selected_date_range = filters.get('date_range')
	if index == 'projects':
		if selected_date_range == 10 or selected_date_range == "10":
			date_range = {
				"bool": {
					"should": [
						# {"range": { "actual_complete_date": { "gte": "now-50y"}}},
						# {"range": { "expected_complete_date": { "gte": "now-50y"}}},
						{"range": { "start_date": { "gte": "now-50y"}}}
					]
				}
			}
		elif selected_date_range != None:
			if selected_date_range == 'future':
				
				date_range = {
				"bool": {
					"should": [
						{"range": { "start_date": { "gte": f"now-{filters.get('date_range')}y"}}}
						]
					}
				}

			else:

				date_range = {
					"should": [
						{"range": { "start_date": { "gte": f"now+{filters.get('date_range')}y"}}}
						]
					}
		
			
		else:
			date_range = None
	else:
		if selected_date_range == 10 or selected_date_range == "10":
			date_range = {
				"bool": {
					"should": [
						{"range": { "publication_date": { "gte": "now-50y"}}}
					]
				}
			}
		elif selected_date_range != None:
			date_range = {
				"bool": {
					"should": [
						{"range": { "publication_date": { "gte": f"now-{filters.get('date_range')}y"}}}
					]
				}
			}
		else:
			date_range = None

	topic_query = filters.get("topic")
	if topic_query == "all":
		topic = {
			"bool":{
				"must":[],
				"should":[],
				"must_not":[]
			}
		}
	elif topic_query != None:
		# topic = {
		# 	"bool":{
		# 		"must":[get_topic_query(topic, index=index)],
		# 	}
		# }
		topic = get_topic_query(topic_query, index=index)
	else:
		topic = None

	must = []
	if index == 'projects':
		_filters = [
				element,
				status,
				date_range,
				topic
			]
		for f in _filters:
			if f:
				must.append(f)
	else:
		_filters = [
				element,
				date_range,
				topic
			]
		for f in _filters:
			if f:
				must.append(f)


	f = [
		{
			"bool":{
				"must":must,
				"should":[],
				"must_not":[]
			}
		}
	]

	return f


def get_topic_query(name, filters=None, index=None):

	if filters:
		filter_clause=get_filter_clause(filters, index)
	else:
		filter_clause = []

	ALL = {
		"bool":{
			"must":[],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	deck = {
		"bool": {
			"must": [
				{
					"bool": {
						"should": [
							{"match": {"title":"decks"}},
							{"match": {"abstract":"decks"}}
						]
					}
				}
			],
			"filter": filter_clause,
			"should": [],
			"must_not":[
				{
					"bool": {
						"should": [
							{"match": {"title":"overlay"}},
							{"match": {"abstract": "overlay"}},
							{"match": {"title.bigram":"wearing surface"}},
							{"match": {"abstract.bigram": "wearing surface"}}
						]
					}
				}
			]
		}	
	}

	overlay = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title":"overlay"}},
						{"match": {"abstract": "overlay"}},
						{"match": {"title.bigram":"wearing surface"}},
						{"match": {"abstract.bigram": "wearing surface"}}
					]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	joints = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title":"joints"}},
						{"match": {"abstract": "joints"}}
					]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	bearings = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title":"bearings"}},
						{"match": {"abstract": "bearings"}}
					]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	construction_quality = {
		"bool": {
			"must": [
				{
					"bool": {
					"should": [
						{"match": {"title":"construction"}},
						{"match": {"abstract":"construction"}}
					]
					}
				}
			],
			"filter": filter_clause,
			"should": [
				{"match":{"title":"quality"}},
				{"match":{"abstract":"quality"}},
				{"match":{"title.bigram":"construction quality"}},
				{"match":{"abstract.bigram":"construction quality"}}
			],
			"must_not":[]
		}
	}

	design_and_details = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title":"design"}},
						{"match": {"abstract":"design"}}
					]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	material_specifications = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title":"materials"}},
						{"match": {"abstract":"materials"}}
					]
					}
				}
			],
			"filter": filter_clause,
			"should":[
				{"match": {"title.bigram":"material specifications"}},
				{"match": {"abstract.bigram":"material specifications"}}
			],
			"must_not":[]
		}
	}

	live_load = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title.bigram":"live load"}},
						{"match": {"abstract.bigram":"live load"}}
					]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	environment = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title":"environment"}},
						{"match": {"abstract":"environment"}}
					]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	maintenance_and_preservation = {
		"bool":{
			"must":[
				{
					"bool": {
						"should": [
							{"match": {"title":"maintenance"}},
							{"match": {"abstract":"maintenance"}},
							{"match": {"title":"preservation"}},
							{"match": {"abstract":"preservation"}}
						]
					}
				}
			],
			"filter": filter_clause,
			"should":[
				{"match": {"title.bigram":"maintenance and preservation"}},
				{"match": {"abstract.bigram":"maintenance and preservation"}}
			],
			"must_not":[]
		}
	}

	structural_integrity = {
		"bool":{
			"must":[
				{
					"bool": {
						"should": [
							{"match": {"title.bigram":"structural integrity"}},
							{"match": {"abstract.bigram":"structural integrity"}}
						]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	structural_condition = {
		"bool":{
			"must":[
				{
					"bool": {
						"should": [
							{"match": {"title.bigram":"structural condition"}},
							{"match": {"abstract.bigram":"structural condition"}}
						]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	functionality = {
		"bool":{
			"must":[
				{
					"bool": {
						"should": [
							{"match": {"title":"functionality"}},
							{"match": {"abstract":"functionality"}}
						]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	cost = {
		"bool":{
			"must":[
				{
					"bool": {
					"should": [
						{"match": {"title":"cost"}},
						{"match": {"abstract":"cost"}}
					]
					}
				}
			],
			"filter": filter_clause,
			"should":[],
			"must_not":[]
		}
	}

	queries = dict(
		all=ALL,
		construction_quality=construction_quality,
		design_and_details=design_and_details,
		material_specifications=material_specifications,
		live_load=live_load,
		environment=environment,
		maintenance_and_preservation=maintenance_and_preservation,
		structural_integrity=structural_integrity,
		structural_condition=structural_condition,
		functionality=functionality,
		cost=cost,
		deck=deck,
		overlay=overlay,
		joints=joints,
		bearings=bearings
	)

	return queries.get(name)


def run_query(index, q, filters=None):

	# initialize search object
	s = Search(using=client, index=index)

	sort_by = filters.get('sort_by', '_score')
	status = filters.get('status')

	# sorting
	if sort_by == 'date':
		if index == 'projects':
			s.sort({"start_date": {"order": "desc"}})
		elif index == 'publications':
			s.sort("-publication_date")

	# query and return the response
	r = s.query(q)
	
	return r


def process_response(r):
	# process documents returned by the search
	hits = {}
	for h in r.scan():
		# get data from document fields
		doc_id = h.meta.id
		title = h.title
		abstract = h.abstract
		# matched_queries = list(h.meta.matched_queries)
		score = h.meta.score
		trid_terms = h.TRID_INDEX_TERMS
		trid_subjects = h.TRID_SUBJECT_AREAS
		# store documents returned by the search
		hits[doc_id] = dict(
			title = title,
			abstract = abstract,
			trid_terms = trid_terms,
			trid_subjects = trid_subjects,
			# matched_queries = matched_queries,
			score = score
		)
	return hits


# def match(query, field, name='match'):
# 	"""
# 	Return 'match' query object for the provided
# 	query and field.

# 	Parameters
# 	----------
# 	query : str
# 	The provided query string.
# 	field : str
# 	The field to be queried.
# 	[name] : str
# 	A name given to the query.

# 	Returns
# 	-------
# 	A query object for the provided query and field.

# 	"""
# 	# construct the query
# 	q = Q(
# 	{
# 		"match": {
# 		f"{field}": {
# 			"query": query,
# 			"_name": f"[{name}]{field}:{query}"
# 		}
# 		}
# 	}
# 	)

# 	return q


# def wildcard(query, field, name='wildcard'):
# 	"""
# 	Return 'wildcard' query object for the provided
# 	query and field.

# 	Parameters
# 	----------
# 	query : str
# 	The provided query string.
# 	field : str
# 	The field to be queried.
# 	[name] : str
# 	A name given to the query.

# 	Returns
# 	-------
# 	A query object for the provided query and field.

# 	"""
# 	# construct the query
# 	q = Q(
# 	{
# 		"wildcard": {
# 		f"{field}": {
# 			"value": query,
# 			"_name": f"[{name}]{field}:{query}"
# 		}
# 		}
# 	}
# 	)

# 	return q


# def get_query_func(query_type):
# 	"""
# 	Return query function for provided query_type.

# 	Parameters
# 	----------
# 	query_type : str
# 	The provided query type.

# 	Returns
# 	-------
# 	A query function for the provided query type.
# 	"""
# 	query_functions = {
# 	"match": match,
# 	"wildcard": wildcard,
# 	}
# 	return query_functions.get(query_type)


# def boolean(must=None, should=None, must_not=None):
# 	"""
# 	Return 'bool' query object for the provided 'must',
# 	'should', and 'must_not' queries.

# 	'must' queries require a document to match the query in
# 	the provided field for the specified query type.

# 	'must_not' queries exclude documenta that match the query
# 	in the provided field for the specified query type.

# 	'should' queries only affect the relevance score of the
# 	matched documents (i.e. the ordering of the documents returned).

# 	Parameters
# 	----------
# 	must      : dict
# 	Dictionary in the form of {type:[(field,query),...]} for
# 	queries that must match in the provided field for the
# 	specified query type.
# 	should    : dict
# 	Dictionary in the form of {type:[(field,query),...]} for
# 	queries that must match in the provided field for the
# 	specified query type.
# 	must_not  : dict
# 	Dictionary in the form of {type:[(field,query),...]} for
# 	queries that must match in the provided field for the
# 	specified query type.

# 	Returns
# 	-------
# 	A query object for the provided queries and field(s).

# 	"""
# def get_bool_queries(clause, name):
# 	# example input: clause=dict(type=[(field,query),...])
# 	queries = []
# 	if clause is not None:
# 		# construct list of boolean clauses
# 		for query_type in clause.keys():
# 		query_func = get_query_func(query_type)
# 		for field, query in clause.get(query_type):
# 			queries.append(query_func(query, field, name=name))
# 	return queries

# 	# get must queries
# 	must_clauses = get_bool_queries(must, 'must')
# 	# get should queries
# 	should_clauses = get_bool_queries(should, 'should')
# 	# get must_not queries
# 	not_clauses = get_bool_queries(must_not, 'must_not')

# 	# construct the query
# 	q = Q("bool",
# 	must=must_clauses,
# 	should=should_clauses,
# 	must_not=not_clauses
# 	)

# 	return q


# def multimatch(query, fields, query_type='match'):
# 	"""
# 	Return 'multi_match' query object for the provided query
# 	and list of fields.

# 	Parameters
# 	----------
# 	query : str
# 	The provided query string.
# 	fields : list
# 	The list of fields to be queried.
# 	[query_type] : str
# 	The default query type.

# 	Returns
# 	-------
# 	A query object for the provided queries and field(s).
# 	"""
# 	# check if wildcard query is needed
# 	if "*" in query:
# 	query_type='wildcard'

# 	# construct 'should' data strucutre
# 	should = {query_type: []}
# 	for field in fields:
# 	should[query_type].append((field,query))

# 	# this bool query is equivalent to the multi_match query
# 	# with a most_fields type
# 	q = boolean(should=should)

# 	return q

# 	# function that constructs should clause for queries and fields
# def construct_bool_clause(queries, fields):
# 	all_queries=[]
# 	for query in queries:
# 	for field in fields:
# 		query_field = get_query_field(query, field)
# 		all_queries.append((query_field,query))
# 	should = dict(match=all_queries)
# 	return should

# 	# function that returns a list of fields based on provided query
# def get_query_field(query, field):
# 	n_terms = len(query.split(" "))
# 	if n_terms == 1:
# 	return field
# 	if n_terms == 2:
# 	return field + ".bigram"
# 	if n_terms == 3:
# 	return field + ".trigram"
# 	if n_terms == 4:
# 	return field + ".quadragram"
# 	if n_terms == 5:
# 	return field + ".pentagram"
# 	# otherwise
# 	return field

# 	# function that constructs phrase from query term and prefixes
# def construct_phrase_queries(query, prefixes):
# 	phrase_queries = []
# 	for prefix in prefixes:
# 		phrase_queries.append(f"{prefix} {query}")
# 	return phrase_queries

