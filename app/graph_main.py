from langgraph.graph import StateGraph
from app.utils.classes import State
from app.nodes.node_funcs import init_user, pdf_is, ans, just_talk, search_in_documents, rewrite_query


graph = StateGraph(State)

#NODES
graph.add_node('get_user', init_user)
graph.add_node('write_in_vbd', pdf_is)
graph.add_node('final', ans)
graph.add_node('talk', just_talk)
graph.add_node('rewrite', rewrite_query)
graph.add_node('search', search_in_documents)

#edges
graph.add_conditional_edges('get_user', lambda x: x['mode'], {
    'FileStates:waiting_for_file': 'write_in_vbd', 'FileStates:talking': 'talk',
    'FileStates:waiting_for_text_search': 'rewrite'
})
graph.add_edge('write_in_vbd', 'final')
graph.add_edge('rewrite', 'search')



#points
graph.set_entry_point('get_user')
graph.set_finish_point('final')
graph.set_finish_point('talk')
graph.set_finish_point('search')

'''app = graph.compile()

graph_image = app.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(graph_image)
'''
