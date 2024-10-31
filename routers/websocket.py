from fastapi import APIRouter,WebSocket


def get_websocket_router(supabase_url: str):
    router = APIRouter(prefix="/ws", tags=["Websocket"])
    
    @router.websocket("/ranking")
    async def websocket_endpoint(websocket: WebSocket):
        pass