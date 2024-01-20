import SemantickiAnalizator
import generative_tree
from Node import Node
from Variable import Variable
from Function import Function
import fileinput
from generative_tree import build_tree
from RecursiveDescent import RecursiveDescent, DescentException
from Node import Node

scope_mem_loc = {"global": []}
level = ["global"]
func_list = {}
ind = [0]
op_join = [False]

def get_children_names(node: Node):
    return list(map(lambda child: child.name, node.children))


def global_write(file, Variable):
    for loc in Variable.mem_loc:
        file.write(f"{loc}\t\tDW %D 0\n")


def find_outer_declaration(node, global_var_node, func_root_node):
    children_names = get_children_names(node)
    if node.name == "<vanjska_deklaracija>":
        if children_names == ["<deklaracija>"]:
            var = Variable()
            var.root_node = node.children[0]
            var.var_global = True
            global_var_node.append(var)
        elif children_names == ["<definicija_funkcije>"]:
            func = Function()
            func.node = node.children[0]
            func_root_node.append(func)
    for n in node.children:
        find_outer_declaration(n, global_var_node, func_root_node)
    return global_var_node, func_root_node


def check_variable_node(node):
    children_names = get_children_names(node)
    if node.name == "<izravni_deklarator>":
        if children_names == ["IDN"] or children_names == [
            "IDN",
            "L_UGL_ZAGRADA",
            "BROJ",
            "D_UGL_ZAGRADA",
        ]:
            return True
    for n in node.children:
        if check_variable_node(n):
            return True
    return False


def define_var(node, var, var_list):
    if node.name == "<specifikator_tipa>":
        var_type = str(node.children[0].value)
        var.var_type = var_type

    elif node.name == "<init_deklarator>":
        new_var = Variable()
        new_var.var_type = var.var_type
        new_var.root_node = node
        var_list.append(new_var)

        # print(new_var.root_node.children[0].children[0].value)
        return var_list

    for n in node.children:
        if n.name.startswith("<"):
            var_list = define_var(n, var, var_list)

    return var_list


def declaration_analysis(node, Variable, file, Function):
    if node.name == "<izravni_deklarator>":
        name = str(node.children[0].value)
        Variable.var_name = name.upper()
        if Function == None:
            tip = "G"
        else:
            func_name = level[0].split("-")[0]
            nivo = level[0].split("-")[1]
            tip = func_list[func_name][0]
        if len(node.children) > 1:
            Variable.list = True
            for i in range(int(node.children[2].value)):
                name = Variable.var_name
                name = name + f"{i}"
                if level[0] == "global":
                    mem_loc = f"{name}{tip}"
                else:
                    mem_loc = f"{name}{tip}_{nivo}"
                Variable.mem_loc.append(mem_loc)
                if level[0] not in scope_mem_loc:
                    scope_mem_loc[level[0]] = [mem_loc]
                else:
                    scope_mem_loc[level[0]].append(mem_loc)
        else:
            name = Variable.var_name
            if level[0] == "global":
                mem_loc = f"{name}{tip}"
            else:
                mem_loc = f"{name}{tip}_{nivo}"
            Variable.mem_loc.append(mem_loc)
            if level[0] not in scope_mem_loc:
                scope_mem_loc[level[0]] = [mem_loc]
            else:
                scope_mem_loc[level[0]].append(mem_loc)
      
    # je li fakat u deklaraciji samo izraz_pridruživanja
    elif node.name == "<inicijalizator>":
        if len(node.children) > 1:
            value = calculate_value(
                node.children[1], Variable, file, Function, index=-1
            )
        else:
            value = calculate_value(
                node.children[0], Variable, file, Function, index=-1
            )
        if not Variable.string_var and not Variable.list:
            mem_loc = Variable.mem_loc[Variable.id]
            pop(file, "R0", Function)
            file.write(f"\t\tSTORE R0, ({mem_loc})\n")
        return Variable

    for n in node.children:
        declaration_analysis(n, Variable, file, Function)
    return Variable


def find_mem_loc_name(file, name, Function):
    func = level[0].split("-")[0]
    nivo = level[0].split("-")[1]

    tip = func_list[func][0]

    for i in range(int(nivo), -1, -1):
        key = f"{func}-{i}"
        
        local_vars = scope_mem_loc[key]

        mem_loc = f"{name}{tip}_{i}"
   
        if mem_loc in local_vars:
            return mem_loc

    for par in Function.params:
        if name in par:
            param = par[name]
            num = param[0]
            if Function.stog !=0:
                num += 4*Function.stog
            num = hex(num).upper()
            num = num[2:]
            if len(num)==1:
                num = f"0{num}"
            mem_loc = f"R7+{num}"
            return mem_loc
    mem_loc = f"{name}G"
    local_vars = scope_mem_loc["global"]
    if mem_loc in local_vars:
        return mem_loc
    return None


def push(file, r, Function):
    if Function != None:
        Function.stog += 1
    file.write(f"\t\tPUSH {r}\n")


def pop(file, r, Function):
    if Function != None:
        Function.stog -= 1
    file.write(f"\t\tPOP {r}\n")


def calculate_value(node, Variable, file, Function, index):
    # problematika s onim "abc" varijablama

    value = 0
    ne_push = 0
    if (
        node.name == "<lista_izraza_pridruzivanja>"
        or node.name == "<izraz>"
        or node.name == "<lista_argumenata>"
    ):
        for n in node.children:
            value = calculate_value(n, Variable, file, Function, index)
          
           
    elif node.name == "<izraz_pridruzivanja>":

        if len(node.children) > 1:

            value = calculate_value(node.children[2], Variable, file, Function , index)
            pop(file, "R0", Function)
            op_join[0] = True
            value = calculate_value(node.children[0], Variable, file, Function, index)
            op_join[0] = False
        elif Variable != None:
                value = calculate_value(node.children[0], Variable, file, Function, index)
                mem_loc = Variable.mem_loc[Variable.id]
                if Variable.list == True:
                    Variable.id += 1
                    pop(file, "R0", Function)
                    file.write(f"\t\tSTORE R0, ({mem_loc})\n")
        else:
            value = calculate_value(node.children[0], Variable, file, Function, index)

    elif node.name == "<postfiks_izraz>":
        if len(node.children) == 2:
            
            value = calculate_value(node.children[0], Variable, file, Function, index)
       
            name = value.upper()
            mem_loc = find_mem_loc_name(file, name, Function)
            pop(file, "R0", Function)
            if node.children[1].name == "OP_INC":
                push(file, "R0", Function)
                file.write("\t\tADD R0, 1, R0\n")
                file.write(f"\t\tSTORE R0, ({mem_loc})\n")
            elif node.children[1].name == "OP_DEC":
                Function.stog += 1
                push(file, "R0", Function)
                file.write("\t\tSUB R0, 1, R0\n")
                file.write(f"\t\tSTORE R0, ({mem_loc})\n")
        elif len(node.children) > 2:
          
            if node.children[1].name == "L_ZAGRADA":
            
                value = calculate_value(
                    node.children[0].children[0], Variable, file, Function, index
                )
           
                name = f"F_{value.upper()}"
                called_func = func_list[name][1]
                if len(node.children) > 3:
                    # argumenti
                    value = calculate_value(
                        node.children[2], Variable, file, Function, index
                    )
               
                file.write(f"\t\tCALL {name}\n")
                if called_func.mem_loc != "F_MAIN":
                    if len(called_func.params)!=0:
                        reset_stack = 0
                        reset_stack = list(called_func.params[-1].values())[0][0]
                        # for par in called_func.params:
                        #     reset_stack +=list(par.values())[0][0]
                        file.write(f"\t\tADD R7,{reset_stack},R7\n")
                        Function.stog -= len(called_func.params)
                push(file,"R6",Function)
            elif node.children[1].name == "L_UGL_ZAGRADA":
                index = 2
                value = calculate_value(
                    node.children[0].children[0], Variable, file, Function, index
                )
                name = value.upper()
                value = calculate_value(
                    node.children[2], Variable, file, Function, index
                )
                name = name + f"{value}"
                mem_loc = find_mem_loc_name(file, name, Function)
                if op_join[0]:
                    file.write(f"\t\tSTORE R0, ({mem_loc})\n")
                else:
                    file.write(f"\t\tLOAD R0, ({mem_loc})\n")
                    push(file,"R0",Function)

        else:
           
            value = calculate_value(node.children[0], Variable, file, Function, index)
            children_names = get_children_names(node.children[0])
            if children_names == ["IDN"]:
                name = value.upper()
                
             
                mem_loc = find_mem_loc_name(file, name, Function)
                if not op_join[0]:
                    file.write(f"\t\tLOAD R0, ({mem_loc})\n")
                    if index != 4:
                        push(file, "R0", Function)
                else:
                    file.write(f"\t\tSTORE R0, ({mem_loc})\n")

            elif children_names == ["BROJ"]:
                if index != 2:
                    file.write(f"\t\tMOVE %D {value}, R0\n")
                    push(file, "R0", Function)
                else:
                    index = 0
            elif children_names==["ZNAK"]:
                if index != 2:
                    file.write(f"\t\tMOVE %D {value}, R0\n")
                    push(file, "R0", Function)
                else:
                    index = 0

    elif node.name == "<primarni_izraz>":
        children_names = get_children_names(node)
        value = node.children[0].value
        if children_names == ["IDN"]:
            value = value
        elif children_names == ["BROJ"]:
            value = value
        elif children_names == ["ZNAK"]:
            value = ord(value)
        elif children_names == ["NIZ_ZNAKOVA"]:
            Variable.string_var = True
            for char in value:
                value = ord(char)
                file.write(f"\t\tMOVE %D {value}, R0\n")
                push(file, "R0", Function)
                pop(file, "R0", Function)
                file.write(f"\t\tSTORE R0, ({Variable.mem_loc[Variable.id]})\n")
                Variable.id += 1
        else:
            value = calculate_value(node.children[1], Variable, file, Function, index)

    elif len(node.children) > 1:
        if len(node.children) > 2:
            if node.name == "<log_i_izraz>":
                ne_push = 1
                value = calculate_value(
                    node.children[0], Variable, file, Function, index
                )
                pop(file, "R0", Function)
                file.write("\t\tCMP R0, 0\n")
                file.write(f"\t\tJP_NE NO1_{ind[0]}\n")
                file.write("\t\tMOVE 0, R0\n")
                file.write(f"\t\tJP NEXT_{ind[0]}\n")
             
                value = calculate_value(
                    node.children[2], Variable, file, Function, index
                )
                
                file.write(f"NO1_{ind[0]}\n")
                pop(file, "R0", Function)
                file.write("\t\tCMP R0, 0\n")
                file.write(f"\t\tJP_NE NO2_{ind[0]}\n")
                file.write("\t\tMOVE 0, R0\n")
                file.write(f"\t\tJP NEXT_{ind[0]}\n")
                file.write(f"NO2_{ind[0]}\t\tMOVE 1, R0\n")
                file.write(f"NEXT_{ind[0]}\n")
                ind[0] += 1
               
            elif node.name == "<log_ili_izraz>":
                ne_push = 1
                value = calculate_value(
                    node.children[0], Variable, file, Function, index
                )
                pop(file, "R0", Function)
                file.write("\t\tCMP R0, 0\n")
                file.write(f"\t\tJP_EQ NO1_{ind[0]}\n")
                file.write("\t\tMOVE 1, R0\n")
                file.write(f"\t\tJP NEXT_{ind[0]}\n")
            
                value = calculate_value(
                    node.children[2], Variable, file, Function, index
                )
               
                file.write(f"NO1_{ind[0]}")
                pop(file, "R0", Function)
                file.write("\t\tCMP R0, 0\n")
                file.write(f"\t\tJP_EQ NO2_{ind[0]}\n")
                file.write("\t\tMOVE 1, R0\n")
                file.write(f"\t\tJP NEXT_{ind[0]}\n")
                file.write(f"NO2_{ind[0]}\t\tMOVE 0, R0\n")
                file.write(f"NEXT_{ind[0]}\n")
                ind[0] += 1
              
            else:
                value = calculate_value(
                    node.children[0], Variable, file, Function, index
                )

                value = calculate_value(
                    node.children[2], Variable, file, Function, index
                )
                pop(file, "R1", Function)
                pop(file, "R0", Function)
                if node.name == "<bin_ili_izraz>":
                    file.write("\t\tOR R0, R1, R0\n")
                elif node.name == "<bin_i_izraz>":
                    file.write("\t\tAND R0, R1, R0\n")
                elif node.name == "<bin_xili_izraz>":
                    file.write("\t\tXOR R0, R1, R0\n")

                elif node.name == "<jednakosni_izraz>":
                    if node.children[1].name == "OP_EQ":
                        file.write("\t\tCMP R0, R1\n")
                        file.write(f"\t\tJP_NE NO_{ind[0]}\n")
                        file.write("\t\tMOVE 1, R0\n")
                        file.write(f"\t\tJP NEXT_{ind[0]}\n")
                        file.write(f"NO_{ind[0]}\t\tMOVE 0, R0\n")
                        file.write(f"NEXT_{ind[0]}\n")
                        ind[0] += 1
                    elif node.children[1].name == "OP_NEQ":
                        file.write("\t\tCMP R0, R1\n")
                        file.write(f"\t\tJP_NE NO_{ind[0]}\n")
                        file.write("\t\tMOVE 0, R0\n")
                        file.write(f"\t\tJP NEXT_{ind[0]}\n")
                        file.write(f"NO_{ind[0]}\t\tMOVE 1, R0\n")
                        file.write(f"NEXT_{ind[0]}\n")
                        ind[0] += 1
                elif node.name == "<odnosni_izraz>":
                    if node.children[1].name == "OP_LT":
                        file.write("\t\tCMP R0, R1\n")
                        file.write(f"\t\tJP_SLT NO_{ind[0]}\n")
                        file.write("\t\tMOVE 0, R0\n")
                        file.write(f"\t\tJP NEXT_{ind[0]}\n")
                        file.write(f"NO_{ind[0]}\t\tMOVE 1, R0\n")
                        file.write(f"NEXT_{ind[0]}\n")
                        ind[0] += 1
                    elif node.children[1].name == "OP_GT":
                        file.write("\t\tCMP R0, R1\n")
                        file.write(f"\t\tJP_SGT NO_{ind[0]}\n")
                        file.write("\t\tMOVE 0, R0\n")
                        file.write(f"\t\tJP NEXT_{ind[0]}\n")
                        file.write(f"NO_{ind[0]}\t\tMOVE 1, R0\n")
                        file.write(f"NEXT_{ind[0]}\n")
                        ind[0] += 1
                    elif node.children[1].name == "OP_LTE":
                        file.write("\t\tCMP R0, R1\n")
                        file.write(f"\t\tJP_SLE NO_{ind[0]}\n")
                        file.write("\t\tMOVE 0, R0\n")
                        file.write(f"\t\tJP NEXT_{ind[0]}\n")
                        file.write(f"NO_{ind[0]}\t\tMOVE 1, R0\n")
                        file.write(f"NEXT_{ind[0]}\n")
                        ind[0] += 1
                    elif node.children[1].name == "OP_GTE":
                        file.write("\t\tCMP R0, R1\n")
                        file.write(f"\t\tJP_SGE NO_{ind[0]}\n")
                        file.write(f"\t\tMOVE 0, R0\n")
                        file.write(f"\t\tJP NEXT_{ind[0]}\n")
                        file.write(f"NO_{ind[0]}\t\tMOVE 1, R0\n")
                        file.write(f"NEXT_{ind[0]}\n")
                        ind[0] += 1
                elif node.name == "<aditivni_izraz>":
                    if node.children[1].name == "PLUS":
                        file.write("\t\tADD R0, R1, R0\n")
                    elif node.children[1].name == "MINUS":
                        file.write("\t\tSUB R0, R1, R0\n")

                elif node.name == "<multiplikativni_izraz>":
                    if node.children[1].name == "OP_PUTA":
                        file.write("\t\tMOVE 2, R4\n")
                        file.write("\t\tCMP R0, 0\n")
                        file.write(f"\t\tJP_SGE OTHER_{ind[0]}\n")
                        file.write("\t\tSUB R4, 1, R4\n")
                        file.write("\t\tMOVE 0FFFFFFFF, R2\n")
                        file.write("\t\tSUB R2, R0, R0\n")
                        file.write("\t\tADD R0, 1, R0\n")
                        file.write(f"OTHER_{ind[0]}\t\tCMP R1, 0\n")
                        file.write(f"\t\tJP_SGE YES_{ind[0]}\n")
                        file.write("\t\tSUB R4, 1, R4\n")
                        file.write("\t\tMOVE 0FFFFFFFF, R2\n")
                        file.write("\t\tSUB R2, R1, R1\n")
                        file.write("\t\tADD R1, 1, R1\n")

                        file.write(f"YES_{ind[0]}\t\tMOVE R0, R3\n")
                        file.write(f"RE_{ind[0]}\t\tCMP R1,1\n")
                        file.write(f"\t\tJP_SLE NEXT_{ind[0]}\n")
                        file.write("\t\tADD R0, R3, R0\n")
                        file.write("\t\tSUB R1, 1, R1\n")
                        file.write(f"\t\tJP RE_{ind[0]}\n")
                        file.write(f"NEXT_{ind[0]}\t\tCMP R4, 1\n")
                        file.write(f"\t\tJP_NE DONE_{ind[0]}\n")
                        file.write("\t\tMOVE 0FFFFFFFF, R2\n")
                        file.write("\t\tSUB R2, R0, R0\n")
                        file.write("\t\tADD R0, 1, R0\n")
                        file.write(f"DONE_{ind[0]}\n")
                        ind[0] += 1
                    elif node.children[1].name == "OP_DIJELI":
                        file.write("\t\tMOVE 2, R4\n")
                        file.write("\t\tCMP R1, 0\n")
                        file.write(f"\t\tJP_SGE OTHER_{ind[0]}\n")
                        file.write("\t\tSUB R4, 1, R4\n")
                        file.write("\t\tMOVE 0FFFFFFFF, R2\n")
                        file.write("\t\tSUB R2, R1, R1\n")
                        file.write("\t\tADD R1, 1, R1\n")
                        file.write(f"OTHER_{ind[0]}\t\tCMP R0, 0\n")
                        file.write(f"\t\tJP_SGE YES_{ind[0]}\n")
                        file.write("\t\tSUB R4, 1, R4\n")
                        file.write("\t\tMOVE 0FFFFFFFF, R2\n")
                        file.write("\t\tSUB R2, R0, R1\n")
                        file.write("\t\tADD R0, 1, R0\n")

                        file.write(f"YES_{ind[0]}\t\tMOVE R0, R3\n")
                        file.write("\t\tMOVE 0, R0\n")
                        file.write(f"RE_{ind[0]}\t\tCMP R3, R1\n")
                        file.write(f"\t\tJP_SLT NEXT_{ind[0]}\n")
                        file.write("\t\tADD R0, 1, R0\n")
                        file.write("\t\tSUB R3, R1, R3\n")
                        file.write(f"\t\tJP RE_{ind[0]}\n")

                        file.write(f"NEXT_{ind[0]}\t\tCMP R4, 1\n")
                        file.write(f"\t\tJP_NE DONE_{ind[0]}\n")
                        file.write("\t\tMOVE 0FFFFFFFF, R2\n")
                        file.write("\t\tSUB R2, R0, R0\n")
                        file.write("\t\tADD R0, 1, R0\n")

                        file.write(f"DONE_{ind[0]}\n")

                        ind[0] += 1
                    elif node.children[1].name == "OP_MOD":
                        file.write("\t\tMOVE R0, R3\n")
                        file.write("\t\tMOVE 0, R0\n")
                        file.write("\t\tCMP R3,0\n")
                        file.write(f"\t\tJP_NE YES_{ind[0]}\n")
                        file.write("\t\tMOVE R1, R0\n")
                        file.write(f"\t\tJP NEXT_{ind[0]}\n")
                        file.write(f"YES_{ind[0]}\t\tCMP R3,R1\n")
                        file.write(f"\t\tJP_SLT NEXT_{ind[0]}\n")
                        file.write("\t\tADD R0, 1, R0\n")
                        file.write("\t\tSUB R3, R1, R3\n")
                        file.write(f"\t\tJP YES_{ind[0]}\n")
                        file.write(f"NEXT_{ind[0]}\n")
                        file.write("\t\tMOVE R3, R0\n")

                        ind[0] += 1

        else:
            if node.name == "<unarni_izraz>":
                value = calculate_value(
                    node.children[1], Variable, file, Function, index
                )
                name = value.upper()
                mem_loc = find_mem_loc_name(file, name, Function)
                pop(file, "R0", Function)
                if node.children[0].name == "OP_INC":
                    file.write("\t\tADD R0, 1, R0\n")
                    file.write(f"\t\tSTORE R0, ({mem_loc})\n")
                elif node.children[0].name == "OP_DEC":
                    file.write("\t\tSUB R0, 1, R0\n")
                    file.write(f"\t\tSTORE R0, ({mem_loc})\n")
                else:
                    unarni_op = node.children[0].children[0].name
                    if unarni_op == "MINUS":
                        file.write("\t\tMOVE 0FFFFFFFF, R2\n")
                        file.write("\t\tSUB R2, R0, R0\n")
                        file.write("\t\tADD R0, 1, R0\n")
                    # elif unarni_op == "PLUS":
                    #     pass
                    elif unarni_op == "OP_TILDA":
                        file.write("\t\tMOVE 0, R1\n")
                        file.write("\t\tSUB R1, 1, R1\n")
                        file.write("\t\tSUB R1, R0, R0\n")
                    elif unarni_op == "OP_NEG":
                        file.write("\t\tCMP R0, 0\n")
                        file.write(f"\t\tJP_NE NEG_{ind[0]}\n")
                        file.write(f"\t\tMOVE 1, R0\n")
                        file.write(f"\t\tJP NEXT_{ind[0]}\n")
                        file.write(f"NEG_{ind[0]}\t\tMOVE 0, R0\n")
                        file.write(f"NEXT_{ind[0]}\n")
                        ind[0] += 1
        if not ne_push:
            push(file, "R0", Function)

    elif len(node.children)!=0:
        value = calculate_value(node.children[0], Variable, file, Function, index)
    return value

def find_func_params(Function, node):
    # 0 = int/char, 1=array, len(Function.params) = num_of_params
    
    if node.name == "<deklaracija_parametra>":
        ime_para = node.children[1].value.upper()
        print(ime_para)
        
        if len(node.children) > 3:
           
            Function.params.append({ime_para:(0,1)})
        else:
      
            Function.params.append({ime_para:(0,0)})
        return
    elif node.name == "<lista_parametara>":
        for n in node.children:
            find_func_params(Function, n)
    return Function


def define_func(Function):
    node = Function.node
    name = node.children[1].value.upper()
    Function.mem_loc = f"F_{name}"
    values = list(func_list.values())
    if len(values) == 0:
        value = 0
    else:
        value = values[-1][0] + 1
    if node.children[3].name == "<lista_parametara>":
        Function = find_func_params(Function, node.children[3])
        stack_num = 4* len(Function.params)
        for par in Function.params:
            key = list(par.keys())[0]
            num = list(par.values())[0][1]
            par[key] = (stack_num,num)
            stack_num -= 4
        if len(Function.params)==0:
            stack_num = 4
        else:
            stack_num = list(Function.params[-1].values())[0][0]+4
    func_list.update({Function.mem_loc: (value,Function)})
  
    return Function


def block_analysis(file, node, Function, var_list, con_br):
   
    if (
        node.name == "<lista_naredbi>"
        or node.name == "<lista_deklaracija>"
        or node.name == "<slozena_naredba>"
    ):
        for n in node.children:
            block_analysis(file, n, Function, var_list,con_br)
    elif node.name == "<deklaracija>":
        if check_variable_node(node):
            var = Variable()
            var.root_node = node
            vars = define_var(var.root_node, var, [])
            for var in vars:
                var_list.append(
                    declaration_analysis(var.root_node, var, file, Function)
                )

    elif node.name == "<naredba>":
        if node.children[0].name == "<slozena_naredba>":
            value = int(level[0].split("-")[1])
            level[0] = f"{Function.mem_loc}-{value+1}"
            scope_mem_loc.update({level[0]: []})
            var_list = block_analysis(file, node.children[0], Function, var_list, con_br)
        elif node.children[0].name == "<izraz_naredba>":
            # neke spike s for petljom
            # ovdje je <izraz> koji vodi do <izraz_pridruzivanja>
            temp_node = node.children[0]
            if len(temp_node.children)>1:
                value = calculate_value(
                    temp_node.children[0],
                    Variable=None,
                    file=file,
                    Function=Function,
                    index=0,
                )

        elif node.children[0].name == "<naredba_grananja>":
            temp_node = node.children[0]
            value = calculate_value(temp_node.children[2],Variable = None,file=file,Function=Function,index=-1)
            pop(file,"R0",Function)
            file.write("\t\tCMP R0, 0\n")
            if len(temp_node.children) > 5:
                file.write(f"\t\tJP_EQ ELSE_{ind[0]}\n")
                before = Function.stog
                var_list = block_analysis(file, temp_node.children[4], Function, var_list,con_br)
                file.write(f"\t\tJP NEXT_{ind[0]}\n")
                file.write(f"ELSE_{ind[0]}\n")
                Function.stog = before
                var_list = block_analysis(file, temp_node.children[6], Function,  var_list,con_br)
                file.write(f"NEXT_{ind[0]}\n")
                Function.stog = before
            else:
                file.write(f"\t\tJP_EQ NEXT_{ind[0]}\n")
                var_list = block_analysis(file, temp_node.children[4], Function, var_list,con_br)
                file.write(f"NEXT_{ind[0]}\n")
            ind[0]+=1
        elif node.children[0].name == "<naredba_petlje>":
            temp_node = node.children[0]
            if temp_node.children[0].name == "KR_WHILE":
                con_br = (f"CHECK_{ind[0]}",f"NEXT_{ind[0]}")
                file.write(f"CHECK_{ind[0]}\n")
                value = calculate_value(temp_node.children[2],Variable=None, file=file,Function=Function, index=-1)
                pop(file, "R0", Function)
                file.write("\t\tCMP R0, 0\n")
                file.write(f"\t\tJP_EQ NEXT_{ind[0]}\n")
                var_list = block_analysis(file, Function, var_list, con_br)
                file.write(f"\t\tJP CHECK_{ind[0]}\n")
                file.write(f"NEXT_{ind[0]}\n")
                ind[0]+=1
            else:
                
                izraz1 = temp_node.children[2]
                izraz2 = temp_node.children[3]
                naredba = temp_node.children[5]
                con_br = (f"LOOP_{ind[0]}",f"NEXT_{ind[0]}")
                ind[0]+=1
                if len(izraz1.children)>1:
                    value = calculate_value(izraz1.children[0],Variable=None, file=file, Function=Function, index = 4)
                file.write(f"{con_br[0]}\n")
                if len(izraz2.children)>1:
                    value = calculate_value(izraz2.children[0],Variable=None, file=file, Function=Function, index = -1)
                    pop(file, "R0", Function)
                    file.write("\t\tCMP R0, 0\n")
                    file.write(f"\t\tJP_EQ {con_br[1]}\n")
                if len(temp_node.children) > 6:
                    izraz3 = temp_node.children[4]
                    naredba = temp_node.children[6]
                    var_list = block_analysis(file,naredba,Function,var_list,con_br)
                    value = calculate_value(izraz3.children[0],Variable=None, file=file, Function=Function, index = -1)
                    file.write(f"\t\tPOP R0\n")
                else:
                    var_list = block_analysis(file,naredba,Function,var_list,con_br)
                file.write(f"\t\tJP {con_br[0]}\n")
                file.write(f"{con_br[1]}\n")



        elif node.children[0].name == "<naredba_skoka>":
            temp_node = node.children[0]

            if temp_node.children[0].name == "KR_RETURN":
                # skidanje lokalnih varijabli sa stoga
                if len(temp_node.children) > 2:
                   
                    value = calculate_value(
                        temp_node.children[1], None, file, Function, index=0
                    )
                 
                 
              
                    pop(file,"R6",Function)
                    if Function.stog > 0:
                        
                        for i in range(Function.stog):
                            pop(file, "R0", Function)
                
                file.write("\t\tRET\n")

            elif temp_node.children[0].name == "KR_CONTINUE":
                file.write(f"\t\tJP {con_br[0]}")
            elif temp_node.children[0].name == "KR_BREAK":
                file.write(f"\t\tJP {con_br[1]}")

    return var_list


def func_analysis(file, node, Function, var_list):
    file.write(f"{Function.mem_loc}\n")
    if node.name == "<slozena_naredba>":
        
        level[0] = f"{Function.mem_loc}-0"
        scope_mem_loc.update({level[0]: []})
        con_br = (None,None)
        var_list = block_analysis(file, node, Function, var_list, con_br)

    return var_list


def generate_code(file, node):
    
    global_var = list(
        filter(lambda x: x["kind"] == "variable", node.scope.declarations)
    )
    functions = list(filter(lambda x: x["kind"] == "function", node.scope.declarations))
    # moramo proći kroz cijeli niz generiranog stabla i zapamtiti najbitnije stvari za generiranje koda
    # 1. find[0] global varijables and functions->nodes of their beginning to be able to analize inside
    global_var_node, func_root_nodes = find_outer_declaration(node, [], [])
    # od ovih node-ova dalje treba tražiti vrijednosti globalnih varijabli koji se nalaze putem deklaracija->onda provjera da se ne radi o deklaraciji funkcije
    # a za funkcije je druga prica jer treba iz analizirati, ali barem znas od kojih node-ova krenuti

    # ovdje naci type =     declaration_var_type = find[0]_var_type(node,"")

    global_var_node = [n for n in global_var_node if check_variable_node(n.root_node)]

    global_vars = []
    for var in global_var_node:
        vars = define_var(var.root_node, var, [])
        global_vars.extend(vars)
    func_root_nodes = [define_func(func) for func in func_root_nodes]
    # for i in func_root_nodes:
    #     print(i.mem_loc)
    global_var_node_new = []
    #     print(i.params)

    # if Function == None : global smo
    file.write("\t\tMOVE 40000, R7\n")
    for var in global_vars:
        new_var = declaration_analysis(var.root_node, var, file, None)
        global_var_node_new.append(new_var)
    file.write("\t\tCALL F_MAIN\n")
    file.write("\t\tHALT\n")
    for func in func_root_nodes:
        node = func.node.children[5]
        global_var_node_new = func_analysis(file, node, func, global_var_node_new)
 
    for var in global_var_node_new:
        global_write(file, var)
    # ovdje idu sve funkcije
    # Ovdje napiši globalne varijable na kraju

    # ===> ideja je da se izračuna taj izraz za globalnu varijablu ovdje i da se onda zapiše kao DW u .frisc datoteci

    # izravni deklarator = IDN/ IDN L_UGL_Zagrada BROJ D_UGL_ZAGRADA
    # Kako dobiti vrijednosti varijabli bilo globalnih ili lokalnih?
    # status quo : R6 povratni registar, R7 stog -> inicijaliziran na 4000, lokalne varijable na stogu
    # na stogu računati izraze, parametre funkcija stavljati na stog,
    # inače krećemo od R0 sve ostale stvari
    # potrebno je raditi pred analizu generativnog stabla
    # Što se sve treba provjeravati?
    # koje funckije postoje?
    # koliko ima globalnih varijabli?
    # itd
    return


if __name__ == "__main__":
    

    lines = []

    for line in fileinput.input():
        lines.append(line)

    tree = build_tree(lines)
    recursive_descent = RecursiveDescent(tree)

    recursive_descent.descend()
    frisc = open("a.frisc", "w")
    generate_code(frisc, tree)
    frisc.close()


