import websockets
from datetime import datetime
import asyncio
import json
import uuid
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, inspect
from utils.logger import Logger
from utils.system_profiler import SystemProfiler

Base = declarative_base()

class settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
    
    def to_dict(self):
        return {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class ThinAgent(Logger):
    def __init__(self):
        super().__init__(self.__class__.__name__, 'thinagent.log', 'DEBUG')
        self.engine = create_engine('sqlite:///thinagent.db')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        if 'agent_id' not in self.settings:
            agent_id = uuid.uuid4().hex
            self.new_setting('agent_id', agent_id)
        self.websocket = None
        self.logger.debug(f'Agent ID: {self.settings["agent_id"]}')
        
    @property
    def agent_id(self):
        return self.settings['agent_id']
    
    @property
    def settings(self):
        return {setting.key: setting.value for setting in self.session.query(settings).all()}
        
    def update_setting(self, key, new_value):
        # Query the database for the setting
        setting = self.session.query(settings).filter_by(key=key).first()

        # If the setting exists, update its value
        if setting is not None:
            setting.value = new_value

            # Commit the changes to the database
            self.session.commit()

            # Update the value in the dictionary as well
            self.logger.debug(f'Setting {key} updated to {new_value}')
            self.settings[key] = new_value
            
            # Return True to indicate success
            self.logger.debug(f'Setting {key} updated to {new_value}')
            return True
        else:
            # Log an error if the setting was not found and return False
            self.logger.error(f'Setting {key} not found in the database.')
            return False
        
    def new_setting(self, key, value):
        # Create a new setting object
        setting = settings(key=key, value=value)

        # Add the setting to the session
        self.session.add(setting)

        # Commit the changes to the database
        self.session.commit()

        # Add the setting to the dictionary
        self.settings[key] = value
        
    def get_system_info(self):
        profiler = SystemProfiler(logger=self.logger)
        system_info = profiler.system_profile
        return system_info
            
    async def connect(self):
        self.websocket = await websockets.connect('ws://localhost:8080/ws')
            
    async def send(self, data):
        await self.websocket.send(data)
    
    async def receive(self):
        return await self.websocket.recv()
    
    async def main(self):
        await self.connect()
        while True:
            try:
                await self.send(f'get_client&id={self.agent_id}')
                response = await asyncio.wait_for(self.receive(), timeout=1)
                self.logger.debug(f'Received: {response}')
                now = datetime.now().timestamp()
                self.logger.debug(f'Now: {now}')
                data = json.loads(response)
                if 'last_seen' in data:
                    self.last_seen = data['last_seen']
                    self.logger.debug(f'Client last seen: {self.last_seen}')
                if now - self.last_seen > 60:
                    system_info = self.get_system_info()
                    await self.send(f"update_client&id={self.agent_id}&data={json.dumps(system_info)}")
                    self.logger.debug(f'Client updated: {system_info}')
                elif now - self.last_seen < 60:
                    self.logger.debug('Client is up to date.')
                    continue
            except json.JSONDecodeError:
                if response == 'Invalid request':
                    self.logger.error('Invalid request')
                elif response == 'Client not found':
                    system_info = self.get_system_info()
                    await self.send(f"add_client&id={self.agent_id}&data={json.dumps(system_info)}")
                    self.logger.debug(f'Client added: {system_info}')
            except Exception as e:
                self.logger.error(f'Error: {e}')
            finally:
                self.logger.debug('Next iteration in 30 seconds...')
                await asyncio.sleep(30)
            
        
    @property
    def loop(self):
        return asyncio.get_event_loop()

        
    
if __name__ == '__main__':
    agent = ThinAgent()
    agent.loop.run_until_complete(agent.main())
    