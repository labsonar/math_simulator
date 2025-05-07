import streamlit as st

import lps_synthesis.streamlit.propagation as lps_st_propag

def main():
    """Main test function"""

    st.set_page_config(layout="wide")
    st.title("Editor de Descrição de Canal")

    ssp = lps_st_propag.SSP()

    with st.sidebar:
        with st.expander("Configuração do Canal", expanded=True):
            ssp.configure()

    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.header("Perfil de Velocidade do Som")
        ssp.plot()

    ssp.check_dialogs()

if __name__ == "__main__":
    main()
