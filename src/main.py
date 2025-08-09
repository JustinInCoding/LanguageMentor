import gradio as gr  # 导入 Gradio 库，用于构建用户界面
from agents.conversation_agent import ConversationAgent  # 导入对话代理类
from agents.scenario_agent import ScenarioAgent  # 导入场景代理类
from utils.logger import LOG  # 导入日志记录工具

# 模型选择选项
MODEL_CHOICES = [
    ("llama3.1:8b-instruct-q8_0", "llama3.1:8b-instruct-q8_0"),
    ("deepseek-r1:7b", "deepseek-r1:7b")
]

# 创建对话代理实例
def create_conversation_agent(model_name):
    return ConversationAgent(model_name=model_name)

# 定义场景代理的选择与调用
def create_scenario_agent(scenario_name, model_name):
    return ScenarioAgent(scenario_name, model_name=model_name)

# 当前模型名称
current_model_name = "llama3.1:8b-instruct-q8_0"

# 初始化对话代理
conversation_agent = create_conversation_agent(current_model_name)

# 模型选择组件
model_dropdown = gr.Dropdown(
    choices=MODEL_CHOICES,
    value=current_model_name,
    label="选择大模型",
    interactive=True
)

def update_model(model_name):
    global current_model_name, conversation_agent
    current_model_name = model_name
    conversation_agent = create_conversation_agent(model_name)
    return f"已切换模型为: {model_name}"

# 处理用户对话的函数
def handle_conversation(user_input, chat_history):
    bot_message = conversation_agent.chat_with_history(user_input)  # 获取聊天机器人的回复
    LOG.info(f"[ChatBot]: {bot_message}")  # 记录聊天机器人的回复
    return bot_message  # 返回机器人的回复

# 获取场景介绍的函数
def get_scenario_intro(scenario):
    with open(f"content/page/{scenario}.md", "r") as file:  # 打开对应场景的介绍文件
        scenario_intro = file.read().strip()  # 读取文件内容并去除多余空白
    return scenario_intro  # 返回场景介绍内容

# 场景代理处理函数，根据选择的场景调用相应的代理
# 移除handle_scenario函数，直接在ChatInterface中使用内联函数

# Gradio 界面构建
with gr.Blocks(title="LanguageMentor 英语私教") as language_mentor_app:
    # 模型选择组件
    model_dropdown.render()
    model_dropdown.change(
        fn=update_model,
        inputs=model_dropdown,
        outputs=[]
    )
    
    with gr.Tab("场景训练"):  # 场景训练标签
        gr.Markdown("## 选择一个场景完成目标和挑战")  # 场景选择说明
        
        # 创建单选框组件
        scenario_radio = gr.Radio(
            choices=[
                ("求职面试", "job_interview"),  # 求职面试选项
                ("酒店入住", "hotel_checkin"),  # 酒店入住选项
            ], 
            label="场景"  # 单选框标签
        )

        scenario_intro = gr.Markdown()  # 场景介绍文本组件
        scenario_chatbot = gr.Chatbot(
            placeholder="<strong>你的英语私教 DjangoPeng</strong><br><br>选择场景后开始对话吧！",  # 聊天机器人的占位符
            height=600,  # 聊天窗口高度
        )

        # 更新场景介绍
        scenario_radio.change(
            fn=get_scenario_intro,
            inputs=scenario_radio,
            outputs=scenario_intro
        )

        # 场景聊天界面
        def scenario_chat_fn(message, history, scenario):
            # 每次对话都创建新的agent实例以确保使用最新模型
            return create_scenario_agent(scenario, current_model_name).chat_with_history(message)

        gr.ChatInterface(
            fn=scenario_chat_fn,
            chatbot=scenario_chatbot,
            additional_inputs=[scenario_radio],
            retry_btn=None,
            undo_btn=None,
            clear_btn="清除历史记录",
            submit_btn="发送"
        )

    with gr.Tab("对话练习"):  # 对话练习标签
        gr.Markdown("## 练习英语对话 ")  # 对话练习说明
        
        conversation_chatbot = gr.Chatbot(
            placeholder="<strong>你的英语私教 DjangoPeng</strong><br><br>想和我聊什么话题都可以，记得用英语哦！",  # 聊天机器人的占位符
            height=800,  # 聊天窗口高度
        )

        def conversation_chat_fn(message, history):
            return conversation_agent.chat_with_history(message)

        gr.ChatInterface(
            fn=conversation_chat_fn,
            chatbot=conversation_chatbot,
            retry_btn=None,
            undo_btn=None,
            clear_btn="清除历史记录",
            submit_btn="发送"
        )

# 启动应用
if __name__ == "__main__":
    language_mentor_app.launch(share=True, server_name="0.0.0.0")  # 启动 Gradio 应用并共享
