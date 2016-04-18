# coding=utf-8
# Created by Tian Yuanhao on 2016/4/17.
import traceback

from file_handler.data_dict import DataDict
from file_handler.table_file import TableFile
from frontend.nodes import NodeType
from config.config import *
import os


def execute_create_table(node):
    data_dict = DataDict(DATA_DICT_PATH)
    if data_dict.has_table(node.table_name):
        print "Error: This table already exists."
        return
    else:
        data_dict.dict[node.table_name] = node.attr_list
        data_dict.write_back()


def execute_show_tables(node):
    data_dict = DataDict(DATA_DICT_PATH)
    print data_dict.tables_name()


def execute_insert(node):
    data_dict = DataDict(DATA_DICT_PATH)
    if not data_dict.has_table(node.table_name):
        print "Error: The table does not exist."
        return
    table = TableFile(data_dict, node.table_name, node.value_list)
    table.insert()


def execute_drop_table(node):
    data_dict = DataDict(DATA_DICT_PATH)
    if not data_dict.has_table(node.table_name):
        print "Error: The table does not exist."
        return
    del data_dict.dict[node.table_name]     # remove data dict
    data_dict.write_back()
    os.remove(TABLES_PATH + node.table_name) # remove table file
    # TODO remove index
    print "Drop table successful."


def print_table(names, data, width = COLUMN_WIDTH):
    table = "┌"
    n = len(names)
    for i in range(n): table += "─" * width + ("┬" if i != n - 1 else "┐\n")
    fmt = "│%" + str(width*2) + "s"
    for name in names: table += fmt % name
    table += "│\n├"
    for i in range(n): table += "─" * width + ("┼" if i != n - 1 else "┤\n")
    for line in data:
        for item in line: table += fmt % item
        table += "│\n"
    table += "└"
    for i in range(n): table += "─" * width + ("┴" if i != n - 1 else "┘\n")
    print table.decode('utf-8')


def execute_print_table(node):
    data_dict = DataDict(DATA_DICT_PATH)
    if not data_dict.has_table(node.table_name):
        print "Error: The table does not exist."
        return
    names = data_dict.table_attr_names(node.table_name)
    data = TableFile(data_dict, node.table_name).load_data()
    print_table(names, data)


def execute_alert(node):
    data_dict = DataDict(DATA_DICT_PATH)
    if not data_dict.has_table(node.table_name):
        print "Error: The table does not exist."
        return
    names = data_dict.table_attr_names(node.table_name)
    table = TableFile(data_dict, node.table_name)
    data = table.load_data()
    if node.op == "ADD":
        if node.attr_list.attr_name in names:
            print "Error: The attr's name already exists."
            return
        data_dict.dict[node.table_name] += [node.attr_list]
        for idx in range(len(data)): data[idx].append("0")
    elif node.op == "DROP":
        attr_name = node.attr_list[0]
        if attr_name not in names:
            print "Error: The attr's name does not exist."
            return
        old_list = data_dict.dict[node.table_name]
        data_dict.dict[node.table_name] = [attr for attr in old_list if attr.attr_name != attr_name]
        idx_remove = names.index(attr_name)
        for idx in range(len(data)): del data[idx][idx_remove]
    table.data_list = data
    table.write_back()
    data_dict.write_back()


def execute_delete(node):
    data_dict = DataDict(DATA_DICT_PATH)
    if not data_dict.has_table(node.table_name):
        print "Error: The table does not exist."
        return
    names = data_dict.table_attr_names(node.table_name)
    table = TableFile(data_dict, node.table_name)
    data = table.load_data()
    try:
        table.data_list = [line for line in data if not check_where(node.where_list, names, line)]
    except Exception, e:
        print "Error: %s." % e
    table.write_back()


def set_value(data, names, set_list):
    # print "set_value() data:" + str(data)
    dict = {}
    for idx in range(len(names)): dict[names[idx]] = data[idx]
    left = set_list[0].attr_name
    a = __get_value(set_list[0], dict)
    b = __get_value(set_list[1], dict)

    if type(a) != type(b):
        raise Exception("Type not match.")
    data[names.index(left)] = b


def execute_update(node):
    data_dict = DataDict(DATA_DICT_PATH)
    if not data_dict.has_table(node.table_name):
        print "Error: The table does not exist."
        return
    names = data_dict.table_attr_names(node.table_name)
    table = TableFile(data_dict, node.table_name)
    data = table.load_data()
    try:
        for idx in range(len(data)):
            if check_where(node.where_list, names, data[idx]):
                set_value(data[idx], names, node.set_list)
    except Exception, e:
        print "Error: %s." % e
        print traceback.format_exc()
        return
    table.write_back()


def execute_select(node):
    pass


def __get_value(node, dict):
    if node.type == NodeType.relation_attr:
        return dict[node.attr_name]
    else:
        return node.value


def __check_node(node, dict):
    assert(node.type == NodeType.condition)
    if node.op == "AND":
        return __check_node(node.left, dict) and __check_node(node.right, dict)
    elif node.op == "OR":
        return __check_node(node.left, dict) or __check_node(node.right, dict)
    elif node.op == ">=":
        return __get_value(node.left, dict) >= __get_value(node.right, dict)
    elif node.op == "<=":
        return __get_value(node.left, dict) <= __get_value(node.right, dict)
    elif node.op == ">":
        return __get_value(node.left, dict) > __get_value(node.right, dict)
    elif node.op == "<":
        return __get_value(node.left, dict) < __get_value(node.right, dict)
    elif node.op == "=":
        return __get_value(node.left, dict) == __get_value(node.right, dict)
    elif node.op == "!=":
        return __get_value(node.left, dict) != __get_value(node.right, dict)


def check_where(where_node, names, data_line):
    dict = {}
    for idx in range(len(names)):
        dict[names[idx]] = data_line[idx]
    return __check_node(where_node, dict)


def execute_main(command):
    """
    执行相应sql命令
    :param command: sql语法树根节点
    :return:
    """
    type = command.type
    if type == NodeType.create_table:
        execute_create_table(command)
    elif type == NodeType.show_tables:
        execute_show_tables(command)
    elif type == NodeType.drop_table:
        execute_drop_table(command)
    elif type == NodeType.insert:
        execute_insert(command)
    elif type == NodeType.alert:
        execute_alert(command)
    elif type == NodeType.delete:
        execute_delete(command)
    elif type == NodeType.update:
        execute_update(command)
    elif type == NodeType.select:
        execute_select(command)
    elif type == NodeType.print_table:
        execute_print_table(command)
