from lab3.utils.tree import Node
from lab3.utils.types import Types

class DescentException(Exception):
    def __init__(self, message):
        super().__init__(message)


class RecursiveDescent:
    def __init__(self, tree: Node):
        self.tree = tree

    def descend(self):
        self._translation_unit(self.tree)

    @staticmethod
    def _get_children_names(node: Node):
        return list(map(lambda child: child.name, node.children))

    def _terminate(self, message):
        raise DescentException(message)

    ## SEMANTIC RULES ##

    def _primary_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['IDN']:
            # TODO: Implement variables scoping ...
            pass
        elif children_names == ['BROJ']:
            if not Types.validate_int(node.children[0].value):
                self._terminate('Int invalid')

            return Types.INT, False
        elif children_names == ['ZNAK']:
            if not Types.validate_char(node.children[0].value):
                self._terminate('Int invalid')

            return Types.CHAR, False
        elif children_names == ['NIZ_ZNAKOVA']:
            return Types.ARRAY_CONST_CHAR, False
        elif children_names == ['L_ZAGRADA', '<izraz>', 'D_ZAGRADA']:
            return self._expression(node.children[1])

    def _postfix_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<primary_expression>']:
            return self._primary_expression(node.children[0])
        elif children_names == ['<postfiks_izraz>', 'L_UGL_ZAGRADA', '<izraz>', 'D_UGL_ZAGRADA']:
            pass
        elif children_names == ['<postfiks_izraz>', 'L_ZAGRADA', 'D_ZAGRADA']:
            pass
        elif children_names == ['<postfiks_izraz>', 'L_ZAGRADA', '<lista_argumenata>', 'D_ZAGRADA']:
            pass
        elif children_names == ['<postfiks_izraz>', 'OP_INC'] or children_names == ['<postfiks_izraz>', 'OP_DEC']:
            pass
        


    def _expression(self, node: Node):
        pass

    def _translation_unit(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<vanjska_deklaracija>']:
            self._outer_declaration(node.children[0])
        elif children_names == ['<prijevodna_jedinica>', '<vanjska_deklaracija>']:
            self._translation_unit(node.children[0])
            self._outer_declaration(node.children[0])


    def _outer_declaration(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<definicija_funkcije>']:
            self._function_definition(node.children[0])
        elif children_names == ['<deklaracija>']:
            self._declaration(node.children[0])

    def _function_definition(self, node: Node):
        pass

    def _declaration(self, node: Node):
        pass