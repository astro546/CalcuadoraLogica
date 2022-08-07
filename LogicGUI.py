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
        '''Called when a table row is clicked.'''

        key = instance_row.text
        term = self.rows_table[key]
        if instance_row.ids.check.state == 'down' and term not in self.minterms:
            self.minterms.append(term)
        elif term in self.minterms:
            index = self.minterms.index(term)
            self.minterms.pop(index)


        '''term = int(current_row[1])
        self.checked_rows = instance_table.get_row_checks()
        if term not in self.minterms:
            self.minterms.append(term)
        elif current_row not in self.checked_rows:
            index = self.minterms.index(term)
            self.minterms.pop(index)'''

        print(self.minterms)



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

    def deleteTerms(self):
        self.minterms = []
        self.maxterms = []

    def delete_rows(self):
        self.checked_rows = []

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

    def syntax_error(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title=self.title,
                text=self.text,
                buttons=[
                    MDFlatButton(
                        text="Salir",
                        on_release=self.close_dialog
                    ),

                ]
            )
        self.dialog.open()

    def release_error(self, text, title):
        self.text = text
        self.title = title
        if self.dialog is not None:
            self.dialog.text = self.text
        self.syntax_error()

    def close_dialog(self, obj):
        self.dialog.dismiss()
        self.dialog = None



class MinMaxWindow(Screen):
    pass

class HomeWindow(Screen):
    pass


class ResWindow(Screen):
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

    def deleteResTable(self):
        self.table_res.clear_widgets()

    def set_func_label(self, func):
        self.table_res.func_res.text = func

    def is_func_label(self, children):
        if len(children) == 2:
            return True
        else:
            return False

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

    def build(self):
        self.GUI = Builder.load_file('Home.kv')
        return self.GUI

    def close_dialog(self, obj):
        self.dialog.dismiss()
        self.dialog = None

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


    def option_min_max(self, instance_check):
        button_list = MDCheckbox.get_widgets(instance_check)
        index = len(button_list)-1
        if button_list[index].active:
            self.min_or_max = 1
        else:
            self.min_or_max = 0

        print(button_list[index-1].active, button_list[index].active)


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

    def release_error(self, text, title):
        self.text = text
        self.title = title
        if self.dialog is not None:
            self.dialog.text = self.text
        self.syntax_error()

    def close_dialog(self, obj):
        self.dialog.dismiss()
        self.dialog = None


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
            terms.sort()
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


            other_terms.sort()

            if self.min_or_max_input == 0:
                return terms, other_terms, dont_care_terms
            else:
                return other_terms, terms, dont_care_terms

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

    def exeTable(self, terms, table, input_bits):
        n = int(input_bits)
        imp = Logic.QM_tables(terms, self.min_or_max, n)
        sim_func, list_var = Logic.QM_imp_res(imp, self.min_or_max, terms, [], n)
        self.root.current = "fourth"
        return sim_func, terms, table, list_var

    def tryCreateTable(self, input_bits):
        try:
            input_bits = int(input_bits)
            return True
        except ValueError:
            return False

    def data_error(self):
        self.root.current = "second"
        title = "Error de dato"
        text = "Ingrese solo valores numericos"
        self.release_error(text, title)


Example().run()