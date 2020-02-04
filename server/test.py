from events.producer import CallbackProducer
from events.consumer import CallbackConsumer, CountConsumer
from events.ingestor import LabelIngestor

import asyncio

import random

async def main():
	prods = []
	cons  = []

	chance_create_con = 0.5
	chance_create_prd = 0.5
	chance_destory_con = 0.6
	chance_destory_prd = 0 #0.3

	limit_con = 20
	limit_prd = 1

	chance_gen_event = 1

	for i in range(10000):
		if len(prods) < limit_prd and random.random() < chance_create_prd:
			prods.append(CallbackProducer())
			# print("New Producer")
		if len(cons) < limit_con and len(prods) > 0 \
				and random.random() < chance_create_con:
			c = CallbackConsumer(lambda x: print(len(cons), x))
			cons.append(c)
			p = random.choice(prods)
			p.register(c)
			asyncio.ensure_future(c.listen())
			# print("New Consumer")

		for p in prods:
			if random.random() < chance_gen_event:
				# print("Notified", i)
				asyncio.ensure_future(p.notify(i))

		if len(prods) > 0 and random.random() < chance_destory_prd:
			p = random.choice(prods)
			if p.active:
				prods.remove(p)
				asyncio.ensure_future(p.exit())
			# print("Del Producer")
		prods = list(filter(lambda x:x.active, prods))

		if len(cons) > 0 and random.random() < chance_destory_con:
			c = random.choice(cons)
			if c.active:
				cons.remove(c)
				asyncio.ensure_future(c.exit())
			# print("Del Consumer")
		cons = list(filter(lambda x:x.active, cons))

		await asyncio.sleep(0)

	await asyncio.sleep(3)
	# conA = CallbackConsumer(lambda x: print("A", x))
	# conB = CallbackConsumer(lambda x: print("B", x))
	# prod.register(conA)
	# prod.register(conB)
	# asyncio.ensure_future(conA.listen())
	# asyncio.ensure_future(conB.listen())

async def main2():
	lIngestor = LabelIngestor("A")
	l = CallbackProducer()
	d = CallbackProducer()
	
	p = CallbackConsumer(lambda x: print("DATA:", x))
	asyncio.ensure_future(p.listen())

	lIngestor.registerProducer(l, 0)
	lIngestor.registerProducer(d, 1)

	lIngestor.registerConsumer(p)

	asyncio.ensure_future(d.notify(1))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(2))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(3))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(4))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(5))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(6))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(7))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(8))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(9))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(10))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(11))
	await asyncio.sleep(0.01)

	asyncio.ensure_future(d.notify(12))
	await asyncio.sleep(0.01)


	asyncio.ensure_future(l.notify("B"))
	await asyncio.sleep(0)
	asyncio.ensure_future(d.notify(13))
	await asyncio.sleep(0.01)



	await asyncio.sleep(2)






asyncio.run(main2())
