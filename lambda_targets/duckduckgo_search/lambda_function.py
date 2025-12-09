"""
DuckDuckGo Search - Lambda Target
"""
import json
from duckduckgo_search import DDGS

def lambda_handler(event, context):
    """
    DuckDuckGo検索を実行
    
    Args:
        event: {
            "query": "search query",
            "max_results": 5
        }
    """
    try:
        query = event.get('query')
        max_results = event.get('max_results', 5)
        
        if not query:
            return {
                'error': 'query parameter is required'
            }
        
        # 検索実行
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        return {
            'results': results,
            'query': query,
            'count': len(results)
        }
        
    except Exception as e:
        return {
            'error': str(e)
        }
