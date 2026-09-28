import streamlit as st
import Collection

# state_variables = {'_add_entry':False}
types = ['INTEGER','DECIMAL', 'TEXT', 'BOOLEAN', 'CHECKBOX','NONE'] # 'TOGGLE',
def column_types(label, type): 
    match type:
        case 'INTEGER':
            return st.column_config.NumberColumn(label=label,format='%d')
        case 'DECIMAL':
            return st.column_config.NumberColumn(label=label,format='%f')
        case 'BOOLEAN' | 'CHECKBOX':    # 'TOGGLE' |
            return st.column_config.CheckboxColumn(label=label)
        case _:
            return st.column_config.TextColumn(label=label)


def side_panel():
    titles = st.session_state['_titles']
    with st.sidebar:
        st.title("Collections")
        selected_collection = st.selectbox("Pick a collection:",titles)
        create_collection = st.button("Create Collection",icon=":material/add:")
        delete_collection = st.button("Delete Collection",icon=":material/delete:")
        
        if create_collection:
            _new_collection_form()


        if delete_collection:
            _delete_collection(selected_collection)
    st.session_state['_selected_collection'] = selected_collection

def table(selected_collection, editable=False):
    data = Collection.fetch_from_collection(selected_collection)
    columns_and_types = Collection.fetch_collection_details(selected_collection)
    column_config = {}
    columns = []
    for column, type in columns_and_types:
        column_config[column] = column_types(column,type)
        if column != 'id':
            columns.append(column)

    if editable:
        table = st.data_editor(
            data,
            key=selected_collection,
            column_order=columns,
            column_config=column_config,
            hide_index=True,
            num_rows='dynamic',
            disabled=['id']
        )
        edits_in_table = st.session_state[selected_collection]
        # print(edits_in_table)
        print(st.session_state[selected_collection])
    else:
        table = st.dataframe(
            data,
            column_order=columns,
            column_config=column_config,
            hide_index=True
        )
    return data['id']

def save_changes(ids):
    selected_collection = st.session_state['_selected_collection']
    changes = st.session_state[selected_collection]
    edits = changes['edited_rows']
    additions = changes['added_rows']
    deletions = changes['deleted_rows']
    if edits:
        edit_ids = {}
        for index, change in edits.items():
            edit_ids[int(ids.iloc[index])] = change
        Collection.edit_collection_using_ids(selected_collection,edit_ids)
    if additions:
        Collection.add_multi_to_collection(selected_collection,additions)
    if deletions:
        delete_ids = ids.iloc[deletions].to_list()
        Collection.remove_from_collection_using_ids(selected_collection,delete_ids)

    st.session_state['_edit_table'] = False

@st.dialog("Create Collection")
def _new_collection_form():
    with st.form(
        key='new_collection_form',
        clear_on_submit=True,
        enter_to_submit=False
    ):
        title = st.text_input('title')
        data = {"field":[""],"type":[""]}
        headings = st.data_editor(
            data,
            num_rows='dynamic',
            column_config={
                "type": st.column_config.SelectboxColumn(
                    options = types
                )
            }
        )
        submit = st.form_submit_button('Submit')
        if submit:
            _columns = headings['field']
            _types = headings['type']
            Collection.create_collection(title,*_columns)
            Collection.save_collection_info(title,zip(_columns,_types))
            st.session_state['_titles'].append(title)
            st.session_state['_collections'][title] = list(zip(_columns,_types))
            st.rerun()

@st.dialog("Confirm action")
def _delete_collection(title):
    st.markdown(f""" 
    # Do you want to delete {title}?  
    This action cannot be undone.
    """)
    col1, col2, _ = st.columns([1,1,4],gap='small',)
    with col1:
        delete_confirmation = st.button("Yes",type='primary')
    with col2:
            do_not_delete = st.button("No",type='secondary')
    if delete_confirmation:
        Collection.delete_collection(title)
        Collection.delete_collection_info(title)
        st.session_state['_collections'].pop(title)
        st.session_state['_titles'].remove(title)
        st.rerun()
    if do_not_delete:
        st.rerun()


@st.dialog("Add columns to Collection")
def _add_column_form():
    pass

@st.dialog("Delete columns from Collection")
def _delete_column_from_collection():
    pass