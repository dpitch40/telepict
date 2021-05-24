import asyncio

import aioboto3

from . import ImageBackend, logger

class S3ImageBackend(ImageBackend):
    def __init__(self, bucket=None):
        self.bucket = bucket
        logger.info('S3ImageBackend initialized with bucket %s', self.bucket)

    def generate_key(self, d):
        return f'{d.stack.game_id}/{d.stack.owner.name}_{d.stack.id_}/{d.author.name}_{d.stack_pos}.jpg'

    async def _load(self, drawing):
        async with aioboto3.client('s3') as s3:
            obj = await s3.get_object(Bucket=self.bucket,
                                      Key=self.generate_key(drawing))
            return await obj['Body'].read()

    def _save(self, drawing):
        asyncio.run(self._save_async(drawing))

    async def _save_async(self, drawing):
        async with aioboto3.client('s3') as s3:
            await s3.put_object(Bucket=self.bucket,
                                Body=drawing.drawing,
                                Key=self.generate_key(drawing))
