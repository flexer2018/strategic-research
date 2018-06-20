from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from models import Project

tags = [
  "live load",
  "truck load",
  "environment",
  "freeze-thaw",
  "maintenance",
  "deicing",
  "construction",
  "material specifications",
  "reinforcement",
  "cover",
  "cracking",
  "delamination",
  "deterioration",
  "sealing",
  "destructive evaluation",
  "material sampling",
  "field testing",
  "data collection",
  "preservation",
  "overlay",
  "service life",
  "truck load",
  "wheel load"
  "washing",
  "bridge joints",
  "bridge bearings",
  "bridge deck",
  "curing",
  "construction",
  "cost",
  "admixture",
  "temperature",
  "precipitation",
  "visual inspection"
]

index = 'projects'
doc_type = 'doc'
fields = ["title","abstract","notes","TRID_INDEX_TERMS","TRID_SUBJECT_AREAS"]
client = Elasticsearch()
s = Search(using=client,index=index)

for tag in tags:
  
  q = Q(
    {
      "multi_match":{
        "query": tag,
        "type":"best_fields",
        "fields": fields
      }
    }
  )
 
  response = s.query(q)
  count = response.count()
  print(f'[{count} Hit(s) for Tag = "{tag}"]')

  for r in response.scan():
    id = r.meta.id
    doc = Project.get(using=client,index=index,id=id)
    tags = list(doc.tags)
    tags.append(tag)
    tag_set = set(tags)
    doc.update(using=client,index=index,tags=list(tag_set))
    print(f'\tDoc ({id}): updated')

  



#   q = {
#      "script": {
#         "inline": "ctx._source.tags.append='Test'",
#         "lang": "painless"
#      },
#      "query": {
#         "multi_match":{
#           "query": tag,
#           "type":"best_fields",
#           "fields": fields
#         }
#      }
# }