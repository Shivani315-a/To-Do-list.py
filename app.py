import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- MongoDB setup ---
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["todo_db"]
todos_collection = db["todos"]

USER_CREDENTIALS = {
    "admin": "password123",
    "user1": "mypassword"
}

# --- Helper functions ---

def add_todo(task):
    if task:
        existing = todos_collection.find_one({"task": {"$regex": f"^{task}$", "$options": "i"}})
        if existing:
            return False
        else:
            todos_collection.insert_one({"task": task, "completed": False})
            return True
    return None

def get_todos():
    return list(todos_collection.find())

def update_todo_status(todo_id, status):
    todos_collection.update_one({"_id": ObjectId(todo_id)}, {"$set": {"completed": status}})

def delete_todo(todo_id):
    todos_collection.delete_one({"_id": ObjectId(todo_id)})

# --- Streamlit page config ---
st.set_page_config(page_title="📝 To-Do Application with Login", page_icon="🔐")

# --- Session state for login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# --- Login page ---
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# --- To-Do app page ---
def todo_app():
    st.title(f"📝 To-Do Application - Logged in as {st.session_state.username}")

    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # Add task form
    with st.form(key="todo_form", clear_on_submit=True):
        task = st.text_input("Add a new task", key="task_input", placeholder="Type your task here...")
        submitted = st.form_submit_button("➕ Add Task")

        if submitted:
            success = add_todo(task)
            if success:
                st.success("✅ Task added!")
                st.rerun()
            elif success is False:
                st.warning("⚠️ This task already exists!")

    st.markdown("---")

    todos = get_todos()

    if not todos:
        st.info("🎉 Your to-do list is empty! Add a task above.")
    else:
        for todo in todos:
            col1, col2, col3 = st.columns([0.1, 0.75, 0.15])

            with col1:
                completed = st.checkbox("", value=todo["completed"], key=str(todo["_id"]))
                if completed != todo["completed"]:
                    update_todo_status(todo["_id"], completed)
                    st.rerun()

            with col2:
                task_text = todo["task"]
                if todo["completed"]:
                    st.markdown(f"✔️ <span style='color:green;text-decoration:line-through;'>{task_text}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"🕗 <span style='color:red;'>{task_text}</span>", unsafe_allow_html=True)

            with col3:
                if st.button("❌", key=f"del_{todo['_id']}"):
                    delete_todo(todo["_id"])
                    st.rerun()


if not st.session_state.logged_in:
    login()
else:
    todo_app()
