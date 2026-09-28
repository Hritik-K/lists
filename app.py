import streamlit as st
import Collection
import components


#useful only if info_table is not already initialized
#Note: to remove this part when another way is found 
if '_initialized' not in st.session_state:
    Collection.create_info_table()
    st.session_state['_initialized'] = True

#set collections in state
if '_collections' not in st.session_state:
    collections = Collection.fetch_all_collections_details()
    st.session_state['_collections'] = collections
    st.session_state['_titles'] = list(collections.keys())

# for variable,variable_default in components.state_variables.items():
#     if variable not in st.session_state:
#         st.session_state[variable] = variable_default


# side panel
components.side_panel()


# main window
st.title("My Lists:")

if st.session_state['_titles']:
    selected_collection = st.session_state['_selected_collection']
    if '_edit_table' not in st.session_state:
        st.session_state['_edit_table']=False
    st.header(selected_collection)

    if st.button('',icon=":material/edit:"):
        st.session_state['_edit_table'] = not st.session_state['_edit_table']

    ids = components.table(selected_collection,editable=st.session_state['_edit_table'])
    if st.session_state['_edit_table']:
        st.button('',icon=":material/save:",on_click=components.save_changes,args=[ids])
else:
    st.markdown(""" ## No collections to show
    Add a collection from sidepanel""")

