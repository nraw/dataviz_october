def get_markdown_info(G, node):
    if node:
        title = f"#### {node}"
        info = G.node[node]
        text_info_list = [f"##### {field}:\n{value}" for field, value in info.items()]
        text_info = '\n'.join(text_info_list)
        markdown_info = title + '\n' + text_info
    else:
        markdown_info = None
    return markdown_info