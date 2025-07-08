from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import asyncio

app = FastAPI()

# Mount overlay folder
app.mount("/overlay", StaticFiles(directory="overlay"), name="overlay")

# WebSocket connection pool
active_sockets = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_sockets.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    except:
        pass
    finally:
        active_sockets.remove(websocket)

# Broadcast RGB to all connected overlays
async def broadcast_rgb(r, g, b):
    message = f"{r},{g},{b}"
    for ws in list(active_sockets):
        try:
            await ws.send_text(message)
        except:
            active_sockets.remove(ws)

# Handle OSC input
def handle_rgb(addr, r, g, b):
    asyncio.create_task(broadcast_rgb(int(r), int(g), int(b)))

# Start OSC + WebSocket server together
def start_osc():
    dispatcher = Dispatcher()
    dispatcher.map("/rgb", handle_rgb)
    server = ThreadingOSCUDPServer(("0.0.0.0", 5005), dispatcher)
    print("OSC listening on UDP 5005")
    server.serve_forever()

if __name__ == "__main__":
    import threading
    import uvicorn

    osc_thread = threading.Thread(target=start_osc, daemon=True)
    osc_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8080)
