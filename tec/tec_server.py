import json
import asyncio
import os
import websockets
from datetime import datetime

from fastapi import FastAPI, WebSocket
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, inspect, Float
from utils.logger import Logger

Base = declarative_base()

class thinclients(Base):
    __tablename__ = 'thinclients'
    id = Column(String, primary_key=True)
    hostname = Column(String)
    ips = Column(JSON)
    bios = Column(JSON)
    mac = Column(String)
    os_ver = Column(String)
    os_arch = Column(String)
    os_build = Column(String)
    memory = Column(JSON)
    cpu = Column(JSON)
    gpu = Column(String)
    disks = Column(JSON)
    last_seen = Column(Float)
    status = Column(String)
    last_settings_update = Column(Float)
    
    def to_dict(self):
        return {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class TECServer(Logger):
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), 'tec_server.json')
        if not os.path.exists(config_path):
            print('Config file not found. Please create tec_server.json file and try again.')
            exit(1)
        else:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        super().__init__(self.__class__.__name__, 'tec_server.log', self.config['log_level'])
        self.engine = create_engine('sqlite:///tec_server.db')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        #self.api = FastAPI()
        #self.api.add_websocket_route('/ws', self.websocket_handler)
        self.websocket = None
        
    async def connect_to_client(self, protocol, client_ip, client_port):
        self.logger.info(f'Connecting to client @ {protocol}://{client_ip}:{client_port}')
        uri = f'{protocol}://{client_ip}:{client_port}'
        self.websocket = await websockets.connect(uri)
        
    async def send_data(self, data):
        await self.websocket.send(data)
    
    async def receive_data(self):
        return await self.websocket.recv()
    
    async def poll_client(self, protocol, ip, port):
        await self.connect_to_client(protocol, ip, port)
        await self.send_data(json.dumps({'message': 'client_id?'}))
        client_id = json.loads(await self.receive_data())['client_id']
        self.logger.debug(f"Client ID: {client_id}")
        await self.send_data(json.dumps({'message': 'OK'}))
        response = await self.receive_data()
        if json.loads(response) == {'message': 'OK'}:
            await self.send_data(json.dumps({'message': 'system_info?'}))
            response = await self.receive_data()
            self.logger.debug(f'System Info: {response}')
            system_info = json.loads(response)
            system_info['last_seen'] = datetime.now().timestamp()
            if self.session.query(thinclients).filter_by(id=client_id).first():
                self.session.query(thinclients).filter_by(id=client_id).update(system_info)
                self.session.commit()
                self.logger.info(f'System info updated in database for client {client_id}')
            else:
                self.session.add(thinclients(id=client_id, **system_info))
                self.session.commit()
                self.logger.info(f"System info saved to database for client {client_id}")
            
        else:
            self.logger.error('Error connecting to client.')
        self.logger.info('Closing connection...')
        await self.send_data(json.dumps({'message': 'Connection closed.'}))
        await self.websocket.close()
        await self.websocket.wait_closed()
        self.logger.info('Connection closed.')
                
            
    def run(self):
        asyncio.run(self.poll_client('ws', '127.0.0.1', '8765'))
    
if __name__ == '__main__':
    server = TECServer()
    server.run()
