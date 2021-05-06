import re


class PrototypeHelper:

    @staticmethod
    def normalize_parameter(contains_parameters: str) -> str:
        prototype = contains_parameters
        i = prototype.index('(')+1
        j = prototype.index(')')

        parameter_str = ''.join(prototype[i:j].split())

        return prototype[:i]+parameter_str+prototype[j:]

    def denormalize_parameter(contains_parameters: str) -> str:
        prototype = contains_parameters
        i = prototype.index('(')+1
        j = prototype.index(')')

        parameters = re.findall('[ZBCSIJFD]|L.+;|\\[', prototype[i:j])

        for index in range(len(parameters)):
            if parameters[index] == '[':
                parameters[index] = None
                parameters[index-1] = '['+parameters[index-1]

        parameter_str = ' '.join([p for p in parameters if p])

        return prototype[:i]+parameter_str+prototype[j:]

    @staticmethod
    def get_class_and_signature(prototype: str) -> str:
        i = prototype.index(';')+1
        j = prototype.index('->')+2 if '->' in prototype else i
        k = prototype.index('(')

        class_name = prototype[:i].strip()
        method_name = prototype[j:k].strip()
        descriptor = prototype[k:].strip()

        return class_name, method_name+descriptor

    def get_method_name_and_descriptor(signature: str) -> str:
        index = signature.index('(')

        return signature[:index].strip(), signature[index:].strip()

    @staticmethod
    def get_num_of_parameter(prototype: str) -> int:
        l_index = prototype.index('(')+1
        r_index = prototype.index(')')
        parameter_str = prototype[l_index:r_index].strip()

        parameter_list = re.findall('[ZBCSIJFD]|L.+;|\\[', parameter_str)

        array_count = len([p for p in parameter_list if p == '['])

        return len(parameter_list) - array_count

    @staticmethod
    def is_return_void(contains_return_value: str) -> bool:
        return contains_return_value[-1] == 'V'
