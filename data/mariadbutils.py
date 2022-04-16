from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement

class json_length(FunctionElement):
	name = "json_length"
	inherit_cache = True

@compiles(json_length)
def compile(element, compiler, **kwargs):
	return "json_length(%s)" % compiler.process(element.clauses)