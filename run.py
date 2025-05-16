from app import create_app
from app.models import get_all_servants, get_servant_by_name, search_servants

app = create_app()

# 测试数据库功能
if __name__ == '__main__':
    with app.app_context():
        # # print("测试数据库功能...")
        
        # # 获取所有从者
        # servants = get_all_servants()
        # print(f"共有 {len(servants)} 个从者")
        
        # # 通过名称获取从者
        # artoria = get_servant_by_name("阿尔托莉雅·潘德拉贡")
        # if artoria:
        #     print(f"找到从者: {artoria.name}, 职介: {artoria.class_name}, 特性: {artoria.traits}")
        # else:
        #     print("未找到阿尔托莉雅·潘德拉贡")
            
        # # 通过别名获取从者
        # gil = get_servant_by_name("金闪闪")
        # if gil:
        #     print(f"通过别名找到从者: {gil.name}, 职介: {gil.class_name}, 别名: {gil.aliases}")
        # else:
        #     print("未找到金闪闪")
        
        # # 搜索从者
        # search_results = search_servants("莉雅")
        # if search_results:
        #     print(f"搜索结果: {', '.join(s.name for s in search_results)}")
        # else:
        #     print("未找到匹配的从者")
        ...
            
    # 运行Flask应用
    app.run(host='0.0.0.0', port=68000, debug=False)