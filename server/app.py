from sanic import Sanic
from sanic.exceptions import NotFound, ServerError
from sanic.request import Request
from sanic.websocket import WebSocketProtocol, ConnectionClosed
from sanic.response import html, json
from asyncio import Event, ensure_future
from json import dumps as json_string
from jinja2 import Template
from loguru import logger

# Set up a logfile for the sake of debugging/DDoS forensics/postmortems
logger.add("alma_server.log", rotation="50 KB")

app = Sanic(configure_logging=False)
# Use WebSockets to live-update the index page
app.enable_websocket()
# Static bindings allow Sanic to serve files from disk
# These are explicitly named to avoid someone accidentally placing something secret in one of these folders
app.static('/res/style.css', './res/style.css')
# app.static('/favicon.ico', './res/favicon.ico')

# Load page templates - it should be easy to change these templates later.
# These are loaded once at the start of the program, and never again.
with open("res/index.htm") as f:
    index_template = Template(f.read())


# Here, rr is the tournament object - replace this if using a different tournament type.
# More details on how this works are found in the RR class.


@app.route("/")
async def index(request: Request):
    global feed_event
    logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
    # We need to wait for Sanic to do the first asyncio call, because Sanic uses a different loop than Python by default.
    # The tournament therefore starts the first time the page is loaded.
    index_html = index_template.render()
    return html(index_html)



# @app.route("/dogs/<dogId>")
# async def netid_lookup(request: Request, netid: str):
#     logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
#     errors = rr.get_errors(netid)
#     team = rr.get_team(netid)
#     netid_html = netid_template.render(netid=netid, team=team, errors=errors)
#     return html(netid_html)


# @app.route("/teams/<team_name>")
# async def team(request: Request, team_name: str):
#     logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
#     standing = rr.get_rank_score(team_name)
#     team_html = team_template.render(standing=standing, games=rr.get_games(team=team_name))
#     return html(team_html)


# @app.route("/matches/<team1>/<team2>")
# async def match(request: Request, team1: str, team2: str):
#     logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
#     match = rr.get_match(team1, team2)
#     t1_json = rr.get_rank_score(team1)
#     t2_json = rr.get_rank_score(team2)
#     match_html = match_template.render(match=match, team1=t1_json, team2=t2_json)
#     return html(match_html)


# @app.route("/grades")
# async def grades(request: Request):
#     logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
#     if request.args['password'] != ['spimspameroni']:
#         logger.critical(f"Client at {request.ip}:{request.port} requested grades but provided an incorrect password {request.args['password']}!")
#         return html(missing_template.render(), status=404)
#     return json(rr.get_grades())

# @app.websocket("/ws/feed")
# async def feed_socket(request: Request, ws: WebSocketProtocol):
#     logger.info(f"Client at {request.ip}:{request.port} opened websocket at {request.url}.")
#     # This is the WebSocket code.
#     # It infinite loops (until the socket is closed when the client disconnects...) and waits on new matches.
#     # When a new match is found, it sends a JSON blob containing the tournament data.
#     while True:
#         json_blob = {"standings": rr.get_standings(), "games": rr.get_games(), "last_video": rr.get_video(), "queue_status": rr.get_queue()}
#         binary_blob = json_string(json_blob)
#         try:
#             await ws.send(binary_blob)
#             logger.info(f"Updated feed for client at {request.ip}:{request.port}.")
#         except ConnectionClosed:
#             logger.info(f"Feed disconnected from client at {request.ip}:{request.port}.")
#             break
#         await rr.update()


async def ise_handler(request, exception):
    # Handle internal server errors by displaying a custom error page.
    return html(ise_template.render(), status=500)


async def missing_handler(request, exception):
    # Handle 404s by displaying a custom error page.
    return html(missing_template.render(), status=404)


app.error_handler.add(ServerError, ise_handler)
app.error_handler.add(NotFound, missing_handler)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)