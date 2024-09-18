from model.event import Event
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class EventRepo():
    def __init__(self,supabase_url:str):
        self.engine = create_engine(supabase_url)

    def add_events(self,input:Event):
        title = input.title
        description = input.description
        is_all_day = input.is_all_day
        start_time = input.start_time
        end_time = input.end_time
        closing_time = input.closing_time
        location_name = input.location_name
        location_point = input.location_point
        cost = input.cost
        message = input.message
        manager_id = input.manager_id
        option = input.options.title
        with self.engine.connect() as conn:
            try:
                event_id = conn.execute(text("""
                    INSERT INTO events(
                        title, description, is_all_day, start_date_time, end_date_time, closing_date_time, loacton_name, location_point, cost, message, manager_id
                    ) 
                    VALUES(title, description, is_all_day, start_time, end_time, closing_time, location_name, location_point, cost, message, manager_id, options) 
                    RETURNING id
                    """)).mappings()
                result = conn.execute(text("INSERT INTO options(event_id,title) VALUE(:event_id, :option)"),{"event_id":event_id, "option":option}).mappings()
                return event_id
            except SQLAlchemyError as e:
                return str(e)
            