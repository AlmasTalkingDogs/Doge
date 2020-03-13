from events.consumer import EventConsumer, AwaitCallbackConsumer as CallbackConsumer
from events.producer import EventProducer, CallbackProducer
from asyncio import ensure_future

class EventIngestor():
	def __init__(self, producers: [EventProducer], consumers: [EventConsumer]):
		self.active = True
		self.consumers = consumers

		self.producer = CallbackProducer()
		for c in consumers:
			self.registerConsumer(c)
			# self.producer.register(c)

		self.callconsumers = {}

		for i, p in enumerate(producers):
			self.registerProducer(p, srcId=i)

	def registerProducer(self, p, srcId: int):
		if not self.active:
			raise Exception("Not active")
		if srcId in self.callconsumers and self.callconsumers[srcId].active:
			raise Exception("srcId", srcId, "is already registered for ingestor", self.callconsumers[srcId].active)
		c = CallbackConsumer(self.ingest, srcId=srcId)
		p.register(c)
		ensure_future(c.listen())
		self.callconsumers[srcId] = c

	def registerConsumer(self, c):
		if not self.active:
			raise Exception("Not active")
		self.producer.register(c)

	async def ingest(self, data, srcId):
		raise Exception("not implemented")

	async def notifyAll(self, data):
		if not self.active:
			# raise Exception("Not active")
			return
		await self.producer.notify(data)

	async def exit(self):
		print(self.callconsumers)
		self.active = False
		for i in self.callconsumers:
			c = self.callconsumers[i]
			print(i,c)
			if c.active:
				await c.exit()
		await self.producer.exit()

class LabelIngestor(EventIngestor):
	def __init__(self, init_label: str):
		super().__init__([], [])
		self.label = init_label

	async def ingest(self, data, srcId):
		if srcId == 0:
			self.label = data
		elif srcId == 1:
			await self.notifyAll(str(data) + "," + str(self.label) + "\n")
