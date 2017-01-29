from bot.models import PoliciaTransito
def load():
	with open('policias.bd') as f:
		for line in f.readlines():
			divided = line.split()
			poli = PoliciaTransito(p_id=int(divided[0]),name=' '.join(divided[1:]))
			poli.save()