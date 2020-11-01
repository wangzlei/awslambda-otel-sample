import os
import logging
# import jsonpickle
import aiohttp
import asyncio
import boto3

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def callAioHttp():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'http://httpbin.org/')
        # logger.info(html)

# Customer's lambda function
def lambda_handler(event, context):
    # logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    # logger.info('## EVENT\r' + jsonpickle.encode(event))
    # logger.info('## CONTEXT\r' + jsonpickle.encode(context))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(callAioHttp())

    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)

    return "200 OK"

