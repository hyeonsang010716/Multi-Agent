from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
@tool
def chart_generator(command: str):
    """이 도구는 create_pandas_dataframe_agent를 사용하여 차트를 생성하고 차트를 /charts 폴더에 저장합니다."""
    stock_data = pd.read_csv(DATA_DIR / "stock_data.csv") # csv 위치로 가져오기
    finance_data = pd.read_csv(DATA_DIR / "finance_data.csv") # csv 위치로 가져오기
    custom_prefix = """
    Please make the chart and save in './charts' folder.
    stock_data path is './data/stock_data.csv'.
    finance_data path is './data/finance_data.csv'
    """
    agent = create_pandas_dataframe_agent(
        ChatOpenAI(model_name="gpt-4o"), #모델 지정 
        [stock_data, finance_data], # 데이터 지정
        verbose=True, #과정
        allow_dangerous_code=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        prefix=custom_prefix # AI에게 주는 힌트
    )
    result = agent.invoke(command)
    return result
