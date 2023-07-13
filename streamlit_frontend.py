import random
from io import StringIO

import streamlit as st
from streamlit import session_state as ss

from generators.piplines import TaskGenerator
from text_tools.txt_to_df import make_df
from try_save_variables import stash

blank = '___'

st.header('Генератор упражнений по английскому')
st.subheader(f'Правильных ответов: {stash.count_wins()}  Ошибок {stash.count_losses()}')
# Настройка боковой панели
st.sidebar.title(f"Панель управления", )
st.sidebar.info(
    "Загрузите текстовый файл (формата txt),"
    " выберете число упражнений и/или их тип"
)
uploaded_file = st.sidebar.file_uploader('Upload text', help="Выберете файл txt c английским текстом", type=['txt'])

tasks_count = st.sidebar.selectbox(label='Число упражнений', options=[5, 10, 20, 25], key='task_count')
selected_types = st.sidebar.multiselect(
    'Типы заданий',
    options=stash.tasks_types,
    key='selected_types'

)

is_reset = st.sidebar.button('Новый набор', type='primary')
st.sidebar.button('Сбросить статистику', on_click=stash.clean_stats)


def reset_tasks():
    stash.seed = random.randint(2, 100000)
    stash.clean()
    for key in ss.keys():
        if 'sbx' in key:
            ss[key] = blank
    st.session_state.selection = 'nolabel'


if is_reset:
    reset_tasks()


@st.cache_data
def upload_txt():
    with StringIO(uploaded_file.getvalue().decode("utf-8")) as steam:
        string_data = steam.read()

    return string_data


def create_text_df(text):
    st.text_area(label=uploaded_file.name, value=text)
    return make_df(text)


def create_tasks(seed):
    if not selected_types:
        tasks = stash.generator.get_tasks(tasks_count, seed=seed)
    else:
        tasks = stash.generator.get_tasks(tasks_count, selected_types, seed=seed)
    return tasks


def render_tasks(tasks):
    for index, task in enumerate(tasks):
        col1, col2 = st.columns(2)
        with col1:
            st.write('')
            st.write(str(task['sentence']))

        with col2:
            for i in range(len(task['options'])):
                option = task['options'][i]
                task['result'][i] = st.selectbox(f'nolabel-{index}',
                                                 [blank] + option,
                                                 label_visibility="hidden",
                                                 key=f'sbx-{index}'
                                                 )
                if task['result'][i] == blank:
                    pass
                elif task['result'][i].lower() == task['answers'][i].lower():
                    st.success('', icon="✅")
                    stash.wins[hash(task['sentence'])] = 1
                    task['total'] = True
                else:
                    st.error('', icon="😟")
                    stash.losses[hash(task['sentence'])] = 1
                    task['total'] = False
        # task['total'] = task['result'] == task['answers']
        '---'

    total_sum = sum(task['total'] for task in tasks)

    if total_sum == len(tasks):
        st.success('Успех!')
        st.balloons()
        st.button('Дальше', type='primary', on_click=reset_tasks)

    return True


if uploaded_file is not None:
    text = upload_txt()
    if not stash.tasks:
        if not stash.generator:
            stash.generator = TaskGenerator(create_text_df(text))
            stash.generator.run_pipeline(is_shuffle=False)
        if len(stash.tasks_types) < 2:
            stash.tasks_types = stash.generator.get_tasks_types()
        st.subheader('Выберите правильные варианты пропущенных слов:')
        stash.tasks = create_tasks(stash.seed)

    render_tasks(stash.tasks)
