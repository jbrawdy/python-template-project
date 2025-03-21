// Main JavaScript file
document.addEventListener("DOMContentLoaded", () => {
  const todoInput = document.getElementById("newTodo");
  const addButton = document.getElementById("addTodo");
  const todoList = document.getElementById("todoList");

  // Load existing todos
  loadTodos();

  // Add new todo
  addButton.addEventListener("click", () => addTodo());
  todoInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      addTodo();
    }
  });

  async function loadTodos() {
    try {
      const response = await fetch("/api/todos");
      const todos = await response.json();

      todoList.innerHTML = "";
      todos.forEach((todo) => {
        addTodoToList(todo);
      });
    } catch (error) {
      console.error("Error loading todos:", error);
    }
  }

  async function addTodo() {
    const task = todoInput.value.trim();
    if (!task) return;

    try {
      const response = await fetch("/api/todos", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ task }),
      });

      if (!response.ok) {
        throw new Error("Failed to add todo");
      }

      const todo = await response.json();
      addTodoToList(todo);
      todoInput.value = "";
    } catch (error) {
      console.error("Error adding todo:", error);
    }
  }

  async function completeTodo(id) {
    try {
      const response = await fetch(`/api/todos/${id}`, {
        method: "PUT",
      });

      if (!response.ok) {
        throw new Error("Failed to complete todo");
      }

      const todoItem = document.querySelector(`[data-id="${id}"]`);
      if (todoItem) {
        todoItem.style.opacity = "0";
        setTimeout(() => todoItem.remove(), 300);
      }
    } catch (error) {
      console.error("Error completing todo:", error);
    }
  }

  function addTodoToList(todo) {
    const li = document.createElement("li");
    li.className = "todo-item";
    li.dataset.id = todo.id;

    const checkbox = document.createElement("div");
    checkbox.className = "todo-checkbox";
    checkbox.addEventListener("click", () => completeTodo(todo.id));

    const text = document.createElement("span");
    text.className = "todo-text";
    text.textContent = todo.task;

    li.appendChild(checkbox);
    li.appendChild(text);

    todoList.insertBefore(li, todoList.firstChild);
  }
});
