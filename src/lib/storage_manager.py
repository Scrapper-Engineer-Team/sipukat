import json
import s3fs
import configparser
import os
from loguru import logger

class StorageManager:
    def __init__(self, key=None, secret=None, ip=None, port=None, config_path=None):
        config = configparser.ConfigParser()
        if config_path:
            config.read(config_path)
        else:
            config.read(os.path.join(os.path.dirname(__file__), '../../config.ini'))

        self.key = key or config.get('s3', 'key')
        self.secret = secret or config.get('s3', 'secret')
        self.ip = ip or config.get('s3', 'ip')
        self.port = port or config.get('s3', 'port')

        self.s3 = s3fs.S3FileSystem(
            key=self.key,
            secret=self.secret,
            client_kwargs={'endpoint_url': f'http://{self.ip}:{self.port}'}
        )

    def save(self, path_file, response):
        if path_file.startswith('s3://'):
            with self.s3.open(path_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.success(f'Downloaded to s3 : {path_file}')
        else:
            directory = os.path.dirname(path_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f'Created directory: {directory}')
            
            with open(path_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.success(f'Downloaded to local : {path_file}')

    def save_json(self, path_file, data):
        if path_file.startswith('s3://'):
            with self.s3.open(path_file, 'w') as f:
                f.write(json.dumps(data, indent=4, ensure_ascii=False))
            logger.success(f'Saved JSON to s3 :{path_file}')
        else:
            directory = os.path.dirname(path_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f'Created directory: {directory}')
            
            with open(path_file, 'w') as f:
                f.write(json.dumps(data, indent=4, ensure_ascii=False))
            logger.success(f'Saved JSON to local :{path_file}')
