## Important Terms in the context of this project

### Token -
#### 1. A token is not a word but a collection of characters (3-4 letters). So a "unbelievable" is made up of 4 tokens "unb" , "eli" , "eva" , "ble".
#### 2. Every api call costs a token (input and output) and every model has a hard limit.Taking some famous models into consideration
    1. Gemini-1.5-flash : 1 million tokens
    2. GPt-4o : 128K tokens
#### 3. Every prompt and output must fit inside this range.This range is also called as the context window
#### 4. When this window is filled up the previous parts of the conversation must be deleted.This will result in the model losing/ "forgetting" this information
#### 5. So in my project we will have multiple agents arguing and conversing with each other.All the conversation,arguments and everything is stored under the context window.This will result in the window filling up pretty quickly and the some parts will have to be erased leading the model to loose context and hallucinate
#### 6. Hence we will be using something called as a context manager.So the manager will manage the context in these 3 levels:
    1. Short term - last 2 rounds are kept fully intact in the window
    2. Medium term - the previous rounds are compressed into a dense message.like a log less tokens more info
    3. Long term - That info can be stored in a vector database
#### 7. Limitations - 
    1. Compressing the text may lead to loss of fine details
    2. Incase a previous conversation is omitted the agents might keep going over it again and again like an infinite loop
    3. Also summarzing the conversation every interval will increase cost and latency

### Temperature and Sampling
#### 1. Temperature is for how sharp or flat the distribution is
        1. When Temperature is 0: prints highest probability token.It's like a fact checker only facts.Must be deterministic
        2. When Temperature is 0.7-1: Must have some creativity.They improvise within the style.
        3. When Temperature is 2 : sample wildly,often incoherent
#### 2. Top-P (Nucleus Sampling)
        1. Top-P limits the pool of choices before the temperature is applied. 
        2. A setting of `top_p=0.95` tells the model to only consider the top 95% of the most likely tokens, cutting off the bottom 5% of absolute nonsense.
        3. This acts as a safety net. It ensures that even at higher creative temperatures (0.7–1.0), the model is physically blocked from choosing completely irrelevant words.
#### So when we are making agents suppose for particular application.When we have a team of agents the fact-checker will have a temperature of 0,0.7 for the researcher for creative angles(you know to add a little jazz),Skeptic 0.5 so that not that much jazz but structured and should be able to argue

### System Prompt
#### 1. This the the invisible prompt given to the model.Its like a job description which usally is given to the employees on their first day.
#### 2. This will tell the agent how to act and what is its job
#### 3. The model treats it as ground truth
#### 4. In production systems it is stored in text files
#### 5. A good prompt ensures that the agent works efficiently and rightly
#### 6. Also always the system prompt must consider the edge cases not just the happy path 

### Tool Use Internals
#### 1. An LLM cannot run a tool.A tool can be run by our code and code alone.
#### 2. So a user sends a system prompt,the user prompt and a list of tools
#### 3. A model will return what tool to use
#### 4. Our code will validate if the its safe to use the tool,then will execute the python program for the tool,will catch exception and format the result
#### 5. Then user will send back the result to the model or stop the program
#### 6. Model will return either another toolcall or fisnish the execution(finish_call == true)
#### 7. Is repeated till task is completed

### Embeddings and Vector Search
#### 1. The long term memory of the model is stored in something called as a vector db
#### 2. When we want to store certain sentence or a certain word.The embedding algorithm will convert the input in 768 numbers(vectors)
#### 3. These vectors encode the meaning of the text and not its words.So "king" and "queen" are near to each other.Compared to "Apple the fruit" and "Apple the company" this is placed very far from each other
#### 4. To find if the query is similar to a stored text we use something called as the dot product or cosine similarity.The highest score in all of the vector db will win.Chromadb can be used for this

### Model Memory
#### 1. <i>In context memory<i>:The conversation history is inside the context window.This memory gets deleted when the program stops running.Has a limited length and temporary
#### 2. <i>External Memory<i>:The long term history which is stored in the vectordb.This survives restart and is semantically searchable
#### 3. <i>Procedural Memory<i>: the agent's skills and rules, baked into its identity. Can't be updated at runtime. Used for: agent roles, output formats, behavioral constraints.System prompt files
#### 4. <i> Episodic Memory<i>: a database of what happened: which agent said what, in which round, with what confidence score. Used for: audit trail, building the final report, evaluating agent quality over time.






