from sanic import Sanic
from sanic.exceptions import NotFound, ServerError
from sanic.request import Request
from sanic.websocket import WebSocketProtocol, ConnectionClosed
from sanic.response import html, json
from asyncio import Event, ensure_future, sleep, wait
from json import dumps as json_string
from jinja2 import Template
from loguru import logger

from events.producer import WebsocketProducer
from events.consumer import WebsocketConsumer, FileConsumer
from events.ingestor import LabelIngestor

# Set up a logfile for the sake of debugging/DDoS forensics/postmortems
logger.add("alma_server.log", rotation="50 KB")

app = Sanic(configure_logging=False)
# Use WebSockets to live-update the index page
app.enable_websocket()
# Static bindings allow Sanic to serve files from disk
# These are explicitly named to avoid someone accidentally placing something secret in one of these folders
app.static('/res/style.css', './res/style.css')
app.static('/res/live.js', './res/live.js')
# app.static('/favicon.ico', './res/favicon.ico')

# Load page templates - it should be easy to change these templates later.
# These are loaded once at the start of the program, and never again.
with open("res/index.htm") as f:
	index_template = Template(f.read())

datasources = {}
writeFile = FileConsumer('temp.log')
labelSource = None
dataSource = None
# labelizer = LabelIngestor()

@app.route("/")
async def index(request: Request):
	global feed_event
	logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
	# We need to wait for Sanic to do the first asyncio call, because Sanic uses a different loop than Python by default.
	# The tournament therefore starts the first time the page is loaded.
	index_html = index_template.render()
	return html(index_html)

@app.websocket("/ws/data/write/<source_id>")
async def produce_data(request: Request, ws: WebSocketProtocol, source_id: int):
	if source_id not in datasources:
		logger.info(f"Client at {request.ip}:{request.port} registered source {source_id}")
	else:
		logger.info(f"Client at {request.ip}:{request.port} registered source {source_id}: Kicked old consumer")
		await datasources[source_id].exit()

	datasources[source_id] = WebsocketProducer(ws)
	await datasources[source_id].listen()

@app.websocket("/ws/data/read/<source_id>")
async def consume_data(request: Request, ws: WebSocketProtocol, source_id: str):
	logger.info(f"Client at {request.ip}:{request.port} opened websocket at {request.url}.")
	if source_id not in datasources:
		logger.info(f"Client at {request.ip}:{request.port} failed to find source {source_id}")
		return
	logger.info(f"Client at {request.ip}:{request.port} requested to consume {source_id}")
	consumer = WebsocketConsumer(ws)
	datasources[source_id].register(consumer)
	await consumer.listen()






@app.websocket("/ws/ing/label/<source_id>")
async def produce_data(request: Request, ws: WebSocketProtocol, source_id: int):
	global labelSource
	labelSource = WebsocketProducer(ws)
	await labelSource.listen()

@app.websocket("/ws/ing/data/<source_id>")
async def consume_data(request: Request, ws: WebSocketProtocol, source_id: int):
	global dataSource
	dataSource = WebsocketProducer(ws)
	labelizer = LabelIngestor(labelSource, dataSource, writeFile, 1)
	ensure_future(writeFile.listen())
	await dataSource.listen()




@app.websocket("/ws/feed")
async def feed_socket(request: Request, ws: WebSocketProtocol):
	logger.info(f"Client at {request.ip}:{request.port} opened websocket at {request.url}.")
	# This is the WebSocket code.
	# It infinite loops (until the socket is closed when the client disconnects...) and waits on new matches.
	# When a new match is found, it sends a JSON blob containing the tournament data.
	number = 0
	while True:
		json_blob = {"number": str(number)}
		number = (number + 1) % 10
		binary_blob = json_string(json_blob)
		try:
			await ws.send(binary_blob)
			logger.info(f"Updated feed for client at {request.ip}:{request.port}.")
		except ConnectionClosed:
			logger.info(f"Feed disconnected from client at {request.ip}:{request.port}.")
			break
		await sleep(1)


# @app.route("/dogs/<dogId>")
# async def netid_lookup(request: Request, netid: str):
#     logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
#     errors = rr.get_errors(netid)
#     team = rr.get_team(netid)
#     netid_html = netid_template.render(netid=netid, team=team, errors=errors)
#     return html(netid_html)


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