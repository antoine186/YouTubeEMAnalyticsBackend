import openai

def summarise_from_list_using_chatgpt(list_to_summarise, llm_testing):
    prompt_string = 'Please summarise the following feedback: '
    for text in list_to_summarise:
        prompt_string += text + '. '

    if llm_testing:
        reply = 'Example ChatGPTs response'
    else:
        messages = [ {"role": "system", "content": prompt_string} ]
        chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages, max_tokens=50
            )
        
        reply = chat.choices[0].message.content

    return reply
