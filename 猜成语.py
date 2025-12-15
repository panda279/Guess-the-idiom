import streamlit as st
import pandas as pd
import random
import time
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="表情包猜成语",
    page_icon="😀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 初始化session state
def init_session_state():
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_attempted' not in st.session_state:
        st.session_state.total_attempted = 0
    if 'correct_count' not in st.session_state:
        st.session_state.correct_count = 0
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
    if 'answer_submitted' not in st.session_state:
        st.session_state.answer_submitted = False

# 加载题库 
def load_idioms():
    csv_path = Path("emoji_idioms.csv")
    if not csv_path.exists():
        return None, "读取失败：找不到题库文件 'emoji_idioms.csv'"
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        # 检查必要的列
        required_columns = ['表情包', '成语', '解释']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, f"读取失败：题库文件缺少必要列: {', '.join(missing_columns)}"
        
        if len(df) == 0:
            return None, "读取失败：题库文件为空"
        
        return df, None
    except Exception as e:
        return None, f"读取失败：{str(e)}"

# 获取随机成语
def get_random_idiom(df):
    return df.sample(1).iloc[0]

# 开始新游戏
def start_new_game(df):
    st.session_state.game_started = True
    st.session_state.show_answer = False
    st.session_state.user_answer = ""
    st.session_state.answer_submitted = False
    st.session_state.current_idiom = get_random_idiom(df)
    st.session_state.start_time = time.time()

# 检查答案
def check_answer():
    if not st.session_state.current_idiom:
        return False
    
    user_answer = st.session_state.user_answer.strip()
    correct_answer = st.session_state.current_idiom['成语']
    
    # 精确匹配
    is_correct = (user_answer == correct_answer)
    
    # 更新统计
    st.session_state.total_attempted += 1
    if is_correct:
        st.session_state.correct_count += 1
        st.session_state.score += 10
    
    st.session_state.last_result = is_correct
    st.session_state.answer_submitted = True
    st.session_state.show_answer = True
    return is_correct

# 主应用
def main():
    # 初始化
    init_session_state()
    
    # 加载题库
    idioms_df, error_msg = load_idioms()
    
    # 标题
    st.title("😀 表情包猜成语")
    st.markdown("---")
    
    # 显示错误信息（如果有）
    if error_msg:
        st.error(f"**{error_msg}**")
        st.info("""
        **请按照以下步骤操作：**
        1. 创建名为 `emoji_idioms.csv` 的文件
        2. 文件应包含以下列：`表情包`, `成语`, `解释`
        3. 每行一个成语，例如：`😍🐉,叶公好龙,比喻表面上爱好某事物，实际上并不真爱好，甚至畏惧它`
        4. 将文件放在与 `app.py` 相同的目录下
        5. 刷新页面
        """)
        return
    
    # 显示统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("当前得分", st.session_state.score)
    with col2:
        st.metric("答题总数", st.session_state.total_attempted)
    with col3:
        st.metric("题库总数", len(idioms_df))
    
    st.markdown("---")
    
    # 游戏区域
    if not st.session_state.game_started:
        # 开始界面
        st.markdown("""
        <div style='text-align: center; padding: 40px 0;'>
            <h2>🎮 游戏规则</h2>
            <p style='font-size: 1.2em; margin: 20px 0;'>
                根据表情包组合，猜出对应的成语<br>
                在下方输入框中**手打输入**你的答案
            </p >
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 开始游戏", type="primary", use_container_width=True):
                start_new_game(idioms_df)
                st.rerun()
    else:
        # 游戏进行中
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
        st.markdown("### 📝 输入你的答案")
        
        # 创建两个并排的列
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 输入框
            user_input = st.text_input(
                "请输入成语：",
                value=st.session_state.user_answer,
                key="answer_input",
                placeholder="在此输入你的答案...",
                label_visibility="collapsed"
            )
            st.session_state.user_answer = user_input
        
        with col2:
            # 提交按钮
            if st.button("📤 提交答案", type="primary", use_container_width=True):
                if user_input.strip():
                    check_answer()
                    st.rerun()
                else:
                    st.warning("请输入答案！")
        
        # 显示结果（如果已提交）
        if st.session_state.answer_submitted:
            st.markdown("---")
            
            if st.session_state.last_result:
                st.success(f"🎉 **恭喜！答对了！** 正确答案是：**{current['成语']}**")
                st.balloons()
            else:
                st.error(f"❌ **很遗憾，答错了！** 正确答案是：**{current['成语']}**")
            
            # 显示解释
            with st.expander("📖 查看成语解释"):
                st.markdown(f"**成语：** {current['成语']}")
                st.markdown(f"**解释：** {current['解释']}")
            
            # 下一题按钮
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 下一题", type="primary", use_container_width=True):
                    start_new_game(idioms_df)
                    st.rerun()
        else:
            # 显示当前思考时间
            current_time = time.time() - st.session_state.start_time
            st.caption(f"⏱️ 思考时间: {int(current_time)}秒")

# 运行应用
if __name__ == "__main__":
    main()