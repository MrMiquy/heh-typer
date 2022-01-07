from bs4 import BeautifulSoup
import requests, re

class parser_class:
    def __init__(self, lang = 'en'):
        self.page = "https://" + lang + ".wikipedia.org/wiki/Special:Random"
        self.texts = list()
        
    def set_language(self, lang: str):
        self.page = "https://" + lang + ".wikipedia.org/wiki/Special:Random"
        
    def _parse(self):
        self.texts = BeautifulSoup(requests.get(self.page).content, "lxml").find("div", class_ = "mw-parser-output").find_all("p")

        for i in range(len(self.texts)):
            self.texts[i] = self.texts[i].text
            self.texts[i] = re.sub(r'\[[^\]]+\]', '', self.texts[i])
            self.texts[i] = re.sub(r'\([^()]*\)', '', self.texts[i])
            self.texts[i] = re.sub(r'^\s+\n\s+$', '', self.texts[i])

        del self.texts[-1]

    def _count(self):
        temp = 0

        for paragraph in self.texts:
            temp += len(paragraph)

        return temp

    def _is_valid(self, min):
        if self._count() >= min:
            return True
        return False

    def _normalize(self, min):
        if self._is_valid(min):
            string = ""
            for item in self.texts:
                string += ' ' + item
                if len(string) > min:
                    if len(string) > min * 2:
                        string = string.split('. ')
                        qstr = ""
                        for i in range(len(string)):
                            if len(qstr) > min:
                                qstr = qstr.strip()
                                return qstr    
                            qstr += string[i] + ". "
                    else:
                        return string
        else:
            self._parse()
            self._normalize(min)

    def text(self, min = 100):
        self._parse()
        return self._normalize(min)