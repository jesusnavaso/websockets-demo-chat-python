from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from connection_manager import ConnectionManager  # Importing the ConnectionManager

app = FastAPI()
connection_manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.broadcast(f"Client #{id(websocket)}: {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast(f"Client #{id(websocket)} left the chat")

@app.get("/")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat Application</h1>
        <div id="chat">
            <ul id="messages"></ul>
        </div>
        <form id="form">
            <input id="input" autocomplete="off" placeholder="Type your message here..." />
            <button>Send</button>
        </form>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            const messages = document.getElementById('messages');
            const form = document.getElementById('form');
            const input = document.getElementById('input');

            ws.onmessage = function(event) {
                const messageItem = document.createElement('li');
                messageItem.textContent = event.data;
                messages.appendChild(messageItem);
                window.scrollTo(0, document.body.scrollHeight);
            };

            // Handle the WebSocket onclose event. You can execute we.close() in the browser console
            ws.onclose = function(event) {
                console.log("Disconnected from the WebSocket server");
                const messageItem = document.createElement('li');
                messageItem.textContent = "You have been disconnected from the chat";
                messageItem.style.color = "red";
                messages.appendChild(messageItem);
            };

            form.addEventListener('submit', function(event) {
                event.preventDefault();
                if (input.value) {
                    ws.send(input.value);
                    input.value = '';
                }
            });

            // Actions to perform before closing the browser window
            // window.addEventListener('beforeunload', function() {
            //     ws.send("The client has closed the tab");
            // });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html_content)