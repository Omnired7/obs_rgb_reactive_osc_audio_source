from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import asyncio
import threading # to handle OSC and WebSocket concurrently

main_loop = None



socket_lock = threading.Lock()
active_sockets = set()

async def lifespan(app: FastAPI):
    global main_loop
    main_loop = asyncio.get_running_loop()
    print("🌐 Main event loop captured")
    yield  # app continues running here

app = FastAPI(lifespan=lifespan)

# Mount overlay folder
app.mount("/overlay", StaticFiles(directory="overlay"), name="overlay")

# WebSocket connection pool
active_sockets = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    with socket_lock:
        active_sockets.add(websocket)
    print("🟢 WebSocket connected")

    try:
        while True:
            await websocket.receive_text()
    except:
        pass
    finally:
        with socket_lock:
            active_sockets.remove(websocket)
            


# Broadcast RGB to all connected overlays
async def broadcast_rgb(r, g, b):
    message = f"{r},{g},{b}"
    print(f"🔴 Broadcasting: {message}")
    with socket_lock:
        sockets = list(active_sockets)

    for ws in sockets:
        try:
            await ws.send_text(message)
            print("✅ Sent to WebSocket")
        except Exception as e:
            print("❌ Failed to send", e)
            with socket_lock:
                active_sockets.discard(ws)

# Handle OSC input
def handle_rgb(addr, *args):
    print(f"Received /rgb from {addr} with args: {args}")
    if len(args) != 3:
        print("Invalid RGB input: expected 3 values, got", args)
        return
    try:
        r, g, b = map(int, args)
        # Schedule coroutine in main event loop from OSC thread
        asyncio.run_coroutine_threadsafe(broadcast_rgb(r, g, b), main_loop)
    except Exception as e:
        print("Error handling RGB values:", e)

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
    
    # Main event loop for asyncio
    main_loop = asyncio.get_event_loop()

    osc_thread = threading.Thread(target=start_osc, daemon=True)
    osc_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8080)
