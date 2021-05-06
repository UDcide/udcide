from udcide.util import PrototypeHelper

class TestPrototypeHelper:
    def test_normalize_parameter(self):
        prototype = 'Lahmyth/mine/king/ahmyth/FileManager;->walk(Ljava/lang/String; B)Lorg/json/JSONArray;'
        assert PrototypeHelper.normalize_parameter(prototype) == 'Lahmyth/mine/king/ahmyth/FileManager;->walk(Ljava/lang/String;B)Lorg/json/JSONArray;'

        signature = 'walk(Ljava/lang/String; B)Lorg/json/JSONArray;'
        assert PrototypeHelper.normalize_parameter(signature) == 'walk(Ljava/lang/String;B)Lorg/json/JSONArray;'

    def test_denormalize_parameter(self):
        prototype = 'Lahmyth/mine/king/ahmyth/FileManager;->walk(Ljava/lang/String;B)Lorg/json/JSONArray;'
        assert PrototypeHelper.denormalize_parameter(prototype) == 'Lahmyth/mine/king/ahmyth/FileManager;->walk(Ljava/lang/String; B)Lorg/json/JSONArray;'

        signature = 'walk(Ljava/lang/String;B)Lorg/json/JSONArray;'
        assert PrototypeHelper.denormalize_parameter(signature) == 'walk(Ljava/lang/String; B)Lorg/json/JSONArray;'

    def test_get_class_and_signature(self):
        prototype = 'Lahmyth/mine/king/ahmyth/FileManager;->walk(Ljava/lang/String;B)Lorg/json/JSONArray;'
        assert PrototypeHelper.get_class_and_signature(prototype) == ('Lahmyth/mine/king/ahmyth/FileManager;', 'walk(Ljava/lang/String;B)Lorg/json/JSONArray;')

    def test_get_method_name_and_descriptor(self):
        signature = 'walk(Ljava/lang/String;B)Lorg/json/JSONArray;'
        assert PrototypeHelper.get_method_name_and_descriptor(signature) == ('walk', '(Ljava/lang/String;B)Lorg/json/JSONArray;')
    
    def test_get_num_of_parameter(self):
        prototype = 'Lahmyth/mine/king/ahmyth/FileManager;->walk(Ljava/lang/String;B)Lorg/json/JSONArray;'
        assert PrototypeHelper.get_num_of_parameter(prototype) == 2

        prototype = 'Lahmyth/mine/king/ahmyth/FileManager;->walk(Ljava/lang/String; B)Lorg/json/JSONArray;'
        assert PrototypeHelper.get_num_of_parameter(prototype) == 2

    def test_is_return_viod(self):
        prototype = 'Lahmyth/mine/king/ahmyth/FileManager;->walk(Ljava/lang/String;B)Lorg/json/JSONArray;'
        assert not PrototypeHelper.is_return_void(prototype)