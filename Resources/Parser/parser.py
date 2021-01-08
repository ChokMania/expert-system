import re
from Resources.Utils.log import Logger

OPERATORS = "+|^"


OPERATORS = ['!', '+', '|', '^', '(', ')']
PRIORITY = {'^': 0, '|': 1, '+': 2, '!': 3}


class Rule:
	def __init__(self, line, splited_line, vb):
		self.vb = vb
		self.logger = Logger("Parser.Rule", self.vb)
		if line.count("(") != line.count(")"):
			self.logger.error("Mismatching parantheses")
		self.expression = self.create_rule(splited_line[0])
		self.implication = "<=>" if "<=>" in line else "=>"
		self.result = self.create_rule(splited_line[1])

	def create_rule(self, rule):
		stack = []
		output = ''
		for value in rule:
			if value not in OPERATORS:
				output += value
			elif value == '(':
				stack.append('(')
			elif value == ')':
				while stack and stack[-1] != '(':
					output += stack.pop()
				stack.pop()
			else:
				while stack and stack[-1] != '(' and value != '!' and PRIORITY[value] <= PRIORITY[stack[-1]]:
					output += stack.pop()
				stack.append(value)
		while stack:
			output += stack.pop()
		output = output.replace('!!', '')
		return output

	def __repr__(self):
		return f"\n{self.expression} {self.implication} {self.result}"

	def __str__(self):
		return f"Conditions : {self.expression:<10}\tImplication : {self.implication:<3}\tResult : {self.result}\n"


class Parser:
	def __init__(self, file, vb):
		self.vb = vb
		self.logger = Logger("Parser.Parser", self.vb)
		self.input = file.readlines()
		self.facts = []
		self.queries = []
		self.rules = []
		self.logger.info("Initialization of class")
		self.parsing()

	def parsing(self):
		rule_d = 0
		self.logger.info("Starting parsing")
		for line in self.input:
			line = line.split("#", 1)[0]
			line = (''.join(line.split()))
			if not line:
				continue
			if line[0] == "=":
				self.fact_parsing(line[1:])
			elif line[0] == "?":
				self.queries_parsing(line[1:])
			else:
				if "=>" not in line and "<=>" not in line:
					self.logger.error("Rule format incorrect")
				splited_line = re.split("=>|<=>", line)
				rule = Rule(line, splited_line, self.vb)
				self.rules.append(rule)
				if rule_d == 0:
					self.logger.info("Rules detected")
					rule_d = 1
		if rule_d == 0:
			self.logger.warning("No rules detected")


		if len(self.queries) == 0:
			self.logger.error("No queries")
		if len(self.facts) == 0:
			self.logger.error("No facts")
		self.logger.info("End of parsing")

	def fact_parsing(self, line):
		if len(self.facts) != 0:
			self.logger.error("Facts already defined")
		if line.isalpha() and line.isupper():
			self.facts = list(line)
			self.logger.info(f"Facts detected : {self.facts}")
		else:
			self.logger.error("Facts format incorrect")

	def queries_parsing(self, line):
		if len(self.queries) != 0:
			self.logger.error("Queries already defined")
		if line.isalpha() and line.isupper():
			self.queries = list(line)
			self.logger.info(f"Queries detected : {self.queries}")
		else:
			self.logger.error("Queries format incorrect")

	def convert_rules(self):
		print(self.rules)
		for idx, rule in enumerate(self.rules, start=0):
			result = rule.result
			count_xor_or_operator = result.count("|") + result.count("^")
			if count_xor_or_operator == 0:
				continue
			elif count_xor_or_operator > 1:
				raise ValueError("Only one 'XOR' or 'OR' operator are allowed in result.")

			rule_let = []
			nb = 0
			op = []
			for l in result:
				if l.isalpha() and l.isupper():
					rule_let.append(l)
					nb += 1
				else:
					op.append(l)
			if nb > 2:
				raise ValueError(
					"Only two letters can be set in result when using 'XOR' or 'OR' operator"
				)
			if nb != 1:
				print(rule)
				for l in rule_let:
					other_let = []
					for x in rule_let:
						if x != l:
							other_let.append(x)
					if len(other_let) > 0:
						line = rule.expression + '!'+ str(other_let[0]) + " => " + l
						splited = line.split()
						print(line)
						splited.pop(1)
						print(splited)
						self.rules.append(Rule(line,splited,"vb"))
				self.rules.pop(idx)

		print("##RULES##")
		print(self.rules)
		print("########")

