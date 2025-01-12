from warnings import filterwarnings
filterwarnings("ignore", message="flaml.automl is not available.*")

import os
from autogen import ( # type: ignore
    ConversableAgent, 
    GroupChat, 
    GroupChatManager, 
    register_function
)
from datetime import datetime, timezone
from json import dump
from dotenv import load_dotenv # type: ignore
from prompts import (
    SYSTEM_PROMPT_AGENT_INGESTION, DESCRIPTION_AGENT_INGESTION, 
    SYSTEM_PROMPT_AGENT_RETRIEVE, DESCRIPTION_AGENT_RETRIEVE, 
    SYSTEM_PROMPT_AGENT_ANSWER, DESCRIPTION_AGENT_ANSWER, 
    SYSTEM_PROMPT_AGENT_ROUTER, DESCRIPTION_AGENT_ROUTER, 
)
from tools_ingestion import path_to_db, text_to_db
from tools_retrieve import retrieve_str


#####################
### Configuration ###
#####################

load_dotenv()
llm_config = {
    "config_list": [
        {
            "model": "gpt-4o-mini", 
            "api_key": os.environ["OPENAI_API_KEY"], 
            "temperature": 0.7,
            # "cache_seed": None
        }
    ]
}


#########################
### Agents definition ###
#########################

human = ConversableAgent(
    name = "human",
    system_message = '',
    description = "You are a human user.",
    human_input_mode = "ALWAYS",
)

agent_ingestion = ConversableAgent(
    name = "agent_ingestion",
    system_message = SYSTEM_PROMPT_AGENT_INGESTION,
    description = DESCRIPTION_AGENT_INGESTION,
    llm_config = llm_config,
    human_input_mode = "NEVER",
    silent=False
)

agent_retrieve = ConversableAgent(
    name = "agent_retrieve",
    system_message = SYSTEM_PROMPT_AGENT_RETRIEVE,
    description = DESCRIPTION_AGENT_RETRIEVE,
    llm_config = llm_config,
    human_input_mode = "NEVER",
    silent=False
)

agent_answer = ConversableAgent(
    name = "agent_answer",
    system_message = SYSTEM_PROMPT_AGENT_ANSWER,
    description = DESCRIPTION_AGENT_ANSWER,
    llm_config = llm_config,
    human_input_mode = "NEVER",
    silent=False
)

agent_router = ConversableAgent(
    name = "agent_router",
    system_message = SYSTEM_PROMPT_AGENT_ROUTER,
    description = DESCRIPTION_AGENT_ROUTER,
    llm_config = llm_config,
    human_input_mode = "NEVER",
)


####################
### Adding tools ###
####################

register_function(
    path_to_db,
    caller=agent_ingestion,  
    executor=agent_ingestion,  
    name="path_to_db",  
    description="Ingest new knowledge from a text file given its path.", 
)

register_function(
    text_to_db,
    caller=agent_ingestion,  
    executor=agent_ingestion,  
    name="text_to_db",  
    description="Ingest new knowledge from a piece of conversation.",
)

register_function(
    retrieve_str,
    caller=agent_retrieve,  
    executor=agent_retrieve,  
    name="retrieve_str",  
    description="Retrieve useful information from internal DB.",
)


#########################
### Nested group chat ###
#########################

group_chat = GroupChat(
    agents = [
        agent_router,
        agent_ingestion, 
        agent_retrieve, 
        agent_answer
    ],
    messages=[],
    send_introductions=False,
    max_round=10,
    speaker_selection_method="auto", 
    speaker_transitions_type="allowed", 
    allowed_or_disallowed_speaker_transitions={
        agent_router: [agent_ingestion, agent_retrieve, agent_answer],
        agent_ingestion: [agent_router],
        agent_retrieve: [agent_answer],
        agent_answer: [agent_router],
    }, 
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config, 
    silent=False, 
    is_termination_msg=lambda msg: "(to human)" in msg["content"].lower()
)

nested_chats = [
    {
        "recipient": group_chat_manager,
        "summary_method": "last_msg",
    }
]

agent_router.register_nested_chats(
    nested_chats,
    trigger=lambda sender: sender in [human],
)


################################################################################
################################################################################
################################################################################


if __name__ == "__main__":
    chat_results = human.initiate_chat(
        agent_router, 
        message=input("Ciao! How can I assist you today? 😊 : "), 
        max_turns = 100
    )
    tms_now = datetime.now(timezone.utc).strftime("%d_%B_%Y_%H_%M_%S_%Z_%z")
    with open("chat_logs/%s.json" % (tms_now), "w") as f:
        dump({
            "chat_history": chat_results.chat_history, 
            "nested_chat": list(group_chat_manager.chat_messages.values())[-1]
        }, f, indent=4)

