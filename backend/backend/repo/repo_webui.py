import gradio as gr
import requests

# 后端 API 配置
BASE_URL = "http://your-api-endpoint"
MODEL_NAME = "DeepSeek-R1"

def get_tree_data(branch, path=""):
    """获取目录内容"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/repo/{MODEL_NAME}/tree/{branch}",
            params={"path": path}
        )
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

def get_file_content(branch, path):
    """获取文件内容"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/repo/{MODEL_NAME}/file/{branch}/{path}"
        )
        return response.text if response.status_code == 200 else "File not found"
    except Exception:
        return "Error fetching file"

def render_file_list(items):
    """生成文件列表 HTML"""
    html = """
    <style>
        .file-table { width: 100%; border: 1px solid #e1e4e8; border-radius: 6px; }
        .file-row { display: flex; padding: 12px 16px; border-bottom: 1px solid #e1e4e8; align-items: center; }
        .file-row:hover { background-color: #f6f8fa; }
        .file-icon { width: 24px; margin-right: 8px; color: #6a737d; }
        .file-name { flex: 1; color: #0969da; cursor: pointer; }
        .file-info { display: flex; gap: 24px; color: #6a737d; }
    </style>
    <div class="file-table">
    """
    
    for item in items:
        icon = "📁" if item["type"] == "dir" else "📄"
        html += f"""
        <div class="file-row" onclick="{'handleDirClick' if item['type'] == 'dir' else 'handleFileClick'}('{item['name']}')">
            <span class="file-icon">{icon}</span>
            <div class="file-name">{item['name']}</div>
            <div class="file-info">
                <span>{item.get('size', '')}</span>
                <span>{item.get('date', '')}</span>
            </div>
        </div>
        """
    html += "</div>"
    return html

def update_file_list(branch, path=""):
    """更新文件列表"""
    data = get_tree_data(branch, path)
    if not data:
        return gr.HTML.update(value="<div>Error loading data</div>"), path
    
    current_path = path
    return gr.HTML.update(value=render_file_list(data["items"])), current_path

def update_file_viewer(branch, path):
    """更新文件查看器"""
    content = get_file_content(branch, path)
    return gr.Code.update(value=content)

with gr.Blocks(css=".gradio-container {max-width: 1280px !important; margin: 0 auto;}") as app:
    # 状态存储
    current_branch = gr.State(value="main")
    current_path = gr.State(value="")
    
    # 头部
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown(f"# deepseek-ai/{MODEL_NAME}")
            gr.Markdown("⭐ 10.9k | 👁️ 43.5k")
        with gr.Column(scale=1):
            with gr.Row():
                gr.Button("Clone", variant="secondary")
                gr.Button("Train", variant="primary")

    # 导航栏
    with gr.Row():
        tabs = gr.Radio(
            ["Files and versions", "Model card", "Merge"],
            value="Files and versions",
            label="Navigation",
            interactive=True
        )

    # 分支选择
    branch_dropdown = gr.Dropdown(
        label="Branch",
        choices=["main", "dev", "test", "release"],
        value="main"
    )

    # 主内容区
    with gr.Tabs(visible=False) as content_tabs:
        with gr.TabItem("Files", id="files"):
            with gr.Column(visible=True) as file_browser:
                file_list = gr.HTML()
                path_display = gr.Textbox(interactive=False, label="Current Path")
            
            with gr.Column(visible=False) as file_viewer:
                back_btn = gr.Button("← Back")
                file_content = gr.Code(language="markdown")

    # 事件处理
    branch_dropdown.change(
        fn=lambda b: update_file_list(b, "")[0],
        inputs=[branch_dropdown],
        outputs=[file_list]
    )

    file_list.change(
        fn=lambda path: gr.Textbox.update(value=path),
        inputs=[current_path],
        outputs=[path_display]
    )

    back_btn.click(
        fn=lambda: (gr.Column.update(visible=True), gr.Column.update(visible=False)),
        outputs=[file_browser, file_viewer]
    )

    # 自定义 JS 处理
    app.load(
        fn=None,
        js="""
        function() {
            window.handleDirClick = (name) => {
                const currentPath = document.querySelector('[data-testid="path_display"]').value;
                const newPath = currentPath ? `${currentPath}/${name}` : name;
                const branch = document.querySelector('[data-testid="branch_dropdown"]').value;
                const event = new CustomEvent('dir-click', { 
                    detail: { branch: branch, path: newPath } 
                });
                document.dispatchEvent(event);
            }
            
            window.handleFileClick = (name) => {
                const currentPath = document.querySelector('[data-testid="path_display"]').value;
                const fullPath = currentPath ? `${currentPath}/${name}` : name;
                const branch = document.querySelector('[data-testid="branch_dropdown"]').value;
                const event = new CustomEvent('file-click', { 
                    detail: { branch: branch, path: fullPath } 
                });
                document.dispatchEvent(event);
            }
        }
        """
    )

    # 自定义事件处理
    app.events.extend([
        {
            "name": "dir-click",
            "fn": lambda evt: update_file_list(evt.detail.branch, evt.detail.path),
            "inputs": [current_branch, current_path],
            "outputs": [file_list, current_path]
        },
        {
            "name": "file-click",
            "fn": lambda evt: (
                gr.Column.update(visible=False),
                gr.Column.update(visible=True),
                update_file_viewer(evt.detail.branch, evt.detail.path)
            ),
            "inputs": [current_branch, current_path],
            "outputs": [file_browser, file_viewer, file_content]
        }
    ])

if __name__ == "__main__":
    app.launch()