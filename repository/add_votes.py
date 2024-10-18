from sqlalchemy import create_engine, text

class AddVotes():
  def __init__(self,supabase_url:str) ->None:
    self.engine = create_engine(supabase_url)
  
  def add_votes(self):
    with self.engine.connect() as conn:
      with conn.begin():
        conn.execute(text(""))