from lab3.utils.helpers import *
from lab3.utils.generative_tree import Node
from lab3.utils.types import Types


class DescentException(Exception):
    def __init__(self, message):
        super().__init__(message)


class RecursiveDescent:
    def __init__(self, tree: Node):
        self.tree = tree
        self.function_declarations = []

    def descend(self):
        self._translation_unit(self.tree)

        if not self._main_exists():
            self._terminate(message='main')
        if self._non_defined_function_exists():
            self._terminate(message='funkcija')

    def _main_exists(self):
        for declaration in self.tree.scope.declarations:
            if declaration['kind'] == 'function' and declaration['identifier'] == 'main' and declaration[
                'parameter_types'] == [Types.VOID] and declaration['return_type'] == Types.INT:
                return True

        return False

    def _non_defined_function_exists(self):
        for i, declaration in enumerate(self.function_declarations):
            if declaration['definition']:
                continue
            for definition in filter(lambda d: d['definition'] is True, self.function_declarations[:i]):
                if declaration['identifier'] == definition['identifier'] and declaration['parameter_types'] == \
                        definition['parameter_types'] and declaration['return_type'] == definition['return_type']:
                    continue
            return True
        return False

    @staticmethod
    def _get_children_names(node: Node):
        return list(map(lambda child: child.name, node.children))

    def _terminate(self, node: Node = None, message: str = ''):
        if not message:
            message = f'{node.name} ::='
            for child in node.children:
                if is_non_terminal(child.name):
                    message += f' {child.name}'
                else:
                    if child.name == 'NIZ_ZNAKOVA':
                        child.value = f'"{child.value}"'
                    elif child.name == 'ZNAK':
                        child.value = f"'{child.value}'"

                    message += f' {child.name}({child.line},{child.value})'

        raise DescentException(message)

    ## SEMANTIC RULES ##

    def _primary_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['IDN']:
            if declaration := node.get_declaration(node.children[0].value):
                if declaration['kind'] == 'variable':
                    var_type = declaration['return_type']
                    return var_type, not (Types.is_const(var_type) or Types.is_array(var_type))
                else:
                    return declaration, False
            else:
                self._terminate(node)

        elif children_names == ['BROJ']:
            if not Types.validate_int(node.children[0].value):
                self._terminate(node)

            return Types.INT, False
        elif children_names == ['ZNAK']:
            if not Types.validate_char(node.children[0].value):
                self._terminate(node)

            return Types.CHAR, False
        elif children_names == ['NIZ_ZNAKOVA']:
            if not Types.validate_string(node.children[0].value):
                self._terminate(node)

            return Types.ARRAY_CONST_CHAR, False
        elif children_names == ['L_ZAGRADA', '<izraz>', 'D_ZAGRADA']:
            return self._expression(node.children[1])

    def _postfix_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<primarni_izraz>']:
            return self._primary_expression(node.children[0])
        elif children_names == ['<postfiks_izraz>', 'L_UGL_ZAGRADA', '<izraz>', 'D_UGL_ZAGRADA']:
            postfix_type, postfix_l_expression = self._postfix_expression(node.children[0])

            if not Types.is_array(postfix_type):
                self._terminate(node)

            expression_type, _ = self._expression(node.children[2])
            if not Types.is_castable(expression_type, Types.INT):
                self._terminate(node)

            return Types.get_array_type(postfix_type), not Types.is_const(postfix_type)

        elif children_names == ['<postfiks_izraz>', 'L_ZAGRADA', 'D_ZAGRADA']:
            postfix_exp_type, _ = self._postfix_expression(node.children[0])
            if postfix_exp_type['parameter_types'] != [Types.VOID]:
                self._terminate(node)

            return postfix_exp_type['return_type'], False
        elif children_names == ['<postfiks_izraz>', 'L_ZAGRADA', '<lista_argumenata>', 'D_ZAGRADA']:
            postfix_exp_type, _ = self._postfix_expression(node.children[0])
            argument_list_types = self._argument_list(node.children[2])

            if len(postfix_exp_type['parameter_types']) != len(argument_list_types):
                self._terminate(node)
            for parameter_type, argument_type in zip(postfix_exp_type['parameter_types'], argument_list_types):
                if not Types.is_castable(argument_type, parameter_type):
                    self._terminate(node)

            return postfix_exp_type['return_type'], False
        elif children_names == ['<postfiks_izraz>', 'OP_INC'] or children_names == ['<postfiks_izraz>', 'OP_DEC']:
            postfix_type, postfix_l_expression = self._postfix_expression(node.children[0])

            if not Types.is_castable(postfix_type, Types.INT) or postfix_l_expression is False:
                self._terminate(node)

            return Types.INT, False

    def _argument_list(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<izraz_pridruzivanja>']:
            assigment_exp_type, _ = self._assignment_expression(node.children[0])

            return [assigment_exp_type]
        if children_names == ['<lista_argumenata>', 'ZAREZ', '<izraz_pridruzivanja>']:
            argument_list_type = self._argument_list(node.children[0])
            assigment_exp_type, _ = self._assignment_expression(node.children[2])

            return argument_list_type + [assigment_exp_type]

    def _unary_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<postfiks_izraz>']:
            return self._postfix_expression(node.children[0])
        elif children_names == ['OP_INC', '<unarni_izraz>'] or children_names == ['OP_DEC', '<unarni_izraz>']:
            unary_exp_type, unary_exp_l_exp = self._unary_expression(node.children[1])
            if unary_exp_l_exp == False or not Types.is_castable(unary_exp_type, Types.INT):
                self._terminate(node)

            return Types.INT, False
        elif children_names == ['<unarni_operator>', '<cast_izraz>']:
            cast_exp_type, _ = self._cast_expression(node.children[1])
            if not Types.is_castable(cast_exp_type, Types.INT):
                self._terminate(node)

            return Types.INT, False

    def _cast_expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<unarni_izraz>']:
            return self._unary_expression(node.children[0])
        elif children_names == ['L_ZAGRADA', '<ime_tipa>', 'D_ZAGRADA', '<cast_izraz>']:
            type_name_type = self._type_name(node.children[1])
            cast_exp_type, _ = self._cast_expression(node.children[3])

            if not Types.is_explicitly_castable(cast_exp_type, type_name_type):
                self._terminate(node)

            return type_name_type, False

    def _type_name(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<specifikator_tipa>']:
            return self._type_specifier(node.children[0])
        elif children_names == ['KR_CONST', '<specifikator_tipa>']:
            type_specifier_type = self._type_specifier(node.children[1])
            if type_specifier_type == Types.VOID:
                self._terminate(node)

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
                self._terminate(node)

            type_two, _ = cond_two_check_two(node.children[2])
            if not Types.is_castable(type_two, Types.INT):
                self._terminate(node)

            return Types.INT, False

    def _multiplicative_expression(self, node: Node):
        children_names = self._get_children_names(node)

        return self._single_operator_meta_expression(
            node,
            children_names == ['<cast_izraz>'],
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
                self._terminate(node)

            return postfix_exp_type, False

    def _expression(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<izraz_pridruzivanja>']:
            return self._assignment_expression(node.children[0])
        elif children_names == ['<izraz>', 'ZAREZ', '<izraz_pridruzivanja>']:
            self._expression(node.children[0])
            assignment_exp_type, _ = self._assignment_expression(node.children[2])

            return assignment_exp_type, False

    def _complex_command(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['L_VIT_ZAGRADA', '<lista_naredbi>', 'D_VIT_ZAGRADA']:
            self._command_list(node.children[1])
        elif children_names == ['L_VIT_ZAGRADA', '<lista_deklaracija>', '<lista_naredbi>', 'D_VIT_ZAGRADA']:
            self._declarations_list(node.children[1])
            self._command_list(node.children[2])

    def _command_list(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<naredba>']:
            self._command(node.children[0])
        elif children_names == ['<lista_naredbi>', '<naredba>']:
            self._command_list(node.children[0])
            self._command(node.children[1])

    def _command(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<slozena_naredba>']:
            self._complex_command(node.children[0])
        elif children_names == ['<izraz_naredba>']:
            self._expression_command(node.children[0])
        elif children_names == ['<naredba_petlje>']:
            self._loop_command(node.children[0])
        elif children_names == ['<naredba_skoka>']:
            self._jump_command(node.children[0])
        elif children_names == ['<naredba_grananja>']:
            self._if_command(node.children[0])

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
                self._terminate(node)

            self._command(node.children[4])
        elif children_names == ['KR_IF', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>', 'KR_ELSE', '<naredba>']:
            expression_type, _ = self._expression(node.children[2])
            if not Types.is_castable(expression_type, Types.INT):
                self._terminate(node)

            self._command(node.children[4])
            self._command(node.children[6])

    def _loop_command(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['KR_WHILE', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>']:
            exp_type, _ = self._expression(node.children[2])
            if not Types.is_castable(exp_type, Types.INT):
                self._terminate(node)
            self._command(node.children[4])
        elif children_names == ['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', 'D_ZAGRADA', '<naredba>']:
            self._expression_command(node.children[2])
            exp_command_type = self._expression_command(node.children[3])
            if not Types.is_castable(exp_command_type, Types.INT):
                self._terminate(node)
            self._command(node.children[5])
        elif children_names == ['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', '<izraz>', 'D_ZAGRADA',
                                '<naredba>']:
            self._expression_command(node.children[2])
            exp_command_type = self._expression_command(node.children[3])
            if not Types.is_castable(exp_command_type, Types.INT):
                self._terminate(node)
            self._expression(node.children[4])
            self._command(node.children[6])

    def _jump_command(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['KR_CONTINUE', 'TOCKAZAREZ'] or children_names == ['KR_BREAK', 'TOCKAZAREZ']:
            working_node = node
            while working_node.parent is not None:
                if working_node.name == '<naredba_petlje>':
                    return
                working_node = working_node.parent

            self._terminate(node)
        elif children_names == ['KR_RETURN', 'TOCKAZAREZ']:
            working_node = node
            while working_node.parent is not None:
                working_node = working_node.parent
                if working_node.scope is None:
                    continue

                for declaration in working_node.scope.declarations:
                    if declaration['kind'] == 'function' and declaration['return_type'] == Types.VOID:
                        return

            self._terminate(node)
        elif children_names == ['KR_RETURN', '<izraz>', 'TOCKAZAREZ']:
            exp_type, _ = self._expression(node.children[1])
            parent = node.parent
            while parent.parent:
                parent = parent.parent

            if parent.scope is None:
                return None

            for declaration in parent.scope.declarations:
                if declaration['kind'] == 'function' and Types.is_castable(exp_type, declaration['return_type']):
                    return

            self._terminate(node)

    def _translation_unit(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<vanjska_deklaracija>']:
            self._outer_declaration(node.children[0])
        elif children_names == ['<prijevodna_jedinica>', '<vanjska_deklaracija>']:
            self._translation_unit(node.children[0])
            self._outer_declaration(node.children[1])

    def _outer_declaration(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<definicija_funkcije>']:
            self._function_definition(node.children[0])
        elif children_names == ['<deklaracija>']:
            self._declaration(node.children[0])

    def _function_definition(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<ime_tipa>', 'IDN', 'L_ZAGRADA', 'KR_VOID', 'D_ZAGRADA', '<slozena_naredba>']:
            type_name_type = self._type_name(node.children[0])
            if Types.is_const(type_name_type):
                self._terminate(node)

            if declaration := node.get_declaration(node.children[1].value, only_global=True):
                if declaration['definition'] or declaration['return_type'] != type_name_type or declaration[
                    'parameter_types'] != [Types.VOID]:
                    self._terminate(node)

            self.function_declarations.append(
                node.declare_function(node.children[1].value, [Types.VOID], type_name_type, True)
            )
            self._complex_command(node.children[5])
        elif children_names == ['<ime_tipa>', 'IDN', 'L_ZAGRADA', '<lista_parametara>', 'D_ZAGRADA',
                                '<slozena_naredba>']:
            type_name_type = self._type_name(node.children[0])
            if Types.is_const(type_name_type):
                self._terminate(node)

            param_list_types, param_list_names = self._parameter_list(node.children[3])
            if declaration := node.get_declaration(node.children[1].name, only_global=True):
                if declaration['definition'] or declaration['return_type'] != type_name_type or declaration[
                    'parameter_types'] != param_list_types:
                    self._terminate(node)

            self.function_declarations.append(
                node.declare_function(node.children[1].value, param_list_types, type_name_type, True)
            )
            for var_type, var_name in zip(param_list_types, param_list_names):
                node.children[5].declare_variable(var_name, var_type)

            self._complex_command(node.children[5])

    def _parameter_list(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<deklaracija_parametra>']:
            param_declaration_type, param_declaration_name = self._parameter_declaration(node.children[0])

            return [param_declaration_type], [param_declaration_name]
        elif children_names == ['<lista_parametara>', 'ZAREZ', '<deklaracija_parametra>']:
            param_list_types, param_list_names = self._parameter_list(node.children[0])
            param_declaration_type, param_declaration_name = self._parameter_declaration(node.children[2])

            if param_declaration_name in param_list_names:
                self._terminate(node)

            return param_list_types + [param_declaration_type], param_list_names + [param_declaration_name]

    def _parameter_declaration(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<ime_tipa>', 'IDN']:
            type_name_type = self._type_name(node.children[0])
            if type_name_type == Types.VOID:
                self._terminate(node)

            return type_name_type, node.children[1].value
        elif children_names == ['<ime_tipa>', 'IDN', 'L_UGL_ZAGRADA', 'D_UGL_ZAGRADA']:
            type_name_type = self._type_name(node.children[0])
            if type_name_type == Types.VOID:
                self._terminate(node)

            return Types.to_array(type_name_type), node.children[1].value

    def _declarations_list(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<deklaracija>']:
            self._declaration(node.children[0])
        elif children_names == ['<lista_deklaracija>', '<deklaracija>']:
            self._declarations_list(node.children[0])
            self._declaration(node.children[1])

    def _declaration(self, node: Node):
        if self._get_children_names(node) == ['<ime_tipa>', '<lista_init_deklaratora>', 'TOCKAZAREZ']:
            type_name_type = self._type_name(node.children[0])
            self._init_declarators_list(node.children[1], type_name_type)

    def _init_declarators_list(self, node: Node, ntype: str):
        children_names = self._get_children_names(node)

        if children_names == ['<init_deklarator>']:
            self._init_declarator(node.children[0], ntype)
        elif children_names == ['<lista_init_deklaratora>', 'ZAREZ', '<init_deklarator>']:
            self._init_declarators_list(node.children[0], ntype)
            self._init_declarator(node.children[2], ntype)

    def _init_declarator(self, node: Node, ntype: str):
        children_names = self._get_children_names(node)

        if children_names == ['<izravni_deklarator>']:
            direct_declarator_type, _ = self._direct_declarator(node.children[0], ntype)
            if Types.is_const(direct_declarator_type):
                self._terminate(node)
        elif children_names == ['<izravni_deklarator>', 'OP_PRIDRUZI', '<inicijalizator>']:
            direct_declarator_type, direct_declarator_n = self._direct_declarator(node.children[0], ntype)
            initializer_result = self._initializer(node.children[2])

            if Types.is_array(direct_declarator_type):
                initializer_n, initializer_types_list = initializer_result
                if initializer_n > direct_declarator_n:
                    self._terminate(node)
                for list_type in initializer_types_list:
                    if not Types.is_castable(list_type, Types.get_array_type(direct_declarator_type)):
                        self._terminate(node)
            else:
                initializer_type = initializer_result
                if not Types.is_castable(initializer_type, direct_declarator_type):
                    self._terminate(node)

    def _direct_declarator(self, node: Node, ntype: str):
        children_names = self._get_children_names(node)

        if children_names == ['IDN']:
            if ntype == Types.VOID:
                self._terminate(node)
            if node.get_declaration(node.children[0].value, 1):
                self._terminate(node)

            node.declare_variable(node.children[0].value, ntype)
            return ntype, 0
        elif children_names == ['IDN', 'L_UGL_ZAGRADA', 'BROJ', 'D_UGL_ZAGRADA']:
            if (ntype == Types.VOID
                    or node.get_declaration(node.children[0].value, 1)
                    or int(node.children[2].value) > 1024 or int(node.children[2].value) < 1):
                self._terminate(node)

            node.declare_variable(node.children[0].value, Types.to_array(ntype))
            return Types.to_array(ntype), int(node.children[2].value)

        elif children_names == ['IDN', 'L_ZAGRADA', 'KR_VOID', 'D_ZAGRADA']:
            if declaration := node.get_declaration(node.children[0].value, 1):
                if declaration['return_type'] != ntype or declaration['parameter_types'] != [Types.VOID]:
                    self._terminate(node)
            else:
                self.function_declarations.append(
                    node.declare_function(node.children[0].value, [Types.VOID], ntype)
                )

            return Types.FUNCTION([Types.VOID], ntype)
        elif children_names == ['IDN', 'L_ZAGRADA', '<lista_parametara>', 'D_ZAGRADA']:
            param_list_types, _ = self._parameter_list(node.children[2])

            if declaration := node.get_declaration(node.children[0].value, 1):
                if declaration['return_type'] != ntype or declaration['parameter_types'] != param_list_types:
                    self._terminate(node)
            else:
                self.function_declarations.append(
                    node.declare_function(node.children[0].value, param_list_types, ntype)
                )

            return Types.FUNCTION(param_list_types, ntype)

    def _initializer(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<izraz_pridruzivanja>']:
            working_node = node
            while working_node.children:
                working_node = working_node.children[0]

            result = self._assignment_expression(node.children[0])
            if working_node.name == 'NIZ_ZNAKOVA':
                return len(working_node.value) + 1, [Types.CHAR] * len(working_node.value)
            else:
                return result[0]
        elif children_names == ['L_VIT_ZAGRADA', '<lista_izraza_pridruzivanja>', 'D_VIT_ZAGRADA']:
            return self._assignment_expressions_list(node.children[1])

    def _assignment_expressions_list(self, node: Node):
        children_names = self._get_children_names(node)

        if children_names == ['<izraz_pridruzivanja>']:
            assignment_expression_type, _ = self._assignment_expression(node.children[0])

            return 1, [assignment_expression_type]
        elif children_names == ['<lista_izraza_pridruzivanja>', 'ZAREZ', '<izraz_pridruzivanja>']:
            assignment_expressions_list_n, assignment_expressions_list_types = self._assignment_expressions_list(
                node.children[0])

            assignment_expression_type, _ = self._assignment_expression(node.children[2])
            return assignment_expressions_list_n + 1, assignment_expressions_list_types + [assignment_expression_type]
