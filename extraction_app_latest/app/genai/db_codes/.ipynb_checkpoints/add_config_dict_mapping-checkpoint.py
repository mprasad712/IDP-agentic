def map_fields(header, line, config_name):
    # Initialize the dictionary structure
    a = {
        'field_info': {
            'config_name': config_name,
            'standard_dict': ['File_Name'],
            'custom_dict': [],
            'custom_dict_datatype': [],
            'table_static_dict': [],
            'table_custom_dict': [],
            'table_custom_fields_mapping_name': [],
            'custom_dict_mapping': [],
            'datatype_standard_dict': ['File_Name|text'],
            'datatype_custom_dict': []
        }
    }

    # Map headers to the custom dictionary
    for key in header.keys():
        a['field_info']['custom_dict'].append(key)
        a['field_info']['custom_dict_datatype'].append('alphanumeric')
        a['field_info']['datatype_custom_dict'].append(f"{key}|alphanumeric")

    # Map lines to the table custom dictionary
    for key in line.keys():
        a['field_info']['table_custom_dict'].append(f"{key}|text")

    return a

# # Example header and line input
# header = {'invoice_number', 'invoice_amount'}
# line = {'tax_rates', 'description'}

# # Map the fields
# mapped_dict = map_fields(header, line)

# # Print the resulting dictionary
# print(mapped_dict)
