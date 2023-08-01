import os
import openai
import pandas as pd

openai.api_key = open('apikey.txt', 'r').read().strip('\n')


def get_completion(message_history, model="gpt-3.5-turbo"):
    """
    Request to OpenAI API chatGPT completion endpoint. 
    User inputs a list of messages, and chatGPT provides a response

    Input
    message_history - list<dict> - History of messages between user and chatGPT
                                   [{"role": "****", "content": prompt}, ...]
    model - str - chatGPT model to use. Default is gpt-3.5-turbo

    Output
    _ - str - response recieved from ChatGPT model
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=message_history,
        temperature=0, # this is the degree of randomness of the model's output
    )

    return response.choices[0].message["content"]


def gpt_conversation(df:object, columns:list):
    """
    High level function to return modified table from generic table

    Input
    df - object - pandas dataframe of table to be modified
    columns - list - columns names to be returned

    Output
    response - str - ChatGPT response
    """
    message_history = []
    response = ''

    try:
        # Let ChatGPT know what the task is
        prompt = 'I have a tables, can you find which columns are similar to one another'
        message_history.append({"role": "user", "content": prompt})
        response = get_completion(message_history)
        message_history.append({"role": "assistant", "content": response})

        # Provide data
        prompt = f'Here is the table <table>{df}</table>'
        message_history.append({"role": "user", "content": prompt})
        response = get_completion(message_history)
        message_history.append({"role": "assistant", "content": response})

        # Transform Data into a single table
        prompt = f'Can you transform the data from the table so it fits into a table with the following columns, and return it to me <table-columns>{columns}</table-columns> using html format only.'
        message_history.append({"role": "user", "content": prompt})
        response = get_completion(message_history)
        message_history.append({"role": "assistant", "content": response})
    
    except:
        print('An error occurred, please try again.')
        return {"message_history": "AN ERROR OCCURRED, PLEASE TRY AGAIN", "response": "AN ERROR OCCURRED, PLEASE TRY AGAIN"}


    return message_history, response


def gpt_step_by_step(df:object, message_history:list=[]):
    """
    GPT functionality where user and ChatGPT work together to process CSV

    Input
    message_history - list - conversation objects between user and ChatGPT
    df - object - pandas dataframe of table to be modified

    Output
    response - str - ChatGPT response
    """

    # If the user has not interacted with ChatGPT, setup the basic formatting rules
    if message_history == []:
        # Let ChatGPT know what the task is
        prompt = 'I have a tables, can you find which columns are similar to one another'
        message_history.append({"role": "user", "content": prompt})
        response = get_completion(message_history)
        message_history.append({"role": "assistant", "content": response})

        # Provide data
        prompt = f'Here is the table <table>{df}</table>'
        message_history.append({"role": "user", "content": prompt})
        response = get_completion(message_history)
        message_history.append({"role": "assistant", "content": response})
    else:
        print(message_history)
        response = get_completion(message_history)
        message_history.append({"role": "assistant", "content": response})

    return message_history




