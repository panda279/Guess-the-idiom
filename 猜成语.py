import sys
import asyncio
import streamlit as st
import pandas as pd
import random
from pathlib import Path

# 修复 Windows 上的 asyncio 问题
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 页面配置
st.set_page_config(
    page_title="表情包猜成语",
    page_icon="😀",
    layout="centered"
)

# 初始化session state
def init_session_state():
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_attempted' not in st.session_state:
        st.session_state.total_attempted = 0
    if 'current_idiom' not in st.session_state:
        st.session_state.current_idiom = None
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = ""
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None

# 加载题库
def load_idioms():
    csv_path = Path("问题.csv")
    if not csv_path.exists():
        return None, "读取失败：找不到题库文件 '问题.csv'"
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            return None, "读取失败：题库文件内容为空"
        
        lines = content.split('\n')
        data = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 支持多种分隔符
            if '——' in line:
                parts = line.split('——', 1)
            elif '—' in line:
                parts = line.split('—', 1)
            elif ',' in line:
                parts = line.split(',', 1)
            elif '，' in line:
                parts = line.split('，', 1)
            elif '\t' in line:
                parts = line.split('\t', 1)
            else:
                continue
            
            if len(parts) == 2:
                emoji = parts[0].strip()
                idiom = parts[1].strip()
                if emoji and idiom:
                    data.append([emoji, idiom])
        
        if len(data) == 0:
            return None, "读取失败：题库文件格式不正确"
        
        df = pd.DataFrame(data, columns=['表情包', '成语'])
        return df, None
        
    except Exception as e:
        return None, f"读取失败：{str(e)}"

# 获取随机成语
def get_random_idiom(df):
    if df is None or len(df) == 0:
        return None
    return df.sample(1).iloc[0]

# 开始新游戏
def start_new_game(df):
    if df is None or len(df) == 0:
        return
    
    st.session_state.game_started = True
    st.session_state.show_answer = False
    st.session_state.user_answer = ""
    st.session_state.current_idiom = get_random_idiom(df)

# 检查答案
def check_answer():
    # 正确检查 Pandas Series 对象是否为空
    if st.session_state.current_idiom is None or st.session_state.current_idiom.empty:
        return False
    
    user_answer = st.session_state.user_answer.strip()
    correct_answer = st.session_state.current_idiom['成语']
    
    is_correct = (user_answer == correct_answer)
    
    st.session_state.total_attempted += 1
    if is_correct:
        st.session_state.score += 10
    
    st.session_state.last_result = is_correct
    st.session_state.show_answer = True
    return is_correct

# 主应用
def main():
    init_session_state()
    
    st.title("😀 表情包猜成语")
    st.markdown("---")
    
    # 加载题库
    idioms_df, error_msg = load_idioms()
    
    # 显示错误信息
    if error_msg:
        st.error(f"**{error_msg}**")
        st.info("""
        **文件格式要求：**
        创建名为 `问题.csv` 的文件，每行格式：`表情包,成语`
        
        **示例：**
        ```
        😍🐉,叶公好龙
        🙉🔔,掩耳盗铃
        🦊🐯,狐假虎威
        ```
        """)
        return
    
    # 显示统计信息
    col1, col2 = st.columns(2)
    with col1:
        st.metric("当前得分", st.session_state.score)
    with col2:
        st.metric("答题总数", st.session_state.total_attempted)
    
    st.markdown("---")
    
    # 游戏区域
    if not st.session_state.game_started:
        st.markdown("""
        <div style='text-align: center; padding: 40px 0;'>
            <h2>🎮 游戏规则</h2>
            <p style='font-size: 1.2em; margin: 20px 0;'>
                根据表情包猜成语<br>
                在输入框中手打输入答案
            </p >
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 开始游戏", type="primary", use_container_width=True):
            start_new_game(idioms_df)
            st.rerun()
    else:
        # 正确检查 current_idiom 是否有效
        if st.session_state.current_idiom is None or st.session_state.current_idiom.empty:
            st.error("获取题目失败，请重新开始游戏")
            st.session_state.game_started = False
            return
        
        current = st.session_state.current_idiom
        
        # 显示表情包
        st.markdown(f"""
        <div style='text-align: center; margin: 40px 0;'>
            <div style='font-size: 5em; letter-spacing: 15px; margin: 30px 0;'>
                {current['表情包']}
            </div>
            <p style='font-size: 1.2em; color: #666;'>
                根据表情包猜一个成语
            </p >
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 答案输入区域
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_input = st.text_input(
                "请输入成语：",
                value=st.session_state.user_answer,
                key="answer_input",
                placeholder="在此输入你的答案...",
                label_visibility="collapsed"
            )
            st.session_state.user_answer = user_input
        
        with col2:
            if st.button("📤 提交答案", type="primary", use_container_width=True):
                if user_input.strip():
                    check_answer()
                    st.rerun()
                else:
                    st.warning("请输入答案！")
        
        # 显示结果
        if st.session_state.show_answer:
            st.markdown("---")
            
            if st.session_state.last_result:
                st.success("🎉 **恭喜！答对了！**")
                st.balloons()
            else:
                st.error(f"❌ **答错了！** 正确答案：**{current['成语']}**")
            
            if st.button("🔄 下一题", type="primary", use_container_width=True):
                start_new_game(idioms_df)
                st.rerun()

if __name__ == "__main__":
    main()