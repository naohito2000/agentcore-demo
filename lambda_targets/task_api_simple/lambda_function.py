"""
Task API Lambda (API Gateway用、Zip形式)
"""
import json
import os
import uuid
from datetime import datetime
import boto3

TABLE_NAME = os.environ.get('TABLE_NAME', 'agentcore-tasks')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    API Gateway経由でタスクを作成・取得
    """
    print(f"Event: {json.dumps(event)}")
    
    try:
        # HTTPメソッド確認
        http_method = event.get('httpMethod', 'POST')
        
        # GETリクエスト - タスク一覧取得
        if http_method == 'GET':
            response = table.scan()
            tasks = response.get('Items', [])
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'success': True, 'tasks': tasks})
            }
        
        # POSTリクエスト - タスク作成
        # API Gateway Payload Format 2.0
        if 'body' in event and isinstance(event['body'], str):
            data = json.loads(event['body'])
        else:
            data = event
        
        title = data.get('title')
        description = data.get('description', '')
        assignee = data.get('assignee', '')
        due_date = data.get('due_date', '')
        priority = data.get('priority', 'medium')
        
        if not title:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'success': False, 'error': 'title is required'})
            }
        
        # タスク作成
        task = {
            'id': str(uuid.uuid4()),
            'title': title,
            'description': description,
            'status': 'todo',
            'priority': priority,
            'assignee': assignee,
            'due_date': due_date,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # DynamoDB書き込み
        table.put_item(Item=task)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': True, 'task': task})
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': False, 'error': str(e)})
        }
