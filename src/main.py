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

# 全局模型状态
current_model = gr.State("llama3.1:8b-instruct-q8_0")

# 初始化代理
agents = {
    "job_interview": create_scenario_agent("job_interview", "llama3.1:8b-instruct-q8_0"),
    "hotel_checkin": create_scenario_agent("hotel_checkin", "llama3.1:8b-instruct-q8_0"),
    # "salary_negotiation": create_scenario_agent("salary_negotiation", "llama3.1:8b-instruct-q8_0"),
    # "renting": create_scenario_agent("renting", "llama3.1:8b-instruct-q8_0")
}

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
def handle_scenario(user_input, chat_history, scenario):
    bot_message = agents[scenario].chat_with_history(user_input)  # 获取场景代理的回复
    LOG.info(f"[ChatBot]: {bot_message}")  # 记录场景代理的回复
    return bot_message  # 返回场景代理的回复

# Gradio 界面构建
with gr.Blocks(title="LanguageMentor 英语私教") as language_mentor_app:
    with gr.Tab("场景训练"):  # 场景训练标签
        gr.Markdown("## 选择一个场景完成目标和挑战")  # 场景选择说明
        
        # 模型选择组件
        model_dropdown = gr.Dropdown(
            choices=MODEL_CHOICES,
            value="llama3.1:8b-instruct-q8_0",
            label="选择大模型",
            interactive=True
        )
        
        def update_model(model_name):
            # 更新全局模型
            current_model.value = model_name
            # 重新初始化所有代理
            agents["job_interview"] = create_scenario_agent("job_interview", model_name)
            agents["hotel_checkin"] = create_scenario_agent("hotel_checkin", model_name)
            return f"已切换模型为: {model_name}"
            
        model_dropdown.change(
            fn=update_model,
            inputs=model_dropdown,
            outputs=[]
        )

        # 创建单选框组件
        scenario_radio = gr.Radio(
            choices=[
                ("求职面试", "job_interview"),  # 求职面试选项
                ("酒店入住", "hotel_checkin"),  # 酒店入住选项
                # ("薪资谈判", "salary_negotiation"),  # 薪资谈判选项（注释掉）
                # ("租房", "renting")  # 租房选项（注释掉）
            ], 
            label="场景"  # 单选框标签
        )

        scenario_intro = gr.Markdown()  # 场景介绍文本组件
        scenario_chatbot = gr.Chatbot(
            placeholder="<strong>你的英语私教 DjangoPeng</strong><br><br>选择场景后开始对话吧！",  # 聊天机器人的占位符
            height=600,  # 聊天窗口高度
        )

        # 获取场景介绍并启动新会话的函数
        def start_new_scenario_chatbot(scenario):
            initial_ai_message = agents[scenario].start_new_session()  # 启动新会话并获取初始AI消息

            return gr.Chatbot(
                value=[(None, initial_ai_message)],  # 设置聊天机器人的初始消息
                height=600,  # 聊天窗口高度
            )
        
        # 更新场景介绍并在场景变化时启动新会话
        scenario_radio.change(
            fn=lambda s: (get_scenario_intro(s), start_new_scenario_chatbot(s)),  # 更新场景介绍和聊天机器人
            inputs=scenario_radio,  # 输入为选择的场景
            outputs=[scenario_intro, scenario_chatbot],  # 输出为场景介绍和聊天机器人组件
        )

        # 场景聊天界面
        gr.ChatInterface(
            fn=handle_scenario,  # 处理场景聊天的函数
            chatbot=scenario_chatbot,  # 聊天机器人组件
            additional_inputs=[scenario_radio, current_model],  # 额外输入为场景选择和模型
            retry_btn=None,  # 不显示重试按钮
            undo_btn=None,  # 不显示撤销按钮
            clear_btn="清除历史记录",  # 清除历史记录按钮文本
            submit_btn="发送",  # 发送按钮文本
        )

    with gr.Tab("对话练习"):  # 对话练习标签
        gr.Markdown("## 练习英语对话 ")  # 对话练习说明
        
        # 对话练习也使用全局模型选择
        def update_conversation_model(model_name):
            global conversation_agent
            conversation_agent = create_conversation_agent(model_name)
            return f"对话练习模型已切换为: {model_name}"
            
        model_dropdown.change(
            fn=update_conversation_model,
            inputs=model_dropdown,
            outputs=[]
        )
        conversation_chatbot = gr.Chatbot(
            placeholder="<strong>你的英语私教 DjangoPeng</strong><br><br>想和我聊什么话题都可以，记得用英语哦！",  # 聊天机器人的占位符
            height=800,  # 聊天窗口高度
        )

        gr.ChatInterface(
            fn=handle_conversation,  # 处理对话的函数
            chatbot=conversation_chatbot,  # 聊天机器人组件
            retry_btn=None,  # 不显示重试按钮
            undo_btn=None,  # 不显示撤销按钮
            clear_btn="清除历史记录",  # 清除历史记录按钮文本
            submit_btn="发送",  # 发送按钮文本
        )

# 启动应用
if __name__ == "__main__":
    language_mentor_app.launch(share=True, server_name="0.0.0.0")  # 启动 Gradio 应用并共享
