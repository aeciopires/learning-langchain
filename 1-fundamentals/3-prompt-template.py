"""PromptTemplate: a reusable prompt with {placeholders}. No model needed.

Run: uv run python 1-fundamentals/3-prompt-template.py
"""

from langchain_core.prompts import PromptTemplate

# A template is like a form letter: the text is fixed and only the fields in
# curly braces change. input_variables lists the fields it expects.
template = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?",
)


def main() -> None:
    # format() fills the placeholders and returns a plain string.
    print(template.format(product="colorful socks"))

    # from_template() infers input_variables from the {placeholders}.
    inferred = PromptTemplate.from_template("Explain {topic} to a {audience} in 3 bullet points.")
    print("Inferred variables:", inferred.input_variables)
    print(inferred.format(topic="Kubernetes", audience="beginner"))


if __name__ == "__main__":
    main()
