import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import requests
import urllib3  

# Disable SSL warnings (only for dev!)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="Clarifi Dashboard", page_icon=":bar_chart:", layout="wide")

# -----------------------------
# Title
# -----------------------------
st.markdown(
    """
    <h1 style='text-align:center;font-family:Times New Roman; color:#2C3E50;'>
        Clarifi Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Load Data
# -----------------------------
csv_file = "data/WorkflowDataMaster.csv"   # update path
df = pd.read_csv(csv_file)

# Mock Data
df["Success"] = [1,2,3,4,5,6,7,8,12,21,13,14,15,18,99,87,89,88,81,82,56,76]
df["Failed"] = [10,20,30,0,0,30,50,10,10,40,90,20,0,0,0,0,0,0,0,0,0,0]
df["Unprocessed"] = [20,30,50,60,70,80,80,90,30,40,50,60,0,0,0,0,0,0,0,0,0,0]

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown(
    """
    <style>
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 10px;
        border-radius: 12px;
        background-color: #f9f9f9;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 0px;
    }
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 18px;
        margin: 6px 0;
        max-width: 85%;
        line-height: 1.4;
        font-size: 14px;
    }
    .assistant {
        background-color: #E8F5E9;
        color: #2E7D32;
        border-bottom-left-radius: 4px;
    }
    .user {
        background-color: #E3F2FD;
        color: #1565C0;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Date Filter
# -----------------------------
st.subheader("Filter by Date")
col1, col2, col3, col4 = st.columns([1,1,0.5,0.5])

with col1:
    from_date = st.date_input("From", datetime.date(2018, 4, 1), key="from_date")
with col2:
    to_date = st.date_input("To", datetime.date(2019, 10, 14), key="to_date")
with col3:
    filter_clicked = st.button("Filter")
with col4:
    go_clicked = st.button("Go")

st.markdown("---")

# -----------------------------
# Bar Chart
# -----------------------------
fig = go.Figure()
fig.add_trace(go.Bar(
    y=df["WorkflowName"], x=df["Success"], name="Success",
    orientation='h', marker_color='green'
))
fig.add_trace(go.Bar(
    y=df["WorkflowName"], x=df["Failed"], name="Failed",
    orientation='h', marker_color='red'
))
fig.add_trace(go.Bar(
    y=df["WorkflowName"], x=df["Unprocessed"], name="Unprocessed",
    orientation='h', marker_color='orange'
))
fig.update_layout(
    barmode='group',
    height=400,
    margin=dict(t=30, r=30, l=30, b=20),
    showlegend=True,
    xaxis=dict(title='Count', showgrid=True),
    yaxis=dict(title='Workflows', showgrid=False),
    paper_bgcolor='rgba(245, 246, 249, 1)',
    plot_bgcolor='rgba(245, 246, 249, 1)'
)

# -----------------------------
# Layout: Chart + Chatbot
# -----------------------------
col_chart, col_chat = st.columns([2, 1], gap="large")

# Chart Section
with col_chart:
    st.subheader("Workflow Status Overview")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Workflow Summary")
    st.table(pd.DataFrame({
        '': ['Success', 'Failed', 'Unprocessed'],
        'Order': [7, 2, 0],
        'Product': [4, 1, 1],
        'Inventory': [9, 0, 1],
        'Account': [5, 4, 1]
    }).set_index(''))

# -----------------------------
# Chatbot Section
# -----------------------------
with col_chat:
    st.subheader("Clarifi AI Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello, I’m Clarifi AI. How can I help you today?"}
        ]

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role_class = "assistant" if msg["role"] == "assistant" else "user"
        st.markdown(
            f"<div class='chat-bubble {role_class}'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Type your message...")
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            url = "https://devflow.insync.top/webhook/b58598a0-22dd-4ae6-a4ec-ee2037988c75/chat"
            payload = {"query": user_input}
            # Ignore SSL verification (dev only)
            response = requests.post(url, json=payload, timeout=10, verify=False)

            if response.status_code == 200:
                reply = response.json().get("reply", response.text)
            else:
                reply = f"⚠️ Error {response.status_code}: {response.text}"

        except Exception as e:
            reply = f"⚠️ Failed to connect to assistant: {e}"

        # Add assistant reply
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

