import os  
import uvicorn  
  
if __name__ == '__main__':  
    port_str = os.environ.get('X_ZOHO_CATALYST_LISTEN_PORT', '8000')  
    try:  
        port = int(port_str)  
    except ValueError:  
        port = 8000  
    print(f'Starting uvicorn on 0.0.0.0:{port}')  
    uvicorn.run('app.main:app', host='0.0.0.0', port=port) 
