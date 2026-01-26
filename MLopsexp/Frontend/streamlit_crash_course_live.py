import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px
import time
# =============================================================
# 🚀 STREAMLIT CRASH COURSE - SIMPLE AND CLEAR DEMOS
# Each section shows one or two examples in layman terms.
# =============================================================

# =========================
# PAGE ELEMENTS - TEXT
# =========================
st.title("🎉 Streamlit Crash Course")
st.header("This is a Header - Like a Chapter Title")
st.subheader("This is a Subheader - Like a Section Title")
st.markdown("**Markdown allows formatting like bold and _italic_**")

# Formatted text
st.caption("📌 Small caption text, used for hints")
st.code("print('Hello Streamlit!')", language="python")
st.divider()  # horizontal line
st.latex(r"E = mc^2")

# Utilities
st.html("<b style='color:red'>This is custom HTML</b>")

# =========================
# DATA ELEMENTS
# =========================
df = pd.DataFrame({"Name": ["Aarav", "Priya"], "Marks": [85, 90]})
st.write("Dataframe view:")
st.dataframe(df)
st.write("Static table view:")
st.table(df)
st.metric("Temperature", "30 °C", "+2 °C")
st.json({"student": "Aarav", "marks": 85})

# =========================
# CHART ELEMENTS
# =========================
# Simple charts
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["A", "B", "C"])
st.line_chart(chart_data)
st.bar_chart(chart_data)
st.area_chart(chart_data)

# Map and scatter
map_data = pd.DataFrame({
    "lat": np.random.uniform(12.9, 13.1, 50),
    "lon": np.random.uniform(77.5, 77.7, 50)})
st.map(map_data)
st.scatter_chart(chart_data)

# Advanced charts
st.altair_chart(alt.Chart(chart_data).mark_circle().encode(x="A", y="B", size="C"))
st.plotly_chart(px.scatter(chart_data, x="A", y="B", color="C"))
st.graphviz_chart("digraph G {A -> B; B -> C; C -> A;}")

fig, ax = plt.subplots()
ax.plot([1,2,3],[4,5,6])
st.pyplot(fig)

st.vega_lite_chart(chart_data, {"mark": "bar", "encoding": {"x": {"field": "A"}, "y": {"field": "B"}}})

# =========================
# INPUT WIDGETS
# =========================
# Buttons
if st.button("Click Me"):
    st.write("Button clicked!")
st.download_button("Download Sample", data="Hello World", file_name="sample.txt")
st.link_button("Open Google", "https://google.com")

# Selections
st.checkbox("I agree")
st.color_picker("Pick a color")
st.feedback("thumbs")
st.multiselect("Select multiple", ["A","B","C"])
st.radio("Choose one", ["Option 1","Option 2"])

st.selectbox("Select a student", ["Aarav","Priya"])
st.select_slider("Choose level", ["Low","Medium","High"])
st.toggle("Turn me on/off")

# Numeric
st.number_input("Enter a number", 0, 100)
st.slider("Select a value", 0, 100)

# Date and Time
st.date_input("Pick a date")
st.time_input("Pick a time")

# Text inputs
st.text_input("Enter your name")
st.text_area("Enter feedback")
st.chat_input("Say something")

# Media and Files
st.file_uploader("Upload a file")
st.camera_input("Take a picture")

# =========================
# MEDIA ELEMENTS
# =========================
st.image("https://picsum.photos/200", caption="Random Image")
st.video("https://www.w3schools.com/html/mov_bbb.mp4")
st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
st.logo("https://streamlit.io/images/brand/streamlit-mark-color.png")

# =========================
# LAYOUTS AND CONTAINERS
# =========================
col1, col2 = st.columns(2)
col1.write("Left column")
col2.write("Right column")

with st.expander("Click to expand"):
    st.write("Hidden details here!")

placeholder = st.empty()
placeholder.write("This will be replaced...")
placeholder.write("Now it's updated!")

with st.sidebar:
    st.write("This is in the sidebar")

tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
tab1.write("Content of Tab 1")
tab2.write("Content of Tab 2")

# =========================
# CHAT ELEMENTS
# =========================
st.chat_message("user").write("Hello from the user")
st.chat_message("assistant").write("Hello from Streamlit")
st.write_stream(iter(["Streaming text...", " still going...", " done!"]))

# =========================
# STATUS ELEMENTS
# =========================
st.success("Success message")
st.info("Information message")
st.warning("Warning message")
st.error("Error message")

try:
    1/0
except Exception as e:
    st.exception(e)

st.progress(50)
with st.spinner("Loading..."):
    time.sleep(10) 
st.toast("This is a toast message")
st.balloons()
st.snow()

# =========================
# APPLICATION LOGIC
# =========================
if st.button("Go to Google page"):
    st.switch_page("https://google.com")

if st.button("Rerun app"):
    st.rerun()

if st.button("Stop execution now"):
    st.stop()

# Caching and state
@st.cache_data
def get_data():
    return np.random.randn(100)
st.write(get_data())

if "count" not in st.session_state:
    st.session_state.count = 0
if st.button("Increment"):
    st.session_state.count += 1
st.write("Counter value:", st.session_state.count)
