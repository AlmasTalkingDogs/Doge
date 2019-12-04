from asyncio import Event, sleep, Queue

# Consumers will consume events
class EventConsumer():
	def __init__(self):
		self.active = False
		self.consumer = None

	def _register(self, p):
		self.consumer = p
		self.active = True

	async def notify(self, data):
		if not self.active:
			raise Exception("Consumer is not active")

	async def listen(self):
		while self.active:
			data = await self.consumer.get()
			if data is None:
				break
			await self.notify(data)
			self.consumer.task_done()
		self.exit()

	# Let our consumer know we are closing the connections
	def exit(self):
		self.active = False
		return True


class WebsocketConsumer(EventConsumer):
	def __init__(self, ws, parse=None, **kwargs):
		super().__init__()
		self.ws = ws
		self.parse = parse
		self.parse_kwargs = kwargs

	async def notify(self, data):
		await super().notify(None)
		if self.parse is not None:
			data = self.parse(data, self.parse_kwargs)
		self.ws.send(data)

	def exit(self):
		super().exit()
		return self.ws.close()

class FileConsumer(EventConsumer):
	def __init__(self, path):
		super().__init__()
		self.file = open(path,'a')

	async def notify(self, data):
		await super().notify(data)
		self.file.write(data)
		self.file.flush()
		return

	def exit(self):
		super().exit()
		self.file.close()
		return True

class AwaitCallbackConsumer(EventConsumer):
	def __init__(self, callback, done=None, **kwargs):
		super().__init__()
		self.callback = callback
		self.done = done
		self.kwargs = kwargs

	async def notify(self, data):
		await super().notify(data)
		await self.callback(data, **self.kwargs)

	def exit(self):
		super().exit()
		if self.done is not None:
			return self.done(self.kwargs)
		return True

class CallbackConsumer(EventConsumer):
	def __init__(self, callback, done=None, **kwargs):
		super().__init__()
		self.callback = callback
		self.done = done
		self.kwargs = kwargs

	async def notify(self, data):
		await super().notify(data)
		self.callback(data, **self.kwargs)

	def exit(self):
		super().exit()
		if self.done is not None:
			return self.done(self.kwargs)
		return True
