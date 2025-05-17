from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import BaseModel
import mcp.server.stdio
from mcp.server.sse import SseServerTransport
from mcp.server.websocket import websocket_server
import argparse
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute, Route, Mount
import uvicorn

mcp_server = Server("calculator-mcp")

class AddRequest(BaseModel):
    a: int
    b: int

def add(request: AddRequest) -> int:
    return request.a + request.b

class SubtractRequest(BaseModel):
    a: int
    b: int

def subtract(request: SubtractRequest) -> int:
    return request.a - request.b

class MultiplyRequest(BaseModel):
    a: int
    b: int

def multiply(request: MultiplyRequest) -> int:
    return request.a * request.b

class DivideRequest(BaseModel):
    a: int
    b: int

def divide(request: DivideRequest) -> float | str:
    if request.b == 0:
        return "cannot divide by 0"
    return request.a / request.b

@mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="add",
            description="Add a and b, returning their sum",
            inputSchema=AddRequest.model_json_schema(),
        ),
        types.Tool(
            name="subtract",
            description="Subtract b from a, returning their difference",
            inputSchema=SubtractRequest.model_json_schema(),
        ),
        types.Tool(
            name="multiply",
            description="Multiply a by b, returning their product",
            inputSchema=MultiplyRequest.model_json_schema(),
        ),
        types.Tool(
            name="divide",
            description="Divide a by b, returning their quotient",
            inputSchema=DivideRequest.model_json_schema(),
        ),
    ]

@mcp_server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    match name:
        case "add":
            sum = add(AddRequest(**arguments))
            return [
                types.TextContent(
                    type="text",
                    text=f"The sum of {arguments['a']} and {arguments['b']} is {sum}",
                )
            ]
        case "subtract":
            difference = subtract(SubtractRequest(**arguments))
            return [
                types.TextContent(
                    type="text",
                    text=f"The difference of {arguments['a']} and {arguments['b']} is {difference}",
                )
            ]
        case "multiply":
            product = multiply(MultiplyRequest(**arguments))
            return [
                types.TextContent(
                    type="text",
                    text=f"The product of {arguments['a']} and {arguments['b']} is {product}",
                )
            ]
        case "divide":
            quotient = divide(DivideRequest(**arguments))
            if quotient == "cannot divide by 0":
                return [
                    types.TextContent(
                        type="text",
                        text=quotient,
                    )
                ]
            return [
                types.TextContent(
                    type="text",
                    text=f"The quotient of {arguments['a']} and {arguments['b']} is {quotient}",
                )
            ]
        case _:
            raise ValueError(f"Unknown tool: {name}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ws', action='store_true', help='Run as websocket server')
    parser.add_argument('--sse', action='store_true', help='Run as SSE server')
    args = parser.parse_args()

    if args.ws:
        # TODO: websocket is untested
        print("=== Running as websocket server ===", flush=True)
        # Run the server using websocket
        async def handle_ws(websocket):
            async with websocket_server(
                websocket.scope, websocket.receive, websocket.send
            ) as streams:
                await mcp_server.run(
                    streams[0],
                    streams[1],
                    InitializationOptions(
                        server_name="calculator-mcp",
                        server_version="0.1.0",
                        capabilities=mcp_server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    )
                )
        app = Starlette(
            routes=[
                WebSocketRoute("/ws", endpoint=handle_ws),
            ]
        )
        server_port = 8000
        print(f"=== Starting server on ws://127.0.0.1:{server_port}/ws ===", flush=True)
        uvicorn_server = uvicorn.Server(
            config=uvicorn.Config(
                app=app, host="127.0.0.1", port=server_port, log_level="info"
            )
        )
        await uvicorn_server.serve()
    elif args.sse:
        print("=== Running as SSE server ===", flush=True)
        # Create an SSE transport at an endpoint
        sse = SseServerTransport("/messages/")

        # Define handler functions
        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await mcp_server.run(
                    streams[0], streams[1], InitializationOptions(
                        server_name="calculator-mcp",
                        server_version="0.1.0",
                        capabilities=mcp_server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    )
                )
        # Create Starlette app
        app = Starlette(routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ])
        server_port = 8000
        print(f"=== Starting server on http://127.0.0.1:{server_port}/sse ===", flush=True)
        uvicorn_server = uvicorn.Server(
            config=uvicorn.Config(
                app=app, host="127.0.0.1", port=server_port, log_level="info"
            )
        )
        await uvicorn_server.serve()
    else:
        # Run the server using stdin/stdout streams
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="calculator-mcp",
                    server_version="0.1.0",
                    capabilities=mcp_server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                )
            )
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
