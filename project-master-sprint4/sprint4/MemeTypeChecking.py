#!/usr/bin/env python
# Check the typing of the given data structure.

class TypeChecker:
    def __init__(self, data):
        self.data = data
        self.trans = {
            'DESTRUCTION': int,
            'trigger': bool,
            'words': str,
            'double': float,
            'void': 'void',  # TODO might need to change this
        }
        self.error_thrown = None
        self.vars = {}  # we could also use this to keep track of how many times
        # self.check_variables(self.data)
        self.gen_ir(self.data)

    def gen_ir(self, data, par_func="none"):
        if data['Node'] == 'ID':
            if data['value'] not in self.vars:
                raise Exception("Trying to use undefined variable")
            self.vars[data['value']]['usg'] += 1
            data['type'] = self.vars[data['value']]['type']
            if self.vars[data['value']]['arr']:
                data['arr'] = True

            # increment the number of usages of that variable, so that we would remove it
            return
        if data['Node'] == 'LITERAL':
            data['type'] = type(data['value'])
            return
        if data['Node'] == 'program':
            for function in data['functions']:
                self.gen_ir(function, function['name']['value'])
            if 'main' in data:
                self.gen_ir(data['main'], 'main')
            return
        if data['Node'] == 'main_function':
            if data['name'] in self.vars:
                raise Exception("Function already exists")  # should we allow
            data['rtype'] = self.trans[data['rtype']]
            self.vars[data['name']] = {'Node': 'func_type', 'type': data['rtype'],
                                                'usg': 0, 'arr': False, 'parameter_types': []}
            for elem in data['body']:
                self.gen_ir(elem, par_func)
            return
        if data['Node'] == 'function':
            if data['name']['value'] in self.vars:
                raise Exception("Function already exists")  # should we allow
            data['rtype'] = self.trans[data['rtype']]
            self.vars[data['name']['value']] = {'Node': 'func_type', 'type': data['rtype'],
                                                'usg': 0, 'arr': False, 'parameter_types': []}
            mx = len(data['parameters'])
            for i in range(mx):
                self.gen_ir(data['parameters'][i], par_func)
                temp = {'arr': False, 'type': data['parameters'][i]['type']['type']}
                # 'name': data['parameters'][i]['name']['value']
                if data['parameters'][i]['type']['Node'] == 'ARRAY_TYPE':
                    temp['arr'] = True
                self.vars[data['name']['value']]['parameter_types'].append(temp)
            for elem in data['body']:
                self.gen_ir(elem, par_func)
            return
        if data['Node'] == 'return_stmt':
            func = self.vars[par_func]
            if func['type'] == 'void':
                return
            # TODO: when doing cython probably will need to change this depending on what we can return it
            if len(data['values']) >= 2 and not func['arr']:
                raise Exception("To many variables to return")
            # if len(data['values'])
            # if function call we need to check that the function returns the same type as the current one
            # TODO add array support
            for i in range(len(data['values'])):
                self.gen_ir(data['values'][i], )
                if data['values'][i]['Node'] == 'function_call':
                    f_temp = self.vars[data['values'][i]['name']['value']]
                    if f_temp['type'] != func['type']:
                        raise Exception("Return type does not match")
                else:
                    #  TODO: need test cases for this
                    if data['values'][0]["Node"] == 'ID':
                        if func['type'] != data['values'][i]['type']['type']:
                            raise Exception("Function returns the wrong type ")
                    else:
                        if func['type'] != data['values'][i]['type']:
                            raise Exception("Function returns the wrong type ")

            return
        if data['Node'] == 'parameter':
            if data['type']['Node'] == 'ARRAY_TYPE':
                data['type']['type'] = self.trans[data['type']['type']['type']]
                self.vars[data['name']['value']] = {'Node': 'TYPE', 'type': data['type'], 'usg': 0, 'arr': True}
            else:
                data['type']['type'] = self.trans[data['type']['type']]
                self.vars[data['name']['value']] = {'Node': 'TYPE', 'type': data['type'], 'usg': 0, 'arr': False}
            return
            # self.gen_ir(data['name'])
        if data['Node'] == 'assign_stmt':
            if data['type'] == 'reassignment':
                # theoreticaly we can do later here some logic about local and global scoping
                self.vars[data['name']['value']]['usg'] += 1
                self.gen_ir(data['value'])
                left_type = data['value']['type']
                right_type = self.vars[data['name']['value']]['type']

                if isinstance(left_type, dict):
                    left_type = left_type['type']
                if isinstance(right_type, dict):
                    right_type = right_type['type']

                if left_type != right_type:
                    raise Exception("Trying to assign variable to a wrong type")
            elif data['type']['Node'] == 'array_access':
                self.gen_ir(data['type'])
                self.gen_ir(data['value'])
                if self.vars[data['name']['value']]['type'] != data['value']['type']:
                    raise Exception("Trying to assign wrong value type to an array.")
            else:
                if data['type']['Node'] == 'ARRAY_TYPE':
                    data['type']['type'] = self.trans[data['type']['type']['type']]
                    self.vars[data['name']['value']] = data['type']
                    self.vars[data['name']['value']]['arr'] = True
                    # check all values of the array
                    for elem in data['value']['values']:
                        if type(elem['value']) != data['type']['type']:
                            raise Exception("Trying to assign variable to a wrong type")
                else:
                    data['type']['type'] = self.trans[data['type']['type']]
                    self.vars[data['name']['value']] = data['type']
                    self.vars[data['name']['value']]['arr'] = False
                self.vars[data['name']['value']]['usg'] = 0
                self.gen_ir(data['value'])
            return
        if data['Node'] == 'for_stmt':
            self.gen_ir(data['parameter'])
            self.gen_ir(data['condition'])

            for i in data['body']:
                self.gen_ir(i, par_func)
            return
        if data['Node'] == 'if_block':
            self.gen_ir(data['if_clause'], par_func)
            if 'elif_clause' in data:
                for elif_c in data['elif_clause']:
                    self.gen_ir(elif_c, par_func)
            if 'else_clause' in data:
                self.gen_ir(data['else_clause'], par_func)
            return
        if data['Node'] == 'if_clause':
            self.gen_ir(data['condition'])
            for i in data['body']:
                self.gen_ir(i, par_func)
            return
        if data['Node'] == 'elif_clause':
            self.gen_ir(data['condition'])
            self.gen_ir(data['condition'])
            for i in data['body']:
                self.gen_ir(i, par_func)
            return
        if data['Node'] == 'else_clause':
            for i in data['body']:
                self.gen_ir(i, par_func)
            return
        if data['Node'] == 'array_expr':
            mx = len(data['values'])
            for i in range(mx):
                self.gen_ir(data['values'][i], par_func)
                # TODO: compare type of current element of the array with the
            return
        if data['Node'] == 'while_stmt':
            self.gen_ir(data['condition'])  # this might not be needed
            for elem in data['body']:
                self.gen_ir(elem, par_func)
            return
        if data['Node'] == 'math_bool_expr':
            self.gen_ir(data['left'], par_func)
            self.gen_ir(data['right'], par_func)
            #  TODO add type checking here
            return
        if data['Node'] == 'function_call':
            # Check all of the parameter types are the same as with the function defenition
            if data['name']['value'] not in self.vars:
                raise Exception("Trying to use undefined function")

            # TODO check that right values are passed in
            func_pars = self.vars[data['name']['value']]['parameter_types']
            self.vars[data['name']['value']]['usg'] += 1
            data['type'] = self.vars[data['name']['value']]['type']
            for val in range(len(data['values'])):
                # TODO modify this to contain array logic later on
                self.gen_ir(data['values'][val])
                if data['values'][val]['Node'] == 'array_expr':
                    if not func_pars[val]['arr']:
                        raise Exception("Wrong parameter in function call")
                    continue
                elif data['values'][val]['type'] != func_pars[val]['type']:
                    raise Exception("Wrong parameter in function call")
            return
        if data['Node'] == 'arithmetic_expr' or data['Node'] == 'math_bool_expr':
            self.gen_ir(data['left'])
            self.gen_ir(data['right'])
            left_type = data['left']['type']
            right_type = data['right']['type']

            if isinstance(left_type, dict):
                left_type = left_type['type']
            if isinstance(right_type, dict):
                right_type = right_type['type']

            if left_type != right_type:
                raise Exception("type miss match")
            data['type'] = right_type
            return
        if data['Node'] == 'bool_expr':
            self.gen_ir(data['right'])
            if data['left']:
                self.gen_ir(data['left'])
                if data['left']['type'] != data['right']['type']:
                    raise Exception("type miss match")
            data['type'] = data['right']['type']
            return
        if data['Node'] == 'array_access':
            self.gen_ir(data['name'])
            self.gen_ir(data['index'])
            # if
            if data['index']['type'] != int:
                raise Exception("Index needs to be an integer value")
            data['type'] = data['name']['type']
            return
        return

