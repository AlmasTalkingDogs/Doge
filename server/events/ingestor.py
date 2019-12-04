from events.consumer import EventConsumer, CallbackConsumer
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

		self.callconsumers = {} #[CallbackConsumer(self._produceCallback, srcId=i) for i in range(len(producers))]
		# for p, c in zip(producers, self.callconsumers):
		#	p.register(c)
		#	ensure_future(c.listen())
		for i, p in enumerate(producers):
			self.registerProducer(p, srcId=i)

	def registerProducer(self, p, srcId: int):
		if srcId in self.callconsumers and self.callconsumers[srcId].active:
			raise Exception("srcId", srcId, "is already registered for ingestor", self.callconsumers[srcId].active)
		c = CallbackConsumer(self._produceCallback, srcId=srcId)
		p.register(c)
		ensure_future(c.listen())
		self.callconsumers[srcId] = c

	def registerConsumer(self, c):
		self.producer.register(c)

	async def _produceCallback(self, data, srcId=-1):
		await self.ingest(data, srcId)

	async def ingest(self, data, srcId):
		raise Exception("not implemented")

	async def notifyAll(self, data):
		await self.producer.notify(data)

	def exit(self):
		self.active = False
		for i, c in callconsumers:
			c.exit()
		self.producer.exit()

class LabelIngestor(EventIngestor):
	def __init__(self, init_label: str):
		super().__init__([], [])
		self.label = init_label

	async def ingest(self, data, srcId):
		if srcId == 0:
			self.label = data
		elif srcId == 1:
			await self.notifyAll(str(data) + "," + str(self.label) + "\n")
