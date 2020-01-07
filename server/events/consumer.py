from asyncio import Event, sleep, Queue

# Consumers will consume events
class EventConsumer():
	def __init__(self):
		self.active = False
		self.consumer = None
		self.exit_queue = None

	def _register(self, p, exit_queue):
		self.consumer = p
		self.exit_queue = exit_queue
		self.active = True

	async def notify(self, data):
		if not self.active:
			raise Exception("Consumer is not active")

	async def listen(self):
		if not self.active:
			raise Exception("Must register before listening")
		while True:
			data = await self.consumer.get()
			if data is None:
				# Queue is closed
				break
			elif not self.active:
				break
			await self.notify(data)
			self.consumer.task_done()
			# Allow others to steal focus
			await sleep(0)
		# Do not exit if already active
		if self.active:
			await self.exit()

	# Let our consumer know we are closing the connections
	async def exit(self):
		if not self.active:
			return False
			# raise Exception("Already inactive")
		self.active = False
		if self.exit_queue:
			await self.exit_queue.put(None)
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

	async def exit(self):
		await super().exit()
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

	async def exit(self):
		if await super().exit():
			self.file.close()
			return True
		else:
			return False

class AwaitCallbackConsumer(EventConsumer):
	def __init__(self, callback, done=None, **kwargs):
		super().__init__()
		self.callback = callback
		self.done = done
		self.kwargs = kwargs

	async def notify(self, data):
		await super().notify(data)
		await self.callback(data, **self.kwargs)

	async def exit(self):
		if await super().exit():
			if self.done is not None:
				return self.done(self.kwargs)
			return True
		else:
			return False

class CallbackConsumer(EventConsumer):
	def __init__(self, callback, done=None, **kwargs):
		super().__init__()
		self.callback = callback
		self.done = done
		self.kwargs = kwargs

	async def notify(self, data):
		await super().notify(data)
		self.callback(data, **self.kwargs)

	async def exit(self):
		if await super().exit():
			if self.done is not None:
				return self.done(**self.kwargs)
			return True
		else:
			return False

class CountConsumer(EventConsumer):
	def __init__(self, done=None, **kwargs):
		super().__init__()
		self.count = 0
		self.done = done
		self.kwargs = kwargs

	async def notify(self, data):
		await super().notify(data)
		self.count += 1

	async def exit(self):
		if await super().exit():
			if self.done is not None:
				return self.done(self.count, **self.kwargs)
			return True
		else:
			return False