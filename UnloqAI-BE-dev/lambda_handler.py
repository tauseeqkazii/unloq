# from mangum import Mangum
# from app.main import app

# # Lambda handler
# handler = Mangum(app)

import json
import os
import sys
import traceback

# Diagnostic: Track what's in the current directory
try:
    print(f"DEBUG: Current directory files: {os.listdir('.')}")
except:
    pass

# Ensure current directory is in sys.path
current_dir = os.path.dirname(os.path.realpath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def handler(event, context):
    """Main Lambda handler with resilience and multi-format support"""
    try:
        # 1. IDENTIFY EVENT FORMAT (REST v1.0 vs HTTP v2.0)
        request_context = event.get('requestContext', {})
        http_info = request_context.get('http', {})
        
        # Method and Path extraction (v1.0 vs v2.0)
        method = event.get('httpMethod') or http_info.get('method', 'UNKNOWN')
        path = event.get('path') or event.get('rawPath') or 'no-path'
        
        # Log basic info for EVERY request
        print(f"DEBUG: Received [{method}] {path}")
        
        # 2. HYPER-CORS BYPASS (Immediate response for OPTIONS)
        if method == 'OPTIONS':
            print(f"DEBUG: Handling preflight for {path} at Lambda level")
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Max-Age": "86400"
                },
                "body": json.dumps({"message": "Hyper-CORS preflight successful"})
            }

        # 3. FASTAPI EXECUTION
        from mangum import Mangum
        from app.main import app
        
        # Action logging (for your seed/bedrock tasks)
        action = event.get('action')
        if action:
            print(f"DEBUG: Action requested: {action}")
            if action == 'seed':
                from lambda_seed_handler import seed_handler
                return seed_handler(event, context)
        
        # Default: FastAPI via Mangum
        mangum_handler = Mangum(app)
        return mangum_handler(event, context)
        
    except Exception as e:
        error_msg = f"CRITICAL: Lambda initialization failed: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        
        # Return exact error for debugging
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal Server Error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "sys_path": sys.path,
                "current_dir": os.getcwd(),
                "dir_contents": os.listdir('.') if hasattr(os, 'listdir') else []
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        }
