import logging
import os
import os.path
from collections import defaultdict

from androguard.misc import AnalyzeAPK

from udcide.util import PrototypeHelper

logger = logging.getLogger('UDcide')
logger.setLevel(logging.DEBUG)

class UDcide:
    def __init__(self, apk_path, smali_dir) -> None:
        self._smali_dir = os.path.abspath(smali_dir)
        self._undisabled = defaultdict(set)
        self._disabled = dict()

        self._analysis = AnalyzeAPK(apk_path)[2]
        self._callback = None

    def on_Method_Disabled(self, callback):
        self._callback = callback

    def disable_method(self, prototype):
        class_name, signature = PrototypeHelper.get_class_and_signature(
            prototype)
        self._add_method(class_name, signature)
        self.apply()

    def batch_disable(self, prototype_list):
        self.add_method(prototype_list)
        self.apply()

    def add_method(self, prototype_list):
        for prototype in prototype_list:
            class_name, signature = PrototypeHelper.get_class_and_signature(
                prototype)
            self._add_method(class_name, signature)

    def _add_method(self, class_name, signature):
        signature = PrototypeHelper.normalize_parameter(signature)

        if class_name not in self._undisabled or signature not in self._undisabled[class_name]:
            self._undisabled[class_name].add(signature)

            if not PrototypeHelper.is_return_void(signature):
                for upper in self._get_uppers(class_name, signature):
                    self._add_method(*upper)

    def apply(self):
        logger.info(
            f'Processing {sum([len(m_list) for m_list in self._undisabled.values()])} methods with {len(self._undisabled.keys())} classes')
        for class_name in self._undisabled.keys():
            smali_files = self._get_smali_file(class_name)

            logger.debug(f'Processing {class_name}')

            with open(smali_files[0], 'r') as older:
                with open(smali_files[1], 'w') as newer:
                    for signature in self._comment_method(
                            older, newer, self._undisabled[class_name]):
                        if self._callback:
                            self._callback(class_name, signature)

            os.remove(smali_files[0])

        self._disabled.update(self._undisabled)
        self._undisabled.clear()

    def get_modification_count(self):
        return sum([len(val) for val in self._undisabled.values()])

    def _get_smali_file(self, class_name):
        class_name = class_name[1:-1]
        path = os.path.join(self._smali_dir, class_name+'.smali')
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise ValueError(f'File not found in {path}')
        elif not os.path.isfile(path):
            raise ValueError(f'Expect a file but a folder found in {path}')

        part = os.path.splitext(path)
        old_path = part[0]+'_backup'+part[1]
        os.rename(path, old_path)

        return (old_path, path)

    def _get_uppers(self, class_name: str, signature: str):
        method_name, descriptor = PrototypeHelper.get_method_name_and_descriptor(
            signature)
        descriptor = PrototypeHelper.denormalize_parameter(descriptor)

        encoded = self._analysis.get_method_by_name(
            class_name, method_name, descriptor)
        method = self._analysis.get_method(encoded)

        return [(str(xref[0].name), str(xref[1].name)+str(xref[1].descriptor)) for xref in method.get_xref_from()]

    @staticmethod
    def _comment_method(infile, outfile, signature_list):
        def get_indent(string):
            for i, c in enumerate(string):
                if not c.isspace():
                    return i

        content = 'Go'
        least_signature = ''
        add_void = False
        while content:

            # Not in target method
            content = infile.readline()
            while content:
                if content.startswith('.method'):
                    signature = content.strip().split()[-1]
                    if signature in signature_list:
                        if not PrototypeHelper.is_return_void(signature):
                            indent = get_indent(content)
                            outfile.write(
                                f'{content[:indent]}# {content[indent:]}')
                            add_void = False
                        else:
                            outfile.write(content)
                            add_void = True

                        logger.debug(f' - {signature}')
                        signature_list.discard(signature)
                        least_signature = signature
                        break
                    else:
                        outfile.write(content)
                else:
                    outfile.write(content)

                content = infile.readline()

            # In a target method
            content = infile.readline()
            indent = 4
            while content:
                content = content.expandtabs(4)
                if content.startswith('.end method'):
                    if add_void:
                        # Set locals & Return void
                        indent = "".join([" " for _ in range(indent)])
                        num_of_arg = PrototypeHelper.get_num_of_parameter(
                            least_signature)
                        outfile.write(
                            f'{indent}.locals {num_of_arg}{os.linesep}')
                        outfile.write(f'{indent}return-void{os.linesep}')

                        # End of method
                        outfile.write(content)
                    else:
                        indent = get_indent(content)
                        outfile.write(
                            f'{content[:indent]}# {content[indent:]}')

                    yield least_signature
                    break
                elif content.strip():
                    indent = get_indent(content)
                    outfile.write(f'{content[:indent]}# {content[indent:]}')
                else:
                    outfile.write(content)

                content = infile.readline()
