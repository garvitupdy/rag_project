import streamlit as st
import tempfile
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from vector_db_manager import VectorDBManager

load_dotenv()


st.set_page_config(
    page_title="PDF Q&A Assistant",
    page_icon="📚",
    layout="wide"
)

if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_pdf_hash' not in st.session_state:
    st.session_state.current_pdf_hash = None
if 'current_pdf_metadata' not in st.session_state:
    st.session_state.current_pdf_metadata = None
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = VectorDBManager()

st.title("📚 PDF Q&A Assistant")
st.markdown("Upload a PDF and ask questions about its content!")

# Sidebar
with st.sidebar:
    st.header("📄 PDF Management")
    
    
    all_pdfs = st.session_state.db_manager.list_all_pdfs()
    
    if all_pdfs:
        st.subheader("📚 Your Library")
        
        for pdf_info in all_pdfs:
            with st.expander(f"📖 {pdf_info['filename'][:30]}..."):
                st.write(f"**Pages:** {pdf_info['num_pages']}")
                st.write(f"**Chunks:** {pdf_info['num_chunks']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Load", key=f"load_{pdf_info['hash']}", use_container_width=True):
                        vectorstore = st.session_state.db_manager.load_vectorstore(pdf_info['hash'])
                        st.session_state.vectorstore = vectorstore
                        st.session_state.current_pdf_hash = pdf_info['hash']
                        st.session_state.current_pdf_metadata = pdf_info
                        st.session_state.chat_history = []
                        st.success(f"Loaded: {pdf_info['filename']}")
                        st.rerun()
                
                with col2:
                    if st.button("Delete", key=f"del_{pdf_info['hash']}", use_container_width=True):
                        if st.session_state.db_manager.delete_pdf(pdf_info['hash']):
                            if st.session_state.current_pdf_hash == pdf_info['hash']:
                                st.session_state.vectorstore = None
                                st.session_state.current_pdf_hash = None
                                st.session_state.current_pdf_metadata = None
                                st.session_state.chat_history = []
                            st.success("Deleted successfully!")
                            st.rerun()
        
        st.markdown("---")
    
    
    st.subheader("➕ Add New PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        if st.button("Process PDF", type="primary", use_container_width=True):
            with st.spinner("Processing PDF..."):
                try:
                    pdf_content = uploaded_file.getvalue()
                    pdf_hash = st.session_state.db_manager.get_pdf_hash(pdf_content)
                    

                    if st.session_state.db_manager.pdf_exists(pdf_hash):
                        st.info("📋 This PDF is already in your library! Loading it...")
                        vectorstore = st.session_state.db_manager.load_vectorstore(pdf_hash)
                        metadata = st.session_state.db_manager.get_metadata(pdf_hash)
                    else:

                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(pdf_content)
                            tmp_path = tmp_file.name
                        

                        pdf_hash, metadata = st.session_state.db_manager.process_pdf(
                            tmp_path, pdf_content, uploaded_file.name
                        )
                        
                        
                        vectorstore = st.session_state.db_manager.load_vectorstore(pdf_hash)
                        

                        os.unlink(tmp_path)
                        
                        st.success("✅ PDF processed and saved!")
                    
                    # Set as current
                    st.session_state.vectorstore = vectorstore
                    st.session_state.current_pdf_hash = pdf_hash
                    st.session_state.current_pdf_metadata = metadata
                    st.session_state.chat_history = []
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Show current PDF
    st.markdown("---")
    if st.session_state.current_pdf_metadata:
        st.success("📖 **Current PDF:**")
        st.write(f"**{st.session_state.current_pdf_metadata['filename']}**")
        st.write(f"Pages: {st.session_state.current_pdf_metadata['num_pages']}")
        st.write(f"Chunks: {st.session_state.current_pdf_metadata['num_chunks']}")
    else:
        st.warning("⚠️ No PDF loaded")

# Main chat interface
if st.session_state.vectorstore is not None:
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Chat History")
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            with st.container():
                st.markdown(f"**You:** {question}")
                st.markdown(f"**AI:** {answer}")
                st.markdown("---")
    
  
    st.markdown("### ❓ Ask a Question")
    
    with st.form(key="question_form", clear_on_submit=True):
        user_question = st.text_input(
            "Enter your question:",
            placeholder="What is this document about?",
            label_visibility="collapsed"
        )
        submit_button = st.form_submit_button("Ask", type="primary")
        
        if submit_button and user_question:
            with st.spinner("Thinking..."):
                try:
                   
                    retriever = st.session_state.vectorstore.as_retriever(
                        search_type="mmr",
                        search_kwargs={
                            "k": 4,
                            "fetch_k": 10,
                            "lambda_mult": 0.5
                        }
                    )
                    

                    docs = retriever.invoke(user_question)
                    
                    
                    context = "\n\n".join([doc.page_content for doc in docs])
                    

                    prompt = ChatPromptTemplate.from_messages([
                        (
                            "system",
                            """You are a helpful AI assistant.

Use ONLY the provided context to answer the question.

If the answer is not present in the context,
say: "I could not find the answer in the document."
"""
                        ),
                        (
                            "human",
                            """Context:
{context}

Question:
{question}
"""
                        )
                    ])
                    
                   
                    llm = ChatMistralAI(model="mistral-small-2506")
                    
                   
                    final_prompt = prompt.invoke({
                        "context": context,
                        "question": user_question
                    })
                    
                    response = llm.invoke(final_prompt)
                    answer = response.content
                    

                    st.session_state.chat_history.append((user_question, answer))
                    

                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")

else:
    st.info("👈 Please select or upload a PDF from the sidebar to get started!")
    
    st.markdown("### 📝 Example Questions You Can Ask:")
    st.markdown("""
    - What is the main topic of this document?
    - Summarize the key points
    - What are the conclusions?
    - Explain [specific concept] mentioned in the document
    """)


st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Powered by LangChain, OpenAI, Mistral AI & Streamlit</div>",
    unsafe_allow_html=True
)
