# Product Overview: PJJ Tax & Legal AI System

## Vision

To empower tax and legal professionals with an intelligent, verifiable, and efficient AI assistant for navigating complex Vietnamese tax and legal compliance. By leveraging a curated knowledge base and a human-in-the-loop workflow, the system aims to minimize errors, reduce research time, and enhance the quality of advisory services.

## Mission

To provide a multi-agent AI system that offers accurate, citation-backed tax advice, facilitating compliance and strategic decision-making for businesses operating in Vietnam.

## Target Audience

-   **Tax and Legal Advisors**: Professionals requiring quick, accurate, and verifiable information on Vietnamese tax regulations and precedents.
-   **Businesses in Vietnam**: Companies seeking to understand and comply with local tax laws, especially those dealing with complex international transactions (e.g., Transfer Pricing).

## Key Features

The system is built around a 6-step tax advisory workflow, designed to emulate and assist human experts:

1.  **Request Categorization**: Automatically classifies user queries into relevant tax domains (e.g., CIT, VAT, DTA, Transfer Pricing).
2.  **Past Response Search**: Searches a database of curated past advisory memoranda for similar cases.
3.  **Past Response Review & Selection**: Allows human users to review and select relevant past responses.
4.  **Tax Database Search**: Recommends relevant official tax regulations (circulars, decrees, laws) from a comprehensive database.
5.  **Document Review & Selection**: Enables human users to select the most pertinent regulatory documents.
6.  **Response Synthesis & Citation**: Generates a professional, KPMG-style memorandum, backed by citations from the selected documents, ensuring verifiability and preventing hallucinations.

## Architectural Highlights

-   **Multi-Agent System**: Specialized agents handle different stages of the workflow.
-   **Constraint-based Search**: Agents operate within strict boundaries, ensuring responses are derived only from the approved knowledge base.
-   **Human-in-the-Loop (HITL)**: Critical review and approval stages are built into the workflow, combining AI efficiency with human expertise.
-   **Verifiable Output**: All generated advice includes direct citations to source documents.
-   **Scalable Knowledge Base**: Utilizes a structured database of over 3,400 Vietnamese tax documents and past advisory cases.

## Technology Stack (Summary)

-   **LLM**: Llama 3.3 70B Instruct (via Fireworks AI)
-   **Frontend**: Streamlit
-   **Backend**: Python
-   **Data Storage**: Local file system (structured directories for tax documents and past responses)

## Business Value

-   **Accuracy & Compliance**: Reduces risks associated with misinterpretation of tax laws.
-   **Efficiency**: Significantly cuts down the time spent on research and drafting advisory memos.
-   **Consistency**: Ensures a uniform quality and approach to tax advice.
-   **Knowledge Leverage**: Makes the vast internal knowledge base easily accessible and actionable.

## Future Roadmap Considerations

-   **Enhanced UI/UX**: Further improvements to the Streamlit interface for a more intuitive user experience.
-   **Broader Coverage**: Expansion to include more legal domains beyond tax.
-   **Advanced Analytics**: Integration of data analytics for trends and insights from advisory data.
-   **Multi-user Support**: Implementing robust user management and collaboration features.
