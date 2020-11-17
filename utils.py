maps =  {"mappings": {
            "properties": {
                "text": {
                    "type": "keyword",
                },
                "pos": {
                    "type": "keyword",
                }
            }
        }
    }

query_template = {
        "query": {
            'bool': {
                "must":[]
            }
        }
    }

