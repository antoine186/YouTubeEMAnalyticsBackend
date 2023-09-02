
def summarise_from_list_using_cohere(list_to_summarise, cohere_client, llm_testing):
    prompt_string = 'Please summarise the following feedback: '
    for text in list_to_summarise:
        prompt_string += text + '. '

    if llm_testing:
        reply = 'Example cohere response'
    else:
        response = cohere_client.generate(
            model='command-xlarge-nightly',
            prompt=prompt_string,
            max_tokens=50,
            temperature=0.9,
            k=0,
            p=0.75,
            frequency_penalty=0,
            presence_penalty=0,
            stop_sequences=[],
            return_likelihoods='NONE')
        
        reply = response.generations[0].text

    return reply
