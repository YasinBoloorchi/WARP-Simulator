def generate_unique_string(dictionary):
    
    dictionary_keys = list(dictionary.keys())
    dictionary_keys.sort()
    sorted_dictionary = {key: dictionary[key] for key in dictionary_keys}
    key_value_strings = [f"{key}:{value}" for key, value in sorted_dictionary.items()]
    unique_string = ','.join(key_value_strings)
    return unique_string
    



dictionary = {'F0AB':False, 'F0BC':True}
print(generate_unique_string(dictionary))