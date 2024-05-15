# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long, missing-function-docstring
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

from dataset_generator_langchain import generate_answer
from deep_memory_implementation import load_vector_store, get_answer


from global_variables import (
    YAML_FILE,
    HUB_NAME,
    TRAINED_CORPUS,
    DB_NAME,
    OUTPUT_TEXT_DEEP_MEMORY,
    OUTPUT_TEXT_WITHOUT_DEEP_MEMORY,
    DATASET_NAME_CHOSEN,
)

# LINK_WEBSITE = """
#             Visit <a href="https://www.activeloop.com/activeloop/deep_memory_legal_train_dataset">Activeloop Legal Dataset</a> and run the output query to discover the chunks.\n
#             Visit <a href="https://www.activeloop.com/activeloop/deep_memory_biomed_train_dataset">Activeloop Biomedical Dataset</a> and run the output query to discover the chunks.\n
#             Visit <a href="https://www.activeloop.com/activeloop/deep_memory_finance_train_dataset">Activeloop Finance Dataset</a> and run the output query to discover the chunks.
#             """
DATASETS_NAME = [name for name in YAML_FILE["db"].keys()]
choices = [
    YAML_FILE["db"][DATASETS_NAME[0]]["label"]
    + " : "
    + YAML_FILE["db"][DATASETS_NAME[0]]["name"],
    YAML_FILE["db"][DATASETS_NAME[1]]["label"]
    + " : "
    + YAML_FILE["db"][DATASETS_NAME[1]]["name"],
    YAML_FILE["db"][DATASETS_NAME[2]]["label"]
    + " : "
    + YAML_FILE["db"][DATASETS_NAME[2]]["name"],
]

internal_dataset_path = {
    choices[0]: YAML_FILE["db"][DATASETS_NAME[0]]["name"],
    choices[1]: YAML_FILE["db"][DATASETS_NAME[1]]["name"],
    choices[2]: YAML_FILE["db"][DATASETS_NAME[2]]["name"],
}


def create_model_output(question, deep_memory_available, dataset_choice):
    print(f"entered with {deep_memory_available}")
    global OUTPUT_TEXT_DEEP_MEMORY
    global OUTPUT_TEXT_WITHOUT_DEEP_MEMORY
    chunks_answer = get_answer(
        TRAINED_CORPUS, question, deep_memory=deep_memory_available
    )
    texts = chunks_answer["text"]
    scores = chunks_answer["score"]
    ids = chunks_answer["id"]

    output_text = (
        f"The model with Deep Memory and {dataset_choice} has answered: \n"
        if deep_memory_available
        else f"The model without Deep Memory and dataset {dataset_choice} has answered: \n"
    )
    if deep_memory_available:
        OUTPUT_TEXT_DEEP_MEMORY = output_text
    else:
        OUTPUT_TEXT_WITHOUT_DEEP_MEMORY = output_text

    for single_chunk in generate_answer(texts, question):
        if deep_memory_available:
            OUTPUT_TEXT_DEEP_MEMORY += single_chunk
            output_text = OUTPUT_TEXT_DEEP_MEMORY
        else:
            OUTPUT_TEXT_WITHOUT_DEEP_MEMORY += single_chunk
            output_text = OUTPUT_TEXT_WITHOUT_DEEP_MEMORY
        yield (
            OUTPUT_TEXT_DEEP_MEMORY,
            OUTPUT_TEXT_WITHOUT_DEEP_MEMORY,
            "No runnable queries...",
        )

    url_format = "select * where id == "
    error_message = "I cannot generate an answer"

    if not error_message in output_text:
        # OUTPUT_QUERY = LINK_WEBSITE + "and run the query!"
        query = [url_format + "'" + id + "'" for id in ids]
        percentage = [str(round(el * 100, 2)) for el in scores]
        sources = "\n\n📝 Here are the sources I used to answer your question:\n Check the chunks running the following queries:\n\n"

        sources_percentage = [
            f"{single_sources_url}, relevance score: {single_scores} %"
            for single_sources_url, single_scores in zip(query, percentage)
        ]
        if deep_memory_available:
            # TODO REMOVE PASS AND UNCOMMENT
            pass
            # OUTPUT_TEXT_DEEP_MEMORY += "\n" + sources + "\n".join(sources_percentage)
        else:
            # TODO uncomment this
            # OUTPUT_TEXT_WITHOUT_DEEP_MEMORY += (
            #     "\n" + sources + "\n".join(sources_percentage)
            # )
            # TODO Remove this
            pass
        # output_text += "\n" + sources + "\n".join(sources_percentage)
        db_query_link = str(DB_NAME).split(" : ")[0]
        link_query = YAML_FILE["db"][DATASET_NAME_CHOSEN]["query_link"]
        yield (OUTPUT_TEXT_DEEP_MEMORY, OUTPUT_TEXT_WITHOUT_DEEP_MEMORY, link_query)

        # return output_text


def process_input(dataset_choice, question, markdown):
    global TRAINED_CORPUS
    global DB_NAME
    global YAML_FILE
    global internal_dataset_path
    global OUTPUT_TEXT_DEEP_MEMORY
    global OUTPUT_TEXT_WITHOUT_DEEP_MEMORY
    global DATASET_NAME_CHOSEN
    global DATASETS_NAME

    # only the first time o when the dataset is changed
    if DB_NAME is None or DB_NAME != internal_dataset_path[dataset_choice]:
        DB_NAME = internal_dataset_path[dataset_choice]
        if DB_NAME == YAML_FILE["db"][DATASETS_NAME[0]]["name"]:
            DATASET_NAME_CHOSEN = DATASETS_NAME[0]
        elif DB_NAME == YAML_FILE["db"][DATASETS_NAME[1]]["name"]:
            DATASET_NAME_CHOSEN = DATASETS_NAME[1]
        elif DB_NAME == YAML_FILE["db"][DATASETS_NAME[2]]["name"]:
            DATASET_NAME_CHOSEN = DATASETS_NAME[2]

        print(f"\nLoading the {DB_NAME}...")
        yield (
            "Loading the dataset from the Activeloop Org...",
            "Loading the dataset from the Activeloop Org...",
            "\n\nWaiting...",
        )
        TRAINED_CORPUS = load_vector_store(HUB_NAME, DB_NAME)

    OUTPUT_TEXT_DEEP_MEMORY = "Generating the answer..."
    OUTPUT_TEXT_WITHOUT_DEEP_MEMORY = "Waiting..."
    yield (OUTPUT_TEXT_DEEP_MEMORY, OUTPUT_TEXT_WITHOUT_DEEP_MEMORY, "\n\nWaiting...")

    for (
        partial_output_dm,
        partial_output_without_dm,
        output_query_link,
    ) in create_model_output(question, True, dataset_choice):
        yield (partial_output_dm, partial_output_without_dm, output_query_link)

    for (
        partial_output_dm,
        partial_output_without_dm,
        output_query_link,
    ) in create_model_output(question, False, dataset_choice):
        yield (partial_output_dm, partial_output_without_dm, output_query_link)

    return


# Gradio Interface
iface = gr.Interface(
    fn=process_input,
    inputs=[
        gr.Dropdown(
            [choices[0], choices[1], choices[2]],
            label="Choose the Dataset",
        ),
        # gr.Checkbox(label="Deep Memory", info="Do you want to use Deep Memory?"),
        gr.Textbox(
            lines=1,
            scale=3,
            label="Ask a question!",
        ),  # Casella di testo per l'input
        gr.Markdown(
            f"""Some useful informations: \n 
                    {YAML_FILE["db"][DATASETS_NAME[0]]["model_performance_info"]}\n
                    {YAML_FILE["db"][DATASETS_NAME[1]]["model_performance_info"]}\n
                    {YAML_FILE["db"][DATASETS_NAME[2]]["model_performance_info"]}\n
                    {YAML_FILE["db"][DATASETS_NAME[3]]["link"]}\n"""
        ),
    ],
    outputs=[
        gr.Textbox(
            lines=1,
            scale=3,
            label="Model with Deep Memory!",
        ),
        gr.Textbox(
            lines=1,
            scale=3,
            label="Model without Deep Memory!",
        ),
        gr.Markdown(""),
    ],
    title="LLM and Deep Memory for RAG Applications",
    # article=LINK_WEBSITE,
)


# Avvia l'interfaccia Gradio
if __name__ == "__main__":
    iface.queue()
    iface.launch(share=True)
