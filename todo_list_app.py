"""
Curso Python Full Stack Abril-Mayo 2024
IBM SkillsBuild, de la mano de Bejob
Caso Práctico Final

Autor: Oscar Hidalgo Gutiérrez
Email: oscarhidalgogutierrez@gmail.com
Perfil de LinkedIn: https://www.linkedin.com/in/oscarhidalgo/
Perfil de GitHub: https://github.com/oscarhidalgosica
Enlace GitHub a este programa: https://github.com/oscarhidalgosica/IBMSkillsBuild-Bejob-Python-Full-Stack-2024-Caso-Practico
"""

from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import threading
import webbrowser

app = Flask(__name__)  # Crea la aplicación Flask

class Task:
    def __init__(self, description, completed=False):
        """Constructor de la clase Task, inicializa una nueva tarea con una descripción y estado no completado."""
        self.description = description
        self.completed = completed

    def mark_as_completed(self):
        """Marca la tarea como completada."""
        self.completed = True

    def __str__(self):
        """Devuelve una cadena que representa la tarea, mostrando su descripción y estado (Completada/Pendiente)."""
        return f"{self.description} - {'Completada' if self.completed else 'Pendiente'}"

class ToDoList:
    def __init__(self, use_db=False, db_name='todolist.db'):
        """Constructor de la clase ToDoList, inicializa la lista de tareas y configura la conexión a la base de datos si se requiere."""
        self.tasks = []
        self.use_db = use_db
        if self.use_db:
            self.connection = sqlite3.connect(db_name, check_same_thread=False)
            self.cursor = self.connection.cursor()
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (description TEXT, completed BOOLEAN)''')
            self.connection.commit()
            self.load_tasks_from_db()

    def load_tasks_from_db(self):
        """Carga todas las tareas desde la base de datos al iniciar la aplicación."""
        self.tasks = [Task(description=row[0], completed=bool(row[1])) for row in self.cursor.execute("SELECT * FROM tasks")]

    def add_task(self, description):
        """Añade una nueva tarea a la lista y a la base de datos si está habilitada."""
        task = Task(description)
        self.tasks.append(task)
        if self.use_db:
            self.cursor.execute("INSERT INTO tasks (description, completed) VALUES (?, ?)", (description, False))
            self.connection.commit()

    def mark_task_as_completed(self, index):
        """Marca una tarea como completada tanto en la lista como en la base de datos."""
        self.tasks[index].mark_as_completed()
        if self.use_db:
            self.cursor.execute("UPDATE tasks SET completed = ? WHERE rowid = ?", (True, index + 1))
            self.connection.commit()

    def remove_task(self, index):
        """Elimina una tarea de la lista y de la base de datos si está habilitada."""
        if self.use_db:
            self.cursor.execute("DELETE FROM tasks WHERE rowid = ?", (index + 1,))
            self.connection.commit()
        del self.tasks[index]

    def __del__(self):
        """Cierra la conexión con la base de datos cuando el objeto ToDoList es destruido."""
        if self.use_db:
            self.connection.close()

todo_list = ToDoList(use_db=True)  # Instancia de ToDoList, usa la base de datos

@app.route('/')
def index():
    """Ruta principal que muestra la lista de tareas con opciones para marcar como completadas o eliminarlas."""
    return render_template_string("""
        <h1>To-Do List</h1>
        <ul>
        {% for task in tasks %}
            <li>{{ task.description }} - 
                {% if task.completed %}
                    Completada
                {% else %}
                    <a href="{{ url_for('complete_task', index=loop.index0) }}">Marcar como completada</a>
                {% endif %}
                <a href="{{ url_for('delete_task', index=loop.index0) }}">Eliminar</a>
            </li>
        {% endfor %}
        </ul>
        <form action="/add" method="post">
            <input type="text" name="description" placeholder="Nueva tarea">
            <button type="submit">Agregar Tarea</button>
        </form>
    """, tasks=todo_list.tasks)

@app.route('/add', methods=['POST'])
def add_task():
    """Ruta para agregar una nueva tarea desde la interfaz web."""
    description = request.form.get('description')
    if description:
        todo_list.add_task(description)
    return redirect(url_for('index'))

@app.route('/complete/<int:index>')
def complete_task(index):
    """Ruta para marcar una tarea como completada desde la interfaz web."""
    todo_list.mark_task_as_completed(index)
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_task(index):
    """Ruta para eliminar una tarea desde la interfaz web."""
    todo_list.remove_task(index)
    return redirect(url_for('index'))

def run_web_app():
    """Inicia el servidor web y abre la aplicación en el navegador por defecto."""
    webbrowser.open_new_tab('http://127.0.0.1:5000/')
    app.run(debug=True)

def console_interaction():
    """Interfaz de usuario para la consola, permite gestionar las tareas mediante comandos."""
    while True:
        print("\n--- Lista de Tareas TO-DO ---")
        print("1. Agregar nueva tarea")
        print("2. Marcar tarea como completada")
        print("3. Mostrar todas las tareas")
        print("4. Eliminar una tarea")
        print("5. Salir")
        choice = input("Elige una opción: ")

        if choice == '1':
            description = input("¿Cuál es la descripción de la nueva tarea? ")
            todo_list.add_task(description)
        elif choice == '2':
            index = int(input("¿Cuál es el número de la tarea que quieres marcar como completada? ")) - 1
            if index >= 0 and index < len(todo_list.tasks):
                todo_list.mark_task_as_completed(index)
            else:
                print("Índice fuera de rango.")
        elif choice == '3':
            if todo_list.tasks:
                for i, task in enumerate(todo_list.tasks):
                    print(f"{i + 1}. {task}")
            else:
                print("No hay tareas en tu lista.")
        elif choice == '4':
            index = int(input("¿Cuál es el número de la tarea que quieres eliminar? ")) - 1
            if index >= 0 and index < len(todo_list.tasks):
                todo_list.remove_task(index)
            else:
                print("Índice fuera de rango.")
        elif choice == '5':
            print("¡Nos vemos! Saliendo del programa...")
            break
        else:
            print("Esa opción no es válida. Ingresa un número entre 1 y 5.")

def main():
    """Punto de entrada principal del programa, permite elegir entre interfaz web o consola."""
    mode = input("Selecciona el modo de operación: 'web' para interfaz web, 'console' para consola: ")
    if mode == 'web':
        print("Iniciando la aplicación web...")
        print("Puedes acceder a la aplicación en tu navegador en la siguiente URL: http://127.0.0.1:5000/")
        threading.Thread(target=run_web_app).start()
    elif mode == 'console':
        console_interaction()
    else:
        print("Opción no válida. Ingresa 'web' o 'console'.")

if __name__ == "__main__":
    main()
