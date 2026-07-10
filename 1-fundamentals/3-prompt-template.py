from langchain_core.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?",
)

text = template.format(product="colorful socks")
print(text)