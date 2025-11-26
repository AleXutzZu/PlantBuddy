from server.model.AgentState import AgentState
from server.model.PlantCareCard import PlantCareCard

STRUCTURE_PROMPT_TEMPLATE = """
You are a botanical research assistant. A user wants to know about a specific plant.
You have been given a list of search results from the internet and also information that you already know and trust.

Your *only* job is to parse this information and extract the data to perfectly populate the `PlantCareCard` schema.
Do not add any conversational text. Do not make up information. Where there might be a conflict, rely on the internal knowledge you have.
Also use internal knowledge to fill whatever you cannot fill, if the information you have is suitable.
If some information is missing (e.g., "vase_type"), use `None` if the schema allows it, or do your best to infer a sensible default (e.g., "Standard pot" for `vase_type` if it's a common houseplant).

Internal Knowledge:
{internal_knowledge}

Search Results:
{web_knowledge}
"""

ARTICLE_PROMPT_TEMPLATE = """
You are a friendly and knowledgeable gardening expert which just received a structured data card (`PlantCareCard`) 
with all the key facts about a plant.

Your task is to write a beautiful, engaging, and helpful article for a beginner gardener based *only* on this information.
Start with a warm welcome, introduce the plant by its common and latin name, and then weave its care instructions (temperature, lighting, watering, soil) into a friendly, easy-to-read guide.
Don't forget to mention any common diseases to watch out for! Make it sound encouraging and fun.
Make sure to: 
- use appropriate titles and subtitles
- use bulleted/ordered lists if applicable
- bold important words
- use nicely spaced paragraphs
- Provide this article in markdown format, including all formatting necessary (such as # for titles, and ** for bold etc.)

Here is the data card:
{plant_card_json}
"""

from langchain_core.messages import SystemMessage, HumanMessage


def retrieve_internal_node(state, config):
    vector_store = config["configurable"]["vector_store"]
    prediction = state["plant_name"]


    docs = vector_store.similarity_search(prediction, k=2)

    knowledge_text = "\n".join([d.page_content for d in docs])

    return {"internal_knowledge": knowledge_text}


def predict_node(state: AgentState, config):
    img = state.get("image_buffer")
    if img is None:
        raise RuntimeError(f"Image buffer not found for agent state: {state}")

    predictor = config["configurable"]["predictor"]

    class_name, score = predictor.predict(img)

    return {
        "image_buffer": None,
        "plant_name": class_name,
    }


def search_web_node(state: AgentState, config):
    query = state['plant_name']

    search_queries = [
        f"care instructions for {query}",
        f"scientific name and common name for {query}",
        f"ideal temperature and lighting for {query}",
        f"common diseases and pests for {query}",
        f"ideal soil type for {query}",
    ]

    results = []

    tavily = config["configurable"]["tavily"]

    for q in search_queries:
        response = tavily.search(query=q, max_results=2)
        for r in response["results"]:
            results.append(r["content"])

    search_results_text = "\n".join([str(res) for res in results])

    return {"web_knowledge": search_results_text}


def structure_node(state: AgentState, config):
    web_knowledge = state.get("web_knowledge")
    internal_knowledge = state.get("internal_knowledge")

    llm = config["configurable"]["llm"]

    structured_llm = llm.with_structured_output(PlantCareCard)

    try:
        generated_card = structured_llm.invoke([
            SystemMessage(content=STRUCTURE_PROMPT_TEMPLATE.format(internal_knowledge=internal_knowledge, web_knowledge=web_knowledge)),
            HumanMessage(content=f"Please generate a PlantCareCard with the information you have"),
        ])

        return {"plant_card": generated_card}

    except Exception as e:
        print(f"Error generating structured output: {e}")
        return {"plant_card": None}


def write_article(state: AgentState, config):
    plant_card = state.get("plant_card", None)

    llm = config["configurable"]["llm"]

    if not plant_card:
        article_text = "I'm sorry, I wasn't able to find detailed information or generate a care card for that plant."
        return {
            "article": article_text,
        }

    article = llm.invoke([
        SystemMessage(content=ARTICLE_PROMPT_TEMPLATE.format(plant_card_json=plant_card.model_dump_json(indent=2))),
    ])

    article_text = article.content

    return {
        "article": article_text,
    }
