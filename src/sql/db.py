import csv
import asyncpg
import asyncio
import os

class Database:
    def __init__(self):
        self.connection = None

    async def connect(self):
        self.connection = await asyncpg.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            timeout=60  # set a timeout of n seconds
        )

    async def execute_query(self, query, *params):
        if self.connection is None or self.connection.is_closed():
            await self.connect()

        try:
            async with asyncio.timeout(30):  # set a timeout of n seconds for the query execution
                async with self.connection.transaction():
                    result = await self.connection.fetch(query, *params)
                    return result
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError("Query timed out")
        
    async def export_to_csv(self, query, filename, *params):
        if self.connection is None or self.connection.is_closed():
            await self.connect()

        try:
            async with asyncio.timeout(30):  # set a timeout of n seconds for the query execution
                async with self.connection.transaction():
                    result = await self.connection.fetch(query, *params)
                    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        # Write headers
                        writer.writerow([desc for desc in result[0].keys()])
                        # Write rows
                        for row in result:
                            writer.writerow(row)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError("Query timed out")

    async def close(self):
        await self.connection.close()
