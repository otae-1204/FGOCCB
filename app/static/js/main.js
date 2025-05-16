document.addEventListener('DOMContentLoaded', function() {
    console.log('FGO从者猜猜看已加载');
    
    // 自动关闭闪烁消息
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            }, 3000);
        });
    }
    
    // 难度选择增强
    const difficultyOptions = document.querySelectorAll('.difficulty-option input[type="radio"]');
    if (difficultyOptions.length > 0) {
        difficultyOptions.forEach(option => {
            option.addEventListener('change', function() {
                // 添加选择动画
                const label = this.nextElementSibling;
                label.classList.add('pulse-animation');
                setTimeout(() => {
                    label.classList.remove('pulse-animation');
                }, 500);
            });
        });
    }
    
    // 从者卡片悬停效果
    const servantCards = document.querySelectorAll('.servant-card');
    if (servantCards.length > 0) {
        servantCards.forEach(card => {
            // 添加悬停效果
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
            });
            
            card.addEventListener('mouseleave', function() {
                if (!this.classList.contains('selected')) {
                    this.style.transform = '';
                    this.style.boxShadow = '';
                }
            });
        });
    }
    
    // 提示按钮动画
    const hintButton = document.getElementById('hint-button');
    if (hintButton) {
        hintButton.addEventListener('mouseenter', function() {
            if (!this.disabled) {
                this.classList.add('pulse');
            }
        });
        
        hintButton.addEventListener('mouseleave', function() {
            this.classList.remove('pulse');
        });
    }
    
    // 表格行高亮
    const comparisonRows = document.querySelectorAll('.comparison-table tbody tr');
    if (comparisonRows.length > 0) {
        comparisonRows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.classList.add('highlight-row');
            });
            
            row.addEventListener('mouseleave', function() {
                this.classList.remove('highlight-row');
            });
        });
    }
    
    // 比较属性的交互式解释
    const comparisonCells = document.querySelectorAll('.comparison-table td:not(.servant-name)');
    if (comparisonCells.length > 0) {
        comparisonCells.forEach(cell => {
            // 为每个单元格添加点击事件，显示属性解释
            cell.addEventListener('click', function() {
                const attributeType = this.closest('tr').cells[Array.from(this.parentNode.children).indexOf(this)].textContent.trim();
                const attributeStatus = this.classList.contains('match') ? '匹配' : (this.classList.contains('partial-match') ? '部分匹配' : '不匹配');
                
                alert(`属性: ${attributeType}\n状态: ${attributeStatus}\n\n这是目标从者与你猜测的从者之间的属性比较结果。`);
            });
        });
    }
    
    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        // 在游戏页面使用键盘快捷键
        if (document.getElementById('guess-form')) {
            // 按H键获取提示
            if (e.key.toLowerCase() === 'h') {
                const hintBtn = document.getElementById('hint-button');
                if (hintBtn && !hintBtn.disabled) {
                    hintBtn.click();
                }
            }
            
            // 按Enter键提交当前选中的从者
            if (e.key === 'Enter') {
                const submitBtn = document.getElementById('submit-guess');
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.click();
                }
            }
        }
    });
    
    // 为难度选择添加键盘快捷键
    if (document.querySelector('.difficulty-options')) {
        document.addEventListener('keydown', function(e) {
            if (e.key === '1') {
                document.getElementById('easy').checked = true;
            } else if (e.key === '2') {
                document.getElementById('normal').checked = true;
            } else if (e.key === '3') {
                document.getElementById('hard').checked = true;
            }
        });
    }
    
    // 动态背景效果
    const createBackground = () => {
        const background = document.createElement('div');
        background.classList.add('dynamic-background');
        document.body.appendChild(background);
        
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.classList.add('bg-particle');
            
            // 随机位置和大小
            const size = Math.random() * 30 + 10;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.opacity = Math.random() * 0.2;
            
            // 随机颜色
            const colors = ['#e94560', '#16213e', '#0f3460', '#533483'];
            particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            
            // 随机动画延迟
            particle.style.animationDelay = `${Math.random() * 5}s`;
            particle.style.animationDuration = `${Math.random() * 10 + 10}s`;
            
            background.appendChild(particle);
        }
    };
    
    // 在首页和结果页面添加动态背景
    if (document.querySelector('.welcome-section') || 
        document.querySelector('.result-container') ||
        document.querySelector('.difficulty-container')) {
        createBackground();
    }
    // 查找所有dynamic-background元素并移除
    var bgElements = document.querySelectorAll('.dynamic-background');
    bgElements.forEach(function(element) {
        if(element.parentNode) {
            element.parentNode.removeChild(element);
        }
    });
});
