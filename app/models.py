import json
import random
from app.db import get_db_connection

class Servant:
    def __init__(self, id, name, class_name, rarity, gender, alignment, attribute, noble_phantasm_type, 
                 region=None, card_deck=None, traits=None, aliases=None, 
                 noble_phantasm_card=None, atk_90=None, hp_90=None):
        self.id = id
        self.name = name
        self.class_name = class_name  # 职介
        self.rarity = rarity  # 稀有度（星级）
        self.gender = gender  # 性别
        self.alignment = alignment  # 属性（秩序、善等）
        self.attribute = attribute  # 副属性（天地人星兽）
        self.noble_phantasm_type = noble_phantasm_type  # 宝具类型
        self.region = region or "未知"  # 从者地域/国籍
        self.card_deck = card_deck or ["Q", "A", "A", "B", "B"]  # 指令卡配置
        self.traits = traits or []  # 从者特性
        self.aliases = aliases or []  # 从者别名
        self.noble_phantasm_card = noble_phantasm_card or "B"  # 宝具色卡
        self.atk_90 = atk_90  # 90级ATK
        self.hp_90 = hp_90    # 90级HP
        
    def get_card_deck_display(self):
        """返回配卡的显示格式"""
        if isinstance(self.card_deck[0], str):
            return ",".join(self.card_deck)
        else:
            # 兼容旧格式 [1, 2, 2] -> "Q,A,A,B,B"
            cards = []
            cards.extend(["Q"] * self.card_deck[0])
            cards.extend(["A"] * self.card_deck[1])
            cards.extend(["B"] * self.card_deck[2])
            return ",".join(cards)
    
    @classmethod
    def from_db_row(cls, row, traits=None, aliases=None):
        """从数据库行创建Servant对象"""
        try:
            card_deck = json.loads(row['card_deck'])
        except:
            card_deck = ["Q", "A", "A", "B", "B"]
            
        return cls(
            id=row['id'],
            name=row['name'],
            class_name=row['class_name'],
            rarity=row['rarity'],
            gender=row['gender'],
            alignment=row['alignment'],
            attribute=row['attribute'],
            noble_phantasm_type=row['noble_phantasm_type'],
            region=row['region'],
            card_deck=card_deck,
            traits=traits or [],
            aliases=aliases or [],
            noble_phantasm_card=row['noble_phantasm_card'],
            atk_90=row['atk_90'],
            hp_90=row['hp_90']
        )

def get_all_servants():
    """获取所有从者"""
    conn = get_db_connection()
    servants = []
    
    # 获取所有从者基础信息
    cursor = conn.execute('SELECT * FROM servants ORDER BY id')
    for row in cursor:
        # 获取该从者的特性
        traits_cursor = conn.execute('SELECT trait FROM traits WHERE servant_id = ?', (row['id'],))
        traits = [trait[0] for trait in traits_cursor.fetchall()]
        
        # 获取该从者的别名
        aliases_cursor = conn.execute('SELECT alias FROM aliases WHERE servant_id = ?', (row['id'],))
        aliases = [alias[0] for alias in aliases_cursor.fetchall()]
        
        # 创建从者对象
        servant = Servant.from_db_row(row, traits, aliases)
        servants.append(servant)
    
    conn.close()
    return servants

def get_servant_by_id(servant_id):
    """根据ID获取从者"""
    conn = get_db_connection()
    
    # 查询从者基础信息
    cursor = conn.execute('SELECT * FROM servants WHERE id = ?', (servant_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # 获取该从者的特性
    traits_cursor = conn.execute('SELECT trait FROM traits WHERE servant_id = ?', (servant_id,))
    traits = [trait[0] for trait in traits_cursor.fetchall()]
    
    # 获取该从者的别名
    aliases_cursor = conn.execute('SELECT alias FROM aliases WHERE servant_id = ?', (servant_id,))
    aliases = [alias[0] for alias in aliases_cursor.fetchall()]
    
    # 创建从者对象
    servant = Servant.from_db_row(row, traits, aliases)
    
    conn.close()
    return servant

def get_servant_by_name(name):
    """根据名字或别名获取从者"""
    conn = get_db_connection()
    
    # 首先尝试通过名称查找
    cursor = conn.execute('SELECT * FROM servants WHERE name = ?', (name,))
    row = cursor.fetchone()
    
    if not row:
        # 如果没找到，尝试通过别名查找
        cursor = conn.execute('''
            SELECT s.* FROM servants s
            JOIN aliases a ON s.id = a.servant_id
            WHERE a.alias = ?
        ''', (name,))
        row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # 获取该从者的特性
    traits_cursor = conn.execute('SELECT trait FROM traits WHERE servant_id = ?', (row['id'],))
    traits = [trait[0] for trait in traits_cursor.fetchall()]
    
    # 获取该从者的别名
    aliases_cursor = conn.execute('SELECT alias FROM aliases WHERE servant_id = ?', (row['id'],))
    aliases = [alias[0] for alias in aliases_cursor.fetchall()]
    
    # 创建从者对象
    servant = Servant.from_db_row(row, traits, aliases)
    
    conn.close()
    return servant

def get_random_servant(rarity_list=None, class_list=None):
    """随机获取一个从者
    
    参数:
        rarity_list (list, optional): 限制星级列表，如[2,3,4,5]则随机选择2-5星从者
        class_list (list, optional): 限制职介列表，如["Saber", "Archer"]则随机选择剑弓职介从者
    
    返回:
        Servant: 随机选择的从者对象，如果没有符合条件的从者则返回None
    """
    conn = get_db_connection()
    
    # 构建基本查询
    query = 'SELECT id FROM servants WHERE 1=1'
    params = []
    
    # 如果提供了星级列表，添加过滤条件
    if rarity_list and isinstance(rarity_list, list) and len(rarity_list) > 0:
        placeholders = ', '.join(['?' for _ in rarity_list])
        query += f' AND rarity IN ({placeholders})'
        params.extend(rarity_list)
    
    # 如果提供了职介列表，添加过滤条件
    if class_list and isinstance(class_list, list) and len(class_list) > 0:
        placeholders = ', '.join(['?' for _ in class_list])
        query += f' AND class_name IN ({placeholders})'
        params.extend(class_list)
    
    # 执行查询获取符合条件的从者ID
    cursor = conn.execute(query, params)
    servant_ids = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # 如果没有符合条件的从者，返回None
    if not servant_ids:
        return None
    
    # 随机选择一个ID
    random_id = random.choice(servant_ids)
    
    # 通过ID获取从者
    return get_servant_by_id(random_id)

def search_servants(query):
    """根据查询字符串搜索从者"""
    if not query or len(query) < 1:
        return []
    
    conn = get_db_connection()
    query = f"%{query.lower()}%"
    result = []
    
    # 通过名称搜索
    cursor = conn.execute('''
        SELECT * FROM servants 
        WHERE LOWER(name) LIKE ?
    ''', (query,))
    
    for row in cursor:
        # 检查是否已添加到结果中
        if any(servant.id == row['id'] for servant in result):
            continue
        
        # 获取特性和别名
        traits_cursor = conn.execute('SELECT trait FROM traits WHERE servant_id = ?', (row['id'],))
        traits = [trait[0] for trait in traits_cursor.fetchall()]
        
        aliases_cursor = conn.execute('SELECT alias FROM aliases WHERE servant_id = ?', (row['id'],))
        aliases = [alias[0] for alias in aliases_cursor.fetchall()]
        
        # 创建从者对象并添加到结果中
        servant = Servant.from_db_row(row, traits, aliases)
        result.append(servant)
    
    # 通过别名搜索
    cursor = conn.execute('''
        SELECT s.* FROM servants s
        JOIN aliases a ON s.id = a.servant_id
        WHERE LOWER(a.alias) LIKE ?
    ''', (query,))
    
    for row in cursor:
        # 检查是否已添加到结果中
        if any(servant.id == row['id'] for servant in result):
            continue
        
        # 获取特性和别名
        traits_cursor = conn.execute('SELECT trait FROM traits WHERE servant_id = ?', (row['id'],))
        traits = [trait[0] for trait in traits_cursor.fetchall()]
        
        aliases_cursor = conn.execute('SELECT alias FROM aliases WHERE servant_id = ?', (row['id'],))
        aliases = [alias[0] for alias in aliases_cursor.fetchall()]
        
        # 创建从者对象并添加到结果中
        servant = Servant.from_db_row(row, traits, aliases)
        result.append(servant)
    
    conn.close()
    return result[:10]  # 限制结果数量，避免列表过长

def compare_servants(guess, target, visible_attributes=None):
    """比较猜测的从者与目标从者，返回比较结果
    
    visible_attributes: 列表，包含可见的属性名称，如果为None则全部可见
    """
    result = {}
    all_attributes = {
        "class_name": "职介",
        "rarity": "稀有度",
        "gender": "性别",
        "alignment": "属性",
        "attribute": "副属性",
        "noble_phantasm_type": "宝具类型",
        "traits": "特性",
        "noble_phantasm_card": "宝具色卡",
        "atk_90": "ATK",
        "hp_90": "HP",
        "card_deck": "配卡"
    }
    
    # 如果没有指定可见属性，则全部可见
    if not visible_attributes:
        visible_attributes = list(all_attributes.keys())
    
    # 移除region(地区)如果存在
    if "region" in visible_attributes:
        visible_attributes.remove("region")
    
    # 比较职介
    if "class_name" in visible_attributes:
        result["class_name"] = {
            "display_name": all_attributes["class_name"],
            "value": guess.class_name,
            "match": guess.class_name == target.class_name
        }
    
    # 比较稀有度
    if "rarity" in visible_attributes:
        result["rarity"] = {
            "display_name": all_attributes["rarity"],
            "value": guess.rarity,
            "match": guess.rarity == target.rarity,
            "higher": guess.rarity > target.rarity if guess.rarity != target.rarity else None,
            "difference": abs(guess.rarity - target.rarity) if guess.rarity != target.rarity else 0,
            "close_match": abs(guess.rarity - target.rarity) == 1  # 添加相差1星的标记
        }
    
    # 比较性别
    if "gender" in visible_attributes:
        result["gender"] = {
            "display_name": all_attributes["gender"],
            "value": guess.gender,
            "match": guess.gender == target.gender
        }
    
    # 比较属性 - 修改为分别比较每个部分
    if "alignment" in visible_attributes:
        guess_parts = guess.alignment.split('·')
        target_parts = target.alignment.split('·')
        
        # 确保两边都有足够的部分进行比较
        while len(guess_parts) < 2:
            guess_parts.append("")
        while len(target_parts) < 2:
            target_parts.append("")
        
        # 存储两个部分的匹配结果
        part_matches = [guess_parts[i] == target_parts[i] for i in range(min(len(guess_parts), len(target_parts)))]
        
        result["alignment"] = {
            "display_name": all_attributes["alignment"],
            "value": guess.alignment,
            "match": guess.alignment == target.alignment,
            "parts": guess_parts,
            "part_matches": part_matches
        }
    
    # 比较副属性
    if "attribute" in visible_attributes:
        result["attribute"] = {
            "display_name": all_attributes["attribute"],
            "value": guess.attribute,
            "match": guess.attribute == target.attribute
        }
    
    # 比较宝具类型
    if "noble_phantasm_type" in visible_attributes:
        result["noble_phantasm_type"] = {
            "display_name": all_attributes["noble_phantasm_type"],
            "value": guess.noble_phantasm_type,
            "match": guess.noble_phantasm_type == target.noble_phantasm_type
        }
    
    # 比较特性 - 修改为分别检查每个特性
    if "traits" in visible_attributes:
        guess_traits = getattr(guess, 'traits', [])
        target_traits = getattr(target, 'traits', [])
        
        # 计算每个特性是否匹配目标特性
        trait_matches = [trait in target_traits for trait in guess_traits]
        
        result["traits"] = {
            "display_name": all_attributes["traits"],
            "value": guess_traits,  # 现在保存整个列表而不是字符串
            "match": set(guess_traits) == set(target_traits),
            "trait_matches": trait_matches,
            "common_traits": list(set(guess_traits).intersection(set(target_traits)))
        }
    
    # 比较宝具色卡
    if "noble_phantasm_card" in visible_attributes:
        guess_np_card = getattr(guess, 'noble_phantasm_card', None)
        target_np_card = getattr(target, 'noble_phantasm_card', None)
        
        if guess_np_card and target_np_card:
            result["noble_phantasm_card"] = {
                "display_name": all_attributes["noble_phantasm_card"],
                "value": guess_np_card,
                "match": guess_np_card == target_np_card
            }
    
    # 比较90级ATK
    if "atk_90" in visible_attributes:
        guess_atk = getattr(guess, 'atk_90', None)
        target_atk = getattr(target, 'atk_90', None)
        
        if guess_atk and target_atk:
            difference = abs(guess_atk - target_atk)
            result["atk_90"] = {
                "display_name": all_attributes["atk_90"],
                "value": guess_atk,
                "match": guess_atk == target_atk,
                "higher": guess_atk > target_atk if guess_atk != target_atk else None,
                "difference": difference,
                "difference_percent": round((difference / target_atk) * 100, 1)
            }
    
    # 比较90级HP
    if "hp_90" in visible_attributes:
        guess_hp = getattr(guess, 'hp_90', None)
        target_hp = getattr(target, 'hp_90', None)
        
        if guess_hp and target_hp:
            difference = abs(guess_hp - target_hp)
            result["hp_90"] = {
                "display_name": all_attributes["hp_90"],
                "value": guess_hp,
                "match": guess_hp == target_hp,
                "higher": guess_hp > target_hp if guess_hp != target_hp else None,
                "difference": difference,
                "difference_percent": round((difference / target_hp) * 100, 1)
            }
    
    # 比较配卡
    if "card_deck" in visible_attributes:
        guess_deck = getattr(guess, 'card_deck', None)
        target_deck = getattr(target, 'card_deck', None)
        
        if guess_deck and target_deck:
            if isinstance(guess_deck[0], str) and isinstance(target_deck[0], str):
                # 两者都是新格式
                deck_match = guess_deck == target_deck
                guess_display = guess.get_card_deck_display()
                
                # 计算每张卡是否匹配
                card_matches = [guess_deck[i] == target_deck[i] for i in range(min(len(guess_deck), len(target_deck)))]
                
                result["card_deck"] = {
                    "display_name": all_attributes["card_deck"],
                    "value": guess_display,
                    "cards": guess_deck,
                    "match": deck_match,
                    "card_matches": card_matches
                }
            else:
                # 兼容旧格式
                guess_display = guess.get_card_deck_display()
                result["card_deck"] = {
                    "display_name": all_attributes["card_deck"],
                    "value": guess_display,
                    "match": False  # 默认不匹配
                }
    
    return result