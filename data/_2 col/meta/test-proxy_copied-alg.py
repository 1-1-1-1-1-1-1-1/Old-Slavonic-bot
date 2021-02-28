Python 3.8.0 (tags/v3.8.0:fa919fd, Oct 14 2019, 19:37:50) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> 

>>> class Proxy:      
#создаем класс
    proxy_url = 'http://www.ip-adress.com/proxy_list/'     
#переменной присваиваем ссылку сайта, выставляющего прокси-сервера
    proxy_list = []      
#пустой массив для заполнения 

    def __init__(self):       
#функция конструктора класса с передачей параметра self	
        r = requests.get(self.proxy_url)      
#http-запрос методом get, запрос нужно осуществлять только с полным url
        str = html.fromstring(r.content)      
#преобразование документа к типу lxml.html.HtmlElement
        result = str.xpath("//tr[@class='odd']/td[1]/text()")      
#берем содержимое тега вместе с внутренними тегами для получение списка прокси
        for i in result:       
#перебираем все найденные прокси
            if i in massiv:      
#если есть совпадение с прокси уже использованными
                yy = result.index(i)       
#переменная равна индексу от совпавшего прокси в result
                del result[yy]      
#удаляем в result этот прокси
        self.list = result      
#конструктору класса приравниваем прокси
        
    def get_proxy(self):
#функция с передачей параметра self
        for proxy in self.list:
#в цикле перебираем все найденные прокси
            if 'https://'+proxy == proxy1:
#проверяем, совпдает ли до этого взятый прокси с новым, если да:
                    global massiv
#massiv объявляем глобальным 
                    massiv = massiv + [proxy]
#добавляем прокси к массиву
            url = 'https://'+proxy
#прибавляем протокол к прокси
            return url
#возвращаем данные

        
>>> # (Copied from https://habr.com/ru/post/322608/)
>>> 
>>> # Changing style...
>>> class Proxy:
	proxy_url = 'http://www.ip-adress.com/proxy_list/'  # переменной присваиваем ссылку сайта, выставляющего прокси-сервера
	proxy_list = []  # пустой массив для заполнения

	def __init__(self):
		r = requests.get(self.proxy_url)
		# http-запрос методом get, запрос нужно осуществлять только с полным url
		str = html.fromstring(r.content)
		# преобразование документа к типу lxml.html.HtmlElement

		result = str.xpath("//tr[@class='odd']/td[1]/text()")
		#берем содержимое тега вместе с внутренними тегами для получения списка прокси

		for i in result: #перебираем все найденные прокси
			if i in massiv: #если есть совпадение с прокси уже использованными
				yy = result.index(i)
				# переменная равна индексу от совпавшего прокси в result
				del result[yy]
				# удаляем в result этот прокси
		self.list = result
		# конструктору класса приравниваем прокси

	def get_proxy(self):  # функция с передачей параметра self
		for proxy in self.list:  # в цикле перебираем все найденные прокси
			if 'https://' + proxy == proxy1:  # проверяем, совпдает ли до этого взятый прокси с новым, если да:

				global massiv # massiv объявляем глобальным
				massiv = massiv + [proxy] # добавляем прокси к массиву
			url = 'https://' + proxy  # прибавляем протокол к прокси
		return url  # возвращаем данные  #?!

	
>>> class Proxy:
	proxy_url = 'http://www.ip-adress.com/proxy_list/'
	proxy_list = []

	def __init__(self):
		r = requests.get(self.proxy_url)
		str = html.fromstring(r.content)
		# преобразование документа к типу lxml.html.HtmlElement

		result = str.xpath("//tr[@class='odd']/td[1]/text()")
		# берем содержимое тега вместе с внутренними тегами для получения списка прокси

		for i in result:
			if i in massiv:
				yy = result.index(i)
				del result[yy]
		self.list = result  # конструктору класса приравниваем прокси

	def get_proxy(self):
		for proxy in self.list:  # в цикле перебираем все найденные прокси
			if 'https://' + proxy == proxy1:  # проверяем, совпдает ли до этого взятый прокси с новым, если да:

				global massiv
				massiv = massiv + [proxy]
				# добавляем прокси к массиву
			url = 'https://' + proxy
		return url  # возвращаем данные  #?!
