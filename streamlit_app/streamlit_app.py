import streamlit as st
import httpx

st.header("Pipreqs API Frontend")
st.write(
    "Streamlit App to drive [pipreqs-api](https://github.com/gerardrbentley/pipreqs-api)."
)
st.write("Made with ❤️ from [Gar's Bar](https://tech.gerardbentley.com/)")

default_url = "https://github.com/gerardrbentley/pipreqs-api"
with st.form("form"):
    code_url = st.text_input("Git Code Url", default_url)
    submitted = st.form_submit_button("Generate Requirements")

if not submitted:
    st.info("Press 'Generate Requirements' to continue")
    st.stop()
with st.spinner("Fetching response"):
    response = httpx.get(
        "https://pipreqs-api.herokuapp.com/pipreqs", params={"code_url": code_url}
    )

if not response.status_code == 200:
    st.error("Couldn't run pipreqs on the repo. See API error below")
    st.json(response.json())
    st.stop()

st.code(response.text)

st.download_button(
    "Download Requirements.txt",
    response.text,
    file_name="requirements.txt",
    mime="text/plain",
)
