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
        super().__init__(self.__class__.__name__, 'thinagent.log', 'INFO')
        self.engine = create_engine('sqlite:///thinagent.db')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.last_seen = 0
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
      
    async def route(self, data):
        self.logger.debug(f'Routing: {data}')
        if 'message' in data and data['message'] == 'OK':
            await self.send({'message': 'OK'})
        if 'message' in data and data['message'] == 'client_id?':
            await self.send({'client_id': self.agent_id})
        elif 'message' in data and data['message'] == 'system_info?':
            try:
                system_info = self.get_system_info()
                await self.send(system_info)
            except Exception as e:
                self.logger.error(f'Error getting system info: {e}')
        elif 'message' in data and data['message'] == 'settings':
            await self.send(self.settings)
        elif 'message' in data and data['message'] == 'update_setting':
            if 'key' in data and 'value' in data:
                self.update_setting(data['key'], data['value'])
                await self.send({'message': 'Setting updated.'})
            else:
                await self.send({'message': 'Invalid request.'})
        elif 'message' in data and data['message'] == 'Connection closed':
            await self.websocket.close()
            self.websocket = None
            return True
            
    async def websocket_handler(self, websocket):
        self.websocket = websocket
        while True:
            try:
                response = await asyncio.wait_for(self.receive(), 5)
                try:
                    response = json.loads(response)
                except json.JSONDecodeError as e:
                    self.logger.error(f'Error decoding response: {e}')
                self.logger.debug(f'Received: {response}')
                stop = await self.route(response)
                if stop:
                    break
            except websockets.exceptions.ConnectionClosedError as e:
                self.logger.error(f'Connection closed: {e}')
                self.websocket = None
                break
            except websockets.exceptions.ConnectionClosedOK as e:
                self.logger.error(f'Connection closed: {e}')
                self.websocket = None
                break
            except Exception as e:
                self.logger.error(f'Error handling websocket: {e}')
                self.websocket = None
                break
            
                
    async def send(self, data):
        if type(data) == dict:
            try:
                data = json.dumps(data)
            except Exception as e:
                self.logger.error(f'Error converting data to json: {e}')
            try:
                await self.websocket.send(data)
            except websockets.exceptions.ConnectionClosedError as e:
                self.logger.error(f'Connection closed abnormally: {e}')
            except websockets.exceptions.ConnectionClosedOK as e:
                self.logger.error(f'Connection closed: {e}')
            except Exception as e:
                self.logger.error(f'Error sending data: {e}')
        else:
            self.logger.error('Data must be a dictionary.')
        
    
    async def receive(self):
        try:
            return await self.websocket.recv()
        except websockets.exceptions.ConnectionClosedError as e:
            return json.dumps({'message': 'Connection closed'})
        except websockets.exceptions.ConnectionClosedOK as e:
            return json.dumps({'message': 'Connection closed'})
        except Exception as e:
            return json.dumps({'message': f"Error receiving data. {e}"})
    
    async def main(self):
        async with websockets.serve(self.websocket_handler, 'localhost', 8765):
            await asyncio.Future()
     
    @property
    def loop(self):
        return asyncio.get_event_loop()

        
if __name__ == '__main__':
    agent = ThinAgent()
    try:
        agent.loop.run_until_complete(agent.main())
    except KeyboardInterrupt:
        agent.logger.info('Exiting...')
        agent.loop.stop()
        agent.loop.close()
        exit(0)
    