PROMPT_TEXT_CHUNKING = ''' 

Rewrite the given text into coherent chunks, each with a short descriptive context. 
In the context provide the main subject of the text and the particular information contained in the chunk. 
Do not shorten the text or remove any information. 
The goal is to enhance structure and clarity while preserving all original content.
For each chunk use this format: 
<chunk>
<context>short context here</context>
<content>section content here</content>
</chunk>
 
'''