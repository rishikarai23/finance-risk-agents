## Important Terms in the context of this project

### Token -
#### 1. A token is not a word but a collection of characters (3-4 letters). So a "unbelievable" is made up of 3 token    "un" , "believ" , "able".
#### 2. Every api call costs a token (input and output) and every model has a hard limit.Taking some famous models into consideration
    1. Gemini-1.5-flash : 1 million tokens
    2. GPt-4o : 128K tokens
#### 3. Every prompt and output must fit inside this range.This range is also called as the context window
#### 4. When this window is filled up the previous parts of the conversation must be deleted.This will result in the model losing/ "forgetting" this information
#### 5. So in my project we will have multiple agents arguing and conversing with each other.All the conversation,arguments and everything is stored under the context window.This will result in the window filling up pretty quickly and the some parts will have to erased leading the model to loose context and hallucinate
#### 6. Hence we will using something called as a context manager.So the manager will manage the context in these 3 levels:
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
#### 2. This will the the agent how to act and what is its job
#### 3. The model treats it as ground truth
#### 4. In production systems it is stored in text files
#### 5. A good prompt ensures that the agent works efficiently and rightly
#### 6. Also always the system prompt must consider the edge cases not just the happy path 




