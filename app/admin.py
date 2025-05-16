from app.db import get_db_connection
import json

def add_servant(name, class_name, rarity, gender, alignment, attribute, noble_phantasm_type,
                region=None, card_deck=None, traits=None, aliases=None, 
                noble_phantasm_card=None, atk_90=None, hp_90=None, id=None, access=None):
    """添加新从者"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 处理alignment参数，确保它是字符串
    if isinstance(alignment, list):
        alignment = "·".join(alignment) if alignment else "未知"
    
    # 处理属性参数，确保它是字符串
    if isinstance(attribute, list):
        attribute = attribute[0] if attribute else "未知"
        
    # 使用自定义ID或获取新ID
    if id is not None:
        new_id = id
        # 检查是否已存在该ID
        c.execute("SELECT id FROM servants WHERE id = ?", (new_id,))
        if c.fetchone():
            conn.close()
            raise ValueError(f"ID {new_id} 已被使用")
    else:
        # 获取最大ID值
        c.execute("SELECT MAX(id) FROM servants")
        max_id = c.fetchone()[0] or 0
        new_id = max_id + 1
    
    try:
        # 插入从者基础信息
        c.execute("""
        INSERT INTO servants (id, name, class_name, rarity, gender, alignment, attribute, noble_phantasm_type, 
                            region, card_deck, noble_phantasm_card, atk_90, hp_90)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_id, name, class_name, rarity, gender, alignment, attribute, noble_phantasm_type, 
            region or "未知", 
            json.dumps(card_deck or ["Q", "A", "A", "B", "B"]), 
            noble_phantasm_card or "B", 
            atk_90, 
            hp_90
        ))
        
        # 插入别名
        if aliases:
            for alias in aliases:
                if alias:  # 确保别名非空
                    c.execute("INSERT INTO aliases (servant_id, alias) VALUES (?, ?)", (new_id, alias))
        
        # 插入特性
        if traits:
            for trait in traits:
                if trait:  # 确保特性非空
                    c.execute("INSERT INTO traits (servant_id, trait) VALUES (?, ?)", (new_id, trait))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    
    conn.close()
    return new_id

def update_servant(servant_id, **kwargs):
    """更新从者信息"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 处理可能的列表类型参数
    if 'alignment' in kwargs and isinstance(kwargs['alignment'], list):
        kwargs['alignment'] = "·".join(kwargs['alignment']) if kwargs['alignment'] else "未知"
    
    if 'attribute' in kwargs and isinstance(kwargs['attribute'], list):
        kwargs['attribute'] = kwargs['attribute'][0] if kwargs['attribute'] else "未知"
    
    # 更新基础信息
    updates = []
    params = []
    
    for key, value in kwargs.items():
        # 处理特殊字段access
        if key == 'access':
            continue

        if key == 'card_deck' and value:
            updates.append(f"{key} = ?")
            params.append(json.dumps(value))
        elif key not in ('aliases', 'traits') and value is not None:
            updates.append(f"{key} = ?")
            params.append(value)
    
    if updates:
        query = f"UPDATE servants SET {', '.join(updates)} WHERE id = ?"
        params.append(servant_id)
        c.execute(query, params)
    
    # 更新别名
    if 'aliases' in kwargs and kwargs['aliases'] is not None:
        # 删除旧的别名
        c.execute("DELETE FROM aliases WHERE servant_id = ?", (servant_id,))
        
        # 添加新的别名
        for alias in kwargs['aliases']:
            c.execute("INSERT INTO aliases (servant_id, alias) VALUES (?, ?)", (servant_id, alias))
    
    # 更新特性
    if 'traits' in kwargs and kwargs['traits'] is not None:
        # 删除旧的特性
        c.execute("DELETE FROM traits WHERE servant_id = ?", (servant_id,))
        
        # 添加新的特性
        for trait in kwargs['traits']:
            c.execute("INSERT INTO traits (servant_id, trait) VALUES (?, ?)", (servant_id, trait))
    
    conn.commit()
    conn.close()

def delete_servant(servant_id):
    """删除从者"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 删除从者的别名
    c.execute("DELETE FROM aliases WHERE servant_id = ?", (servant_id,))
    
    # 删除从者的特性
    c.execute("DELETE FROM traits WHERE servant_id = ?", (servant_id,))
    
    # 删除从者
    c.execute("DELETE FROM servants WHERE id = ?", (servant_id,))
    
    conn.commit()
    conn.close()