## Context.py
### 1. we have used pydantic library in this
### 2. This is for data validation , parsing and serialization
### 3. This becomes very much needed in the Financial context
### 4. This file desscribes types for variables for example ticker and company names are meant to be strings
### 5. This is like a rulebook for important variables that our product will use
### 6. If invalid data is assigned,Pydantic raises clear errors

## Budget.py
### 1. We have discussed about tokens in our terminology.md
### 2. The budget.py file has functions to implement all budget functions.When we assign a job to an agent we need to check whether they are using tokens in limit.This will prevent the system from being to expensive

