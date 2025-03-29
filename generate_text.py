import requests
import json
from models_and_keys import keys, urls
def generate_text(prompt, md_enable=False, enter_enable=False, content="",
                  model="deepseek-v3-250324", max_tokens=1000, temperature=0.7,
                  word_limit=-1, history=[]):
    url = urls[model]
    headers = {
        "Content-Type": "application/json",
        "Authorization": keys[model]
    }
    if not md_enable:
        prompt = "去除markdown格式 " + prompt
    if not enter_enable:
        prompt = "去除换行符用纯文本回复 " + prompt
    if word_limit != -1:
        prompt = "控制回复字数在" + str(word_limit) + "字以内 " + prompt
    # 构建消息历史
    messages = [{"role": "system", "content": content}]
    messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    # 发送请求
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # 处理响应
    if response.status_code == 200:
        result = response.json()
        response_message = result["choices"][0]["message"]
        # 将本次对话加入历史
        history.append({"role": "user", "content": prompt})
        history.append(response_message)
        return {"status": "success", "text": response_message["content"], "history": history}
    else:
        return {"status": "error"}
