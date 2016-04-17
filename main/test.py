# coding=utf-8
# Created by Tian Yuanhao on 2016/4/5.
from string import upper

from frontend.lexer import lexer as lex
from frontend.parser import parser

create_table_test = """
create table A(
  name char(10),
  age int,
  grade int,
  id int,
  PRIMARY KEY (id)
);
"""

insert_test = "insert into A values(1, 2, 3, 'ABC'), (3, 4, 5, 'CDF');"

delete_test = "delete from A where id = 1;"

update_test = "update A set age = 1 where id > 100;"

print_test = "print A;"

alert_add_test = "alert table A add num char(20);"

alert_drop_test = "alert table A drop num;"

drop_table_test = "drop table A;"

res = parser.parse(alert_drop_test, lexer=lex)
print vars(res)

