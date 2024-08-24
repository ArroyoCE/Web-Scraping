import requests
import json
import pprint

url = "https://api-publica.datajud.cnj.jus.br/api_publica_trf4/_search"

payload = json.dumps({
  "query": {
    "match": {
      "numeroProcesso": "50464207720204047000"
    }
  }
})

headers = {
  'Authorization': 'ApiKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

pprint.pprint(response.text)


input()