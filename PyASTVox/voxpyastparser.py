import ast
from pprint import pprint

# class for the object used for returns from emit functions
# making the return to a class to make it easier for future expension
class Speech:
    def __init__(self):  # initialize member variables
        self.text = []  # used to hold the generate speech text
        self.data = {}  # used to hold other data
        return

class astparser:
    # init function. does nothing at the moment
    def __init__(self):
        return

    # helper function to study the internal of a ast node
    def ast_node_explore(self, node):
        # print("Iter fields")
        for field, value in ast.iter_fields(node):
            print(field, value)

        print("Iter children")
        for child in ast.iter_child_nodes(node):
            print(child)


    # generate dict key for statements
    def gen_Dict_Key(self, node, level):
        if isinstance(node, ast.Expr):
            return "ExprStmt-" + str(level)
        elif isinstance(node, ast.BinOp):
            return "BinOpStmt-" + str(level)
        elif isinstance(node, ast.Assign):
            return "BinOpStmt-" + str(level)

    # parse an ast.Add/Mult/Assi... node
    def emit_Opcode(self, node):
        if isinstance(node, ast.Add):
            return 'plus'
        elif isinstance(node, ast.Mult):
            return 'multiply'
        elif isinstance(node, ast.Sub):
            return "subtract"
        elif isinstance(node, ast.Div):
            return "divide"
        elif isinstance(node, ast.Mod):
            return "Mod"
        elif isinstance(node, ast.FloorDiv):
            return "FloorDiv"
        elif isinstance(node, ast.MatMult):
            return "MatMult"
        else:
            raise Exception("Unknown Opcode" + str(node))


    # generate speech for comparison
    def emit_compare(self, node, level):

        # create an empty array to hold the values
        speech = Speech()
        
        # handle left operand
        print(node.left)
        left_speech = self.emit(node.left)
        
        # handle the comparator
        ops = node.ops[0]
        
        if isinstance(ops, ast.NotIn):
            op_text = "not in"
        elif isinstance(ops, ast.Lt):
            print('less than')
            op_text = "less than"
        elif isinstance(ops, ast.Gt):
            op_text = "greater than"
        elif isinstance(ops, ast.GtE):
            op_text = "great than equal to"
        elif isinstance(ops, ast.LtE):
            op_text = "less than equal to"
        elif isinstance(ops, ast.Eq):
            op_text = "equal to"
        elif isinstance(ops, ast.NotEq):
            op_text = "not equal to"
        elif isinstance(ops, ast.Is):
            op_text = "Is"
        elif isinstance(ops, ast.If):
            op_text = "if"
        else:
            raise Exception("Unknown Opcode" + str(test))

        # handle the right operand
        # this only handles one right operand, not sure what multi-operand test
        # look like
        for right_opr in node.comparators:
            right_speech = self.emit(right_opr)
            
            speech.text = left_speech.text + " " + op_text + " " + right_speech.text
            
        return speech


    # parse an ast.Name code and # parse an ast.Num code$$ Helping extract the
    # num part from the comparators
    def emit_Name(self, node):
        speech = Speech()
        
        speech.text = node.id
        speech.data = ast.dump(node)

        return speech

    # parse an ast.Num code$$ Helping extract the num part from the comparators
    def emit_Num(self, node, level):
        speech = Speech()

        speech.text = str(node.n)
        speech.data = ast.dump(node)

        return speech


    # emit for Assign nodes
    def emit_Assign(self, node, level):
        # an empty array that holds a value is created
        speech = Speech()
        
        # handles the LHS of assigments
        target_str = []

        # there could be multiple targets, i.e., multiple variables being
        # assigned values to. Cannot handle this multi-target case yet.
        # need to implement tuple support
        for target in node.targets:
            target_str.append(self.emit(target).text)

            # handles the RHS of assigment
            value_str = self.emit(node.value).text

        #   language specification based on number of items in target_str
        if (len(target_str) == 1):
            speech.text = ",".join(target_str)
            speech.text = speech.text + " is assigned with " + value_str
        else:
            speech.text = ",".join(target_str)
            speech.text = speech.text + " are assigned with " + value_str

        return speech


    # emit for BinOp nodes
    def emit_BinOp(self, node, level):
        # create an empty array to hold the values
        speech = Speech()
        
        # generate speech for left operand
        left_speech = self.emit(node.left, level+1)
        
        # visit operation
        speech.data['op'] = self.emit_Opcode(node.op)
        
        # generate speech for right operand
        right_speech = self.emit(node.right, level+1)
        
        speech.text = (left_speech.text + " " +
                       speech.data['op'] + " " +
                       right_speech.text)

        return speech

    # parse an ast.Return statment
    # current probably only handles returning a variable or a number
    def emit_Return(self, node, level):
        speech = Speech()
        
        # generate speech for return value
        ret_val_speech = self.emit(node.value)
        
        # combine and generate speech
        speech.text = "return value " + ret_val_speech.text
        
        return speech

    # emit for ast.If
    def emit_IfExp(self, node, level):
        # create an empty array to hold the values
        speech = Speech()
        
        # generate the speech for the test
        # I use emit() here to make the processing generic
        test_speech = self.emit(node.test, level+1)
        
        # generate the speech for the body
        # again, I use emit() here to make the processing generic
        for stmt in node.body:
            body_speech = self.emit(stmt, level+1)
            
        # combine speech
        speech.text = "if statement with the test is " + test_speech.text
        speech.text = speech.text + " and the body is " + body_speech.text
        
        return speech


    # emit for ast.Expr
    def emit_Expr(self, node, level):
        speech = Speech()
        # for each child, emit the speech for it
        # !!! This is very likely WRONG: only tested1 for BinOp child.
        # This will also only return the speech of the last child
        for child in ast.iter_child_nodes(node):
            speech = self.emit(child, level + 1)

        return speech


    # emit for ast.Module
    def emit_Module(self, node, level):
        # for each child, emit the speech for it
        # !!! This is likely WRONG: I don't know how many children there
        # can be in a Module node. So "speech" will be set by
        # only the last child
        for child in ast.iter_child_nodes(node):
            speech = self.emit(child, level + 1)

        return speech


    # emit: the main entrance function
    # It calls the emit function for each type of nodes
    #
    def emit(self, node, level=0):
        # for each type of the node, call the corresponding emit function
        if isinstance(node, ast.Module):
            return self.emit_Module(node, level)
        if isinstance(node, ast.Expr):
            return self.emit_Expr(node, level)
        elif isinstance(node, ast.BinOp):
            return self.emit_BinOp(node, level)
        elif isinstance(node, ast.Assign):
            return self.emit_Assign(node, level)
        elif isinstance(node, ast.If):
            return self.emit_IfExp(node, level)
        elif isinstance(node, ast.Compare):
            return self.emit_compare(node, level)
        elif isinstance(node, ast.Name):
            return self.emit_Name(node)
        elif isinstance(node, ast.Num):
            return self.emit_Num(node, level)
        elif isinstance(node, ast.Return):
            return self.emit_Return(node, level)
        else:
            print("Unhandled node type:", type(node))
            return
