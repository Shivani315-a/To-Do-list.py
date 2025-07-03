import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- MongoDB Setup ---
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["todo_db"]
tasks_collection = db["tasks"]

# --- Hardcoded Login Credentials ---
USERNAME = "user1"
PASSWORD = "pass123"

# --- Session State Defaults ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- LOGIN PAGE ---
def login_page():
    st.title("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# --- TO-DO APP PAGE ---
def todo_app():
    st.set_page_config(page_title="To-Do App", page_icon="📝")
    st.sidebar.title(f"Welcome, {st.session_state.username}! 👋")
    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # --- DB Functions ---
    def add_task(title):
        if title.strip():
            tasks_collection.insert_one({"title": title.strip(), "completed": False})

    def get_tasks():
        return list(tasks_collection.find())

    def update_task(task_id, completed):
        tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"completed": completed}})

    def delete_task(task_id):
        tasks_collection.delete_one({"_id": ObjectId(task_id)})

    # --- Session State ---
    if "task_input" not in st.session_state:
        st.session_state.task_input = ""
    if "should_rerun" not in st.session_state:
        st.session_state.should_rerun = False

    # --- Callback (Enter Key) ---
    def on_enter_pressed():
        task = st.session_state.task_input.strip()
        if task:
            add_task(task)
            st.session_state.task_input = ""
            st.session_state.should_rerun = True

    # --- Title ---
    st.title("📝 To-Do List App")

    # --- Input ---
    st.text_input("Add a new task", key="task_input", on_change=on_enter_pressed)

    if st.button("➕ Add Task"):
        task = st.session_state.task_input.strip()
        if task:
            add_task(task)
            st.session_state.task_input = ""
            st.session_state.should_rerun = True
        else:
            st.warning("Please enter a task.")

    if st.session_state.should_rerun:
        st.session_state.should_rerun = False
        st.rerun()

    # --- Display Tasks ---
    st.subheader("Your Tasks")
    tasks = get_tasks()

    if not tasks:
        st.info("No tasks yet. Add one above!")
    else:
        for task in tasks:
            cols = st.columns([0.1, 0.8, 0.1])
            checked = cols[0].checkbox("", value=task["completed"], key=str(task["_id"]))
            if checked != task["completed"]:
                update_task(task["_id"], checked)
                st.rerun()
            cols[1].markdown(f"~~{task['title']}~~" if checked else task["title"])
            if cols[2].button("🗑️", key=f"del_{task['_id']}"):
                delete_task(task["_id"])
                st.rerun()

# --- PAGE ROUTING BASED ON LOGIN STATUS ---
if st.session_state.logged_in:
    todo_app()
else:
    login_page()
