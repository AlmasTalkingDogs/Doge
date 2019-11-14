from events.consumer import EventConsumer, CallbackConsumer
from events.producer import EventProducer, CallbackProducer
from asyncio import ensure_future
class EventIngestor():
	def __init__(self, producers: [EventProducer], consumers: [EventConsumer]):
		self.consumers = consumers

		self.producer = CallbackProducer()
		for c in consumers:
			self.producer.register(c)

		self.callconsumers = [CallbackConsumer(self._produceCallback, srcId=i) for i in range(len(producers))]
		for p, c in zip(producers, self.callconsumers):
			p.register(c)
			ensure_future(c.listen())

	async def _produceCallback(self, data, srcId=-1):
		await self.ingest(data, srcId)

	async def ingest(self, data, srcId):
		raise Exception("not implemented")

	async def notifyAll(self, data):
		print("HERE HER HERE")
		await self.producer.notify(data)


class LabelIngestor(EventIngestor):
	def __init__(self, label: EventProducer, data: EventProducer, dest: EventConsumer, init_label: str):
		super().__init__([label, data], [dest])
		self.label = init_label

	async def ingest(self, data, srcId):
		if srcId == 0:
			self.label = data
		elif srcId == 1:
			print("Writing data to file")
			await self.notifyAll(str(data) + "," + str(self.label) + "\n")

