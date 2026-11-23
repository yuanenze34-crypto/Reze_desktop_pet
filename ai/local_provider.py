import json
import random
from ai.provider import AIProvider
from pet.settings import ROOT

class LocalProvider(AIProvider):
    def __init__(self):
        try:
            self.lines = json.loads((ROOT / 'config/dialogue.json').read_text(encoding='utf-8'))
            if not isinstance(self.lines, dict):
                self.lines = {}
        except (OSError, ValueError):
            self.lines = {}

    def phrase(self, topic):
        choices = self.lines.get(topic)
        if not isinstance(choices, list) or not choices or not all(isinstance(x, str) for x in choices):
            return '我在这里陪着你。'
        return random.choice(choices)

    def reply(self, message):
        text = message.lower()
        for topic, words in [('sleep', ('睡', '困', '晚安', 'sleep')), ('work', ('工作', '学习', '累', 'work')), ('hello', ('你好', 'hello', 'hi'))]:
            if any(word in text for word in words):
                return self.phrase(topic)
        return self.phrase('default')
