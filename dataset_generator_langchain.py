from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.chains import LLMChain

prompt_template = "What is a good name for a company that makes {product}?"


def get_chunk_question(context):
    system_message = """
    Generate a question related to the context.
    The input is provided in the following format: 
    Context: [The context that for the generated question] 
    The output is in the following format: 
    #Question#: [Text of the question] 
    The context is: {context}
    """

    client = OpenAI()

    prompt = system_message.format(
        context=context,
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": prompt}],
    )
    response_message = response.choices[0].message.content
    return response_message


def generate_answer(context, question):
    system_message_output_answer = """
        Generate an answer to the question provided in the input using the context provided. They will have the following format:
        Context: ["Context1", "Context2", "Context3", "Context4"]
        Question: [Text of the question]
        The context is: {context}
        The question is: {question}
    """
    # llm = OpenAI(temperature=0)
    llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0, max_tokens=512)

    formatted_message = system_message_output_answer.format(
        context=context, question=question
    )
    for chunk in llm.stream(formatted_message):
        print(chunk, end="", flush=True)
        yield chunk
    # llm_chain = LLMChain(
    #     llm=llm, prompt=PromptTemplate.from_template(system_message_output_answer)
    # )

    # output = llm_chain((context, question))
    # return output["text"]
