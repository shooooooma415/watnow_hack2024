from sqlalchemy import create_engine, text

class AddVotes():
  def __init__(self,supabase_url:str) ->None:
    self.engine = create_engine(supabase_url)
  
  def insert_vote(self, option_id:int, user_id:int):
    with self.engine.connect() as conn:
      with conn.begin():
        conn.execute(text(
          "INSERT INTO votes (option_id, user_id) VALUES (:option_id, :user_id)"),
          {"option_id": option_id, "user_id": user_id}
        )
  
  def delete_vote(self, option_id: int, user_id: int):
    with self.engine.connect() as conn:
      with conn.begin():
        conn.execute(text(
          "DELETE FROM votes WHERE option_id = :option_id AND user_id = :user_id"),
          {"option_id": option_id, "user_id": user_id}
        )
