from asyncio import Event, Queue, wait, QueueEmpty, sleep
from sanic.websocket import ConnectionClosed

# Producers create events
class EventProducer():
	def __init__(self):
		super().__init__()
		self.consumers = []
		self.active = True

	def register(self, c):
		q = Queue()
		exit_q = Queue()
		self.consumers.append((q,exit_q))
		c._register(q, exit_q)
		# return q

	def _trimInactive(self, item):
		q, exit_q = item
		try:
			item = exit_q.get_nowait()
			if item is None:
				return False
		except QueueEmpty:
			pass
		return True

	async def notify(self, data):
		self.consumers = list(filter(self._trimInactive, self.consumers))

		if len(self.consumers) > 0:
			await wait([c.put(data) for c, _ in self.consumers])

	async def exit(self):
		if not self.active:
			return True
		self.active = False
		for c,_ in self.consumers:
			await c.put(None)
		return True

class WebsocketProducer(EventProducer):
	def __init__(self, ws, parse=None, **kwargs):
		super().__init__()
		self.consumers = []
		self.ws = ws
		self.parse = parse
		self.parse_kwargs = kwargs

	async def listen(self):
		while self.active:
			try:
				data = await self.ws.recv()
				if self.parse is not None:
					data = self.parse(data, self.parse_kwargs)
				await self.notify(data)
			except ConnectionClosed as ex:
				break
			except:
				break
			# Allow others to steal focus
			await sleep(0)
		await self.exit()

class CallbackProducer(EventProducer):
	def __init__(self):
		super().__init__()

	async def listen(self):
		raise Exception("not implemented for callback producer")

	async def notify(self, data):
		await super().notify(data)
