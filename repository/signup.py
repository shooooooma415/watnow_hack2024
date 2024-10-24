from sqlalchemy import create_engine, text

class signup:
    def __init__(self,supabase_url:str) ->None:
        self.engine = create_engine(supabase_url)