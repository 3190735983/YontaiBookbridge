# 检索
# 搜索框是文书内容的全文搜索，并类似知网提供筛选条件(高级检索)
from flask import Blueprint

searcher_bp=Blueprint('searcher',__name__,template_folder='app/templates/searcher',static_folder='app/static/searcher',url_prefix='/searcher')
