from fastapi import APIRouter,HTTPException
from model.profile import UserProfile,Name
from repository.profile import Profile
from service.fetch_profile import ProfileService
from service.notification import SendNotification
from model.auth import SuccessResponse



def get_users_router(supabase_url: str):
    router = APIRouter(prefix="/users", tags=["Users"])
    profile_service = ProfileService(supabase_url)
    profile = Profile(supabase_url)
    notification = SendNotification(supabase_url)

    @router.get("/{user_id}/profile",response_model=UserProfile)
    def get_name(user_id: int):
        user_profile = profile_service.fetch_profile(user_id)
        
        if user_profile is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user_profile

    @router.put("/{user_id}/profile/name", response_model=SuccessResponse)
    def renew_profile(input:Name,user_id:int):
        profile.update_name(user_id,input.name)
        return SuccessResponse(is_success = True)
    
    @router.put("/{user_id}/profile/aliase", response_model=SuccessResponse)
    def update_aliase(user_id:int):
        aliase_id = profile_service.judge_aliase(user_id)
        profile.update_aliase_id(user_id,aliase_id)
        notification.send_renew_aliase(user_id)
        return SuccessResponse(is_success = True)
    
    @router.get("/board")
    def get_all_user():
        pass
    
    return router