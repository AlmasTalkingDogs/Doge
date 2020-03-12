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
from events.consumer import WebsocketConsumer, FileConsumer, CallbackConsumer
from events.ingestor import LabelIngestor

from registry.resources import Registry
from entities.dog import Dog
import random
import uuid

# Set up a logfile for the sake of debugging/DDoS forensics/postmortems
logger.add("alma_server.log", rotation="50 KB")

app = Sanic(configure_logging=False)
# Use WebSockets to live-update the index page
app.enable_websocket()
# Static bindings allow Sanic to serve files from disk
# These are explicitly named to avoid someone accidentally placing something secret in one of these folders
app.static('/res/style.css', './res/style.css')
app.static('/res/graph.js', './res/graph.js')
app.static('/res/live.js', './res/live.js')
app.static('/graph.html', './res/graph.html')
# app.static('/favicon.ico', './res/favicon.ico')

# Load page templates - it should be easy to change these templates later.
# These are loaded once at the start of the program, and never again.

with open("res/data.htm") as f:
	data_input_template = Template(f.read())

registry = Registry()


@app.route("/")
async def index(request: Request):
	with open("res/index.htm") as f:
		index_template = Template(f.read())
		logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
		index_html = index_template.render(dogs=registry.get_dogs())
		return html(index_html)


@app.route("/labeler.html")
async def labeler_page(request: Request):
	global feed_event
	logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
	index_html = data_input_template.render()
	return html(index_html)

@app.route("/dog/<dog_id>")
async def labeler_page(request: Request, dog_id:int):
	logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
	with open("res/dog.htm") as f:
		template = Template(f.read())
		dog_html = template.render(id=dog_id, config=["data1"])
		return html(dog_html)


@app.websocket("/ws/data/write/<source_id>")
async def produce_data(request: Request, ws: WebSocketProtocol, source_id: int):
	if registry.available(request.path):
		logger.info(f"Client at {request.ip}:{request.port} registered source {source_id}")
	else:
		logger.info(f"Client at {request.ip}:{request.port} registered source {source_id}; Kicked out old producer")
		registry.kick(request.path)

	registry.register(request.path, WebsocketProducer(ws))
	await registry.get(request.path).listen()
	logger.info(f"Client at {request.ip}:{request.port} stoped writing to source {source_id}")


@app.websocket("/ws/data/read/<source_id>")
async def consume_data2(request: Request, ws: WebSocketProtocol, source_id: str):
	logger.info(f"Client at {request.ip}:{request.port} opened websocket at {request.url}.")
	writeRsrc = f"/ws/data/write/{source_id}"
	if registry.available(writeRsrc):
		logger.info(f"Client at {request.ip}:{request.port} failed to find source {source_id}")
		return
	logger.info(f"Client at {request.ip}:{request.port} requested to consume {source_id}")
	consumer = WebsocketConsumer(ws)

	p = registry.get(writeRsrc)
	p.register(consumer)
	await consumer.listen()


# Creates random data for testing purposes
@app.websocket("/ws/data/random")
async def consume_data3(request: Request, ws: WebSocketProtocol):
	await sleep(5)
	label = random.randint(0, 1)
	while True:
		data = random.randint(0, 100)
		data2 = random.randint(0, 100)
		if random.randint(0, 1) == 0:
			label = random.randint(0, 1)
		await ws.send(f"{data},{data2},{label}")
		await sleep(1)


# logger.info(f"Client at {request.ip}:{request.port} opened websocket at {request.url}.")
# writeRsrc = f"/ws/data/write/{source_id}"
# if not registry.available(writeRsrc):
# 	logger.info(f"Client at {request.ip}:{request.port} failed to find source {source_id}")
# 	return
# logger.info(f"Client at {request.ip}:{request.port} requested to consume {source_id}")
# consumer = WebsocketConsumer(ws)

# p = registry.get(writeRsrc)
# p.register(consumer)
# await consumer.listen()


@app.route("/rsrc/ing/<dog_id>", methods=["POST", ])
async def consume_data4(request: Request, dog_id: str):
	if not registry.available(f"/rsrc/ing/{dog_id}"):
		logger.debug(f"Client at {request.ip}:{request.port} cannot create an ingestor for {dog_id}")
		return json(
			{"success": False, "msg": f"Client at {request.ip}:{request.port} ingestor for dog {dog_id} is already registered"})


	fileName = 'temp.log'
	if 'fileName' in request.json:
		fileName = request.json['fileName']

	writeFile = FileConsumer(fileName)
	logger.info(f"Client at {request.ip}:{request.port} created ingestor {dog_id}.")

	labelizer = LabelIngestor(0)

	registry.register(f"/rsrc/ing/{dog_id}", labelizer)

	labelizer.registerConsumer(writeFile)

	ensure_future(writeFile.listen())
	if 'log' in request.json and request.json['log']:
		print(request.json)
		printConsumer = CallbackConsumer(lambda x: print(f"dog_id {dog_id}:", x))
		labelizer.registerConsumer(printConsumer)
		ensure_future(printConsumer.listen())
	return json({"success": True})


@app.websocket("/ws/ingread/<dog_id>")
async def read_ing_data(request: Request, ws: WebSocketProtocol, dog_id: int):
	if registry.available(f"/rsrc/ing/{dog_id}"):
		logger.debug(f"Client at {request.ip}:{request.port} failed to find dog {dog_id} for consumption")
		return

	consumer = WebsocketConsumer(ws)

	ing = registry.get(f"/rsrc/ing/{dog_id}")
	ing.registerConsumer(consumer)

	await consumer.listen()


@app.websocket("/ws/ing/<ing_id>/<source_id>")
async def produce_data2(request: Request, ws: WebSocketProtocol, ing_id: int, source_id: int):
	if registry.available(f"/rsrc/ing/{ing_id}"):
		logger.debug(f"Client at {request.ip}:{request.port} failed to find ingestor {ing_id}")
		return
	if not registry.available(f"/ws/ing/{ing_id}/{source_id}"):
		print("active:", registry.get(f"/ws/ing/{ing_id}/{source_id}").active)
		logger.debug(f"Client at {request.ip}:{request.port} failed to free up resource /ws/ing/{ing_id}/{source_id}")
		return
	ing = registry.get(f"/rsrc/ing/{ing_id}")
	wp = WebsocketProducer(ws)
	registry.register(f"/ws/ing/{ing_id}/{source_id}", wp)
	ing.registerProducer(wp, srcId=int(source_id))
	await wp.listen()


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
			data = await ws.recv()
			print(data)
			logger.info(f"Updated feed for client at {request.ip}:{request.port}.")
		except (ConnectionClosed):
			logger.info(f"Feed disconnected from client at {request.ip}:{request.port}.")
			break
		except Exception as ex:
			print("Failed", ex, type(ex))
			break
		# await sleep(1)

@app.route("/rsrc/dog/", methods=["POST",])
async def create_dog(request: Request):
	dog_id = str(uuid.uuid1())
	dog = Dog("Chuchu", dog_id)
	registry.add_dog(dog)
	logger.info(f"Client {request.ip}:{request.port} created a new dog {dog.name} id: {dog.id}")
	return json({"id": dog_id})


@app.route("/rsrc/dog/<dog_id>", methods=["GET",])
async def get_dog_json(request: Request, dog_id: int):
	dog = registry.get_dog_object(dog_id)
	return json({"id":dog.id, "name":dog.name})


@app.websocket("/ws/dog/<dog_id>")
async def write_dog_data(request: Request, ws: WebSocketProtocol, dog_id: int):
	dog = registry.get(f"/dog/{dog_id}")
	wp = WebsocketProducer(ws)
	dog.set_producer(wp)
	await wp.listen()


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
	app.run(host='0.0.0.0', port=8080)
