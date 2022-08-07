import re
import numpy as np

#Le da un correcto formato en forma de lista a los numeros en binario dependiendo del numero de variables
def format_bin(num, var):
    num_bin = list(bin(num))
    num_bin.pop(0)
    num_bin.pop(0)
    if len(num_bin) < var:
        fill = var-len(num_bin)
        for z in range(fill):
            num_bin.insert(0,'0')
    return num_bin

#Crea la tabla con los numeros binarios
def createTable (var, terms):
    table = []
    for f in range(2**var):
        ter = format_bin(f, var)
        table.append(ter)

    if terms is not None:
        for min in terms[0]:
            table[min].append('1')

        for max in terms[1]:
            table[max].append('0')

        for d in terms[2]:
            table[d].append('X')

    return table

#cuenta cuantas variables hay en la funcion
def detectVar(func):
    var = 0
    list_var = []
    for i in func:
        if ((ord(i) >= 97 and ord(i) <= 122) or (ord(i) >= 65 and ord(i) <= 90)) and i not in list_var:
            var += 1
            list_var.append(i)
    list_var.sort()

    return var, list_var

#Le da un formato correcto a la funcion antes de evaluar
def addecuateFunc(func):
    and_patt = r'\w{2,}'
    not_patt = r'¬\w'

    if len(func) == 1:
        return func

    search_not = re.findall(not_patt, func)
    set_search_not = list(set(search_not))
    set_search_not.sort()
    tempFunc = func

    if len(set_search_not) > 0:
        deleting_repeats = True
        s = 0
        while deleting_repeats:
            not_term = set_search_not[s]
            if search_not.count(not_term) > 1:
                edit_bit = f"({not_term})"
                tempFunc = re.sub(not_term, edit_bit, tempFunc)
                set_search_not.remove(not_term)

            else:
                s += 1

            if s == len(set_search_not) or len(set_search_not) == 0:
                deleting_repeats = False

        for j in set_search_not:
            edit_bit = f"({j})"
            tempFunc = re.sub(j, edit_bit, tempFunc)

    search_and = re.findall(and_patt, tempFunc)
    set_search_and = list(set(search_and))
    set_search_and.sort()

    if len(set_search_and) > 0:
        deleting_repeats = True
        s = 0
        while deleting_repeats:
            try:
                and_term = set_search_and[s]
                if search_and.count(and_term) > 1:
                    edit_bit = f"({and_term})"
                    tempFunc = re.sub(and_term, edit_bit, tempFunc)
                    set_search_and.remove(and_term)

                else:
                    s += 1

                if s == len(set_search_and) or len(set_search_and) == 0:
                    deleting_repeats = False
            except IndexError:
                print(f"indice erroneo: {s}")
                print(len(set_search_and))
                break

        for i in set_search_and:
            edit_bit = f"({i})"
            tempFunc = re.sub(i, edit_bit, tempFunc)

    newFunc = list(tempFunc)

    i=0
    active = True
    while active:
        is_letter_i = (ord(newFunc[i]) >= 97 and ord(newFunc[i]) <= 122) or (ord(newFunc[i]) >= 65 and ord(newFunc[i]) <= 90)
        is_letter_next = ((ord(newFunc[i+1]) >= 97 and ord(newFunc[i+1]) <= 122) or (ord(newFunc[i+1]) >= 65 and ord(newFunc[i+1]) <= 90))
        is_parentesis_open = ord(newFunc[i+1]) == 40
        is_parentesis_close = ord(newFunc[i]) == 41
        if (is_letter_i and is_letter_next) or (is_letter_i and is_parentesis_open) or (is_parentesis_close and is_letter_next) or (is_parentesis_close and is_parentesis_open):
            newFunc.insert(i+1, '*')
            i += 1
        else:
            i += 1

        if i >= len(newFunc)-1:
            active = False

    newFunc = ' '.join(newFunc)
    newFunc = newFunc.replace('+', 'or')
    newFunc = newFunc.replace('*', 'and')
    newFunc = newFunc.replace('¬', 'not')
    newFunc = newFunc.replace('⊕', '^')

    return newFunc

#Evalua la funcion en la tabla
def evalFunc(func_exe, list, table):
    inter_index = 0
    func_eval = func_exe
    forbidden_letters = ['a','n','d','o','r','t']
    is_forbidden = False
    for num in range(len(table)):
        for j in table[num]:
            if list[inter_index] in forbidden_letters:
                is_forbidden = True
                func_eval = func_eval.replace('and', '*')
                func_eval = func_eval.replace('or', '+')
                func_eval = func_eval.replace('not', '¬')
            else:
                is_forbidden = False

            if j == '0':

                func_eval = func_eval.replace(list[inter_index], '0')
                inter_index += 1

            else:

                func_eval = func_eval.replace(list[inter_index], '1')
                inter_index += 1

            if is_forbidden:
                func_eval = func_eval.replace('*', 'and')
                func_eval = func_eval.replace('+', 'or')
                func_eval = func_eval.replace('¬', 'not')

        res = eval(func_eval)

        if res :
            table[num].append('1')
        else:
            table[num].append('0')

        func_eval = func_exe
        inter_index = 0

    return table

#Agrupa minterminos y maxterminos
def minter_maxter(table_res, var):
    cont_dec = 0
    maxterms = []
    minterms = []
    dont_care = []
    for i in table_res:
        if i[var] == '0':
            maxterms.append(cont_dec)
        elif i[var] == '1':
            minterms.append(cont_dec)
        else:
            dont_care.append(cont_dec)
        cont_dec += 1

    return minterms, maxterms, dont_care

#Agrega terminos dont_care a minterminos o maxterminos
def dont_care(terms , min_or_max):
    if len(terms[2]) > 0:
        for i in terms[2]:
            terms[min_or_max].append(i)
        terms[min_or_max].sort()
        return terms
    else:
        return terms

#Simplifica funciones con el metodo de quine-mckluskey
#QM_tables hace la primera parte del metodo, que es hacer la tabla de implicantes
def QM_tables(terms, min_or_max, var):
    implicants = {}

    for t in terms[min_or_max]:
        num_bin = format_bin(t, var)
        ones_key = num_bin.count('1')
        implicants[f"{ones_key}"] = {}

    for i in terms[min_or_max]:
        num_bin = format_bin(i, var)
        ones = num_bin.count('1')
        implicants[f"{ones}"][i] = [tuple(num_bin), False]

    groups = list(implicants.keys())
    if len(groups) == 1:
        return implicants
    else:

        making_tables = True
        groups_index = 0
        num_dif = 1
        while making_tables:
            groups = list(implicants.keys())
            current_group = groups[groups_index]
            next_group = groups[groups_index+1]
            if len(next_group) > num_dif:
                if groups_index + 1 < len(groups) - 1:
                    groups_index += 1
                current_group = groups[groups_index]
                next_group = groups[groups_index + 1]
                num_dif += 1


            new_group = list(set(list(f"{current_group}{next_group}")))
            new_group.sort()
            new_group = ''.join(new_group)

            implicants[new_group] = {}
            for i in implicants[f"{current_group}"].keys():
                for j in implicants[f"{next_group}"].keys():
                    cont_dif = 0
                    for d in range(var):

                        try:
                            if implicants[f"{current_group}"][i][0][d] != implicants[f"{next_group}"][j][0][d]:
                                cont_dif += 1
                                index = d

                            if cont_dif > 1:
                                index = None
                                break
                        except TypeError:
                            print(f"Error: Indices = i: {i}, j: {j}, tup_index: {0}, d: {d}")
                            print(implicants[f"{current_group}"][i])
                            print(implicants[f"{next_group}"][j])


                    if index is not None:

                        new_imp = list(implicants[f"{current_group}"][i][0])
                        new_imp[index] = '_'
                        if type(i) == int and type(i) == int:
                            new_key = (i,j)
                            implicants[f"{current_group}"][i][1] = True
                            implicants[f"{next_group}"][j][1] = True
                            implicants[new_group][new_key] = [tuple(new_imp), False]
                        else:
                            new_key = list(i+j)
                            new_key.sort()
                            new_key = tuple(new_key)
                            implicants[f"{current_group}"][i][1] = True
                            implicants[f"{next_group}"][j][1] = True
                            if new_key not in implicants[new_group].keys():
                                implicants[new_group][new_key] = [tuple(new_imp), False]

            groups_index += 1

            if groups_index > len(groups)-2:
                making_tables = False

        return implicants

#Es la segunda parte del metodo Quine-Mckluskey
#QM_imp_res hace la tabla de primos implicantes, y determina cuales de ellos son esenciales
#Devuelve un string con la funcion simplificada de primos esenciales
def QM_imp_res(imp_tab, min_or_max, terms, list_var, var):
    primes = [[], []]

    if len(imp_tab) == 1:
        list_terms = []
        if len(list_var) == 0:
            for v in range(var):
                list_var.append(chr(97 + v))

        group_key = list(imp_tab.keys())[0]
        term_key = list(imp_tab[group_key].keys())

        for g in term_key:

            terms = list(imp_tab[group_key][g][0])
            index_term = 0
            for t in terms:
                if min_or_max == 0:
                    if t == '1':
                        terms[index_term] = f"{list_var[index_term]}"
                    else:
                        terms[index_term] = f"¬{list_var[index_term]}"
                else:
                    if t == '1':
                        terms[index_term] = f"¬{list_var[index_term]}"
                    else:
                        terms[index_term] = f"{list_var[index_term]}"
                index_term +=1
            if min_or_max == 0:
                alg_term = ''.join(terms)
                list_terms.append(alg_term)

            else:
                alg_term = '+'.join(terms)
                list_terms.append(f"({alg_term})")
        if min_or_max == 0:
            sim_func = '+'.join(list_terms)
            return sim_func, list_var
        else:
            sim_func= ''.join(terms)
            return sim_func, list_var


    for p in imp_tab.items():
        for i in p[1].items():
            if i[1][1] == False:
                primes[0].append(i)

    for j in range(len(primes[0])):
        primes[1].append([])

        for t in terms[min_or_max]:
            if type(primes[0][j][0]) == tuple:
                if t in primes[0][j][0]:
                    primes[1][j].append('x')
                else:
                    primes[1][j].append(' ')
            else:
                if t == primes[0][j][0]:
                    primes[1][j].append('x')
                else:
                    primes[1][j].append(' ')

    primes[1] = np.array(primes[1])
    primes[1] = primes[1].T

    essentials = []
    used_terms = ()
    for e in primes[1]:
        if 'x' in e:
            marks, prime_index, counts = np.unique(e, return_index=True, return_counts=True)
            if len(marks) > 1:
                if counts[1] == 1 and primes[0][prime_index[1]] not in essentials:
                    essentials.append(primes[0][prime_index[1]])
                    if type(primes[0][prime_index[1]][0]) == tuple:
                        used_terms += primes[0][prime_index[1]][0]
                    else:
                        used_sigle_term = (primes[0][prime_index[1]][0],)
                        used_terms += used_sigle_term


    used_terms = set(used_terms)
    missing_terms = set(terms[min_or_max])-used_terms

    if len(missing_terms) > 0:
        if len(used_terms) > 0:
            for mt in primes[0]:
                set_terms = set(mt[0])
                if missing_terms.issubset(set_terms):
                    essentials.append(mt)
                    break
        else:
            essentials = primes[0]


    if len(list_var) == 0:
        for v in range(var):
            list_var.append(chr(97 + v))

    temp_func = []
    bit_list = []
    if min_or_max == 0:
        for pie in essentials:
            alg_term = list(pie[1][0])
            for b in range(len(alg_term)):
                if alg_term[b] == '0':
                    alg_term[b] = f"¬{list_var[b]}"
                elif pie[1][0][b] == '1':
                    alg_term[b] = f"{list_var[b]}"

            alg_term_str = ''.join(alg_term)
            alg_term_str = alg_term_str.replace('_','')
            temp_func.append(alg_term_str)


        sim_func = ' + '.join(temp_func)
        return sim_func, list_var


    else:
        for pie in essentials:

            alg_term = list(pie[1][0])
            for b in range(len(alg_term)):
                if alg_term[b] == '0':
                    alg_term[b] = f"{list_var[b]}"
                    bit_list.append(alg_term[b])
                elif alg_term[b] == '1':
                    alg_term[b] = f"¬{list_var[b]}"
                    bit_list.append(alg_term[b])

            alg_term_str = '+'.join(bit_list)
            temp_func.append(f"({alg_term_str})")
            bit_list = []


        sim_func = ''.join(temp_func)
        return sim_func, list_var



'''func = 'a⊕b'
var, list_var = detectVar(func)
tabla = createTable(var, None)
funcExe = addecuateFunc(func)
result = evalFunc(funcExe, list_var, tabla)
for r in result:
    print(r, tuple(r))
t = minter_maxter(result, var)

min_or_max = 0
imp2 = QM_tables(t,min_or_max,var)
sim2 = QM_imp_res(imp2, min_or_max, t, list_var, var)'''

'''terms = ([0,6,8,13,14], [1,3,5,7,13,15], [2,4,10])
terms = dont_care(terms, min_or_max)

var2 = len(str(bin(terms[min_or_max][-1])))-2
imp = QM_tables(terms,min_or_max,var2)
sim_func = QM_imp_res(imp, min_or_max, terms, ['A','B','C','D'], var2)'''

















