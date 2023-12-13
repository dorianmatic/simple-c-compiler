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
            if not Types.validate_string(node.children[0].value):
                self._terminate('')

            return Types.ARRAY_CONST_CHAR, False
        elif children_names == ['L_ZAGRADA', '<izraz>', 'D_ZAGRADA']:
            return self._expression(node.children[1])

    def _postfix_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<primary_expression>']:
            return self._primary_expression(node.children[0])
        elif children_names == ['<postfiks_izraz>', 'L_UGL_ZAGRADA', '<izraz>', 'D_UGL_ZAGRADA']:
            postfix_type, postfix_l_expression = self._postfix_expression(node.children[0])

            if not Types.is_array(postfix_type):
                self._terminate('')

            expression_type, _ = self._expression(node.children[2])
            if not Types.is_castable(expression_type, Types.INT):
                self._terminate('')

            return Types.get_array_type(postfix_type), not Types.is_const(postfix_type)

        elif children_names == ['<postfiks_izraz>', 'L_ZAGRADA', 'D_ZAGRADA']:
            # TODO
            pass
        elif children_names == ['<postfiks_izraz>', 'L_ZAGRADA', '<lista_argumenata>', 'D_ZAGRADA']:
            # TODO
            pass
        elif children_names == ['<postfiks_izraz>', 'OP_INC'] or children_names == ['<postfiks_izraz>', 'OP_DEC']:
            postfix_type, postfix_l_expression = self._postfix_expression(node.children[0])

            if not Types.is_castable(postfix_type, Types.INT) or postfix_l_expression is False:
                self._terminate('')

            return Types.INT, False

    def _argument_list(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<izraz_pridruzivanja>']:
            assigment_exp_type, _ = self._assignment_expression(node.children[0])

            return [assigment_exp_type]
        if children_names == ['<lista_argumenata>', 'ZAREZ', '<izraz_pridruzivanja>']:
            argument_list_type, _ = self._argument_list(node.children[0])
            assigment_exp_type, _ = self._assignment_expression(node.children[2])

            return argument_list_type + assigment_exp_type

    def _unary_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<postfiks_izraz>']:
            return self._postfix_expression(node.children[0])
        elif children_names == ['OP_INC', '<unary_expression>'] or children_names == ['OP_DEC', '<unary_expression>']:
            unary_exp_type, unary_exp_l_exp = self._unary_expression(node.children[0])
            if unary_exp_l_exp == False or not Types.is_castable(unary_exp_type, Types.INT):
                self._terminate('')

            return Types.INT, False
        elif children_names == ['<unarni_operator>', '<cast_izraz>']:
            cast_exp_type, _ = self._cast_expression(node.children[1])
            if not Types.is_castable(cast_exp_type, Types.INT):
                self._terminate('')

            return Types.INT, False

    def _cast_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<unary_expression>']:
            return self._unary_expression(node.children[0])
        elif children_names == ['L_ZAGRADA', '<ime_tipa>', 'D_ZAGRADA', '<cast_izraz>']:
            type_name_type, _ = self._type_name(node.children[1])
            cast_exp_type, _ = self._cast_expression(node.children[3])

            if not Types.is_explicitly_castable(cast_exp_type, type_name_type):
                self._terminate('')

            return type_name_type, False

    def _type_name(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<specifikator_tipa>']:
            return self._type_specifier(node.children[0])
        elif children_names == ['KR_CONST', '<specifikator_tipa>']:
            type_specifier_type = self._type_specifier(node.children[1])
            if type_specifier_type == Types.VOID:
                self._terminate('')

            return Types.to_const(type_specifier_type)

    def _type_specifier(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['KR_VOID']:
            return Types.VOID
        elif children_names == ['KR_CHAR']:
            return Types.CHAR
        elif children_names == ['KR_INT']:
            return Types.INT

    def _single_operator_meta_expression(self, node: Node, condition_one: bool, condition_two: bool,
                                         cond_one_check: callable, cond_two_check_one: callable,
                                         cond_two_check_two: callable):
        if condition_one:
            return cond_one_check(node.children[0])
        elif condition_two:
            type_one, _ = cond_two_check_one(node.children[0])
            if not Types.is_castable(type_one, Types.INT):
                self._terminate('')

            type_two, _ = cond_two_check_two(node.children[2])
            if not Types.is_castable(type_two, Types.INT):
                self._terminate('')

            return Types.INT, False

    def _multiplicative_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<cast_expression>'],
            (children_names == ['<multiplikativni_izraz>', 'OP_PUTA', '<cast_izraz>'] or
             children_names == ['<multiplikativni_izraz>', 'OP_DIJELI', '<cast_izraz>'] or
             children_names == ['<multiplikativni_izraz>', 'OP_MOD', '<cast_izraz>']),
            self._cast_expression,
            self._multiplicative_expression,
            self._cast_expression
        )

    def _additive_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<multiplikativni_izraz>'],
            (children_names == ['<aditivni_izraz>', 'PLUS', '<multiplikativni_izraz>'] or
             children_names == ['<aditivni_izraz>', 'MINUS', '<multiplikativni_izraz>']),
            self._multiplicative_expression,
            self._additive_expression,
            self._multiplicative_expression
        )

    def _relational_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<aditivni_izraz>'],
            (children_names == ['<odnosni_izraz>', 'OP_LT', '<aditivni_izraz>'] or
             children_names == ['<odnosni_izraz>', 'OP_GT', '<aditivni_izraz>'] or
             children_names == ['<odnosni_izraz>', 'OP_LTE', '<aditivni_izraz>'] or
             children_names == ['<odnosni_izraz>', 'OP_GTE', '<aditivni_izraz>']),
            self._additive_expression,
            self._relational_expression,
            self._additive_expression
        )

    def _equivalence_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<odnosni_izraz>'],
            (children_names == ['<jednakosni_izraz>', 'OP_EQ', '<odnosni_izraz>'] or
             children_names == ['<jednakosni_izraz>', 'OP_NEQ', '<odnosni_izraz>']),
            self._relational_expression,
            self._equivalence_expression,
            self._relational_expression
        )

    def _bin_and_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<jednakosni_izraz>'],
            children_names == ['<bin_i_izraz>', 'OP_BIN_I', '<jednakosni_izraz>'],
            self._equivalence_expression,
            self._bin_and_expression,
            self._equivalence_expression
        )

    def _bin_xor_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<bin_i_izraz>'],
            children_names == ['<bin_xili_izraz>', 'OP_BIN_XILI', '<bin_i_izraz>'],
            self._bin_and_expression,
            self._bin_xor_expression,
            self._bin_and_expression
        )

    def _bin_or_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<bin_xili_izraz>'],
            children_names == ['<bin_ili_izraz>', 'OP_BIN_ILI', '<bin_xili_izraz>'],
            self._bin_xor_expression,
            self._bin_or_expression,
            self._bin_xor_expression
        )

    def _logical_and_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<bin_ili_izraz>'],
            children_names == ['<log_i_izraz>', 'OP_I', '<bin_ili_izraz>'],
            self._bin_or_expression,
            self._logical_and_expression,
            self._bin_or_expression
        )

    def _logical_or_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<log_i_izraz>'],
            children_names == ['<log_ili_izraz>', 'OP_ILI', '<log_i_izraz>'],
            self._logical_and_expression,
            self._logical_or_expression,
            self._logical_and_expression
        )

    def _assignment_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<log_ili_izraz>']:
            return self._logical_or_expression(node.children[0])
        elif children_names == ['<postfiks_izraz>', 'OP_PRIDRUZI', '<izraz_pridruzivanja>']:
            postfix_exp_type, postfix_exp_l = self._postfix_expression(node.children[0])
            assignment_exp_type, _ = self._assignment_expression(node.children[2])
            if not Types.is_castable(postfix_exp_type, assignment_exp_type) or postfix_exp_l == False:
                self._terminate('')

            return postfix_exp_type, False

    def _expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<izraz_pridruzivanja>']:
            pass
        elif children_names == ['<izraz>', 'ZAREZ', '<izraz_pridruzivanja>']:
            self._expression(node.children[0])
            assignment_exp_type, _ = self._assignment_expression(node.children[2])

            return assignment_exp_type, False

    def _complex_command(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['L_VIT_ZAGRADA', '<lista_naredbi>', 'D_VIT_ZAGRADA']:
            self._command_list(node.children[1])
        elif children_names == ['L_VIT_ZAGRADA', '<lista_deklaracija>', '<lista_naredbi>', 'D_VIT_ZAGRADA']:
            self._declaration_list(node.children[1])
            self._command_list(node.children[2])

    def _command_list(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<naredba>']:
            self._command(node.children[0])
        elif children_names == ['<lista_naredbi>', '<naredba>']:
            self._command_list(node.children[0])
            self._command(node.children[1])

    def _command(self, node: Node):
         # TODO: Implement this
         pass

    def _expression_command(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['TOCKAZAREZ']:
            return Types.INT
        elif children_names == ['<izraz>', 'TOCKAZAREZ']:
            expression_type, _ = self._expression(node.children[0])

            return expression_type

    def _if_command(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['KR_IF', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>']:
            expression_type, _ = self._expression(node.children[2])
            if not Types.is_castable(expression_type, Types.INT):
                self._terminate('')

            self._command(node.children[4])
        elif children_names == ['KR_IF', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>', 'KR_ELSE', '<naredba>']:
            expression_type, _ = self._expression(node.children[2])
            if not Types.is_castable(expression_type, Types.INT):
                self._terminate('')

            self._command(node.children[4])
            self._command(node.children[6])

    def _loop_command(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['KR_WHILE', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>']:
            exp_type, _ = self._expression(node.children[2])
            if not Types.is_castable(exp_type, Types.INT):
                self._terminate('')
            self._command(node.children[4])
        elif children_names == ['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', 'D_ZAGRADA', '<naredba>']:
            self._expression_command(node.children[2])
            exp_command_type = self._expression_command(node.children[3])
            if not Types.is_castable(exp_command_type, Types.INT):
                self._terminate('')
            self._command(node.children[5])
        elif children_names == ['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', '<izraz>', 'D_ZAGRADA', '<naredba>']:
            self._expression_command(node.children[2])
            exp_command_type = self._expression_command(node.children[3])
            if not Types.is_castable(exp_command_type, Types.INT):
                self._terminate('')
            self._expression(node.children[4])
            self._command(node.children[6])

    def _jump_command(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['KR_CONTINUE', 'TOCKAZAREZ'] or children_names == ['KR_BREAK', 'TOCKAZAREZ']:
            # TODO: Check if inside loop...
            pass
        elif children_names == ['KR_RETURN', 'TOCKAZAREZ']:
            # TODO: Check if inside void function
            pass
        elif children_names == ['KR_RETURN', '<izraz>', 'TOCKAZAREZ']:
            exp_type = self._expression(node.children[1])

            # TODO: Check if exp_type is correct

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
