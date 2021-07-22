from tvmfuzz.expr_generation import generate_tvm_and_np_tree
from tvmfuzz.symboltable import SymbolTable
from tvmfuzz.test_bed import evaluate_tvm_expr,compare_results,evaluate_np_expr
from tvmfuzz.generation_node import GenerationNode
from termcolor import colored
from tvmfuzz.util import get_literal_value
import random, time, datetime
import multiprocessing as mp
import pickle
from tvmfuzz import TIMEOUT

def run(duration: int):
	"""Run for duration minutes"""
	start_time = time.time()
	end_time = start_time + duration * 60

	quick_tests = []

	tirs = []
	hours = 1
	while time.time() < end_time:
		print('Time remaining:', end_time - time.time())
		seed = datetime.datetime.utcnow().timestamp()
		print("timestamp ={0}\n".format(seed))
		random.seed(seed)

		root = generate_tvm_and_np_tree()

		tvm_expr = root.emit_tvm()
		elapsed_time = time.time() - start_time
		tirs.append((elapsed_time, tvm_expr))
		if elapsed_time / 3600 > hours:
			with open(str(hours), 'wb') as f:
				pickle.dump(tirs, f)
			hours += 1
			tirs = []

		print("tree={0}".format(colored(root,"cyan")))

		print("tvm expr={0}".format(colored(tvm_expr,"yellow")))
		np_expr = root.emit_np()
		
		SymbolTable.populate()

		print("SymbolTable.binds={0}".format(SymbolTable.binds))

		np_result = evaluate_np_expr(np_expr)
		if (np_result == "Runtime Exception"):
			print("np error={0}".format(GenerationNode.NP_CULPRIT))

		print("np result={0}".format(np_result))

		lit_value = get_literal_value(tvm_expr)
		if lit_value:
			tvm_result = lit_value
			print("tvm result={0} found in front end".format(tvm_result))
		else:
			with mp.Manager() as m:
				d = m.dict()
				p = mp.Process(target=evaluate_tvm_expr, args=(tvm_expr, d))
				p.start()
				p.join(TIMEOUT)
				if p.is_alive() or p.exitcode != 0:
					p.terminate()
					continue
				else:
					tvm_result = d['ret']
			if(tvm_result == "Runtime Exception"):
				print("tvm error={0}".format(GenerationNode.TVM_CULPRIT))
			print("tvm result={0}".format(tvm_result))


		if(np_result == None and tvm_result == None):
			print("Both crashed.")
		else:
			try:
				is_equal = compare_results(np_result,tvm_result)
			except:
				is_equal = False
			print("equal={0}".format(colored("True","green") if is_equal else colored("False","red")))
			if (not is_equal and tvm_result and np_result):
				root.find_mismatch()
				print("mismatch={0}".format(colored(GenerationNode.MISMATCH_CULPRIT,"red")))
				for arg in GenerationNode.MISMATCH_CULPRIT.m_args:
					with mp.Manager() as m:
						d = m.dict()
						p = mp.Process(target=evaluate_tvm_expr, args=(arg.m_emitted_tvm_op, d))
						p.start()
						p.join(TIMEOUT)
						if p.is_alive() or p.exitcode != 0:
							p.terminate()
							continue
						else:
							tvm_val = d['ret']
					print("\t {0} np val={1}, tvm val={2}".format(arg.m_op.__name__,evaluate_np_expr(arg.m_emitted_np_op), tvm_val))

				quick_test_file_name = _quick_test_file_name(seed)
				quick_test_file = open(quick_test_file_name,"w")
				quick_test_file.write(_quick_test_str(GenerationNode.MISMATCH_CULPRIT))
				quick_test_file.close()
				quick_tests.append(quick_test_file_name)
	
	with open(str(hours), 'wb') as f:
		pickle.dump(tirs, f)
	for quick_test in quick_tests:
		print("Quick test written to {0}".format(quick_test))
					

def _quick_test_str(root):
	""" Create a python program for quick testing

	Returns
	-------
	quick_test : str
		Python program for testing mistmatch
	"""
	ret = "import __init__\n"
	ret += "from symboltable import SymbolTable\n"
	ret += "from expression import *\n"
	ret += "from test_bed import evaluate_tvm_expr,evaluate_np_expr\n"
	ret += "SymbolTable.recover_from_binds(" + str(SymbolTable.binds) + ")\n"
	ret += "tvm_expr=" + str(root) + "\n"
	ret += "np_expr=" + str(root).replace("apply", "apply_np") + "\n"
	ret += "print(evaluate_tvm_expr(tvm_expr))\n"
	ret += "print(evaluate_np_expr(np_expr))\n"
	return ret


def _quick_test_file_name(timestamp):
	return "../quicktests/quick_test_" + str(timestamp)


if __name__ == "__main__":
	run(24*60)
