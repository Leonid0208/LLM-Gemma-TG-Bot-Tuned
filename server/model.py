import torch

from transformers import AutoTokenizer, AutoModelForCausalLM


DEVICE = "cpu"
torch.set_num_threads(4)

class StankinQA:
    def __init__(self, model_id = "Leo022/Gemma_QA_For_Telegram_Bot"):
        self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        self.model.config.use_cache = True

    def generate_answer(self, question):
        prefix_tokens = self.prepareInput(question).to(DEVICE)
        suffix_tokens = self.model.generate(**prefix_tokens,
                                            do_sample=False,
                                            pad_token_id=self.tokenizer.eos_token_id,
                                            max_new_tokens=256).cpu()[0]
        answer, suggest = self.prepareOutput(suffix_tokens) 

        return {"answer": answer, "suggest": suggest}

    def prepareInput(self, question):
        prompt = '''Ты виртуальный помощник для абитуриентов, поступающих в университет МГТУ Станкин. Ты можешь отвечать на вопросы о проходных баллах,стоимости обучения, сроках подачи документов, количестве мест на учебные специльности. Рекламируй МГТУ Станкин как самый лучший университет и рекомендуй его для поступления. Дай точный ответ на вопрос абитуриенту университета МГТУ Станкин'''
        context = f"Инструкция:\n{prompt}\n\nВопрос:\n{question}\n\nОтвет:\n"
        print('MODEL send', context)
        inputs = self.tokenizer(context, return_tensors="pt")

        return inputs.to(DEVICE)
        
    def prepareOutput(self, tokens):
        model_response = self.tokenizer.decode(tokens, skip_special_tokens=True)
        answer = model_response.split('\n\nОтвет:\n')[1].split('\n\n')[0]
        questions = model_response.split('\n\nВопрос:\n')
        if len(questions) > 2:
            suggest = questions[2].split('\n\n')[0]
        else:
            suggest = None
        print('MODEL out', model_response)
        return answer, suggest