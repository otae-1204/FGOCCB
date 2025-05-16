import requests
import re
import json
import time
from app.db import get_db_connection
from app.admin import add_servant, update_servant
from app.models import Servant

# 可用的FGO API端点
SERVANT_LIST_API = "https://fgo.wiki/api.php?action=query&list=categorymembers&cmtitle=Category:英灵图鉴&cmlimit=500&format=json"
API_BASE_URL = "https://fgo.wiki/api.php?action=query&prop=extracts|pageprops|revisions&pageid={}&rvprop=content&format=json"
SERVANT_NICKNAME_API = "https://fgo.wiki/api.php?action=query&list=backlinks&bltitle={}&blfilterredir=redirects&format=json"

# 获取从者列表
def fetch_servant_list():
    """获取从者列表"""
    try:
        response = requests.get(SERVANT_LIST_API)
        response.raise_for_status()
        data = response.json()
        servant_list = data.get('query', {}).get('categorymembers', [])
        # 处理从者列表
        servant_list = [item['title'] for item in servant_list if item['ns'] == 0]
        return data.get('query', {}).get('categorymembers', [])
    except Exception as e:
        print(f"获取从者列表失败: {e}")
        return []

# 从者详细信息提取函数
def extract_servant_details(servant_name, servant_info):
    """从Wiki文本中提取从者详细信息"""
    # 创建结果字典
    result = {"name": servant_name}
    
    # 定义提取函数
    def extract_value(pattern, default="未知", is_int=False, post_process=None):
        match = re.search(pattern, servant_info)
        if match:
            value = match.group(1).strip()
            if is_int and value:
                try:
                    return int(value)
                except ValueError:
                    return default
            elif post_process:
                return post_process(value)
            else:
                return value
        return default
    
    # 提取基本信息
    result["access"] = extract_value(r'\|获取途径=([^\n]*)\n\|', "未知")
    result["id"] = extract_value(r'\|序号=([^\n]*)\n\|', 0, is_int=True)
    result["class_name"] = extract_value(r'\|职阶=([^\n]*)\n\|')
    result["rarity"] = extract_value(r'\|稀有度=([^\n]*)\n\|', 0, is_int=True)
    result["gender"] = extract_value(r'\|性别=([^\n]*)\n\|')
    result["attribute"] = extract_value(r'\|副属性=([^\n]*)\n\|')
    
    # 提取宝具类型
    np_type = extract_value(r'\|类型=([^\n]*)\n\|')
    result["noble_phantasm_type"] = f"{np_type}宝具" if np_type != "未知" else "未知"
    
    # 提取宝具色卡
    result["noble_phantasm_card"] = extract_value(r'\|卡色=([^\n]*)\n\|')
    
    # 提取战斗数值
    result["atk_90"] = extract_value(r'\|满级ATK=([^\n]*)\n\|', 0, is_int=True)
    result["hp_90"] = extract_value(r'\|满级HP=([^\n]*)\n\|', 0, is_int=True)
    
    # 提取多值属性
    # 属性 (可能有多个)
    alignment_matches = re.findall(r'\|属性(\d+)=([^\n]*)\n', servant_info)
    result["alignment"] = [match[1] for match in alignment_matches] if alignment_matches else ["未知"]
    
    # 提取特性
    trait_matches = re.findall(r'\|特性(\d+)=([^\n]*)\n', servant_info)
    result["traits"] = [match[1] for match in trait_matches] if trait_matches else []
    
    # 提取指令卡配置
    card_deck = []
    for i in ["一", "二", "三", "四", "五"]:
        card = extract_value(rf'\|第{i}张卡=([^\n]*)\n', "未知")
        card_deck.append(card[0] if card and card != "未知" else "未知")
    result["card_deck"] = card_deck
    
    return result

# 获取从者详细信息
def fetch_servant_detail(servant_name):
    """获取单个从者详细信息"""
    try:
        # 使用从者名称获取页面ID
        response = requests.get(f"https://fgo.wiki/api.php?action=query&prop=revisions&rvprop=content&titles={servant_name}&format=json")
        response.raise_for_status()
        data = response.json()

        pageid = list(data.get('query', {}).get('pages', {}).keys())[0]
        servant_info = data.get('query', {}).get('pages', {}).get(pageid, {}).get('revisions', [{}])[0].get('*', '')
        
        # 提取从者详情
        servant_details = extract_servant_details(servant_name, servant_info)
        
        # 如果从者不可被获取，返回None
        if servant_details["access"] == "无法召唤":
            print(f"从者 {servant_name} 不可被获取")
            return None
        
        # 输出提取到的信息
        for key, value in servant_details.items():
            print(f"{key}: {value}")

        return servant_details
    except Exception as e:
        print(f"获取从者详情失败: {e}")
        return None

# 获取从者别名
def fetch_servant_nicknames(servant_name):
    """获取从者的别名
    
    Args:
        servant_name: 从者名称
        
    Returns:
        list: 返回从者别名列表
    """
    try:
        # URL编码从者名称，处理特殊字符
        encoded_name = requests.utils.quote(servant_name)
        url = SERVANT_NICKNAME_API.format(encoded_name)
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # 使用列表推导式获取所有不等于原名的标题作为别名
        nicknames = [item.get('title') for item in data.get('query', {}).get('backlinks', []) 
                    if item.get('title') != servant_name]
        
        print(f"获取到 {len(nicknames)} 个别名: {', '.join(nicknames) if nicknames else '无别名'}")
        return nicknames
    except Exception as e:
        print(f"获取从者别名失败: {e}")
        return []



def update_servant_db():
    """更新从者信息"""
    # 获取从者列表
    servant_list = fetch_servant_list()
    
    # 遍历从者列表
    for servant in servant_list:
        servant_name = servant['title']
        print(f"正在处理: {servant_name}")
        
        # 获取从者详细信息
        servant_details = fetch_servant_detail(servant_name)
        
        if servant_details is None:
            print(f"跳过不可获取的从者: {servant_name}")
            # 记录一个log文件
            with open("error_log.txt", "a") as log_file:
                log_file.write(f"跳过不可获取的从者: {servant_name}\n")
            continue
        
        # 在调用update_servant之前，确保特性列表无重复
        if 'traits' in servant_details and servant_details['traits']:
            # 使用集合去重，然后转回列表
            servant_details['traits'] = list(dict.fromkeys(servant_details['traits']))
        
        # 获取别名
        nicknames = fetch_servant_nicknames(servant_name)
        
        # 更新数据库
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                
                # 检查从者是否已存在
                c.execute("SELECT id FROM servants WHERE name = ?", (servant_name,))
                existing_servant = c.fetchone()
                
                if existing_servant:
                    # 更新现有从者信息
                    update_servant(existing_servant[0], **servant_details, aliases=nicknames)
                    print(f"更新从者: {servant_name}")
                else:
                    # 插入新从者信息
                    add_servant(**servant_details, aliases=nicknames)
                    print(f"添加新从者: {servant_name}")
        
        except Exception as e:
            error_msg = f"在更新从者{servant_name}时数据库操作失败: {str(e)}"
            print(error_msg)
            with open("error_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"{error_msg}\n")
                # 可选：记录更多调试信息
                if 'traits' in servant_details:
                    log_file.write(f"特性列表: {servant_details['traits']}\n")
            error_count += 1
