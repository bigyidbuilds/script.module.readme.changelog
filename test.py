

import re

# S = "```\ntest line od code\n```"
# S = "`test`and`another text`"
# S = "**bold** anther **bold**"
# S = "**bold** *itlic* **bold** "
# S = "*italic* **bold** *italic*"
S = "*italic* text *another italic*"
# S = "```\ntest line od code\n``` \n`test` and `another text`\n **bold** *itlic* **bold** *italic* **bold** *italic*"
for S in ["```\ntest line of code\n```","`test`and`another text`","**Bold** anther **bold**","**bold** *itlic* **bold** ","*italic* **bold** *italic*","*italic* text *another italic* *check*"]:
	print(S)
	B=re.compile(r'\*\*[a-zA-Z0-9\s]*\*\*').findall(S)
	I=re.compile(r'\*(?!\*|\s)[a-zA-Z0-9\s]*\*(?!\*)').findall(S)
	T=re.compile(r'(\~\~.+?\~\~)').findall(S)
	C=re.compile(r'`(?!`)(?!`).+?`(?!`)(?!`)').findall(S)
	CB=re.compile(r'```.+?```',flags=re.DOTALL).findall(S)


	print(S,B,'bold')
	print(S,I,'italic')
	print(S,T,'strikethrough')
	print(S,C,'code')
	print(S,CB,'code block')
	print('_________________________new item__________________')