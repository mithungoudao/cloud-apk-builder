import flet as ft
import sqlite3
import os

# Identify a safe write path on the local Android sandbox file-system
DB_PATH = os.path.join(os.path.expanduser("~"), "todo_cloud.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "Cloud SQLite To-Do"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    init_db()

    # Input Box fields
    task_input = ft.TextField(hint_text="What needs to be done?", expand=True)
    todo_list_container = ft.Column()

    def load_tasks():
        todo_list_container.controls.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, task FROM todos")
        rows = cursor.fetchall()
        
        for row in rows:
            task_id, task_text = row[0], row[1]
            
            def make_delete_handler(t_id=task_id):
                return lambda e: delete_task(t_id)

            todo_list_container.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(task_text, size=18),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color="red",
                            on_click=make_delete_handler()
                        )
                    ]
                )
            )
        conn.close()
        page.update()

    def add_task(e):
        if task_input.value.strip() == "":
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todos (task) VALUES (?)", (task_input.value,))
        conn.commit()
        conn.close()
        task_input.value = ""
        load_tasks()

    def delete_task(task_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        load_tasks()

    # UI Element Layout Mapping
    page.add(
        ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("My Cloud To-Do", size=28, weight=ft.FontWeight.BOLD, color="blue"),
                    ft.Row(
                        controls=[
                            task_input,
                            ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_task),
                        ]
                    ),
                    ft.Divider(),
                    todo_list_container
                ]
            )
        )
    )

    load_tasks()

ft.app(target=main)
