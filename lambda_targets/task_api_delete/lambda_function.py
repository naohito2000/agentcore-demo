"""
Task API Delete - Lambda for API Gateway
"""
import json
import os
import boto3

TABLE_NAME = os.environ.get('TABLE_NAME', 'agentcore-tasks')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Delete a task from DynamoDB
    """
    try:
        # pathParametersからIDを取得
        task_id = event.get('pathParameters', {}).get('id')
        
        if not task_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'success': False, 'error': 'task id is required'})
            }
        
        # DynamoDB削除
        table.delete_item(Key={'id': task_id})
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': True, 'id': task_id})
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
