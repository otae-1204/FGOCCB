from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from app.models import (
    get_all_servants, get_servant_by_id, 
    get_random_servant
)
import json
import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """游戏首页"""
    # 获取游戏统计数据
    stats = session.get('game_stats', {'games': 0, 'wins': 0, 'avg_attempts': 0})
    return render_template('index.html', stats=stats)

@main.route('/start', methods=['GET', 'POST'])
def start_game():
    """开始游戏，支持自定义显示属性"""
    if request.method == 'POST':
        # 获取玩家选择的可比较属性
        compare_options = request.form.getlist('compare_options')
        
        # 确保默认包含这些基本选项
        if not compare_options:
            compare_options = ['class_name', 'rarity', 'gender']

        # 将选项保存到会话
        session['compare_options'] = compare_options


        # 获取最大猜测次数
        try:
            max_attempts = int(request.form.get('max_attempts', 10))
            if max_attempts < 1:
                max_attempts = 10
        except:
            max_attempts = 10
        
        # 获取是否启用提示
        hint_enabled = 'hint_enabled' in request.form
        max_hints = 3  # 默认提示次数上限
        
        # 初始化游戏状态
        session['attempts'] = 0
        session['max_attempts'] = max_attempts
        session['hint_enabled'] = hint_enabled
        session['hint_used'] = 0
        session['max_hints'] = max_hints
        session['current_hint'] = None  # 当前展示的提示
        session['guesses'] = []
        session['comparisons'] = []
        session['game_start_time'] = datetime.datetime.now().isoformat()
        session['compare_options'] = compare_options  # 存储为compare_options而非visible_attributes
        
        # print(f"游戏开始，最大尝试次数: {session.get('max_attempts', 10)}, 提示启用: {hint_enabled}, 可比较属性: {compare_options}")


        # 获取限制条件，星级与职介
        raritys = [int(r) for r in request.form.getlist("rarity")]
        class_name = request.form.getlist("class_name")

        # 随机选择目标从者
        target_servant = get_random_servant(rarity_list=raritys, class_list=class_name)
        session['target_servant_id'] = target_servant.id
        
        return redirect(url_for('main.game'))
    else:
        # GET请求展示属性选择页面
        all_attributes = {
            "class_name": "职介",
            "rarity": "稀有度",
            "gender": "性别",
            "alignment": "阵营",
            "attribute": "属性",
            "noble_phantasm_type": "宝具类型",
            "noble_phantasm_card": "宝具色卡",
            "card_deck": "指令卡配置",
            "atk_90": "满级ATK",
            "hp_90": "满级HP",
            "traits": "特性"
        }
        
        default_visible = ["class_name", "rarity", "gender", "alignment", "attribute", "noble_phantasm_type"]
        
        return render_template(
            'customize.html',
            all_attributes=all_attributes,
            default_visible=default_visible
        )

@main.route('/game')
def game():
    """游戏页面"""
    if 'target_servant_id' not in session:
        # 如果没有进行中的游戏，重定向到首页
        return redirect(url_for('main.index'))
    
    # 获取所有从者，按职阶分组
    all_servants = get_all_servants()
    servants_by_class = {}
    for servant in all_servants:
        if servant.class_name not in servants_by_class:
            servants_by_class[servant.class_name] = []
        servants_by_class[servant.class_name].append(servant)
    
    # 获取游戏状态
    attempts = session.get('attempts', 0)
    max_attempts = session.get('max_attempts', 10)
    hint_enabled = session.get('hint_enabled', True)
    hint_used = session.get('hint_used', 0)
    guesses = session.get('guesses', [])
    comparisons = session.get('comparisons', [])
    
    # 获取所有可用的职阶和稀有度，用于筛选
    class_options = sorted(list(set(s.class_name for s in all_servants)))
    rarity_options = sorted(list(set(s.rarity for s in all_servants)))
    
    return render_template(
        'game.html', 
        servants_by_class=servants_by_class,
        attempts=attempts,
        max_attempts=max_attempts,
        hint_enabled=hint_enabled,
        hint_used=hint_used,
        guesses=guesses,
        comparisons=comparisons
    )

@main.route('/guess', methods=['POST'])
def guess():
    """处理玩家的猜测"""
    if 'target_servant_id' not in session:
        flash('没有进行中的游戏', 'warning')
        return redirect(url_for('main.index'))
    
    # 获取玩家猜测的从者ID
    servant_id = request.form.get('servant_id', 0, type=int)
    
    # 添加额外的验证
    if servant_id <= 0:
        flash('请选择一个有效的从者', 'warning')
        return redirect(url_for('main.game'))
    
    # 确保目标从者ID是整数
    target_id = session.get('target_servant_id')
    if not isinstance(target_id, int) or target_id <= 0:
        flash('游戏状态异常，请重新开始', 'error')
        clear_game_session()
        return redirect(url_for('main.index'))
    
    try:
        # 获取从者信息
        from app.models import get_servant_by_id,get_servant_by_name
        # guesses_servant = get_servant_by_name(servant_name)
        guessed_servant = get_servant_by_id(servant_id)
        target_servant = get_servant_by_id(target_id)
        
        # 验证表单数据
        servant_id = request.form.get('servant_id')
        if not servant_id:
            flash('请选择一个有效的从者')
            return redirect(url_for('main.game'))

        # 确保servant_id是整数
        try:
            servant_id = int(servant_id)
        except (ValueError, TypeError):
            flash('无效的从者ID')
            return redirect(url_for('main.game'))


        if not guessed_servant:
            flash(f'未找到ID为{servant_id}的从者', 'error')
            return redirect(url_for('main.game'))
        
        if not target_servant:
            flash(f'未找到目标从者，游戏状态异常', 'error')
            clear_game_session()
            return redirect(url_for('main.index'))
        
        # 记录猜测
        session['attempts'] = session.get('attempts', 0) + 1
        
        # 记录猜测的从者
        guesses = session.get('guesses', [])
        guesses.append({
            'id': guessed_servant.id,
            'name': guessed_servant.name,
            'class_name': guessed_servant.class_name,
            'rarity': guessed_servant.rarity,
            'gender': guessed_servant.gender,
            'alignment': guessed_servant.alignment,
            'attribute': guessed_servant.attribute,
            'atk_90': getattr(guessed_servant, 'atk_90', None),
            'hp_90': getattr(guessed_servant, 'hp_90', None),
            'noble_phantasm_type': getattr(guessed_servant, 'noble_phantasm_type', '未知'),
            'noble_phantasm_card': getattr(guessed_servant, 'noble_phantasm_card', 'B'),
            'card_deck': getattr(guessed_servant, 'card_deck', []),
            'traits': getattr(guessed_servant, 'traits', [])
        })
        session['guesses'] = guesses
        
        # 比较从者属性
        comparison = {}
        
        # 获取要显示的属性列表
        compare_options = session.get('compare_options', ['class_name', 'rarity', 'gender'])
        
        # 创建英文键名到中文键名的映射
        key_mapping = {
            'class_name': '职阶',
            'rarity': '星级',
            'gender': '性别',
            'alignment': '阵营',
            'attribute': '属性',
            'noble_phantasm_type': '宝具类型',
            'noble_phantasm_card': '宝具色卡',
            'card_deck': '指令卡配置',
            'traits': '特性',
            'atk_90': '满级ATK',
            'hp_90': '满级HP'
        }
        
        # 基本比较项 - 始终包含
        comparison['职阶'] = 'match' if guessed_servant.class_name == target_servant.class_name else 'different'
        
        if guessed_servant.rarity == target_servant.rarity:
            comparison['星级'] = 'match'
        elif guessed_servant.rarity > target_servant.rarity:
            comparison['星级'] = 'higher'
        else:
            comparison['星级'] = 'lower'
        
        comparison['性别'] = 'match' if guessed_servant.gender == target_servant.gender else 'different'
        
        # 可选比较项 - 根据游戏设置显示
        for option in compare_options:
            chinese_key = key_mapping.get(option)
            if not chinese_key or chinese_key in comparison:
                continue
            
            # 根据不同属性处理比较逻辑
            if option == 'alignment':
                comparison[chinese_key] = 'match' if guessed_servant.alignment == target_servant.alignment else 'different'
            
            elif option == 'attribute':
                comparison[chinese_key] = 'match' if guessed_servant.attribute == target_servant.attribute else 'different'
            
            elif option == 'atk_90' and hasattr(guessed_servant, 'atk_90') and hasattr(target_servant, 'atk_90'):
                # ATK比较逻辑...
                if guessed_servant.atk_90 == target_servant.atk_90:
                    comparison[chinese_key] = 'match'
                elif abs(guessed_servant.atk_90 - target_servant.atk_90) <= 1000:
                    comparison[chinese_key] = 'close' if guessed_servant.atk_90 < target_servant.atk_90 else 'close-higher'
                else:
                    comparison[chinese_key] = 'higher' if guessed_servant.atk_90 > target_servant.atk_90 else 'lower'
            
            # HP比较逻辑
            elif option == 'hp_90' and hasattr(guessed_servant, 'hp_90') and hasattr(target_servant, 'hp_90'):
                if guessed_servant.hp_90 == target_servant.hp_90:
                    comparison[chinese_key] = 'match'
                elif abs(guessed_servant.hp_90 - target_servant.hp_90) <= 1000:
                    comparison[chinese_key] = 'close' if guessed_servant.hp_90 < target_servant.hp_90 else 'close-higher'
                else:
                    comparison[chinese_key] = 'higher' if guessed_servant.hp_90 > target_servant.hp_90 else 'lower'

            # 宝具类型比较
            elif option == 'noble_phantasm_type':
                comparison[chinese_key] = 'match' if guessed_servant.noble_phantasm_type == target_servant.noble_phantasm_type else 'different'

            # 宝具色卡比较
            elif option == 'noble_phantasm_card':
                comparison[chinese_key] = 'match' if guessed_servant.noble_phantasm_card == target_servant.noble_phantasm_card else 'different'

            # 指令卡配置比较
            elif option == 'card_deck':
                # 检查两个卡组是否相同
                if isinstance(guessed_servant.card_deck, list) and isinstance(target_servant.card_deck, list):
                    guessed_deck = sorted(guessed_servant.card_deck) if guessed_servant.card_deck else []
                    target_deck = sorted(target_servant.card_deck) if target_servant.card_deck else []
                    comparison[chinese_key] = 'match' if guessed_deck == target_deck else 'different'
                else:
                    comparison[chinese_key] = 'different'

            # 特性比较
            elif option == 'traits':
                # 检查从者特性的交集
                guessed_traits = set(guessed_servant.traits) if hasattr(guessed_servant, 'traits') and guessed_servant.traits else set()
                target_traits = set(target_servant.traits) if hasattr(target_servant, 'traits') and target_servant.traits else set()
                
                # 找出匹配的特性
                matching_traits = guessed_traits.intersection(target_traits)
                
                # 决定匹配状态
                if not guessed_traits or not target_traits:
                    comparison[chinese_key] = 'different'
                elif guessed_traits == target_traits:
                    comparison[chinese_key] = 'match'
                elif matching_traits:
                    comparison[chinese_key] = 'partial'  # 部分匹配
                    # 存储匹配的特性供前端显示
                    comparison['匹配特性'] = list(matching_traits)
                else:
                    comparison[chinese_key] = 'different'
        
        # 记录比较结果
        comparisons = session.get('comparisons', [])
        comparisons.append(comparison)
        session['comparisons'] = comparisons
        
        # 检查是否猜对
        if guessed_servant.id == target_servant.id:
            # 记录游戏结果
            update_game_stats(win=True, attempts=session['attempts'])
            
            # 计算游戏时间
            game_time = calculate_game_time(session.get('game_start_time'))

            result_data = {
                'win': True,
                'surrendered': False,
                'target_servant': target_servant,
                'attempts': session.get('attempts', 0),
                'max_attempts': session.get('max_attempts', 10),
                'game_time': game_time,
                'guesses': session.get('guesses', []),
                'comparisons': session.get('comparisons', [])
            }
            # 清除游戏会话
            clear_game_session()

            return render_template('game_result.html', **result_data)
        
        # 检查是否达到最大尝试次数
        max_attempts = session.get('max_attempts', 10)
        if session['attempts'] >= max_attempts:
            # 记录游戏结果
            update_game_stats(win=False, attempts=session['attempts'])
            
            # 计算游戏时间
            game_time = calculate_game_time(session.get('game_start_time'))
            

            
            # 跳转到结算页面
            # 准备结果数据
            result_data = {
                'win': False,
                'surrendered': False,
                'target_servant': target_servant,
                'attempts': session.get('attempts', 0),
                'max_attempts': session.get('max_attempts', 10),
                'game_time': game_time,
                'guesses': session.get('guesses', []),
                'comparisons': session.get('comparisons', [])
            }
            # 清除游戏会话
            clear_game_session()
            # print(f"游戏结束，猜测次数: {session['attempts']}, 最大尝试次数: {max_attempts}, 游戏时间: {game_time}")


            return render_template('game_result.html', **result_data)
        
        # 继续游戏
        return redirect(url_for('main.game'))
        
    except Exception as e:
        # 记录异常并显示更详细的错误信息
        import traceback
        error_msg = traceback.format_exc()
        print(f"猜测过程中出现错误: {error_msg}")
        flash(f'获取从者数据失败: {str(e)}', 'error')
        return redirect(url_for('main.game'))

@main.route('/hint', methods=['POST'])
def get_hint():
    """获取游戏提示"""
    # 检查游戏是否进行中
    if 'target_servant_id' not in session:
        flash('没有正在进行的游戏，无法获取提示', 'error')
        return redirect(url_for('main.index'))
    
    # 检查是否已达到提示使用上限
    max_hints = session.get('max_hints', 3)  # 默认最多3次提示
    hint_used = session.get('hint_used', 0)
    
    if hint_used >= max_hints:
        flash('已达到提示使用上限', 'error')
        return redirect(url_for('main.game'))
    
    # 获取目标从者
    target_servant_id = session.get('target_servant_id')
    target_servant = get_servant_by_id(target_servant_id)
    
    if not target_servant:
        flash('无法获取目标从者信息', 'error')
        return redirect(url_for('main.game'))
    
    # 根据已使用的提示次数提供不同的提示
    hint_content = generate_hint(target_servant, hint_used)
    
    # 更新提示使用次数
    session['hint_used'] = hint_used + 1
    session['current_hint'] = hint_content
    
    return redirect(url_for('main.game'))

def generate_hint(servant, hint_level):
    """根据提示级别生成不同的提示内容"""
    hints = [
        # 第一级提示 - 只给出基本信息
        f"这位从者的<b>名字首位</b>是 <b>{servant.name[0]}</b>",
        
        # 第二级提示 - 给出更多背景
        f"这位从者是<b>{servant.alignment}</b>属性，是<b>{servant.attribute}</b>阵营",
        
        # 第三级提示 - 给出重要特性
        f"这位从者具有以下特性之一: <b>{', '.join(servant.traits[:3])}</b>"
    ]
    
    # 如果提示级别超出预定义内容，随机提供一些额外信息
    if hint_level >= len(hints):
        extra_hints = [
            f"这位从者的宝具是<b>{servant.noble_phantasm_type}</b>类型",
            f"这位从者的宝具卡色是<b>{servant.noble_phantasm_card}</b>",
            f"这位从者的指令卡配置中有{servant.card_deck.count('B')}张Buster、{servant.card_deck.count('A')}张Arts和{servant.card_deck.count('Q')}张Quick"
        ]
        import random
        return random.choice(extra_hints)
    
    return hints[hint_level]

@main.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')

@main.route('/servant_details/<int:servant_id>')
def servant_details(servant_id):
    """获取从者详细信息"""
    servant = get_servant_by_id(servant_id)
    
    if not servant:
        return jsonify({"error": "从者不存在"}), 404
    
    # 转换为字典
    servant_dict = {
        'id': servant.id,
        'name': servant.name,
        'class_name': servant.class_name,
        'rarity': servant.rarity,
        'gender': servant.gender,
        'alignment': servant.alignment,
        'attribute': servant.attribute,
        'noble_phantasm_type': servant.noble_phantasm_type
    }
    
    # 添加可选字段
    if hasattr(servant, 'region'):
        servant_dict['region'] = servant.region
    if hasattr(servant, 'card_deck'):
        servant_dict['card_deck'] = servant.card_deck
    if hasattr(servant, 'traits'):
        servant_dict['traits'] = servant.traits
    
    return jsonify(servant_dict)

@main.route('/search_servants')
def search_servants_api():
    """搜索从者 API"""
    query = request.args.get('q', '')
    if not query or len(query) < 1:
        return jsonify([])
    
    # 简单搜索实现（直接在路由中）
    result = []
    for servant in get_all_servants():
        # 检查名称是否包含查询字符串
        if query.lower() in servant.name.lower():
            # 获取别名（如果有）
            aliases = getattr(servant, 'aliases', [])
            alias_text = f"({', '.join(aliases)})" if aliases else ""
            
            result.append({
                'id': servant.id,
                'name': servant.name,
                'display': f"{servant.name} {alias_text} - {servant.class_name} ({servant.rarity}★)",
                'class_name': servant.class_name,
                'rarity': servant.rarity
            })
            continue
            
        # 检查别名是否包含查询字符串
        if hasattr(servant, 'aliases'):
            for alias in servant.aliases:
                if query.lower() in alias.lower():
                    aliases = getattr(servant, 'aliases', [])
                    alias_text = f"({', '.join(aliases)})" if aliases else ""
                    
                    result.append({
                        'id': servant.id,
                        'name': servant.name,
                        'display': f"{servant.name} {alias_text} - {servant.class_name} ({servant.rarity}★)",
                        'class_name': servant.class_name,
                        'rarity': servant.rarity
                    })
                    break
    
    return jsonify(result[:10])  # 限制结果数量

@main.route('/admin/sync', methods=['GET', 'POST'])
def admin_sync():
    """API数据同步管理页面"""
    if request.method == 'POST':
        try:
            # 导入API同步功能
            from app.api import update_servant_db
            
            # 显示开始同步的提示信息
            flash('开始同步从者数据，这可能需要几分钟时间...', 'info')
            
            # 调用现有的更新函数
            update_servant_db()
            
            # 显示成功信息
            flash('从者数据同步完成！', 'success')
                
        except ImportError:
            flash('无法导入同步功能，请检查API模块是否存在', 'error')
        except Exception as e:
            flash(f'同步过程中发生错误: {str(e)}', 'error')
    
    # 获取当前数据库状态信息
    try:
        from app.models import get_all_servants
        servants = get_all_servants()
        servant_count = len(servants)
        class_stats = {}
        
        for servant in servants:
            if servant.class_name not in class_stats:
                class_stats[servant.class_name] = 0
            class_stats[servant.class_name] += 1
            
        # 按职阶数量排序
        sorted_class_stats = dict(sorted(class_stats.items(), key=lambda x: x[1], reverse=True))
    except:
        servant_count = 0
        sorted_class_stats = {}
    
    # 确保使用正确的模板路径
    return render_template(
        'admin/sync.html',  # 使用正确的模板路径
        servant_count=servant_count,
        class_stats=sorted_class_stats
    )

@main.route('/surrender', methods=['POST'])
def surrender_game():
    """处理玩家投降"""
    if 'target_servant_id' not in session:
        flash('没有进行中的游戏', 'warning')
        return redirect(url_for('main.index'))
    
    # 获取正确答案
    from app.models import get_servant_by_id
    target_servant = get_servant_by_id(session['target_servant_id'])
    
    if not target_servant:
        flash('获取游戏数据失败', 'error')
        return redirect(url_for('main.index'))
    
    # 记录游戏结果
    attempts = session.get('attempts', 0)
    update_game_stats(win=False, attempts=attempts)
    
    # 计算游戏时间
    game_time = calculate_game_time(session.get('game_start_time'))
    
    # 获取所有猜测记录
    guesses = session.get('guesses', [])
    comparisons = session.get('comparisons', [])
    
    max_attempts = session.get('max_attempts', 10)


    # 清除游戏会话
    clear_game_session()
    # 跳转到结算页面，并传递投降标志
    return render_template('game_result.html', 
                          win=False,
                          surrendered=True,  # 添加投降标志
                          target_servant=target_servant,
                          attempts=attempts,
                          max_attempts=max_attempts,
                          game_time=game_time,
                          guesses=guesses,
                          comparisons=comparisons)

def update_game_stats(win, attempts):
    """更新游戏统计"""
    stats = session.get('game_stats', {'games': 0, 'wins': 0, 'avg_attempts': 0})
    
    stats['games'] = stats.get('games', 0) + 1
    
    if win:
        stats['wins'] = stats.get('wins', 0) + 1
    
    # 更新平均尝试次数
    total_attempts = stats.get('avg_attempts', 0) * (stats.get('games', 1) - 1) + attempts
    stats['avg_attempts'] = round(total_attempts / stats['games'], 2)
    
    session['game_stats'] = stats

def calculate_game_time(start_time_iso):
    """计算游戏时间"""
    if not start_time_iso:
        return "未知"
        
    try:
        start_time = datetime.datetime.fromisoformat(start_time_iso)
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        
        # 转换为分钟和秒
        minutes = delta.seconds // 60
        seconds = delta.seconds % 60
        
        return f"{minutes}分{seconds}秒"
    except:
        return "未知"

def clear_game_session():
    """清除游戏状态"""
    keys_to_remove = [
        'target_servant_id', 'attempts', 'max_attempts',
        'hint_enabled', 'hint_used', 'guesses', 'comparisons',
        'game_start_time', 'compare_options', 'max_hints', 'current_hint'
    ]
    
    for key in keys_to_remove:
        if key in session:
            session.pop(key)