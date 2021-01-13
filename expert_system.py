import argparse
import re

from Resources.Utils.log import Logger
from Resources.Parser.parser import Parser, Rule
from Resources.Tree.tree import Tree
from Resources.Tree.truth_table import Truth_table
from Resources.Tree.tree_printer import TreePrinter
from Resources.Solver.queries_solver import QueriesSolver
from Resources.Shell.shell import Shell

def parsing_shell(vb):
	logger = Logger("Main", vb)
	shell = Shell(completekey="tab")
	shell.cmdloop()
	parser = Parser(None, vb)
	for it, line in enumerate(shell.rules):
		splited_line = re.split("=>|<=>", line)
		rule = Rule(line, splited_line, it, vb)
		parser.rules.append(rule)
	parser.facts = list(shell.facts.keys())
	parser.queries = list(shell.queries.keys())
	if len(parser.queries) == 0:
		logger.error("No queries")
	return parser


def parsing(file, vb):
	# logger = Logger("Main", vb)
	parser = Parser(file.readlines(), vb)
	parser.parsing()
	return parser


def main_test(file, vb):
	try:
		parser = parsing(file, vb)
		tree = Tree(vb)
		tree.create_all_letternode(parser.rules, parser.facts, parser.queries)
		tree.init_letters_state(parser.rules, parser.facts, parser.queries)
		tree.rules = parser.rules
		tree.create_rules_tree()
		result = "Nothing"
		return result
	except Exception as error:
		return "Error :" + error.args[1]


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Expert System")
	parser.add_argument("-vb", "--verbose", action="store_true", help="Enable verbose")
	subparsers = parser.add_subparsers()
	file = subparsers.add_parser("file")
	file.set_defaults(which="file")
	shell = subparsers.add_parser("shell")
	file.add_argument("filename", type=argparse.FileType("r"), help="The file containing rules")
	shell.set_defaults(which="shell")
	args = parser.parse_args()
	try:
		parser = (
			parsing_shell(args.verbose)
			if args.which == "shell"
			else parsing(args.filename, args.verbose)
		)
	except Exception as error:
		pass
	tree = Tree(args.verbose)
	tree.create_all_letternode(parser.rules, parser.facts, parser.queries)
	tree.init_letters_state(parser.rules, parser.facts, parser.queries)
	tree.rules = parser.rules
	tree.create_rules_tree()
	tree_printer = TreePrinter()
	truth_table = Truth_table()
	solver = QueriesSolver(vb=args.verbose,queries=parser.queries, tree=tree)
	print()
	for letter in parser.queries:
		letter_node = tree.letters[letter]
		print("letter name : ", letter_node.name, "\tletter.state : ", letter_node.state)

	# ###Trust_table TRYOUT
	# truth_table.find_operand_value(
	#     tree.letters["A"].expression_parents[0],
	#     tree.letters["A"].expression_parents[0].children[0],
	#     tree.letters["A"].expression_parents[0].children[1],
	# )
	# truth_table.find_operand_value(
	#     tree.letters["D"].expression_parents[0],
	#     tree.letters["D"].expression_parents[0].children[0],
	#     tree.letters["D"].expression_parents[0].children[1],
	# )
	# truth_table.find_operand_value(
	#     tree.letters["G"].expression_parents[0],
	#     tree.letters["G"].expression_parents[0].children[0],
	#     tree.letters["G"].expression_parents[0].children[1],
	# )
	# ###END TRYOUT
	# print("\nTesting print rules for A: ")
	# for idx, rule in enumerate(tree.letters["A"].rules_implied_in):
	#     print("rule number ", idx, " :", rule)
	# print("\nTesting print result parent for letter A : ")
	# tree_printer.print_all_result_parents_from_node(tree.letters["A"])
	# print("\nTesting print expression parent for letter A : ")
	# tree_printer.print_all_expression_parents_from_node(tree.letters["A"])
	# print("\nTesting print graph for letter A : ")
	# tree_printer.travel_graph_for_node(tree.letters["A"], tree.letters["A"])
