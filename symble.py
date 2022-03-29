import sys
from string import ascii_letters as letters

letters += "_"

def program2text(instructs, sep="\n"):
    text = ""
    for l in instructs:
        for i in l:
            text += repr(i) + " "
        text = text[:-1] + sep
    return text[:-len(sep)]

def error(msg: str, line: int, instructs: list):
    exit(f"{msg} (line {line + 1})")
def expectedType(expected, got, line):
    if type(expected) is list:
        if not type(got) in expected:
            opts = ""
            for i in expected:
                opts += i.__name__.lower() + "/"
            opts = opts[:-1]
            exit(f"expected {opts}, got {got.__class__.__name__.lower()} (line {line + 1})")
    else:
        if not type(got) is expected:
            exit(f"expected {expected.__name__.lower()}, got {got.__class__.__name__.lower()} (line {line + 1})")
def expectedExpr(amount, instruct, line):
    if not len(instruct) > amount:
        exit(f"missing argument, need {amount} got {len(instruct) - 1} (line {line + 1})")

class Int:
    def __init__(self, number: int):
        self.val = int(number)
    def __repr__(self):
        return f"[int {self.val}]"
    def __str__(self):
        return str(self.val)
class Float:
    def __init__(self, number: float):
        self.val = number
    def __repr__(self):
        return f"[float {self.val}]"
    def __str__(self):
        return str(self.val)
# work in progress >
class Binary:
    def __init__(self, number: int):
        self.val = bin(number)
    def __repr__(self):
        return f"[bin {self.val}]"
class Hex:
    def __init__(self, number: int):
        self.val = hex(number)
    def __repr__(self):
        return f"[hex {self.val}]"
class Octal:
    def __init__(self, number: int):
        self.val = oct(number)
    def __repr__(self):
        return f"[oct {self.val}]"
# < work in progress
class Bool:
    def __init__(self, boolean: bool):
        self.val = boolean
    def __repr__(self):
        if self.val:
            return f"[bool true]"
        else:
            return f"[bool false]"
    def __str__(self):
        if self.val:
            return "true"
        else:
            return "false"
class Str:
    def __init__(self, string: str):
        self.val = (string.replace("\\n", "\n")).replace("\\t", "\t")
    def __repr__(self):
        val = (self.val.replace("\n", "\\n")).replace("\t", "\\t")
        return f'[str "{val}"]'
    def __str__(self):
        return self.val
class Null:
    def __init__(self):
        self.val = None
    def __repr__(self):
        return f"[null]"
    def __str__(self):
        return "null"
class List:
    def __init__(self, l: list):
        self.val = l
    def __repr__(self):
        return f"[list {self.val}]"
    def __str__(self):
        text = "["
        for i in self.val:
            if type(i) is Str:
                text += '"' + str(i) + '" '
            else:
                text += str(i) + " "
        text = text[:-1]
        text += "]"
        return text
class Eval:
    def __init__(self, eval: list):
        self.eval = eval
    def __repr__(self):
        return f"[eval {self.eval}]"
    def __str__(self):
        return "eval"
class Var:
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return f"[var {self.name}]"
    def __str__(self):
        return self.name
class Index:
    def __init__(self, org, val):
        self.org = org
        self.val = val
    def __repr__(self):
        return f"[index {repr(self.org)} {repr(self.val)}]"
    def __str__(self):
        return "index"
class Body:
    def __init__(self, content):
        self.content = content
    def __repr__(self):
        return "[body { " + program2text(self.content, ' : ') + " } ]"
    def __str__(self):
        return "body"
class Get:
    def __init__(self, t):
        self.type = t
    def __repr__(self):
        return f"[get {self.type}]"
    def __str__(self):
        return "get"
class Neg:
    def __init__(self, val):
        self.val = val
    def __repr__(self):
        return f"[- {repr(self.val)}]"
    def __str__(self):
        return f"-({repr(self.val)})"
class Not:
    def __init__(self, val):
        self.val = val
    def __repr__(self):
        return f"[not {repr(self.val)}]"
    def __str__(self):
        return f"!({repr(self.val)})"

class Op:
    def __init__(self, t: str):
        self.type = t
    def __repr__(self):
        return f"[op {self.type}]"
    def __str__(self):
        return "op"

class Grammar:
    def __init__(self):
        self.ignore = [" ", "\n", "\t"]
        self.sep = ";"
        self.eval = "()"
        self.body = "{}"
        self.list_def = "[]"
        self.str_def = '""'
        self.comment_def = "''"
        self.indexer = ":"
        self.bool_not = "!"
        self.ops = ["@", ".", "@@", "<-", "<<", "++", "--", "?", "?_", "??", "%", "?#"]
        self.gets = ["+", "*", "/", "**", "=", ">", "<", ">=", "<=", "+_", "#", "&", "|", "int", "float", "str"]
        self.bool = ("true", "false")
        self.null = "null"
        self.values = [Int, Float, Binary, Hex, Octal, Bool, Str, List, Null]
grammar = Grammar()

def eval(token, line, instructs):
    global VARS
    if type(token) in grammar.values: return token
    if type(token) is Eval: return getEval(token.eval, line, instructs)
    if type(token) is Index:
        org = eval(token.org, line, instructs)
        index = eval(token.val, line, instructs)
        expectedType([List, Str], org, line)
        try:
            if type(org) is List: return org.val[index.val]
        except IndexError:
            error(f"list index out of range, {index.val} of {len(org.val) - 1}", line, instructs)
        try:
            if type(org) is Str: return org.val[index.val]
        except IndexError:
            error(f"str index out of range, {index.val} of {len(org.val) - 1}", line, instructs)
    if type(token) is Neg:
        negatee = eval(token.val, line, instructs)
        assert type(negatee) in [Int, Float], error("expected int or float", line, instructs)
        if type(negatee) is Int: return Int(-negatee.val)
        if type(negatee) is Float: return Float(-negatee.val)
    if type(token) is Not:
        t = eval(token.val, line, instructs)
        assert type(t) is Bool, error("expected bool", line, instructs)
        return Bool(not t.val)
    if type(token) is Var:
        assert token.name in VARS, error(f"var '{token.name}' not stored", line, instructs)
        return VARS[token.name]
    error(f"unknown token to evaluate '{token}'", line, instructs)

def getEval(evals, line, instructs):
    global VARS
    expectedType(Get, evals[0], line)
    if evals[0].type == "+":
        expectedExpr(2, evals, line)
        number_type = Int
        t1 = eval(evals[1], line, instructs)
        expectedType([Float, Int], t1, line)
        if type(t1) is Float: number_type = Float
        sum = t1.val
        i = 2
        while i <= len(evals) - 1:
            t = eval(evals[i], line, instructs)
            expectedType([Float, Int], t, line)
            if type(t) is Float: number_type = Float
            sum += t.val
            i += 1
        if number_type is Int:
            return Int(sum)
        if number_type is Float:
            return Float(sum)
    if evals[0].type == "*":
        expectedExpr(2, evals, line)
        number_type = Int
        t1 = eval(evals[1], line, instructs)
        expectedType([Float, Int], t1, line)
        if type(t1) is Float: number_type = Float
        sum = t1.val
        i = 2
        while i <= len(evals) - 1:
            t = eval(evals[i], line, instructs)
            expectedType([Float, Int], t, line)
            if type(t) is Float: number_type = Float
            sum *= t.val
            i += 1
        if number_type is Int:
            return Int(sum)
        if number_type is Float:
            return Float(sum)
    if evals[0].type == "**":
        expectedExpr(2, evals, line)
        number_type = Int
        t1 = eval(evals[1], line, instructs)
        expectedType([Float, Int], t1, line)
        if type(t1) is Float: number_type = Float
        sum = t1.val
        i = 2
        while i <= len(evals) - 1:
            t = eval(evals[i], line, instructs)
            expectedType([Float, Int], t, line)
            if type(t) is Float: number_type = Float
            sum = sum ** t.val
            i += 1
        if number_type is Int:
            return Int(sum)
        if number_type is Float:
            return Float(sum)
    if evals[0].type == "/":
        expectedExpr(2, evals, line)
        t1 = eval(evals[1], line, instructs)
        expectedType([Float, Int], t1, line)
        sum = t1.val
        i = 2
        while i <= len(evals) - 1:
            t = eval(evals[i], line, instructs)
            expectedType([Float, Int], t, line)
            sum /= t.val
            i += 1
        return Float(sum)
    if evals[0].type == "=":
        expectedExpr(2, evals, line)
        t1 = eval(evals[1], line, instructs)
        t2 = eval(evals[2], line, instructs)
        expectedType([Int, Float, Bool, Str], t1, line)
        expectedType([Int, Float, Bool, Str], t2, line)
        return Bool(t1.val == t2.val)
    if evals[0].type == ">":
        expectedExpr(2, evals, line)
        t1 = eval(evals[1], line, instructs)
        t2 = eval(evals[2], line, instructs)
        expectedType([Int, Float], t1, line)
        expectedType([Int, Float], t2, line)
        return Bool(t1.val > t2.val)
    if evals[0].type == "<":
        expectedExpr(2, evals, line)
        t1 = eval(evals[1], line, instructs)
        t2 = eval(evals[2], line, instructs)
        expectedType([Int, Float], t1, line)
        expectedType([Int, Float], t2, line)
        return Bool(t1.val < t2.val)
    if evals[0].type == ">=":
        expectedExpr(2, evals, line)
        t1 = eval(evals[1], line, instructs)
        t2 = eval(evals[2], line, instructs)
        expectedType([Int, Float], t1, line)
        expectedType([Int, Float], t2, line)
        return Bool(t1.val >= t2.val)
    if evals[0].type == "<=":
        expectedExpr(2, evals, line)
        t1 = eval(evals[1], line, instructs)
        t2 = eval(evals[2], line, instructs)
        expectedType([Int, Float], t1, line)
        expectedType([Int, Float], t2, line)
        return Bool(t1.val <= t2.val)
    if evals[0].type == "+_":
        expectedExpr(2, evals, line)
        t1 = eval(evals[1], line, instructs)
        expectedType(Str, t1, line)
        con = t1.val
        i = 2
        while i <= len(evals) - 1:
            t = eval(evals[i], line, instructs)
            expectedType(Str, t, line)
            con += t.val
            i += 1
        return Str(con)
    if evals[0].type == "#":
        expectedExpr(1, evals, line)
        t1 = eval(evals[1], line, instructs)
        expectedType([Str, List], t1, line)
        return Int(len(t1.val))
    if evals[0].type == "&":
        expectedExpr(2, evals, line)
        t1 = eval(evals[1], line, instructs)
        t2 = eval(evals[2], line, instructs)
        expectedType(Bool, t1, line)
        expectedType(Bool, t2, line)
        return Bool(t1.val and t2.val)
    if evals[0].type == "|":
        expectedExpr(2, evals, line)
        t1 = eval(evals[1], line, instructs)
        t2 = eval(evals[2], line, instructs)
        expectedType(Bool, t1, line)
        expectedType(Bool, t2, line)
        return Bool(t1.val or t2.val)
    if evals[0].type == "int":
        expectedExpr(1, evals, line)
        t1 = eval(evals[1], line, instructs)
        expectedType([Float, Int, Str, Bool, Null], t1, line)
        if type(t1) is Null: return Int(0)
        if type(t1) is Int: return t1
        if type(t1) is Float: return Int(int(t1.val))
        if type(t1) is Bool: return Int(1 if t1.val else 0)
        if type(t1) is Str:
            try: return Int(int(t1.val))
            except: error(f"cannot cast str '{t1.val}' to int", line, instructs)
    if evals[0].type == "float":
        expectedExpr(1, evals, line)
        t1 = eval(evals[1], line, instructs)
        expectedType([Float, Int, Str, Bool, Null], t1, line)
        if type(t1) is Null: return Float(0.0)
        if type(t1) is Float: return t1
        if type(t1) is Int: return Float(float(t1.val))
        if type(t1) is Bool: return Float(1.0 if t1.val else 0.0)
        if type(t1) is Str:
            try: return Float(float(t1.val))
            except: error(f"cannot cast str '{t1.val}' to float", line, instructs)
    if evals[0].type == "str":
        expectedExpr(1, evals, line)
        t1 = eval(evals[1], line, instructs)
        expectedType([Float, Int, Str, Bool, Null], t1, line)
        if type(t1) is Null: return Str("null")
        if type(t1) is Str: return t1
        if type(t1) is Int: return Str(str(t1.val))
        if type(t1) is Float: return Str(str(t1.val))
        if type(t1) is Bool: return Str(str(t1))
    error(f"unrecognized get {evals[0].type}", line, instructs)

def interpret(instructs):
    global VARS
    del_var = []
    RETURN = Null()
    returned = False
    for l, line in enumerate(instructs):
        expectedType(Op, line[0], l)
        if line[0].type == "<-":
            expectedExpr(1, line, l)
            if len(line) > 2:
                print(str(eval(Eval(line[1:]), l, instructs)))
            else:
                print(str(eval(line[1], l, instructs)))
            continue
        if line[0].type == "@@":
            expectedExpr(1, line, l)
            expectedType(Var, line[1], l)
            assert not line[1].name in VARS, error(f"var '{line[1].name}' already defined", l, instructs)
            if len(line) > 2:
                if len(line) > 3:
                    val = eval(Eval(line[2:]), l, instructs)
                    assert type(val) in grammar.values, error(f"cannot set var to {val.__class__.__name__}", l, instructs)
                    VARS[line[1].name] = eval(Eval(line[2:]), l, instructs)
                else:
                    VARS[line[1].name] = eval(line[2], l, instructs)
                continue
            else:
                VARS[line[1].name] = Null()
                continue
        if line[0].type == ".":
            expectedExpr(2, line, l)
            expectedType(Var, line[1], l)
            assert line[1].name in VARS, error(f"var '{line[1].name}' is not defined", l, instructs)
            if len(line) > 3:
                VARS[line[1].name] = eval(Eval(line[2:]), l, instructs)
            else:
                VARS[line[1].name] = eval(line[2], l, instructs)
            continue
        if line[0].type == "@":
            expectedExpr(1, line, l)
            expectedType(Var, line[1], l)
            assert not line[1].name in VARS, error(f"var '{line[1].name}' already defined", l, instructs)
            if len(line) > 2:
                if len(line) > 3:
                    val = eval(Eval(line[2:]), l, instructs)
                    assert type(val) in grammar.values, error(f"cannot set var to {val.__class__.__name__}", l,
                                                              instructs)
                    VARS[line[1].name] = eval(Eval(line[2:]), l, instructs)
                else:
                    VARS[line[1].name] = eval(line[2], l, instructs)
                del_var.append(line[1].name)
            else:
                VARS[line[1].name] = Null()
            del_var.append(line[1].name)
            continue
        if line[0].type == "?":
            expectedExpr(2, line, l)
            i = 0
            return_ = Null()
            while i <= len(line) - 1:
                assert type(line[i]) is Op, error(f"unexpected expression {line[i]}", l, instructs)
                op = line[i].type
                assert op in ["?", "??", "?_"], error(f"unexpected expression {op}", l, instructs)
                i += 1
                if i <= len(line) - 1:
                    if op in ["?", "??"]:
                        cond = eval(line[i], l, instructs)
                        assert type(cond) is Bool, error("expected bool", l, instructs)
                        i += 1
                        assert i <= len(line) - 1, error("missing expression", l, instructs)
                        assert type(line[i]) is Body, error("expected body", l, instructs)
                        if cond.val is True:
                            return_, returned = interpret(line[i].content)
                            break
                    if op == "?_":
                        assert i <= len(line) - 1, error("missing expression", l, instructs)
                        assert type(line[i]) is Body, error("expected body", l, instructs)
                        return_, returned = interpret(line[i].content)
                        break
                    i += 1
            if returned:
                RETURN = return_
                break
            continue
        if line[0].type == "%":
            expectedExpr(2, line, l)
            cond = eval(line[1], l, instructs)
            expectedType([Bool, Int], cond, l)
            body = line[2]
            expectedType(Body, body, l)
            return_ = Null()
            if type(cond) is Bool:
                while cond.val:
                    return_, returned = interpret(body.content)
                    if returned: break
                    cond = eval(line[1], l, instructs)
                    expectedType(Bool, cond, l)
            else:
                for i in range(cond.val):
                    return_, returned = interpret(body.content)
                    if returned: break
            if returned:
                RETURN = return_
                break
            continue
        if line[0].type == "?#":
            expectedExpr(2, line, l)
            cond = eval(line[1], l, instructs)
            err_text = eval(line[2], l, instructs)
            expectedType(Bool, cond, l)
            expectedType(Str, err_text, l)
            assert cond.val, exit(err_text)
            continue
        if line[0].type == "++":
            expectedExpr(1, line, l)
            expectedType(Var, line[1], line)
            expectedType([Int, Float], VARS[line[1].name], line)
            VARS[line[1].name].val = VARS[line[1].name].val + 1
            continue
        if line[0].type == "--":
            expectedExpr(1, line, l)
            expectedType(Var, line[1], line)
            expectedType([Int, Float], VARS[line[1].name], line)
            VARS[line[1].name].val = VARS[line[1].name].val - 1
            continue
        if line[0].type == "<<":
            returned = True
            if len(line) > 1:
                if len(line) > 2:
                    RETURN = eval(Eval(line[1:]), l, instructs)
                else:
                    RETURN = eval(line[1], l, instructs)
            break
        error(f"unrecognized op '{line[0].type}'", l, instructs)
    for var in del_var:
        if var in VARS:
            del VARS[var]
    return RETURN, returned

def getVal(raw, index, line, instructs):
    i = index
    # evaluation
    if raw[i] == grammar.eval[0]:
        i += 1
        assert i <= len(raw) - 1, error("unclosed evaluation", line, instructs)
        temp = []
        count = 1
        while i <= len(raw) - 1 and count > 0:
            if raw[i] == grammar.eval[0]:
                count += 1
            if raw[i] == grammar.eval[1]:
                count -= 1
            temp.append(raw[i])
            i += 1
        temp = temp[:-1]
        i -= 1
        assert i <= len(raw) - 1, error("unclosed evaluation", line, instructs)
        return Eval(tokenize(temp)[0]), i # evaluation
    # list
    if raw[i] == grammar.list_def[0]:
        i += 1
        assert i <= len(raw) - 1, error("unclosed evaluation", line, instructs)
        temp = []
        count = 1
        while i <= len(raw) - 1 and count > 0:
            if raw[i] == grammar.list_def[0]:
                count += 1
            if raw[i] == grammar.list_def[1]:
                count -= 1
            temp.append(raw[i])
            i += 1
        temp = temp[:-1]
        i -= 1
        assert i <= len(raw) - 1, error("unclosed evaluation", line, instructs)
        l = tokenize(temp)
        assert len(l) == 1, error("';' not allowed in list", line, instructs)
        for val in l[0]:
            if not type(val) in grammar.values:
                error(f"cannot store {val} in list", line, instructs)
        return List(l[0]), i # evaluation
    # bool
    if raw[i] in grammar.bool: return Bool(raw[i] == grammar.bool[0]), i
    # null
    if raw[i] in grammar.null: return Null(), i
    # int
    try: return Int(int(raw[i])), i
    except: pass
    # float
    try: return Float(float(raw[i])), i
    except: pass
    if raw[i][0] in letters:
        return Var(raw[i]), i
    error(f"unknown expression '{raw[i]}'", line, instructs)

def tokenize(raw: list):
    instructs = [[]]
    line = 0
    i = 0
    while i <= len(raw) - 1:
        if raw[i] in grammar.ignore:
            i += 1
            continue
        # string
        if raw[i] == grammar.str_def[0]:
            i += 1
            assert i <= len(raw) - 1, error("missing expression", line, instructs)
            temp = ""
            while i <= len(raw) - 1:
                if raw[i] == grammar.str_def[1]:
                    break
                else:
                    temp += raw[i]
                i += 1
            assert i <= len(raw) - 1, error("unclosed string", line, instructs)
            instructs[line].append(Str(temp))
            i += 1
            continue
        # seperator
        if raw[i] in grammar.sep:
            if len(instructs[line]) > 0:
                instructs.append([])
                line += 1
            i += 1
            continue
        # body
        if raw[i] == grammar.body[0]:
            start_index = i
            i += 1
            assert i <= len(raw) - 1, error("unclosed body", line, instructs)
            temp = []
            count = 1
            while i <= len(raw) - 1 and count > 0:
                if raw[i] == grammar.body[0]:
                    count += 1
                if raw[i] == grammar.body[1]:
                    count -= 1
                temp.append(raw[i])
                i += 1
            temp = temp[:-1]
            i -= 1
            assert i <= len(raw) - 1, error("unclosed body", line, instructs)
            instructs[line].append(Body(tokenize(temp)))
            i += 1
            continue
        # operation
        if raw[i] in grammar.ops:
            instructs[line].append(Op(raw[i]))
            i += 1
            continue
        # get
        if raw[i] in grammar.gets:
            instructs[line].append(Get(raw[i]))
            i += 1
            continue
        # index
        if raw[i] == grammar.indexer:
            i += 1
            assert i <= len(raw) - 1, error("missing expression", line, instructs)
            val, i = getVal(raw, i, line, instructs)

            org = instructs[line][-1]
            instructs[line] = instructs[line][:-1]
            instructs[line].append(Index(org, val))
            i += 1
            continue
        # negate
        if raw[i] == "-":
            i += 1
            while (raw[i] in grammar.ignore) and i <= len(raw) - 1:
                i += 1
            assert i <= len(raw) - 1, error("missing expression", line, instructs)
            val, i = getVal(raw, i, line, instructs)
            if type(val) is Int:
                instructs[line].append(Int(-val.val))
            elif type(val) is Float:
                instructs[line].append(Float(-val.val))
            else:
                instructs[line].append(Neg(val))
            i += 1
            continue
        # not
        if raw[i] == grammar.bool_not:
            i += 1
            while (raw[i] in grammar.ignore) and i <= len(raw) - 1:
                i += 1
            assert i <= len(raw) - 1, error("missing expression", line, instructs)
            val = tokenize(raw[i])[0][0]
            instructs[line].append(Not(val))
            i += 1
            continue
        # bool
        if raw[i] in grammar.bool:
            instructs[line].append(Bool(raw[i] == grammar.bool[0]))
            i += 1
            continue
        # null
        if raw[i] in grammar.null:
            instructs[line].append(Null())
            i += 1
            continue
        # var
        val, i = getVal(raw, i, line, instructs)
        if not val is None:
            instructs[line].append(val)
        i += 1
    while [] in instructs:
        instructs.remove([])
    return instructs

if not len(sys.argv) > 1:
    sys.argv.append("test.sy")
with open(sys.argv[1], "r") as f:
    dev = False
    # raw
    raw = []
    temp = ""
    for c in f.read():
        if c in ([" ", "\n", "\t"] + list(grammar.sep) + list(grammar.eval) + list(grammar.list_def) + list(grammar.indexer) + list(grammar.str_def)  + list(grammar.comment_def) + list(grammar.bool_not)):
            if not temp == "":
                raw.append(temp)
            raw.append(c)
            temp = ""
        else:
            temp += c
    if not temp == "":
        raw.append(temp)
    # comment clearing
    i = 0
    while i < len(raw):
        if raw[i] == "'":
            raw.pop(i)
            while i < len(raw):
                if raw[i] == "'":
                    raw.pop(i)
                    break
                else:
                    raw.pop(i)
        i += 1
    # tokenize
    if dev: print(raw)
    instructs = tokenize(raw)
    # interpret
    if dev: print(program2text(instructs))
    if dev: print("<< out >>")
    VARS = {}
    RETURN, returned = interpret(instructs)
    if returned:
        print("out: ", end="")
        print(RETURN)
    if dev:
        print("vars: ", end="")
        print(VARS)