import gradio as gr

from backend.chat.gradio_webui import app as chat_app
from backend.repo.repo_webui import app as repo_app


with gr.Blocks() as demo:
    with demo.route("chat"):
       chat_app.render()
    with demo.route("repo"):
        repo_app.render()

if __name__ == "__main__":
    demo.launch()