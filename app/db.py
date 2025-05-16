import sqlite3
import os
import json
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "instance" / "servants.db"

def get_db_connection():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    conn = get_db_connection()
    
    # 创建从者表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS servants (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        class_name TEXT NOT NULL,
        rarity INTEGER NOT NULL,
        gender TEXT NOT NULL,
        alignment TEXT NOT NULL,
        attribute TEXT NOT NULL,
        noble_phantasm_type TEXT NOT NULL,
        region TEXT DEFAULT "未知",
        card_deck TEXT NOT NULL,
        noble_phantasm_card TEXT DEFAULT "B",
        atk_90 INTEGER,
        hp_90 INTEGER
    )
    ''')
    
    # 创建别名表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS aliases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        servant_id INTEGER NOT NULL,
        alias TEXT NOT NULL,
        FOREIGN KEY (servant_id) REFERENCES servants(id),
        UNIQUE(servant_id, alias)
    )
    ''')
    
    # 创建特性表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS traits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        servant_id INTEGER NOT NULL,
        trait TEXT NOT NULL,
        FOREIGN KEY (servant_id) REFERENCES servants(id),
        UNIQUE(servant_id, trait)
    )
    ''')
    
    conn.commit()
    conn.close()

# def insert_default_servants():
#     """插入默认从者数据"""
#     conn = get_db_connection()
#     c = conn.cursor()
    
#     # 检查是否已经有数据
#     c.execute("SELECT COUNT(*) FROM servants")
#     if c.fetchone()[0] > 0:
#         conn.close()
#         return

#     # 插入阿尔托莉雅
#     c.execute("""
#     INSERT INTO servants (id, name, class_name, rarity, gender, alignment, attribute, noble_phantasm_type, 
#                         region, card_deck, noble_phantasm_card, atk_90, hp_90)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         1, "阿尔托莉雅·潘德拉贡", "Saber", 5, "女性", "秩序·善", "地", "群体宝具", 
#         "不列颠", json.dumps(["Q", "A", "A", "B", "B"]), "B", 11221, 15150
#     ))
    
#     # 插入阿尔托莉雅的别名
#     aliases = ["阿尔托莉雅", "呆毛王", "蓝Saber", "阿尔托利亚", "Artoria"]
#     for alias in aliases:
#         c.execute("INSERT INTO aliases (servant_id, alias) VALUES (?, ?)", (1, alias))
    
#     # 插入阿尔托莉雅的特性
#     traits = ["骑乘", "龙", "阿尔托莉雅脸", "天地从者", "亚瑟", "王", "人科", "圆桌骑士", "FSN从者", "持有灵衣之人"]
#     for trait in traits:
#         c.execute("INSERT INTO traits (servant_id, trait) VALUES (?, ?)", (1, trait))
    
#     # 插入吉尔伽美什
#     c.execute("""
#     INSERT INTO servants (id, name, class_name, rarity, gender, alignment, attribute, noble_phantasm_type, 
#                         region, card_deck, noble_phantasm_card, atk_90, hp_90)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         2, "吉尔伽美什", "Archer", 5, "男性", "混沌·善", "天", "群体宝具", 
#         "美索不达米亚", json.dumps(["Q", "A", "A", "B", "B"]), "B", 12280, 13097
#     ))
    
#     # 插入吉尔伽美什的别名
#     aliases = ["金闪闪", "AUO", "Gil"]
#     for alias in aliases:
#         c.execute("INSERT INTO aliases (servant_id, alias) VALUES (?, ?)", (2, alias))
    
#     # 插入吉尔伽美什的特性
#     traits = ["王", "神性", "人科", "天地从者", "持有灵衣之人", "FSN从者"]
#     for trait in traits:
#         c.execute("INSERT INTO traits (servant_id, trait) VALUES (?, ?)", (2, trait))
    
#     # 插入更多从者...
#     # 莫扎特
#     c.execute("""
#     INSERT INTO servants (id, name, class_name, rarity, gender, alignment, attribute, noble_phantasm_type, 
#                         region, card_deck)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         21, "莫扎特", "Caster", 1, "男性", "中立·善", "人", "对军宝具", 
#         "欧洲", json.dumps(["Q", "A", "A", "B", "B"])
#     ))
    
#     # 莫扎特特性
#     for trait in ["人类", "艺术家"]:
#         c.execute("INSERT INTO traits (servant_id, trait) VALUES (?, ?)", (21, trait))
    
#     # 清姬
#     c.execute("""
#     INSERT INTO servants (id, name, class_name, rarity, gender, alignment, attribute, noble_phantasm_type, 
#                         region, card_deck)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         22, "清姬", "Berserker", 3, "女性", "混沌·恶", "地", "对人宝具", 
#         "日本", json.dumps(["Q", "A", "A", "B", "B"])
#     ))
    
#     # 清姬特性
#     for trait in ["龙", "日本从者"]:
#         c.execute("INSERT INTO traits (servant_id, trait) VALUES (?, ?)", (22, trait))
    
#     # BB
#     c.execute("""
#     INSERT INTO servants (id, name, class_name, rarity, gender, alignment, attribute, noble_phantasm_type, 
#                         region, card_deck)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         23, "BB", "MoonCancer", 4, "女性", "混沌·恶", "人", "单体宝具", 
#         "SE.RA.PH", json.dumps(["Q", "A", "A", "B", "B"])
#     ))
    
#     # BB特性
#     for trait in ["人工生命", "从者"]:
#         c.execute("INSERT INTO traits (servant_id, trait) VALUES (?, ?)", (23, trait))
    
#     conn.commit()
#     conn.close()