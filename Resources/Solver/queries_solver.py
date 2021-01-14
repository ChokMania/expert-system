from Resources.Tree.truth_table import Truth_table
from Resources.Tree.node import LetterNode, ConnectorNode, Node, LetterOrConnectorNode
from Resources.Utils.log import Logger


class QueriesSolver:
    trust_table = Truth_table()

    def __init__(self, vb, queries, tree):
        self.logger = Logger("QueriesSolver", vb)
        self.logger.info("Initialization of class")
        self.queries = queries
        self.tree = tree
        self.result_operators_functions = {
            "+": self.get_result_and_operator_state,
            "!": self.get_result_not_operator_state,
            "^": self.get_result_xor_operator_state,
            "|": self.get_result_or_operator_state,
            "=>": self.get_implication_state,
        }
        self.result = []

    def get_expression_node_state(self, node: LetterOrConnectorNode) -> bool:
        if node.visited is True:
            return node.state
        if isinstance(node, LetterNode):
            # solving_letter_state is setting node.visited to true
            return self.solving_letter_state(node)
        elif isinstance(node, ConnectorNode):
            node.visited = True
            if node.type == "!":
                ret1 = self.get_expression_node_state(node.children[0])
                return self.trust_table.find_operand_value(node, ret1, None)
            else:
                ret1 = self.get_expression_node_state(node.children[0])
                ret2 = self.get_expression_node_state(node.children[1])
                return self.trust_table.find_operand_value(node, ret1, ret2)

    def get_result_and_operator_state(
        self, node: LetterOrConnectorNode, children_node_looking_for_state: LetterOrConnectorNode
    ):
        if node.visited is not True:
            node.state = self.get_result_node_state(
                node=node.result_parents[0],
                children_node_looking_for_state=children_node_looking_for_state,
            )
            node.visited = True
        return node.state

    def get_result_not_operator_state(
        self, node: LetterOrConnectorNode, children_node_looking_for_state: LetterOrConnectorNode
    ):
        if node.visited is not True:
            ret = self.get_result_node_state(
                node=node.result_parents[0], children_node_looking_for_state=node
            )
            if ret is None:
                node.state = None
            else:
                node.state = not ret
            node.visited = True
        return node.state

    def get_reversed_result_operator_state(
        self, node: LetterOrConnectorNode, children_node_looking_for_state: LetterOrConnectorNode
    ):
        """This method is visiting the result tree from a parent to their childrens to see if
        the current ConnectorNode can be set to true"""
        if node.children[0] != children_node_looking_for_state:
            other_children_node = node.children[0]
        elif node.children[1] != children_node_looking_for_state:
            other_children_node = node.children[0]
        if isinstance(other_children_node, LetterNode):
            return self.solving_letter_state(letter_node=other_children_node)
        else:
            ret = self.get_reversed_result_operator_state(
                node=other_children_node, children_node_looking_for_state=node
            )
            if isinstance(node, ConnectorNode) and node.type == "!":
                return self.trust_table.find_operand_value(node, ret, None)
            else:
                return self.trust_table.find_operand_value(node, ret, True)

    def get_result_xor_operator_state(
        self, node: LetterOrConnectorNode, children_node_looking_for_state: LetterOrConnectorNode
    ):
        raise NotImplementedError
        # other_children_state = None
        # if node.visited is not True:
        #     # Preventing infinite loop when looking for the other child
        #     if node.currently_solving is False:
        #         node.state = self.get_result_node_state(
        #             node=node.result_parents[0], children_node_looking_for_state=node
        #         )
        #         # Getting the other child
        #         if node.children[0] == children_node_looking_for_state:
        #             other_children_node = node.children[1]
        #         else:
        #             other_children_node = node.children[0]
        #         if isinstance(other_children_node, ConnectorNode):
        #             other_children_state = not self.get_reversed_result_operator_state(
        #                 node=other_children_node,
        #                 children_node_looking_for_state=children_node_looking_for_state,
        #             )
        #         else:
        #             pass

        #         node.currently_solving = False
        #         node.visited = True
        #     else:
        #         pass
        # if node.state is True or node.state is None:
        #     if other_children_state is True:
        #         return False
        #     if node.state is True:
        #         return True
        #     else:
        #         return None
        # else:
        #     return False

    def get_result_or_operator_state(
        self, node: LetterOrConnectorNode, children_node_looking_for_state: LetterOrConnectorNode
    ):
        other_children_state_if_not_connector = None
        if node.visited is not True:
            # Preventing infinite loop when looking for the other child
            if node.currently_solving is False:
                node.currently_solving = True
                node.state = self.get_result_node_state(
                    node=node.result_parents[0], children_node_looking_for_state=node
                )
                # Getting the other child
                if node.children[0] == children_node_looking_for_state:
                    other_children_node = node.children[1]
                else:
                    other_children_node = node.children[0]
                # If the child is a "not" operator, getting the reverse state result to know if it's true or not
                if isinstance(other_children_node, ConnectorNode) and (
                    other_children_node.type == "!"
                ):
                    other_children_state_if_not_connector = not self.get_reversed_result_operator_state(
                        node=other_children_node,
                        children_node_looking_for_state=children_node_looking_for_state,
                    )
                node.currently_solving = False
                node.visited = True
            else:
                pass
        if node.state is True or node.state is None:
            if other_children_state_if_not_connector is False and node.state is True:
                return True
            else:
                return None
        else:
            return False

    def get_result_node_state(
        self, node: LetterOrConnectorNode, children_node_looking_for_state: LetterOrConnectorNode
    ):
        if isinstance(node, LetterNode):
            self.logger.error("Something is wrong")
        else:
            return self.result_operators_functions[node.type](
                node=node, children_node_looking_for_state=children_node_looking_for_state
            )

    def get_implication_state(self, node: ConnectorNode, *args, **kwargs):
        if node.visited is False:
            node.state = self.get_expression_node_state(node.children[0])
            node.visited = True
        return node.state

    def get_letter_state(self, letter_node: LetterNode) -> bool:
        """Only usefull for the state_fixed"""
        if letter_node.state is True or letter_node.state_fixed is True:
            return True
        return letter_node.state

    def solving_letter_state(self, letter_node: LetterNode) -> bool:
        """This method solve the letter state and return it's state"""
        self.logger.info("Solving letter : ", letter_node.name)
        if letter_node.currently_solving is False and letter_node.visited is not True:
            letter_node.currently_solving = True
            current_state = self.get_letter_state(letter_node)
            if current_state is not True:
                for result_parent in letter_node.result_parents:
                    ret = self.get_result_node_state(
                        node=result_parent, children_node_looking_for_state=letter_node
                    )
                    if current_state is False or (current_state is None and ret is True):
                        current_state = ret
            letter_node.state = current_state
            letter_node.visited = True
            letter_node.currently_solving = False
        return self.get_letter_state(letter_node)

    def solve_queries(self):
        """Solve queries for a set of letters_node"""
        letters = self.tree.letters
        for querie in self.queries:
            self.logger.info(
                f"Before: Letter : {letters[querie].name} | State : {(letters[querie].state)}"
            )
            self.solving_letter_state(letters[querie])
            self.result.append(f"{letters[querie].name} is {letters[querie].state}")
            self.logger.info(
                f"After:  Letter : {letters[querie].name} | State : {(letters[querie].state)}"
            )

