from events.consumer import EventConsumer
from events.producer import EventProducer
from events.ingestor import EventIngestor
from asyncio import wait

class Registry():
	all_dogs=[]
	def __init__(self):
		self._registry = {}

	def get(self, resource):
		if self.available(resource):
			raise Exception(f"resource \"{resource}\" is not registered")
		return self._registry[resource]

	def register(self, resource, item):
		if not self.available(resource):
			raise Exception(f"resource \"{resource}\" is not available")
		self._registry[resource] = item

	def available(self, resource):
		if resource not in self._registry:
			return True
		elif self._registry[resource] is None:
			return True
		# Make sure that the consumers are active
		elif isinstance(self._registry[resource], EventConsumer):
			return not self._registry[resource].active
		# Make sure that the producers are active
		elif isinstance(self._registry[resource], EventProducer):
			return not self._registry[resource].active
		# Make sure that the ingestor is active
		elif isinstance(self._registry[resource], EventIngestor):
			return not self._registry[resource].active
		else:
			return False

	def get_dogs(self):
		return self.all_dogs

	def get_dog(self, id1):
		for dog in self.all_dogs:
			if dog.id == id1:
				return dog

	def add_dog(self):
		self.all_dogs.append(self)

	async def kick(self, resource):
		rsrc = self.get(resource)
		# Make sure that the consumers are active
		if isinstance(rsrc, EventConsumer):
			rsrc.exit()
		# Make sure that the producers are active
		elif isinstance(rsrc, EventProducer):
			rsrc.exit()
		# Make sure that the ingestor is active
		elif isinstance(rsrc, EventIngestor):
			rsrc.exit()

		self._registry[resource] = None
