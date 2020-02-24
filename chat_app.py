from flask import Flask
from flask import jsonify
from flask import request
from logging.handlers import RotatingFileHandler
from chat_service import chat
from config import Config
import logging


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

@app.route("/chat", methods=['POST'])
def login():
    data = request.get_json()
    question = data['text']
    text = chat(question)
    answer = [{"text":text}]
    qa = "Q:::{0},A:::{1}".format(question,text)
    app.logger.error(qa)
    return jsonify({"answer": answer})  # 返回布尔值



class RequestFormatter(logging.Formatter):  # 自定义格式化类
    def format(self, record):
        record.url = request.url  # 获取请求的url
        record.remote_addr = request.remote_addr  # 获取客户端的ip
        return super().format(record)  # 执行父类的默认操作

def create_logger():
    qa_logger = logging.getLogger('flask.app')
    qa_logger.setLevel(logging.WARNING)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(fmt='[%(asctime)s]    [%(message)s]')
    console_handler.setFormatter(console_formatter)
    qa_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler('logs/qa.log', maxBytes=100 * 1024 * 1024, backupCount=10)  # 转存文件处理器  当达到限定的文件大小时, 可以将日志转存到其他文件中
    file_formatter = RequestFormatter(fmt='[%(asctime)s]    [%(message)s]')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.WARNING)
    qa_logger.addHandler(file_handler)

if __name__ == '__main__':
    create_logger()
    app.run()

