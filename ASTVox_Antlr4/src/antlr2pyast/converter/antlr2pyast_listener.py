# Listener class for converting ANTLR4 AST tree to Python AST tree.
# This class follows the standard Listener interface of ANTLR4.
# For readability, the actual implementation of the member methods are
# provided in separate Python files

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener
from antlr4.error import ErrorListener

# PyAST package
import ast

# Actual implementation of the member methods
from . import atom_name_terminals
from . import expr
from . import basic_rules
from . import flow_stmts
from . import test_stmts
from . import loop_stmts
from . import funcdef
from . import comprehensions
from . import classdef

class antlr2pyast_listener(Python3ParserListener):
    def __init__(self):
        #self.pyast_trees = {}
        return
        
    # Exit a parse tree produced by Python3Parser#atom.
    def exitAtom(self, ctx:Python3Parser.AtomContext):
        atom_name_terminals.convert_atom(self, ctx)

    # Exit a parse tree produced by Python3Parser#name.
    def exitName(self, ctx:Python3Parser.NameContext):
        atom_name_terminals.convert_name(self, ctx)

    # Exit a parse tree produced by Python3Parser#atom_expr.
    def exitAtom_expr(self, ctx:Python3Parser.Atom_exprContext):
        atom_name_terminals.convert_atom_expr(self, ctx)

    # Exit a parse tree produced by Python3Parser#expr.
    def exitExpr(self, ctx:Python3Parser.ExprContext):
        expr.convert_expr(self, ctx)

    # Exit a parse tree produced by Python3Parser#comparison.
    def exitComparison(self, ctx:Python3Parser.ComparisonContext):
        test_stmts.convert_comparison(self, ctx)

    # Exit a parse tree produced by Python3Parser#not_test.
    def exitNot_test(self, ctx:Python3Parser.Not_testContext):
        test_stmts.convert_not_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#and_test.
    def exitAnd_test(self, ctx:Python3Parser.And_testContext):
        test_stmts.convert_and_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#or_test.
    def exitOr_test(self, ctx:Python3Parser.Or_testContext):
        test_stmts.convert_or_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#test.
    def exitTest(self, ctx:Python3Parser.TestContext):
        test_stmts.convert_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#testlist_star_expr.
    def exitTestlist_star_expr(self,
                               ctx:Python3Parser.Testlist_star_exprContext):
        expr.convert_testlist_star_expr(self, ctx)

    # Exit a parse tree produced by Python3Parser#expr_stmt.
    def exitExpr_stmt(self, ctx:Python3Parser.Expr_stmtContext):
        expr.convert_expr_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#simple_stmt.
    def exitSimple_stmt(self, ctx:Python3Parser.Simple_stmtContext):
        basic_rules.convert_simple_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#simple_stmts.
    def exitSimple_stmts(self, ctx:Python3Parser.Simple_stmtsContext):
        basic_rules.convert_simple_stmts(self, ctx)

    # Exit a parse tree produced by Python3Parser#single_input.
    def exitSingle_input(self, ctx:Python3Parser.Single_inputContext):
        basic_rules.convert_single_input(self, ctx)

    # Exit a parse tree produced by Python3Parser#return_stmt.
    def exitReturn_stmt(self, ctx:Python3Parser.Return_stmtContext):
        flow_stmts.convert_return(self, ctx)

    # Exit a parse tree produced by Python3Parser#flow_stmt.
    def exitFlow_stmt(self, ctx:Python3Parser.Flow_stmtContext):
        flow_stmts.convert_flow_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#testlist.
    def exitTestlist(self, ctx:Python3Parser.TestlistContext):
        test_stmts.convert_testlist(self, ctx)

    # Exit a parse tree produced by Python3Parser#block.
    def exitBlock(self, ctx:Python3Parser.BlockContext):
        basic_rules.convert_block(self, ctx)

    # Exit a parse tree produced by Python3Parser#for_stmt.
    def exitFor_stmt(self, ctx:Python3Parser.For_stmtContext):
        loop_stmts.convert_for_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#exprlist.
    def exitExprlist(self, ctx:Python3Parser.ExprlistContext):
        expr.convert_exprlist(self, ctx)

    # Exit a parse tree produced by Python3Parser#compound_stmt.
    def exitCompound_stmt(self, ctx:Python3Parser.Compound_stmtContext):
        basic_rules.convert_compound_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#comp_op.
    def exitComp_op(self, ctx:Python3Parser.Comp_opContext):
        test_stmts.convert_comp_op(self, ctx)

    # Exit a parse tree produced by Python3Parser#while_stmt.
    def exitWhile_stmt(self, ctx:Python3Parser.While_stmtContext):
        loop_stmts.convert_while_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#if_stmt.
    def exitIf_stmt(self, ctx:Python3Parser.If_stmtContext):
        flow_stmts.convert_if_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#stmt.
    def exitStmt(self, ctx:Python3Parser.StmtContext):
        basic_rules.convert_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#star_expr.
    def exitStar_expr(self, ctx:Python3Parser.Star_exprContext):
        expr.convert_star_expr(self, ctx)

    # Exit a parse tree produced by Python3Parser#testlist_comp.
    def exitTestlist_comp(self, ctx:Python3Parser.Testlist_compContext):
        test_stmts.convert_testlist_comp(self, ctx)

    # Exit a parse tree produced by Python3Parser#dictorsetmaker.
    def exitDictorsetmaker(self, ctx:Python3Parser.DictorsetmakerContext):
        atom_name_terminals.convert_dictorsetmaker(self, ctx)

    # Exit a parse tree produced by Python3Parser#tfpdef.
    def exitTfpdef(self, ctx:Python3Parser.TfpdefContext):
        funcdef.convert_tfpdef(self, ctx)

    # Exit a parse tree produced by Python3Parser#typedargslist.
    def exitTypedargslist(self, ctx:Python3Parser.TypedargslistContext):
        funcdef.convert_typedargslist(self, ctx)

    # Exit a parse tree produced by Python3Parser#parameters.
    def exitParameters(self, ctx:Python3Parser.ParametersContext):
        funcdef.convert_parameters(self, ctx)

    # Exit a parse tree produced by Python3Parser#funcdef.
    def exitFuncdef(self, ctx:Python3Parser.FuncdefContext):
        funcdef.convert_funcdef(self, ctx)

    # Exit a parse tree produced by Python3Parser#test_nocond.
    def exitTest_nocond(self, ctx:Python3Parser.Test_nocondContext):
        test_stmts.convert_test_nocond(self, ctx)

    # Exit a parse tree produced by Python3Parser#comp_iter.
    def exitComp_iter(self, ctx:Python3Parser.Comp_iterContext):
        comprehensions.convert_comp_iter(self, ctx)

    # Exit a parse tree produced by Python3Parser#comp_for.
    def exitComp_for(self, ctx:Python3Parser.Comp_forContext):
        comprehensions.convert_comp_for(self, ctx)

    # Exit a parse tree produced by Python3Parser#comp_if.
    def exitComp_if(self, ctx:Python3Parser.Comp_ifContext):
        comprehensions.convert_comp_if(self, ctx)
        
    # Exit a parse tree produced by Python3Parser#arglist.
    def exitArglist(self, ctx:Python3Parser.ArglistContext):
        classdef.convert_arglist(self, ctx)

    # Exit a parse tree produced by Python3Parser#argument.
    def exitArgument(self, ctx:Python3Parser.ArgumentContext):
        classdef.convert_argument(self, ctx)

    # Exit a parse tree produced by Python3Parser#classdef.
    def exitClassdef(self, ctx:Python3Parser.ClassdefContext):
        classdef.convert_classdef(self, ctx)

    # Exit a parse tree produced by Python3Parser#trailer.
    def exitTrailer(self, ctx:Python3Parser.TrailerContext):
        atom_name_terminals.convert_trailer(self, ctx)


    # Exit a parse tree produced by Python3Parser#sliceop.
    def exitSliceop(self, ctx:Python3Parser.SliceopContext):
        atom_name_terminals.convert_sliceop(self, ctx)

    # Exit a parse tree produced by Python3Parser#subscript_.
    def exitSubscript_(self, ctx:Python3Parser.Subscript_Context):
        atom_name_terminals.convert_subscript_(self, ctx)

    # Exit a parse tree produced by Python3Parser#subscriptlist.
    def exitSubscriptlist(self, ctx:Python3Parser.SubscriptlistContext):
        atom_name_terminals.convert_subscriptlist(self, ctx)

    # Exit a parse tree produced by Python3Parser#dotted_as_name.
    def exitDotted_as_name(self, ctx:Python3Parser.Dotted_as_nameContext):
        basic_rules.convert_dotted_as_name(self, ctx)

    # Exit a parse tree produced by Python3Parser#dotted_as_names.
    def exitDotted_as_names(self, ctx:Python3Parser.Dotted_as_namesContext):
        basic_rules.convert_dotted_as_names(self, ctx)

    # Exit a parse tree produced by Python3Parser#import_name.
    def exitImport_name(self, ctx:Python3Parser.Import_nameContext):
        basic_rules.convert_import_name(self, ctx)

    # Exit a parse tree produced by Python3Parser#import_stmt.
    def exitImport_stmt(self, ctx:Python3Parser.Import_stmtContext):
        basic_rules.convert_import_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#import_as_name.
    def exitImport_as_name(self, ctx:Python3Parser.Import_as_nameContext):
        basic_rules.convert_import_as_name(self, ctx)

    # Exit a parse tree produced by Python3Parser#import_as_names.
    def exitImport_as_names(self, ctx:Python3Parser.Import_as_namesContext):
        basic_rules.convert_import_as_names(self, ctx)

    # Exit a parse tree produced by Python3Parser#import_from.
    def exitImport_from(self, ctx:Python3Parser.Import_fromContext):
        basic_rules.convert_import_from(self, ctx)

    # Exit a parse tree produced by Python3Parser#break_stmt.
    def exitBreak_stmt(self, ctx:Python3Parser.Break_stmtContext):
        flow_stmts.convert_break_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#continue_stmt.
    def exitContinue_stmt(self, ctx:Python3Parser.Continue_stmtContext):
        flow_stmts.convert_continue_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#raise_stmt.
    def exitRaise_stmt(self, ctx:Python3Parser.Raise_stmtContext):
        flow_stmts.convert_raise_stmt(self, ctx)


        
# custom error listener to suppress the output of early EOF error to console.
# i.e., the partial statement error.
class antlr2pyast_error_listener(ErrorListener.ErrorListener):

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if offendingSymbol.type == -1:
            # -1 is EOF, statement terminates early.
            # not a problem for screen reader, we read partial statments 
            pass
        else:
            print(msg)
            raise Exception("Syntax Error")

    # disable the default console output error listener
    def disable_builtin_console_output(self, parser: Python3Parser):
        for l in parser._listeners: #supress the console error reporting
            if isinstance(l, antlr4.error.ErrorListener.ConsoleErrorListener):
                parser._listeners.remove(l)
                break

  # ignore other errors for now
  # def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact,
  #                     ambigAlts, configs):
  #   raise Exception("report ambiguity")

  # def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex,
  #                                 conflictingAlts, configs):
  #   raise Exception("report attempting full context")

  # def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex,
  #                              prediction, configs):
  #   raise Exception("report context sensitivity")


    

