import streamlit as st

st.set_page_config(
    page_title="테스트 앱",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Streamlit Cloud 연결 테스트")
st.write("이 앱이 정상적으로 표시되면 Streamlit Cloud 연결이 성공한 것입니다!")

st.success("✅ 연결 성공!")
st.info("이제 메인 앱으로 이동할 수 있습니다.")

if st.button("메인 앱으로 이동"):
    st.switch_page("app.py")
