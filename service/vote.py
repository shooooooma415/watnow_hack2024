from repository.get_attendance import GetAttendance
from repository.add_votes import AddVotes

class Vote():
    def __init__(self,supabase_url:str) -> None:
        self.get_attendance = GetAttendance(supabase_url)
        self.add_votes = AddVotes(supabase_url)
        
    def delete_vote(self, event_id:int, user_id:int):
        sanka_id = self.get_attendance.get_option_id(event_id, "参加")
        husanka_id = self.get_attendance.get_option_id(event_id, "不参加")
        totyuukara_id = self.get_attendance.get_option_id(event_id, "途中から参加")
        
        if self.get_attendance.is_option(user_id, sanka_id):
            self.add_votes.delete_vote(sanka_id,user_id)
        elif self.get_attendance.is_option(user_id, husanka_id):
            self.add_votes.delete_vote(husanka_id,user_id)
        elif self.get_attendance.is_option(user_id, totyuukara_id):
            self.add_votes.delete_vote(totyuukara_id,user_id)