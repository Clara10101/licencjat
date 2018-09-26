import argparse, json, numpy, stops, sys, math, random
import matplotlib.pyplot as plt
import copy, pickle, plot_hexagonal_grid

parser = argparse.ArgumentParser()
parser.add_argument("-j","--json",help="input files",type=argparse.FileType('r'), nargs='+',required=True)
parser.add_argument("-o","--output",help="output file",type=str, nargs=1,required=True)
parser.add_argument("-p","--stops1",help="wykres populacji w czasie",type=str)
parser.add_argument("-g","--stops2",help="hexagonal grid",type=str)
parser.add_argument("-s","--stops3",help="segmenty",type=str)
parser.add_argument("-a","--anim",help="animacja",type=str)
args = parser.parse_args()
parsed_dict = dict()

if args.anim:
	output_data = {}
	plik_out = open( "save_data.p", "wb" )

for f in args.json:
	string_json = f.read()
	try:
		parsed_json = json.loads(string_json)
	except ValueError:
		print "not valid JSON"
	parsed_dict.update(parsed_json)

def check_matrix(mat):
	#macierz ma byc kwadratowa, z wartosciami numerycznymi i typu list
	if type(mat) != list:
		return False
	else:
		rows = len(mat)
		for row in mat:
			i = 0
			for value in row:
				try:
					float(value)
				except:
					return False
				i += 1
			if i != rows:
				return False
	return True

#sprawdzenie czy macierz wplywow zostala podana w pliku json, musi byc podana przy wszystkich rodzajach symulacji
if 'trans_mat' in parsed_dict:
	if check_matrix(parsed_dict['trans_mat']):
		trans_mat = numpy.matrix(numpy.array(parsed_dict['trans_mat']))
		genes_amount = len(trans_mat)
	else:
		print >> sys.stderr, "Exception: niepoprawna macierz wplywow"
		sys.exit(1)
else:
	print >> sys.stderr, "Exception: brak macierzy wplywow w pliku wejsciowym"
	sys.exit(1)

from matplotlib.backends.backend_pdf import PdfPages
pdf = PdfPages(args.output[0])

#przypisanie do zmiennych pozostalych wartosci z pliku json
if 'iter' in parsed_dict:
	if isinstance(parsed_dict['iter'], (int,long)):
		if parsed_dict['iter'] > 0:
			ITER = parsed_dict['iter']
else:
	ITER = 100

if 'secr' in parsed_dict:
	if isinstance(parsed_dict['secr'], (int)):
		if parsed_dict['secr'] > 0:
			SECR = parsed_dict['secr']
else:
	SECR = 1

if 'pop_size' in parsed_dict:
	if isinstance(parsed_dict['pop_size'], (int,long)):
		if parsed_dict['pop_size'] > 0:
			POP_SIZE = parsed_dict['pop_size']
else:
	POP_SIZE = 100

def check_length(vector):
#czy lista o dlugosci rownej ilosci genow, z wartosciami calkowitymi
#do secretion i reception
	if type(vector) == list:
		if len(vector) == genes_amount:
			if all(isinstance(item, int) and 0 <= item < genes_amount for item in vector):
				return True
	return False

def check_length_bound_base(vector):
#czy lista o dlugosci rownej ilosci genow, z wartosciami calkowitymi
#do base i bound
	if type(vector) == list:
		if len(vector) == genes_amount:
			if all(isinstance(item, int) for item in vector):
				return True
	return False

#wektory base, bound, secretion, reception powinny byc dlugosci rownej ilosci genow
if 'bound' in parsed_dict:
	if check_length_bound_base(parsed_dict['bound']):
		bound = numpy.array(parsed_dict['bound'])
	else:
		print >> sys.stderr, "Exception: zla dlugosc wektora bound"
		sys.exit(1)
else:
	bound = None

if 'base' in parsed_dict:
	if check_length_bound_base(parsed_dict['base']):
		base = numpy.array(parsed_dict['base'])
	else:
		print >> sys.stderr, "Exception: zla dlugosc wektora base"
		sys.exit(1)
else:
	base = numpy.zeros(genes_amount).astype(int)

if 'secretion' in parsed_dict:
	if check_length(parsed_dict['secretion']):
		secretion = numpy.array(parsed_dict['secretion'])
	else:
		print >> sys.stderr, "Exception: zla dlugosc secretion"
		sys.exit(1)
else:
	secretion = None

if 'reception' in parsed_dict:
	if check_length(parsed_dict['reception']):
		reception = numpy.array(parsed_dict['reception'])
	else:
		print >> sys.stderr, "Exception: niepoprawna dlugosc wektora reception"
		sys.exit(1)
else:
	reception = None

if 'leak' in parsed_dict:
	if isinstance(parsed_dict['leak'],(int,long)):
		if parsed_dict['leak'] >= 0:
			LEAK = parsed_dict['leak']
else:
	LEAK = 1

if 'init_env' in parsed_dict:
	if isinstance(parsed_dict['init_env'],(int,long)):
		if parsed_dict['init_env'] >= 0:
			INIT_ENV = parsed_dict['init_env']
else:
	INIT_ENV = 0

if 'asym' in parsed_dict:
	if len(parsed_dict['asym']) == 2:
		if check_length_bound_base(parsed_dict['asym'][0]) and check_length_bound_base(parsed_dict['asym'][1]):
			asym = numpy.array(parsed_dict['asym'][0]),numpy.array(parsed_dict['asym'][1])
else:
	asym = None

def check_asym(item):
#sprawdzenie asym_no, div_no, die_no, liczby calkowite z zakresu [-genes_amount;genes_amount - 1]
	if isinstance(item, int) and -genes_amount <= item < genes_amount:
		return True
	return False

if 'asym_no' in parsed_dict:
	if check_asym(parsed_dict['asym_no']):
		asym_no = parsed_dict['asym_no']
else:
	asym_no = -3

if 'div_no' in parsed_dict:
	if check_asym(parsed_dict['div_no']):
		div_no = parsed_dict['div_no']
else:
	div_no = -2

if 'die_no' in parsed_dict:
	if check_asym(parsed_dict['die_no']):
		die_no = parsed_dict['die_no']
else:
	die_no = -1

if args.stops1:
	STOP = stops.Stops(trans_mat, POP_SIZE, base, bound, secretion, reception, asym, asym_no, div_no, die_no, secr_amount = SECR, leak = LEAK, init_env = INIT_ENV, profiling = False, opencl_mode = False, numpy_mode = True)
	from stops import plot
	symulacja = STOP.sim(ITER, plot = True)
	plot1 = plot.plot(symulacja)
	pdf.savefig(plot1)
	plt.cla()
	plt.clf()

	if args.anim:
		#dane do wykresu bokeh
		output_data['stops1'] = symulacja


def convert_to_stops2_interpretation(nparray):
	result = []
	i = 1
	while i < genes_amount:
		for j in range(len(nparray)):
			if nparray[j] == i:
				result.append(j+1)
		i += 1
	return numpy.array(result)

def check_length_init_env_stops2(vector):
#czy lista o dlugosci nie wiekszej niz ilosci genow, z wartosciami calkowitymi
#do HEX_INIT_ENV
	if type(vector) == list:
		if len(vector) <= genes_amount:
			if all(isinstance(item, int) and 0 <= item < genes_amount for item in vector):
				return True
	return False

if args.stops2:
	from utils import generate_pop, HexGrid
	from stops_ import Stops2
	from colors_matplotlib import draw_hex_grid

	if 'receptors' in parsed_dict:
		receptors = numpy.array(parsed_dict['receptors'])
	else:
		receptors = None

	if 'max_con' in parsed_dict:
		max_con = parsed_dict['max_con']
	else:
		max_con = 1000.0

	if 'hex_init_env' in parsed_dict:
		if check_length_init_env_stops2(parsed_dict['hex_init_env']):
			init_env = numpy.array(parsed_dict['hex_init_env'])
	else:
		init_env = None

	if 'diffusion_rate' in parsed_dict:
		diffusion_rate = parsed_dict['diffusion_rate']
	else:
		diffusion_rate = 0.0

	if 'init_pop' in parsed_dict:
		init_pop = numpy.array(parsed_dict['init_pop'])
	else:
		if 'base' in parsed_dict:
			#wektor bazowy * pop_size
			init_pop = generate_pop([(POP_SIZE, numpy.array(base))])
		else:
			print >> sys.stderr, "init_pop/base"
			sys.exit(1)

	if secretion != None:
		s2_secretion = convert_to_stops2_interpretation(secretion)
	else:
		s2_secretion = None

	if reception != None:
		s2_reception = convert_to_stops2_interpretation(reception)
	else:
		s2_reception = None

	n = int(math.sqrt(len(init_pop)))
	grid = HexGrid(n, n, 1)
	color_dict = {}
	x = Stops2(trans_mat, init_pop, grid.adj_mat, range(len(init_pop)), bound, s2_secretion, s2_reception, receptors, init_env, secr_amount = SECR, leak = LEAK, max_con = max_con, diffusion_rate = diffusion_rate, opencl=False, asym = asym, asym_id = asym_no, div_id = div_no, die_id = die_no)

	all_pop_mat = [0]*(ITER+1)
	vectors = []
	for i in range(ITER+1):
		all_pop_mat[i] = copy.copy(x.pop)
		for i, row in enumerate(x.pop):
			key = ' '.join(str(row.astype(int)))
			if key not in vectors:
				vectors.append(key)
		x.step()
	len_vectors = len(vectors)
	colors1 = range(0,101,100/len_vectors)[:len_vectors]
	colors2 = range(0,101,100/len_vectors)[:len_vectors]
	random.shuffle(colors2)
	for i in range(len_vectors):
		color_dict[vectors[i]] = (colors1[i]/100.,colors2[i]/100.)
	for i in range(ITER):
		if i%10 == 0:
			p2 = draw_hex_grid(all_pop_mat[i+1], grid, color_dict)
			pdf.savefig(p2)
			plt.clf()
			plt.cla()
	if args.anim:
		#dane do animacji
		output_data['stops2'] = [grid.shape,all_pop_mat,color_dict]
			
			
def dict_int(name):
	new = {}
	for key in name:
		new[int(key)] = name[key]
	return new

def check_segm(segm_leak):
#lista dlugosci rownej ilosci genow z wartosciami typu float
	if type(segm_leak) == list:
		if len(segm_leak) <= genes_amount:
			for value in segm_leak:
				try:
					float(value)
				except:
					return False
				if not 0.0 <= value <= 1.0:
					return False
			return True
	return False

def convert_to_dict(vector):
	dict = {}
	for i in range(len(vector)):
		dict[str(i+1)] = vector[i]
	return dict

def check_init_env(initenv):
	if type(initenv) == list:
		if len(initenv) != 4:
			return False
		for tab in initenv:
			i = 0
			for value in tab:
				try:
					float(value)
				except:
					return False
				i += 1
			if i > genes_amount:
				return False
		return True
	return False

if args.stops3:
	if 'segm_dyf' in parsed_dict:
		if check_segm(parsed_dict['segm_dyf']):
			epsilon = convert_to_dict(parsed_dict['segm_dyf'])
	else:
		print >> sys.stderr, "SEGM_DIF"
		sys.exit(1)

	if 'segm_init_env' in parsed_dict:
		if check_init_env(parsed_dict['segm_init_env']):
			INIT_ENV2 = {}
			for i in range(len(parsed_dict['segm_init_env'])):
				INIT_ENV2[str(i+1)] = convert_to_dict(parsed_dict['segm_init_env'][i])
	else:
		print >> sys.stderr, "SEGM_INIT_ENV"
		sys.exit(1)

	#co ile krokow zachodzi dyfuzja
	if 'diff_freq' in parsed_dict:
		diff_freq = parsed_dict['diff_freq']
	else:
		diff_freq = 1

	#co ile krokow rysowane wyniki symulacji
	if 'plot_freqs' in parsed_dict:
		plot_freqs = parsed_dict['plot_freqs']
	else:
		plot_freqs = 10

	if 'segm_leak' in parsed_dict:
		if check_segm(parsed_dict['segm_leak']):
			SEGM_LEAK = numpy.array(parsed_dict['segm_leak'])
	else:
		print >> sys.stderr, "SEGM_LEAK"
		sys.exit(1)

	import mm.segments as segments
	import mm.stops as stops
	SEGMENTS = segments.Segments(4, ITER, trans_mat, POP_SIZE, base, bound, secretion, reception, asym=None, asym_no=-1, div_no=-1, die_no=-1, secr_amount=SECR, leak=SEGM_LEAK, init_env=INIT_ENV, profiling=False, numpy_mode=True, opencl_mode=False)
	for i in range(4):
		SEGMENTS.setEnvironment(dict_int(INIT_ENV2[str(i+1)]), i)
	all_freqs_after_reception,all_segm_dicts = SEGMENTS.simulateSegments(diff_freq=diff_freq, epsilon=dict_int(epsilon), plot_freqs=plot_freqs,output_file_pdf=pdf)
		for i in range(len(plots)):
		pdf.savefig(plots[i])
		plots[i].clf()
	if args.anim:
		output_data['stops3'] = [all_freqs_after_reception,all_env_after_diffusion,all_segments]

if args.anim:
	pickle.dump(output_data, plik_out)
	plik_out.close()

pdf.close()