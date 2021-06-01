"""
Generate TIRs and stores them as seeds
"""

from typing import Tuple, List

from tvm import tir
from TVMFuzz.symboltable import SymbolTable
from TVMFuzz.expr_generation import generate_tvm_and_np_tree

import pickle
import argparse
import os

# specify the number of seeds wanna generate and the directory to store them
parser = argparse.ArgumentParser()
parser.add_argument('--number', '-n', type=int, default=100)
parser.add_argument('--dir-to-store', '-d', type=str, default='seeds')
args = parser.parse_args()

# Returns a pair of TIR and its parameter variables(IMPORTANT)
def gen_tir_with_vars() -> Tuple[tir.expr.PrimExpr, List[tir.expr.Var]]:
    SymbolTable.variables = []
    generated_tir: tir.expr.PrimExpr = generate_tvm_and_np_tree().emit_tvm()
    variables: List[tir.expr.Var] = SymbolTable.variables
    return (generated_tir, variables)

if __name__ == '__main__':
    if not os.path.exists(args.dir_to_store):
        os.makedirs(args.dir_to_store)
        print(f"Successfully create directory: {os.path.abspath(args.dir_to_store)}")
    for index in range(args.number):
        with open(os.path.join(args.dir_to_store, str(index)), 'wb') as f:
            data = gen_tir_with_vars()
            pickle.dump(data, f)
