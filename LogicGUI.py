from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.label import Label
import re
import Logic


class WindowManager(ScreenManager):
    pass


class FuncWindow(Screen):
    pass


class TableWindow(Screen):
    pass


class CreateTableWindow(Screen):
    minterms = []
    maxterms = []
    rows_table = {}
    dialog = None
    def ManualCreateMDtable(self, input_bits):
        input_bits = int(input_bits)
        columns = []
        rows = []
        self.rows_table = {}
        num_rows = 2 ** input_bits

        for c in range(input_bits):
            columns.append(chr(97 + c))

        var_str = ' '.join(columns)

        for i in range(num_rows):
            num_bin = Logic.format_bin(i, input_bits)
            num_str = ' '.join(num_bin)
            rows.append((num_str,i))
            self.rows_table[num_str] = i

        Mdtable = MDDataTable(
            use_pagination=True,
            rows_num=8,
            check=True,
            column_data=[
                (var_str, dp(30)),
                ('Termino', dp(20))
            ],
            row_data=rows,
        )


        Mdtable.bind(on_row_press=self.on_row_press)
        self.table_box.add_widget(Mdtable)


    def deleteTable(self):
        self.table_box.clear_widgets()


    def on_row_press(self, instance_table, instance_row):
        '''Llamado cuando se presiona un checkbox.'''

        key = instance_row.text
        term = self.rows_table[key]
        if instance_row.ids.check.state == 'down' and term not in self.minterms:
            self.minterms.append(term)
        elif term in self.minterms:
            index = self.minterms.index(term)
            self.minterms.pop(index)


        print(self.minterms)


    #Crea los terminos
    def createTerms(self, input_bits):
        n = int(input_bits)
        for i in range(2**n):
            if i not in self.minterms:
                self.maxterms.append(i)

        self.minterms.sort()
        self.maxterms.sort()
        self.minterms = list(set(self.minterms))
        self.maxterms = list(set(self.maxterms))
        print(self.minterms, self.maxterms)
        return self.minterms, self.maxterms, []
    #elimina terminos para que no se repitan en la siguiente ejecucion
    def deleteTerms(self):
        self.minterms = []
        self.maxterms = []
    #Elimina filas que no se repitan en la siguiente ejecucion
    def delete_rows(self):
        self.checked_rows = []
    #Crea tabla de resultados en forma de lista
    def createTable(self, input_bits):
        table = []
        n= int(input_bits)
        for m in range(2**n):
            num_bin = Logic.format_bin(m, n)
            table.append(num_bin)

        for n in range(len(table)):
            if n in self.minterms:
                table[n].append('1')
            else:
                table[n].append('0')

        return table


class MinMaxWindow(Screen):
    pass

class HomeWindow(Screen):
    pass


class ResWindow(Screen):
    #Crea la tabla de verdad de resultados con la lista
    def createMDtable(self, table, list_var):
        columns = []
        rows = []
        for c in list_var:
            columns.append((c, dp(10)))
        columns.append(("Salida", dp(10)))

        for i in table:
            rows.append(tuple(i))

        Mdtable = MDDataTable(
            use_pagination=True,
            rows_num=8,
            column_data=columns,
            row_data=rows,
        )

        self.table_res.add_widget(Mdtable)
    #Elimina la tabla para evitar duplicados
    def deleteResTable(self):
        self.table_res.clear_widgets()
    #Agrega la etiqueta de la funcion
    def add_func_label(self, func_text):
        func_label = Label(
            text= func_text,
            font_size= 32,
            color= (.2, .5, .3, 1))

        self.table_res.add_widget(func_label)




class ItemConfirm(OneLineAvatarIconListItem):
    divider = None



class Example(MDApp):
    dialog = None
    min_or_max = NumericProperty(0)
    min_or_max_input = NumericProperty(0)
    func_label = StringProperty("")
    textAyudaFunc = "La sintaxis para las funciones es la siguiente: \nPara el operador AND se puede escribir como: \n" \
                    "AB o A*B\n" \
                    "Para el operador OR se puede escribir de la siguiente manera:\n" \
                    "A+B\n" \
                    "Para el operador NOT se puede escribir de la siguiente manera:\n" \
                    "¬A\n" \
                    "Para el operador XOR se puede escribir de las siguientes maneras:\n" \
                    "A⊕B o A^B" \
                    "Las variables y/o operaciones se pueden escrbir entre parentesis:\n" \
                    "(a)(b), (a)+(b),(ab),(a+b),(a)^(b),(a^b)\n" \
                    "Tambien con los parentesis se pueden escribir funciones compuestas:" \
                    "a(c+d), ¬(a+b)c, (¬a^c+cd)ef\n" \
                    "Si se pretenda poner una expresion negada despues de otra expresion entre parentesis , la expresion negada se debe encerrar en parentesis:\n" \
                    "Ejemplo: ¬((x+y)(¬(x¬y+z))) , (a+b)(¬(cd)), ¬(¬(¬x¬y+xz)(¬(¬x+¬yz))) \n" \
                    "Los parentesis deben de ir cerrados, y las operaciones no deben de estar imcompletas.\n" \
                    "Ademas de que las variables solo deben de ser letras mayusculas o minusculas, no se admiten numeros u otros caracteres especiales como variables." \
                    "Si estas condiciones no se cumplen, generaran errores. Ejemplos de mala sintaxis:\n" \
                    "a+, a¬, (ab, a+b), ab(c+5)"
    textAyudaTable = "Primero ingrese los bits de entrada, los cuales deben de ser estrictamente numeros, no letras ni caracteres especiales.\n" \
                     "Despues, aparece una ventana con una tabla de verdad, en la cual debes de marcar las casillas de las combinaciones cuyas salidas quieres que sea 1," \
                     "una casilla marcada significa 1, y una casilla descamarcada significa 0. Las tablas se presentan en grupos de 8 combinaciones, por lo que , por ejemplo," \
                     "para una tabla de verdad de 4 bits de entrada, esta se dividira en dos partes, una con las primeras 8 combinaciones de entrada, y otra con las otras 8 restantes."
    textAyudaMinMax = "En la casilla de bits de entrada, se ingresa el numero de bits de entrada, no deben de ingresarse letras o caracteres especiales en ese campo.\n" \
                      "\n" \
                      "En la casilla de Terminos se ingresaran los terminos de la funcion, y se debe de marcar si son minterminos o maxterminos. Por default, el programa los toma como minterminos." \
                      "El formato para ingresar los terminos es el siguiente:\n" \
                      "1,2,3,4..,n o 1,2,3,4..,n\n," \
                      "En la casilla de terminos no se debe ingresar letras o caracteres especiales. Tampoco se deben ingresar comas seguidas.\n" \
                      "Ejemplos de mala sintaxis: \n" \
                      "1,2,,3 , ,,,, , ,,1,2  , a,b,c,#,%\n" \
                      "\n" \
                      "La casilla de Dont Cares sirve para ingresar terminos dont cares. Para ingresar terminos dont cares, esta casilla debe de estar activada, ya que esta casilla es opcional.\n" \
                      "La sintaxis que se debe de seguir para ingresar terminos Dont Cares es la misma que para ingresar los terminos de la funcion."
    #Constructor de la clase
    def build(self):
        self.GUI = Builder.load_file('Home.kv')
        return self.GUI
    #Cierra la ventana de dialogo
    def close_dialog(self, obj):
        self.dialog.dismiss()
        self.dialog = None
    #Menu de opciones
    def options_menu(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Opciones de minimizacion",
                type="confirmation",
                items=[
                    ItemConfirm(text="Mintérminos"),
                    ItemConfirm(text="Maxtérminos"),
                ],
                buttons=[

                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release= self.close_dialog
                    ),
                ],
            )
        self.dialog.open()

    #Checa que opcion esta activa
    def option_min_max(self, instance_check):
        button_list = MDCheckbox.get_widgets(instance_check)
        index = len(button_list)-1
        if button_list[index].active:
            self.min_or_max = 1
        else:
            self.min_or_max = 0

        print(button_list[index-1].active, button_list[index].active)

    #Ventana de error
    def syntax_error(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title=self.title,
                text=self.text,
                buttons=[
                    MDFlatButton(
                        text="Salir", text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialog
                    ),

                ]
            )
        self.dialog.open()

    #Pone el texto y titulo y cierra el dialogo si anteriormente se abrio uno
    def release_error(self, text, title):
        self.text = text
        self.title = title
        if self.dialog is not None:
            self.dialog.text = self.text
        self.syntax_error()

    #Rutina que evalua el string de la funcion ingresado por el usuario
    def exeFunc(self, func):
        if func:
            try:
                var, list_var = Logic.detectVar(func)
                table = Logic.createTable(var, None)
                funcExe = Logic.addecuateFunc(func)
                table_res = Logic.evalFunc(funcExe, list_var, table)
                tuple_res = Logic.minter_maxter(table_res, var)
                imp = Logic.QM_tables(tuple_res, self.min_or_max, var)
                sim_func, list_var = Logic.QM_imp_res(imp, self.min_or_max, tuple_res, list_var, var)
                terms_res = list(tuple_res)
                self.root.current = "fourth"
                self.func_label = sim_func
                print(self.func_label)
                return sim_func, terms_res, table_res, list_var
            except SyntaxError:
                text = "Corrija la sintaxis de la función."
                title = "Error de sintaxis"
                self.release_error(text,title)
                return '', None, None
            except IndexError:
                text = "No hay ninguna variable valida, las variables deben ser letras minusculas o mayúsculas, no numeros ni caracteres especiales."
                title = "Error de sintaxis"
                self.release_error(text,title)
                return '', None, None
    #Crea la lista de terminos de los strings dados por el usuario
    def createMinMax(self, text_terms, dont_care, input_bits):
        term_patt = r'\d,?[\d,]*'
        error_patt = r'\D+'

        error = re.findall(error_patt, text_terms)
        error = list(set(error))
        if len(error) > 1 or error[0] != ',':
            text = "Solo se permiten numeros y comas al ingresar terminos"
            title = "Error de sintaxis"
            self.release_error(text, title)
            return [], [], []

        valid = re.search(term_patt, text_terms)

        if valid is None:
            text = "Terminos no validos, los terminos deben ser numericos y separados por comas. (Ejemplo: 1,2,3)"
            title = "Error de sintaxis"
            self.release_error(text,title)
            return [], [], []
        else:
            other_terms = []
            dont_care_terms = []
            num_patt = r'\d+'
            terms = re.findall(num_patt, text_terms)
            terms = list(set(terms))
            number_bits = (2**input_bits)

            if not dont_care.disable:

                dont_care_terms = re.findall(num_patt, dont_care.text)
                dont_care_terms = list(set(dont_care_terms))
                dont_care_terms.sort()

                for d in range(len(dont_care_terms)):
                    if dont_care_terms[d] not in terms:
                        dont_care_terms[d] = int(dont_care_terms[d])
                    else:
                        text= "Un termino no puede estar en la lista de minterminos/maxterminos y en la lista de dont cares a la vez."
                        title= "Error de terminos"
                        self.release_error(text,title)
                        return [], [], []


            for t in range(number_bits):
                if str(t) not in terms and t not in dont_care_terms:
                    other_terms.append(t)

            for i in range(len(terms)):
                terms[i] = int(terms[i])

            terms.sort()
            other_terms.sort()

            if self.min_or_max_input == 0:
                return terms, other_terms, dont_care_terms
            else:
                return other_terms, terms, dont_care_terms
    #Evalua la lista de terminos creada anteriormente
    def exeMinMax(self, text_terms, dont_care, input_bits_text):
        try:
            input_bits = int(input_bits_text)
        except:
            text="En este campo solo se admiten valores numericos"
            title= "Error de dato"
            self.release_error(text, title)
            return '', None, None

        tuple_terms = self.createMinMax(text_terms, dont_care, input_bits)
        table = Logic.createTable(input_bits, tuple_terms)
        tuple_terms = Logic.dont_care(tuple_terms, self.min_or_max)
        imp = Logic.QM_tables(tuple_terms, self.min_or_max, input_bits)
        sim_func, list_var = Logic.QM_imp_res(imp, self.min_or_max, tuple_terms, [], input_bits)
        self.root.current = "fourth"
        return sim_func, tuple_terms, table, list_var
    #Evalua la tabla de verdad creada por el usuario
    def exeTable(self, terms, table, input_bits):
        n = int(input_bits)
        imp = Logic.QM_tables(terms, self.min_or_max, n)
        sim_func, list_var = Logic.QM_imp_res(imp, self.min_or_max, terms, [], n)
        self.root.current = "fourth"
        return sim_func, terms, table, list_var
    #Detecta si no hay un error al ingresas el numero de variables de entrada de la tabla
    def tryCreateTable(self, input_bits):
        try:
            input_bits = int(input_bits)
            return True
        except ValueError:
            return False
    #Lanza el error de datos para la pantalla de ingreso de variables de entrada al crear la tabla (Segunda Pantalla)
    def data_error(self):
        self.root.current = "second"
        title = "Error de dato"
        text = "Ingrese solo valores numericos"
        self.release_error(text, title)


Example().run()