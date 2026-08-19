"""
Week9 D5：Streamlit 界面 —— AI 业代助手可演示成品
输入框 + 回答区 + 来源展示 + 多轮对话（RepChat 持一个实例）
依赖：streamlit、chat.py（同目录，已改进为 import 安全）
"""
import os
import streamlit as st
from chat import RepChat

st.set_page_config(page_title="AI 业代助手", page_icon="🛒")
st.title("🛒 AI 业代助手")
st.caption("基于你的知识库 + DeepSeek 的 RAG 问答（支持多轮对话）")

# 每个会话持一个 RepChat 实例（多轮记忆在实例里）
if "bot" not in st.session_state:
    with st.spinner("正在加载知识库与语义模型…（首次约 5 秒）"):
        st.session_state.bot = RepChat()
if "messages" not in st.session_state:
    st.session_state.messages = []

if not os.getenv("DEEPSEEK_API_KEY"):
    st.warning("⚠️ 未检测到 DEEPSEEK_API_KEY。请在终端先 `source ~/.zshrc` 再启动本程序。")

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

if prompt := st.chat_input("问点什么，比如：陈列费核销需要什么材料？"):
    st.session_state.messages.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("检索知识库 + 调用 DeepSeek…"):
            try:
                answer, sources = st.session_state.bot.chat(prompt)
                if sources:
                    src_line = "\n\n---\n📚 **参考来源**：" + "、".join(dict.fromkeys(sources))
                    full = answer + src_line
                else:
                    full = answer
                st.markdown(full)
                st.session_state.messages.append(("assistant", full))
            except Exception as e:
                err = f"⚠️ 出错：{e}"
                st.markdown(err)
                st.session_state.messages.append(("assistant", err))

with st.sidebar:
    st.header("操作")
    if st.button("🔄 重置对话"):
        st.session_state.messages = []
        st.session_state.bot = RepChat()
        st.rerun()
    st.divider()
    st.caption("知识库：~/fde/week9_ai_rep/knowledge/")
    st.caption("想加内容？往 knowledge/ 丢 .md，重跑 kb.py 即可。")
