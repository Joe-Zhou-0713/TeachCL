# TeachCL lesson-plan co-design assistant

一个用于协助教师共同设计 lesson plan 的 Streamlit 原型。应用通过 OpenAI Responses API 调用 `gpt-5.4`（可用 `OPENAI_MODEL` 环境变量覆盖），以 `prompts/System_Prompt.txt` 作为聊天助手指令。会话完成后，可运行教师互动编码、互动模式识别、反思反馈和雷达图生成。

## 项目结构

```text
app.py                         Streamlit 页面与流程编排
llm_client.py                  OpenAI API 客户端
interaction_tracker.py         教师发言编码与频次统计
pattern_detector.py            会话互动模式识别
feedback_generator.py          反思反馈生成与格式校验
scaffold_selector.py            生成可视化与下一步建议数据
conversation_export.py         对话与分析材料落盘
prompts/
  System_Prompt.txt            聊天助手 system prompt
  Coding_Prompt.txt            A1–D2 互动编码 prompt
  Pattern_Detection_Prompt.txt 互动模式识别 prompt
  Scaffolding Feedback.txt     反馈生成 prompt
  archive/                     原有模式识别 prompt 草稿（保留，不参与运行）
visualization/                  本地雷达图及其他图表
outputs/                        对话记录、分析结果和图表
```

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

在侧边栏输入 OpenAI API key。密钥只用于当前 Streamlit 会话，不会保存到项目文件。默认模型为 `gpt-5.4`；如需指定有权限使用的模型，可设置 `OPENAI_MODEL`。

## GitHub Codespaces

`.devcontainer/devcontainer.json` 为 Codespaces 安装项目依赖并转发 Streamlit 的 8501 端口；入口兼容仓库根目录的 `app.py`、`visualization_feedback_scripts_py/app.py` 和 `visualization_scripts/app.py`。Codespaces 预览参数只用于开发容器。若部署到 Streamlit Community Cloud，应在部署设置中选择实际的入口文件，并使用仓库中的 `requirements.txt`。

## 分析流程与输出

聊天消息会按教师/助手角色传给 system prompt。点击 **Analyze and generate visualization** 后，应用依次：

1. 只对教师发言应用 A1、A2、B1、B2、B3、B4、B5、C1、D2 编码，允许一条发言有多个编码。
2. 结合完整对话和编码结果判断一个主要互动模式。
3. 生成面向本次对话的反思反馈，并把九类编码频次画在雷达图上。
4. 将聊天记录保存为 `outputs/conversation_<session_id>.txt`、`.md` 和 `.json`；页面也提供 `.txt` 下载按钮。编码、模式、反馈与图表信息保存为 `outputs/analysis_<session_id>.json`，图表也保存在 `outputs/`。

编码和模式只是对可观察对话的描述，不是教师能力评分。每次分析会覆盖当前会话对应的 analysis JSON；每次聊天更新会覆盖该会话对应的 conversation 文本、JSON 和 Markdown 文件。

在本地运行时，记录写入项目的 `outputs/` 文件夹。部署到 Streamlit Community Cloud 时，写入的是云端运行环境，不会同步到 GitHub 或本机；平台也不保证这些运行时生成的文件跨会话保留。因此请从页面下载 `.txt` 对话稿，若要长期自动保存多位参与者的材料，需要后续接入持久化数据库或云存储。

## 依赖

`requirements.txt` 列出了运行所需的 Streamlit、OpenAI Python SDK、Matplotlib 和 NumPy。
