from TreeFragment import parse_from_strings, StringParseContext
from Scanning import StringSourceDescriptor
import Symtab
import Naming

class NonManglingModuleScope(Symtab.ModuleScope):

    def __init__(self, prefix, *args, **kw):
        self.prefix = prefix
        Symtab.ModuleScope.__init__(self, *args, **kw)
    
    def mangle(self, prefix, name=None):
        if name:
            if prefix in (Naming.typeobj_prefix, Naming.func_prefix, Naming.var_prefix, Naming.pyfunc_prefix):
                # Functions, classes etc. gets a manually defined prefix easily
                # manually callable instead (the one passed to CythonUtilityCode)
                prefix = self.prefix
            result = "%s%s" % (prefix, name)
        else:
            result = Symtab.ModuleScope.mangle(self, prefix)
        return result

class CythonUtilityCodeContext(StringParseContext):
    scope = None
    
    def find_module(self, module_name, relative_to = None, pos = None, need_pxd = 1):
        if module_name != self.module_name:
            raise AssertionError("Not yet supporting any cimports/includes from string code snippets")
        if self.scope is None:
            self.scope = NonManglingModuleScope(self.prefix,
                                                module_name, parent_module = None, context = self)
        return self.scope

class CythonUtilityCode:
    """
    Utility code written in the Cython language itself.
    """

    def __init__(self, pyx, name="__pyxutil", prefix="", requires=None):
        # 1) We need to delay the parsing/processing, so that all modules can be
        #    imported without import loops
        # 2) The same utility code object can be used for multiple source files;
        #    while the generated node trees can be altered in the compilation of a
        #    single file.
        # Hence, delay any processing until later.
        self.pyx = pyx
        self.name = name
        self.prefix = prefix
        self.requires = requires

    def get_tree(self):
        import Pipeline
        context = CythonUtilityCodeContext(self.name)
        context.prefix = self.prefix
        tree = parse_from_strings(self.name, self.pyx, context=context)
        pipeline = Pipeline.create_pipeline(context, 'utility_code')
        (err, tree) = Pipeline.run_pipeline(pipeline, tree)
        assert not err
        return tree

    def put_code(self, output):
        pass


        