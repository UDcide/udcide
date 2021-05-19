from udcide.util import PrototypeHelper

class TestPrototypeHelper:
    def test_normalize_parameter(self):
        prototype = 'La/b/c/d/Class;->method(Le/f/A; B)Lg/h/Z;'
        assert PrototypeHelper.normalize_parameter(prototype) == 'La/b/c/d/Class;->method(Le/f/A;B)Lg/h/Z;'

        signature = 'method(Le/f/A; B)Lg/h/Z;'
        assert PrototypeHelper.normalize_parameter(signature) == 'method(Le/f/A;B)Lg/h/Z;'

    def test_denormalize_parameter(self):
        prototype = 'La/b/c/d/Class;->method(Le/f/A;B)Lg/h/Z;'
        assert PrototypeHelper.denormalize_parameter(prototype) == 'La/b/c/d/Class;->method(Le/f/A; B)Lg/h/Z;'

        signature = 'method(Le/f/A;B)Lg/h/Z;'
        assert PrototypeHelper.denormalize_parameter(signature) == 'method(Le/f/A; B)Lg/h/Z;'

    def test_get_class_and_signature(self):
        prototype = 'La/b/c/d/Class;->method(Le/f/A;B)Lg/h/Z;'
        assert PrototypeHelper.get_class_and_signature(prototype) == ('La/b/c/d/Class;', 'method(Le/f/A;B)Lg/h/Z;')

    def test_get_method_name_and_descriptor(self):
        signature = 'method(Le/f/A;B)Lg/h/Z;'
        assert PrototypeHelper.get_method_name_and_descriptor(signature) == ('method', '(Le/f/A;B)Lg/h/Z;')
    
    def test_get_num_of_parameter(self):
        prototype = 'La/b/c/d/Class;->method(Le/f/A;B)Lg/h/Z;'
        assert PrototypeHelper.get_num_of_parameter(prototype) == 2

        prototype = 'La/b/c/d/Class;->method(Le/f/A; B)Lg/h/Z;'
        assert PrototypeHelper.get_num_of_parameter(prototype) == 2

        prototype = 'La/b/c/d/Class;->method(Le/f/A;Li/j/B;)Lg/h/Z;'
        assert PrototypeHelper.get_num_of_parameter(prototype) == 2

        prototype = 'La/b/c/d/Class;->method(Le/f/A; Li/j/B;)Lg/h/Z;'
        assert PrototypeHelper.get_num_of_parameter(prototype) == 2

    def test_is_return_viod(self):
        prototype = 'La/b/c/d/Class;->method(Le/f/A;B)Lg/h/Z;'
        assert not PrototypeHelper.is_return_void(prototype)