import json
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
        self.api = FastAPI()
        self.api.add_websocket_route('/ws', self.websocket_handler)
        
    async def websocket_handler(self, websocket: WebSocket):
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            async def route(data):
                if data == 'get_clients':
                    clients = self.session.query(thinclients).all()
                    self.logger.debug(f'Clients were Requested, sending {len(clients)} clients.')
                    for client in clients:
                        await websocket.send_text(json.dumps(client.to_dict()))
                elif 'get_client' in data:
                    try:
                        client_id = data.split('&')[1].split('=')[1] # get client id i.e get_client&id=1
                        client = self.session.query(thinclients).filter_by(id=client_id).first()
                        if client is None:
                            await websocket.send_text('Client not found')
                        else:
                            self.logger.debug(f'Client was Requested: {client.id}')
                            await websocket.send_text(json.dumps(client.to_dict()))
                    except Exception as e:
                        self.logger.error(f'Error getting client: {e}')
                        await websocket.send_text('Invalid request')
                elif 'update_client' in data:
                    try:
                        client_id = data.split('&')[1].split('=')[1] # get client id i.e update_client&id=1
                        client = self.session.query(thinclients).filter_by(id=client_id).first()
                        if client is None:
                            await websocket.send_text('Client not found')
                            return
                        client_data = json.loads(data.split('&')[2].split('=')[1]) # get client data i.e update_client&id=1&data={"hostname": "test"}
                        client_data['last_seen'] = datetime.now().timestamp() # update last_seen
                        if client_data is None:
                            await websocket.send_text('Invalid client data')
                            return
                        for key, value in client_data.items():
                            setattr(client, key, value)
                        self.session.commit()
                        self.logger.debug(f'Client was Updated: {client} with data: {client_data}')
                        await websocket.send_text('Client updated successfully')
                    except Exception as e:
                        self.logger.error(f'Error updating client: {e}')
                        await websocket.send_text('Invalid request')
                elif 'add_client' in data:
                    try:
                        client_id = data.split('&')[1].split('=')[1] # get client id i.e add_client&id=1
                        self.logger.debug(f'Client ID: {client_id}')
                        if not client_id:
                            await websocket.send_text('Invalid client id')
                            return
                        client_data = json.loads(data.split('&')[2].split('=')[1]) # get client data i.e add_client&id=1&data={"hostname": "test"}
                        client_data['last_seen'] = datetime.now().timestamp() # update last_seen
                        self.logger.debug(f'Client Data: {client_data}')
                        if client_data is None:
                            await websocket.send_text('Invalid client data')
                            return
                        client = thinclients(id=client_id, **client_data)
                        self.session.add(client)
                        self.session.commit()
                        self.logger.debug(f'Client was Added: {client} with data: {client_data}')
                        await websocket.send_text('Client added successfully')
                    except Exception as e:
                        self.logger.error(f'Error adding client: {e}')
                        await websocket.send_text('Invalid request')
                else:
                    self.logger.debug(f'Invalid request: {data}')
                    await websocket.send_text('Invalid request')

            await route(data)
            
    def run(self):
        '''
        run is a method that runs the API application.
        
        This method runs the API application using the uvicorn module. The host and port are specified in the config.json file.
        '''
        import uvicorn
        uvicorn.run(self.api, host=self.config['host'], port=int(self.config['port']))
        
if __name__ == '__main__':
    server = TECServer()
    server.run()