import asyncio  
import asyncpg  
  
async def main():  
    conn = await asyncpg.connect(host='db.kqjiayeidevoudpbvtcc.supabase.co', port=5432, user='postgres', password='Bhardwaj#@312', database='postgres')  
    await conn.execute('CREATE EXTENSION IF NOT EXISTS postgis;')  
    await conn.close()  
    print('PostGIS extension enabled.')  
  
if __name__ == '__main__':  
    asyncio.run(main())  
